import logging
import requests
import json
from typing import List, Optional
from src.models.subtitle import Subtitle
from config.constants import MAX_TRANSLATION_BATCH_SIZE

logger = logging.getLogger(__name__)

class TranslationService:
	"""Handles subtitle translation using Hugging Face API"""
	
	SUPPORTED_LANGUAGES = [
		'ace_Arab', 'ace_Latn', 'acm_Arab', 'acq_Arab', 'aeb_Arab', 'afr_Latn', 'ajp_Arab', 'aka_Latn', 'amh_Ethi', 'apc_Arab', 'arb_Arab', 'ars_Arab', 'ary_Arab', 'arz_Arab', 'asm_Beng', 'ast_Latn', 'awa_Deva', 'ayr_Latn', 'azb_Arab', 'azj_Latn', 'bak_Cyrl', 'bam_Latn', 'ban_Latn', 'bel_Cyrl', 'bem_Latn', 'ben_Beng', 'bho_Deva', 'bjn_Arab', 'bjn_Latn', 'bod_Tibt', 'bos_Latn', 'bug_Latn', 'bul_Cyrl', 'cat_Latn', 'ceb_Latn', 'ces_Latn', 'cjk_Latn', 'ckb_Arab', 'crh_Latn', 'cym_Latn', 'dan_Latn', 'deu_Latn', 'dik_Latn', 'dyu_Latn', 'dzo_Tibt', 'ell_Grek', 'eng_Latn', 'epo_Latn', 'est_Latn', 'eus_Latn', 'ewe_Latn', 'fao_Latn', 'pes_Arab', 'fij_Latn', 'fin_Latn', 'fon_Latn', 'fra_Latn', 'fur_Latn', 'fuv_Latn', 'gla_Latn', 'gle_Latn', 'glg_Latn', 'grn_Latn', 'guj_Gujr', 'hat_Latn', 'hau_Latn', 'heb_Hebr', 'hin_Deva', 'hne_Deva', 'hrv_Latn', 'hun_Latn', 'hye_Armn', 'ibo_Latn', 'ilo_Latn', 'ind_Latn', 'isl_Latn', 'ita_Latn', 'jav_Latn', 'jpn_Jpan', 'kab_Latn', 'kac_Latn', 'kam_Latn', 'kan_Knda', 'kas_Arab', 'kas_Deva', 'kat_Geor', 'knc_Arab', 'knc_Latn', 'kaz_Cyrl', 'kbp_Latn', 'kea_Latn', 'khm_Khmr', 'kik_Latn', 'kin_Latn', 'kir_Cyrl', 'kmb_Latn', 'kon_Latn', 'kor_Hang', 'kmr_Latn', 'lao_Laoo', 'lvs_Latn', 'lij_Latn', 'lim_Latn', 'lin_Latn', 'lit_Latn', 'lmo_Latn', 'ltg_Latn', 'ltz_Latn', 'lua_Latn', 'lug_Latn', 'luo_Latn', 'lus_Latn', 'mag_Deva', 'mai_Deva', 'mal_Mlym', 'mar_Deva', 'min_Latn', 'mkd_Cyrl', 'plt_Latn', 'mlt_Latn', 'mni_Beng', 'khk_Cyrl', 'mos_Latn', 'mri_Latn', 'zsm_Latn', 'mya_Mymr', 'nld_Latn', 'nno_Latn', 'nob_Latn', 'npi_Deva', 'nso_Latn', 'nus_Latn', 'nya_Latn', 'oci_Latn', 'gaz_Latn', 'ory_Orya', 'pag_Latn', 'pan_Guru', 'pap_Latn', 'pol_Latn', 'por_Latn', 'prs_Arab', 'pbt_Arab', 'quy_Latn', 'ron_Latn', 'run_Latn', 'rus_Cyrl', 'sag_Latn', 'san_Deva', 'sat_Beng', 'scn_Latn', 'shn_Mymr', 'sin_Sinh', 'slk_Latn', 'slv_Latn', 'smo_Latn', 'sna_Latn', 'snd_Arab', 'som_Latn', 'sot_Latn', 'spa_Latn', 'als_Latn', 'srd_Latn', 'srp_Cyrl', 'ssw_Latn', 'sun_Latn', 'swe_Latn', 'swh_Latn', 'szl_Latn', 'tam_Taml', 'tat_Cyrl', 'tel_Telu', 'tgk_Cyrl', 'tgl_Latn', 'tha_Thai', 'tir_Ethi', 'taq_Latn', 'taq_Tfng', 'tpi_Latn', 'tsn_Latn', 'tso_Latn', 'tuk_Latn', 'tum_Latn', 'tur_Latn', 'twi_Latn', 'tzm_Tfng', 'uig_Arab', 'ukr_Cyrl', 'umb_Latn', 'urd_Arab', 'uzn_Latn', 'vec_Latn', 'vie_Latn', 'war_Latn', 'wol_Latn', 'xho_Latn', 'ydd_Hebr', 'yor_Latn', 'yue_Hant', 'zho_Hans', 'zho_Hant', 'zul_Latn'
	]
	
	def __init__(self, api_url: str = "https://saeidseyfi-hf-translator.hf.space/translate_batch"):
		"""
		Initialize translation service
		
		Args:
			api_url: Hugging Face API endpoint URL for batch translation
		"""
		self.api_url = api_url
		self.headers = {"Content-Type": "application/json"}
	
	def is_language_supported(self, language_code: str) -> bool:
		"""
		Check if language code is supported
		
		Args:
			language_code: Language code to check
			
		Returns:
			True if language is supported
		"""
		return language_code in self.SUPPORTED_LANGUAGES
	
	def get_supported_languages(self) -> List[str]:
		"""
		Get list of supported language codes
		
		Returns:
			List of supported language codes
		"""
		return self.SUPPORTED_LANGUAGES.copy()
	
	def translate_text(self, text: str, src_lang: str, tgt_lang: str) -> str:
		"""
		Translate single text using batch API (for backward compatibility)
		
		Args:
			text: Text to translate
			src_lang: Source language code
			tgt_lang: Target language code
			
		Returns:
			Translated text
			
		Raises:
			Exception: If translation fails
		"""
		try:
			if not self.is_language_supported(src_lang):
				raise ValueError(f"Unsupported source language: {src_lang}")
			if not self.is_language_supported(tgt_lang):
				raise ValueError(f"Unsupported target language: {tgt_lang}")
			
			# Use batch API for single text
			translations = self.translate_batch_texts([text], src_lang, tgt_lang)
			return translations[0] if translations else ""
				
		except Exception as e:
			logger.error(f"Translation failed: {e}")
			raise
	
	def _chunk_texts(self, texts: List[str], chunk_size: int) -> List[List[str]]:
		"""
		Split texts into chunks of specified size
		
		Args:
			texts: List of texts to chunk
			chunk_size: Maximum size of each chunk
			
		Returns:
			List of text chunks
		"""
		return [texts[i:i + chunk_size] for i in range(0, len(texts), chunk_size)]
	
	def translate_batch_texts(self, texts: List[str], src_lang: str, tgt_lang: str) -> List[str]:
		"""
		Translate multiple texts using batch API with automatic chunking
		
		Args:
			texts: List of texts to translate
			src_lang: Source language code
			tgt_lang: Target language code
			
		Returns:
			List of translated texts
			
		Raises:
			Exception: If batch translation fails
		"""
		try:
			if not self.is_language_supported(src_lang):
				raise ValueError(f"Unsupported source language: {src_lang}")
			if not self.is_language_supported(tgt_lang):
				raise ValueError(f"Unsupported target language: {tgt_lang}")
			
			if not texts:
				return []
			
			# Check if we need to chunk the texts
			if len(texts) > MAX_TRANSLATION_BATCH_SIZE:
				logger.info(f"Large batch detected ({len(texts)} texts), splitting into chunks of {MAX_TRANSLATION_BATCH_SIZE}")
				return self._translate_large_batch(texts, src_lang, tgt_lang)
			
			# Filter out empty texts and prepare batch
			valid_texts = [text.strip() for text in texts if text.strip()]
			empty_indices = [i for i, text in enumerate(texts) if not text.strip()]
			
			if not valid_texts:
				# All texts are empty
				return [""] * len(texts)
			
			payload = {
				"texts": valid_texts,
				"src_lang": src_lang,
				"tgt_lang": tgt_lang
			}
			
			logger.debug(f"Translating batch of {len(valid_texts)} texts from {src_lang} to {tgt_lang}")
			
			response = requests.post(
				self.api_url,
				headers=self.headers,
				json=payload,
				timeout=60  # Increased timeout for batch processing
			)
			
			response.raise_for_status()
			
			result = response.json()
			
			if 'translations' in result:
				translations = result['translations']
				
				# Insert empty strings back at their original positions
				final_translations = []
				valid_idx = 0
				
				for i in range(len(texts)):
					if i in empty_indices:
						final_translations.append("")
					else:
						if valid_idx < len(translations):
							final_translations.append(translations[valid_idx])
							valid_idx += 1
						else:
							final_translations.append("")
				
				logger.debug(f"Batch translation successful: {len(final_translations)} texts translated")
				return final_translations
			else:
				raise Exception(f"Unexpected API response format: {result}")
				
		except requests.exceptions.RequestException as e:
			logger.error(f"Batch API request failed: {e}")
			raise Exception(f"Batch translation API request failed: {e}")
		except Exception as e:
			logger.error(f"Batch translation failed: {e}")
			raise
	
	def _translate_large_batch(self, texts: List[str], src_lang: str, tgt_lang: str) -> List[str]:
		"""
		Handle large batches by splitting into chunks and translating each chunk
		
		Args:
			texts: List of texts to translate
			src_lang: Source language code
			tgt_lang: Target language code
			
		Returns:
			List of translated texts
		"""
		chunks = self._chunk_texts(texts, MAX_TRANSLATION_BATCH_SIZE)
		all_translations = []
		
		logger.info(f"Processing {len(chunks)} chunks for {len(texts)} total texts")
		
		for i, chunk in enumerate(chunks):
			try:
				logger.debug(f"Processing chunk {i+1}/{len(chunks)} with {len(chunk)} texts")
				chunk_translations = self.translate_batch_texts(chunk, src_lang, tgt_lang)
				all_translations.extend(chunk_translations)
				
			except Exception as e:
				logger.error(f"Failed to translate chunk {i+1}: {e}")
				# Add empty translations for failed chunk
				all_translations.extend([""] * len(chunk))
		
		return all_translations
	
	def translate_subtitles(self, subtitles: List[Subtitle], src_lang: str, tgt_lang: str) -> List[Subtitle]:
		"""
		Translate list of subtitles using batch API
		
		Args:
			subtitles: List of subtitle objects
			src_lang: Source language code
			tgt_lang: Target language code
			
		Returns:
			List of translated subtitle objects
		"""
		try:
			logger.info(f"Starting batch subtitle translation from {src_lang} to {tgt_lang}")
			
			# Extract all texts for batch translation
			texts = [subtitle.text for subtitle in subtitles]
			
			# Translate all texts in a single batch (with automatic chunking if needed)
			translated_texts = self.translate_batch_texts(texts, src_lang, tgt_lang)
			
			# Create translated subtitle objects
			translated_subtitles = []
			
			for i, (subtitle, translated_text) in enumerate(zip(subtitles, translated_texts)):
				try:
					translated_subtitle = Subtitle(
						start_time=subtitle.start_time,
						end_time=subtitle.end_time,
						text=translated_text,
						confidence=subtitle.confidence
					)
					
					translated_subtitles.append(translated_subtitle)
					
					logger.debug(f"Processed subtitle {i+1}/{len(subtitles)}")
					
				except Exception as e:
					logger.warning(f"Failed to process subtitle {i+1}: {e}")
					translated_subtitles.append(subtitle)
			
			logger.info(f"Batch translation completed: {len(translated_subtitles)} subtitles")
			return translated_subtitles
			
		except Exception as e:
			logger.error(f"Subtitle translation failed: {e}")
			raise
	
	def test_connection(self) -> bool:
		"""
		Test API connection with a simple batch translation
		
		Returns:
			True if connection is successful
		"""
		try:
			result = self.translate_batch_texts(["Hello"], "eng_Latn", "pes_Arab")
			logger.info("Translation API connection test successful")
			return True
		except Exception as e:
			logger.error(f"Translation API connection test failed: {e}")
			return False
