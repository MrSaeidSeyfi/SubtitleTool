import logging
import numpy as np
from typing import List, Tuple, Dict
from sklearn.cluster import KMeans
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import silhouette_score
import librosa
from src.models.subtitle import Subtitle

logger = logging.getLogger(__name__)

class SpeakerDiarizer:
    """Speaker diarization using voice clustering"""
    
    def __init__(self, n_speakers: int = 2, min_segment_duration: float = 0.5):
        """
        Initialize speaker diarizer
        
        Args:
            n_speakers: Number of speakers to detect (default: 2)
            min_segment_duration: Minimum segment duration in seconds
        """
        self.n_speakers = n_speakers
        self.min_segment_duration = min_segment_duration
        self.scaler = StandardScaler()
        self.kmeans = None
        self.speaker_colors = {
            0: 'yellow',  # First speaker
            1: 'white',   # Second speaker
            2: 'cyan',    # Third speaker (if needed)
            3: 'magenta', # Fourth speaker (if needed)
        }
    
    def extract_voice_features(self, audio_path: str, segments: List[Subtitle]) -> Tuple[np.ndarray, List[int]]:
        """
        Extract voice features from audio segments
        
        Args:
            audio_path: Path to audio file
            segments: List of subtitle segments with timestamps
            
        Returns:
            Tuple of (features, segment_indices)
        """
        try:
            logger.info("Loading audio file...")
            # Load audio with higher sample rate for better feature extraction
            audio, sr = librosa.load(audio_path, sr=16000)
            
            features = []
            segment_indices = []
            
            for i, segment in enumerate(segments):
                # Extract audio segment
                start_sample = int(segment.start_time * sr)
                end_sample = int(segment.end_time * sr)
                
                if start_sample >= len(audio) or end_sample > len(audio):
                    continue
                
                segment_audio = audio[start_sample:end_sample]
                
                if len(segment_audio) < sr * self.min_segment_duration:
                    continue
                
                try:
                    # Extract MFCC features
                    mfcc = librosa.feature.mfcc(y=segment_audio, sr=sr, n_mfcc=13)
                    
                    # Extract additional features with proper error handling
                    spectral_centroid = librosa.feature.spectral_centroid(y=segment_audio, sr=sr)
                    spectral_bandwidth = librosa.feature.spectral_bandwidth(y=segment_audio, sr=sr)
                    spectral_rolloff = librosa.feature.spectral_rolloff(y=segment_audio, sr=sr)
                    zero_crossing_rate = librosa.feature.zero_crossing_rate(segment_audio)
                    
                    # Ensure all features are 1D arrays and have proper dimensions
                    mfcc_mean = np.mean(mfcc, axis=1)
                    mfcc_std = np.std(mfcc, axis=1)
                    
                    # Handle potential empty arrays
                    spectral_centroid_mean = np.mean(spectral_centroid) if spectral_centroid.size > 0 else 0.0
                    spectral_bandwidth_mean = np.mean(spectral_bandwidth) if spectral_bandwidth.size > 0 else 0.0
                    spectral_rolloff_mean = np.mean(spectral_rolloff) if spectral_rolloff.size > 0 else 0.0
                    zero_crossing_rate_mean = np.mean(zero_crossing_rate) if zero_crossing_rate.size > 0 else 0.0
                    
                    # Combine features into a single array
                    segment_features = np.concatenate([
                        mfcc_mean,
                        mfcc_std,
                        [spectral_centroid_mean],
                        [spectral_bandwidth_mean],
                        [spectral_rolloff_mean],
                        [zero_crossing_rate_mean]
                    ])
                    
                    # Ensure the feature array is 1D and has consistent length
                    if segment_features.ndim == 1 and len(segment_features) > 0:
                        features.append(segment_features)
                        segment_indices.append(i)
                    else:
                        logger.warning(f"Skipping segment {i}: invalid feature dimensions")
                        
                except Exception as e:
                    logger.warning(f"Error extracting features from segment {i}: {e}")
                    continue
            
            if not features:
                raise ValueError("No valid audio segments found")
            
            # Ensure all feature arrays have the same length
            feature_lengths = [len(f) for f in features]
            if len(set(feature_lengths)) > 1:
                logger.warning(f"Inconsistent feature lengths: {feature_lengths}")
                # Use the most common length
                most_common_length = max(set(feature_lengths), key=feature_lengths.count)
                features = [f for f in features if len(f) == most_common_length]
                segment_indices = [idx for i, idx in enumerate(segment_indices) if len(features[i]) == most_common_length]
            
            features_array = np.array(features)
            logger.info(f"Extracted features from {len(features)} segments")
            
            return features_array, segment_indices
            
        except Exception as e:
            logger.error(f"Error extracting voice features: {e}")
            raise
    
    def cluster_speakers(self, features: np.ndarray) -> np.ndarray:
        """
        Cluster speakers using K-means
        
        Args:
            features: Voice features array
            
        Returns:
            Cluster labels for each segment
        """
        try:
            # Normalize features
            features_scaled = self.scaler.fit_transform(features)
            
            # Determine optimal number of clusters if not specified
            if self.n_speakers is None:
                self.n_speakers = self._find_optimal_clusters(features_scaled)
            
            # Perform clustering
            self.kmeans = KMeans(n_clusters=self.n_speakers, random_state=42, n_init=10)
            labels = self.kmeans.fit_predict(features_scaled)
            
            logger.info(f"Clustered {len(features)} segments into {self.n_speakers} speakers")
            return labels
            
        except Exception as e:
            logger.error(f"Error clustering speakers: {e}")
            raise
    
    def _find_optimal_clusters(self, features: np.ndarray, max_clusters: int = 5) -> int:
        """
        Find optimal number of clusters using silhouette score
        
        Args:
            features: Scaled features
            max_clusters: Maximum number of clusters to try
            
        Returns:
            Optimal number of clusters
        """
        best_score = -1
        best_n_clusters = 2
        
        for n_clusters in range(2, min(max_clusters + 1, len(features))):
            try:
                kmeans = KMeans(n_clusters=n_clusters, random_state=42, n_init=10)
                labels = kmeans.fit_predict(features)
                
                if len(np.unique(labels)) > 1:
                    score = silhouette_score(features, labels)
                    if score > best_score:
                        best_score = score
                        best_n_clusters = n_clusters
                        
            except Exception as e:
                logger.warning(f"Error evaluating {n_clusters} clusters: {e}")
                continue
        
        logger.info(f"Optimal number of clusters: {best_n_clusters} (silhouette score: {best_score:.3f})")
        return best_n_clusters
    
    def assign_speakers(self, audio_path: str, segments: List[Subtitle]) -> List[Subtitle]:
        """
        Assign speakers to subtitle segments
        
        Args:
            audio_path: Path to audio file
            segments: List of subtitle segments
            
        Returns:
            List of subtitle segments with speaker assignments
        """
        try:
            logger.info("Starting speaker diarization...")
            
            # Check if we have enough segments for clustering
            if len(segments) < 2:
                logger.warning("Not enough segments for speaker diarization, assigning all to speaker 0")
                for segment in segments:
                    segment.speaker_id = 0
                    segment.speaker_color = self.speaker_colors[0]
                return segments
            
            # Extract voice features
            features, segment_indices = self.extract_voice_features(audio_path, segments)
            
            # Check if we have enough features
            if len(features) < 2:
                logger.warning("Not enough valid features for clustering, assigning all to speaker 0")
                for segment in segments:
                    segment.speaker_id = 0
                    segment.speaker_color = self.speaker_colors[0]
                return segments
            
            # Cluster speakers
            labels = self.cluster_speakers(features)
            
            # Assign speakers to segments
            for i, segment_idx in enumerate(segment_indices):
                speaker_id = int(labels[i])
                segments[segment_idx].speaker_id = speaker_id
                segments[segment_idx].speaker_color = self.speaker_colors.get(speaker_id, 'white')
                
                logger.debug(f"Segment {segment_idx}: Speaker {speaker_id} ({segments[segment_idx].speaker_color})")
            
            # Assign default speaker to segments that weren't processed
            for i, segment in enumerate(segments):
                if not hasattr(segment, 'speaker_id') or segment.speaker_id is None:
                    segment.speaker_id = 0
                    segment.speaker_color = self.speaker_colors[0]
                    logger.debug(f"Segment {i}: Assigned to default speaker 0")
            
            # Log speaker statistics
            speaker_counts = {}
            for segment in segments:
                if hasattr(segment, 'speaker_id'):
                    speaker_id = segment.speaker_id
                    speaker_counts[speaker_id] = speaker_counts.get(speaker_id, 0) + 1
            
            logger.info("Speaker assignment completed:")
            for speaker_id, count in speaker_counts.items():
                color = self.speaker_colors.get(speaker_id, 'white')
                logger.info(f"  Speaker {speaker_id} ({color}): {count} segments")
            
            return segments
            
        except Exception as e:
            logger.error(f"Error in speaker diarization: {e}")
            logger.info("Falling back to single speaker assignment")
            # Fallback: assign all segments to speaker 0
            for segment in segments:
                segment.speaker_id = 0
                segment.speaker_color = self.speaker_colors[0]
            return segments
    
    def get_speaker_info(self, segments: List[Subtitle]) -> Dict[int, Dict]:
        """
        Get information about detected speakers
        
        Args:
            segments: List of subtitle segments with speaker assignments
            
        Returns:
            Dictionary with speaker information
        """
        speaker_info = {}
        
        for segment in segments:
            if hasattr(segment, 'speaker_id'):
                speaker_id = segment.speaker_id
                if speaker_id not in speaker_info:
                    speaker_info[speaker_id] = {
                        'color': segment.speaker_color,
                        'segments': 0,
                        'total_duration': 0.0,
                        'first_appearance': segment.start_time,
                        'last_appearance': segment.end_time
                    }
                
                speaker_info[speaker_id]['segments'] += 1
                speaker_info[speaker_id]['total_duration'] += segment.duration
                speaker_info[speaker_id]['first_appearance'] = min(
                    speaker_info[speaker_id]['first_appearance'], 
                    segment.start_time
                )
                speaker_info[speaker_id]['last_appearance'] = max(
                    speaker_info[speaker_id]['last_appearance'], 
                    segment.end_time
                )
        
        return speaker_info 