from typing import Dict

from langdetect import detect_langs
import langid

from ..utils.pii import mask_pii
from ..utils.text_normalize import normalize_slang, is_cultural_expression


def detect_language(text: str) -> Dict:
    """
    Return best-effort language detection using both langdetect and langid.
    """
    if not text:
        return {"language": "und", "confidence": 0.0, "script": "unknown"}

    # langdetect returns list of LangProb
    try:
        langs = detect_langs(text)
        best = max(langs, key=lambda l: l.prob)
        lang = best.lang
        conf = float(best.prob)
    except Exception:
        lid, lid_conf = langid.classify(text)
        lang = lid
        conf = float(lid_conf)

    script = _infer_script(text)
    return {"language": lang, "confidence": conf, "script": script}


def normalize_text(text: str, source_lang: str) -> Dict:
    """
    Normalize slang and obfuscation. No translation - Gemini handles multilingual directly.
    """
    if not text:
        return {"original": "", "normalized": "", "source_language": source_lang or "und"}

    # Normalize slang/obfuscation
    normalized = normalize_slang(text)
    
    return {
        "original": text,
        "normalized": normalized,
        "source_language": source_lang or "und"
    }


def preprocess_text(text: str, do_mask: bool = True) -> Dict:
    lang_info = detect_language(text)
    normalized_result = normalize_text(text, lang_info['language'])
    
    # Apply PII masking on normalized text
    masked = mask_pii(normalized_result['normalized']) if do_mask else {"masked_text": normalized_result['normalized'], "detected_pii": []}
    
    return {
        "language": lang_info,
        "normalized": normalized_result,
        "pii": masked,
    }


def _infer_script(text: str) -> str:
    # Very rough script inference
    for ch in text:
        code = ord(ch)
        if 0x4E00 <= code <= 0x9FFF:
            return "cjk"
        if 0x0400 <= code <= 0x04FF:
            return "cyrillic"
        if 0xAC00 <= code <= 0xD7AF:
            return "hangul"
    return "latin"


