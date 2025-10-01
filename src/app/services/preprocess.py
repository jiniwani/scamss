from typing import Dict

from langdetect import detect_langs
import langid

from google.cloud import translate_v2 as translate  # type: ignore
import os

from ..utils.pii import mask_pii
from ..utils.text_normalize import normalize_slang, is_cultural_expression, detect_grammar_awkwardness


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


def translate_if_needed(text: str, source_lang: str, enable_back_translation: bool = False) -> Dict:
    """
    Translate to English only if not English. Optionally verify with back-translation.
    """
    if not text:
        return {"original": "", "translated": "", "source_language": source_lang or "und", "grammar_check": None}

    # Normalize slang/obfuscation before translation
    normalized = normalize_slang(text)

    if (source_lang or '').lower().startswith('en'):
        return {"original": text, "translated": normalized, "source_language": source_lang or "en", "grammar_check": None}

    # Skip external call if ADC not configured (tests/local dev)
    if not os.environ.get('GOOGLE_APPLICATION_CREDENTIALS') and not os.environ.get('GCP_PROJECT'):
        return {"original": text, "translated": normalized, "source_language": source_lang or 'und', "grammar_check": None}

    client = translate.Client()
    
    # Forward translation
    res = client.translate(normalized, target_language='en', source_language=source_lang if source_lang else None)
    translated = res.get('translatedText', normalized)
    detected_lang = res.get('detectedSourceLanguage', source_lang or 'und')
    
    grammar_check = None
    # Back-translation for grammar verification (optional, costly)
    if enable_back_translation and detected_lang != 'en':
        try:
            back_res = client.translate(translated, target_language=detected_lang, source_language='en')
            back_translated = back_res.get('translatedText', '')
            grammar_check = detect_grammar_awkwardness(text, translated, back_translated)
        except Exception:
            pass
    
    return {
        "original": text,
        "translated": translated,
        "source_language": detected_lang,
        "grammar_check": grammar_check
    }


def preprocess_text(text: str, do_mask: bool = True) -> Dict:
    lang_info = detect_language(text)
    tx = translate_if_needed(text, lang_info['language'])
    masked = mask_pii(tx['translated'] if do_mask else tx['original']) if do_mask else {"masked_text": tx['translated'], "detected_pii": []}
    return {
        "language": lang_info,
        "translation": tx,
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


