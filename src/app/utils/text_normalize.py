import re
from typing import Dict


# Slang and abbreviation normalization
SLANG_MAP = {
    # Common chat abbreviations
    r'\bu\b': 'you',
    r'\bur\b': 'your',
    r'\br\b': 'are',
    r'\bu r\b': 'you are',
    r'\bpls\b': 'please',
    r'\bplz\b': 'please',
    r'\bthx\b': 'thanks',
    r'\bthnx\b': 'thanks',
    r'\bty\b': 'thank you',
    r'\bbb\b': 'baby',
    r'\bbby\b': 'baby',
    r'\blol\b': '',
    r'\bomg\b': '',
    
    # Money-related obfuscation
    r'\bca\$h\b': 'cash',
    r'\b\$\$\b': 'money',
    r'\bd0llars?\b': 'dollars',
    r'\bm0ney\b': 'money',
    
    # Number substitution
    r'(\d+)\s*k\b': r'\1000',
    r'1\s*hundr3d': '100',
    r'f1ve': 'five',
    r'tw0': 'two',
    r'thr33': 'three',
    
    # Urgency obfuscation
    r'\burg3nt\b': 'urgent',
    r'\bn0w\b': 'now',
    r'\bt0day\b': 'today',
    
    # Gift card variations
    r'\bg1ft\s*c@rd\b': 'gift card',
    r'\b1tunes\b': 'iTunes',
}


def normalize_slang(text: str) -> str:
    """
    Normalize common slang, abbreviations, and obfuscated terms.
    """
    normalized = text
    for pattern, replacement in SLANG_MAP.items():
        normalized = re.sub(pattern, replacement, normalized, flags=re.IGNORECASE)
    
    # Remove excessive punctuation
    normalized = re.sub(r'[!?]{2,}', '!', normalized)
    normalized = re.sub(r'\.{2,}', '.', normalized)
    
    return normalized


# Cultural whitelists for normal affection expressions
CULTURAL_WHITELIST = {
    'korean': [
        '오빠', '언니', '사랑해', '보고싶어', '좋아해'
    ],
    'japanese': [
        '愛してる', '好き', 'だいすき'
    ],
    'arabic': [
        'حبيبي', 'حياتي'
    ],
    'spanish': [
        'te amo', 'mi amor', 'cariño'
    ],
    'french': [
        "je t'aime", 'mon amour', 'chéri'
    ]
}


def is_cultural_expression(text: str, language: str) -> bool:
    """
    Check if text contains normal cultural affection expressions.
    """
    lang_map = {
        'ko': 'korean',
        'ja': 'japanese',
        'ar': 'arabic',
        'es': 'spanish',
        'fr': 'french'
    }
    
    culture = lang_map.get(language)
    if not culture or culture not in CULTURAL_WHITELIST:
        return False
    
    lowered = text.lower()
    return any(expr.lower() in lowered for expr in CULTURAL_WHITELIST[culture])


def detect_grammar_awkwardness(original: str, translated: str, back_translated: str) -> Dict:
    """
    Detect awkward grammar that might indicate translation-based evasion.
    """
    # Simple heuristic: check for broken word order
    awkward_patterns = [
        r'\b(please|can|will)\s+(assistance|help)\s+(monetary|financial)',
        r'\bneed\s+(for|to)\s+(money|cash|help)',
        r'\bam\s+working\s+in\s+(oil rig|military)',
        r'\bfor\s+making\s+money\b',
    ]
    
    is_awkward = any(re.search(p, translated, re.IGNORECASE) for p in awkward_patterns)
    
    # Check if back-translation differs significantly (simple Levenshtein would be better)
    similarity = _simple_similarity(original.lower(), back_translated.lower())
    
    return {
        'is_awkward': is_awkward,
        'similarity_to_original': similarity,
        'suspicion_level': 'high' if is_awkward and similarity < 0.6 else ('medium' if is_awkward else 'low')
    }


def _simple_similarity(s1: str, s2: str) -> float:
    """
    Simple word-overlap similarity (for demo; use proper edit distance in production).
    """
    words1 = set(s1.split())
    words2 = set(s2.split())
    if not words1 or not words2:
        return 0.0
    overlap = len(words1 & words2)
    return overlap / max(len(words1), len(words2))

