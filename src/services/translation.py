import logging
import requests
import json
from typing import List, Optional
from src.models.subtitle import Subtitle

logger = logging.getLogger(__name__)

class TranslationService:
	"""Handles subtitle translation using Hugging Face API"""
	
	SUPPORTED_LANGUAGES = [
		'ace_Arab', 'ace_Latn', 'acm_Arab', 'acq_Arab', 'aeb_Arab', 'afr_Latn', 'ajp_Arab', 'aka_Latn', 'amh_Ethi', 'apc_Arab', 'arb_Arab', 'ars_Arab', 'ary_Arab', 'arz_Arab', 'asm_Beng', 'ast_Latn', 'awa_Deva', 'ayr_Latn', 'azb_Arab', 'azj_Latn', 'bak_Cyrl', 'bam_Latn', 'ban_Latn', 'bel_Cyrl', 'bem_Latn', 'ben_Beng', 'bho_Deva', 'bjn_Arab', 'bjn_Latn', 'bod_Tibt', 'bos_Latn', 'bug_Latn', 'bul_Cyrl', 'cat_Latn', 'ceb_Latn', 'ces_Latn', 'cjk_Latn', 'ckb_Arab', 'crh_Latn', 'cym_Latn', 'dan_Latn', 'deu_Latn', 'dik_Latn', 'dyu_Latn', 'dzo_Tibt', 'ell_Grek', 'eng_Latn', 'epo_Latn', 'est_Latn', 'eus_Latn', 'ewe_Latn', 'fao_Latn', 'pes_Arab', 'fij_Latn', 'fin_Latn', 'fon_Latn', 'fra_Latn', 'fur_Latn', 'fuv_Latn', 'gla_Latn', 'gle_Latn', 'glg_Latn', 'grn_Latn', 'guj_Gujr', 'hat_Latn', 'hau_Latn', 'heb_Hebr', 'hin_Deva', 'hne_Deva', 'hrv_Latn', 'hun_Latn', 'hye_Armn', 'ibo_Latn', 'ilo_Latn', 'ind_Latn', 'isl_Latn', 'ita_Latn', 'jav_Latn', 'jpn_Jpan', 'kab_Latn', 'kac_Latn', 'kam_Latn', 'kan_Knda', 'kas_Arab', 'kas_Deva', 'kat_Geor', 'knc_Arab', 'knc_Latn', 'kaz_Cyrl', 'kbp_Latn', 'kea_Latn', 'khm_Khmr', 'kik_Latn', 'kin_Latn', 'kir_Cyrl', 'kmb_Latn', 'kon_Latn', 'kor_Hang', 'kmr_Latn', 'lao_Laoo', 'lvs_Latn', 'lij_Latn', 'lim_Latn', 'lin_Latn', 'lit_Latn', 'lmo_Latn', 'ltg_Latn', 'ltz_Latn', 'lua_Latn', 'lug_Latn', 'luo_Latn', 'lus_Latn', 'mag_Deva', 'mai_Deva', 'mal_Mlym', 'mar_Deva', 'min_Latn', 'mkd_Cyrl', 'plt_Latn', 'mlt_Latn', 'mni_Beng', 'khk_Cyrl', 'mos_Latn', 'mri_Latn', 'zsm_Latn', 'mya_Mymr', 'nld_Latn', 'nno_Latn', 'nob_Latn', 'npi_Deva', 'nso_Latn', 'nus_Latn', 'nya_Latn', 'oci_Latn', 'gaz_Latn', 'ory_Orya', 'pag_Latn', 'pan_Guru', 'pap_Latn', 'pol_Latn', 'por_Latn', 'prs_Arab', 'pbt_Arab', 'quy_Latn', 'ron_Latn', 'run_Latn', 'rus_Cyrl', 'sag_Latn', 'san_Deva', 'sat_Beng', 'scn_Latn', 'shn_Mymr', 'sin_Sinh', 'slk_Latn', 'slv_Latn', 'smo_Latn', 'sna_Latn', 'snd_Arab', 'som_Latn', 'sot_Latn', 'spa_Latn', 'als_Latn', 'srd_Latn', 'srp_Cyrl', 'ssw_Latn', 'sun_Latn', 'swe_Latn', 'swh_Latn', 'szl_Latn', 'tam_Taml', 'tat_Cyrl', 'tel_Telu', 'tgk_Cyrl', 'tgl_Latn', 'tha_Thai', 'tir_Ethi', 'taq_Latn', 'taq_Tfng', 'tpi_Latn', 'tsn_Latn', 'tso_Latn', 'tuk_Latn', 'tum_Latn', 'tur_Latn', 'twi_Latn', 'tzm_Tfng', 'uig_Arab', 'ukr_Cyrl', 'umb_Latn', 'urd_Arab', 'uzn_Latn', 'vec_Latn', 'vie_Latn', 'war_Latn', 'wol_Latn', 'xho_Latn', 'ydd_Hebr', 'yor_Latn', 'yue_Hant', 'zho_Hans', 'zho_Hant', 'zul_Latn'
	]
	
	def __init__(self, api_url: str = "https://saeidseyfi-hf-translator.hf.space/translate"):
		"""
		Initialize translation service
		
		Args:
			api_url: Hugging Face API endpoint URL
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
		Translate single text using Hugging Face API
		
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
			
			payload = {
				"text": text,
				"src_lang": src_lang,
				"tgt_lang": tgt_lang
			}
			
			logger.debug(f"Translating text: '{text[:50]}...' from {src_lang} to {tgt_lang}")
			
			response = requests.post(
				self.api_url,
				headers=self.headers,
				json=payload,
				timeout=30
			)
			
			response.raise_for_status()
			
			result = response.json()
			
			if 'translation' in result:
				translated_text = result['translation']
				logger.debug(f"Translation successful: '{translated_text[:50]}...'")
				return translated_text
			else:
				raise Exception(f"Unexpected API response format: {result}")
				
		except requests.exceptions.RequestException as e:
			logger.error(f"API request failed: {e}")
			raise Exception(f"Translation API request failed: {e}")
		except Exception as e:
			logger.error(f"Translation failed: {e}")
			raise
	
	def translate_subtitles(self, subtitles: List[Subtitle], src_lang: str, tgt_lang: str) -> List[Subtitle]:
		"""
		Translate list of subtitles
		
		Args:
			subtitles: List of subtitle objects
			src_lang: Source language code
			tgt_lang: Target language code
			
		Returns:
			List of translated subtitle objects
		"""
		try:
			logger.info(f"Starting subtitle translation from {src_lang} to {tgt_lang}")
			
			translated_subtitles = []
			
			for i, subtitle in enumerate(subtitles):
				try:
					translated_text = self.translate_text(subtitle.text, src_lang, tgt_lang)
					
					translated_subtitle = Subtitle(
						start_time=subtitle.start_time,
						end_time=subtitle.end_time,
						text=translated_text,
						confidence=subtitle.confidence
					)
					
					translated_subtitles.append(translated_subtitle)
					
					logger.debug(f"Translated subtitle {i+1}/{len(subtitles)}")
					
				except Exception as e:
					logger.warning(f"Failed to translate subtitle {i+1}: {e}")
					translated_subtitles.append(subtitle)
			
			logger.info(f"Translation completed: {len(translated_subtitles)} subtitles")
			return translated_subtitles
			
		except Exception as e:
			logger.error(f"Subtitle translation failed: {e}")
			raise
	
	def test_connection(self) -> bool:
		"""
		Test API connection with a simple translation
		
		Returns:
			True if connection is successful
		"""
		try:
			result = self.translate_text("Hello", "eng_Latn", "pes_Arab")
			logger.info("Translation API connection test successful")
			return True
		except Exception as e:
			logger.error(f"Translation API connection test failed: {e}")
			return False
