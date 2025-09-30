import re
from typing import Dict, List


PII_PATTERNS = {
    'phone': r'(\+?\d{1,3}[-.\s]?)?\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}',
    'email': r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b',
    'bank_account': r'\b\d{4}[-\s]?\d{4}[-\s]?\d{4}[-\s]?\d{4}\b',
    # Use non-capturing groups to avoid findall returning partials
    'crypto_wallet': r'(?:\b0x[a-fA-F0-9]{40}\b|\b[13][a-km-zA-HJ-NP-Z1-9]{25,34}\b|\bbc1[a-z0-9]{39,59}\b)',
    'ssn': r'\b\d{3}-\d{2}-\d{4}\b',
    'credit_card': r'\b\d{4}[-\s]?\d{4}[-\s]?\d{4}[-\s]?\d{4}\b',
}


REPLACERS = {
    'phone': '[PHONE]',
    'email': '[EMAIL]',
    'bank_account': '[BANK_ACCOUNT]',
    'crypto_wallet': '[CRYPTO_WALLET]',
    'ssn': '[SSN]',
    'credit_card': '[CREDIT_CARD]',
}


def mask_pii(text: str) -> Dict:
    masked_text = text
    detected: Dict[str, int] = {}

    for pii_type, pattern in PII_PATTERNS.items():
        if pii_type == 'crypto_wallet':
            # Handle multiple wallet formats robustly
            patterns = [
                r'(?<![0-9A-Fa-f])0x[0-9A-Fa-f]{38,42}(?![0-9A-Fa-f])',  # Ethereum len-tolerant
                r'\b[13][a-km-zA-HJ-NP-Z1-9]{25,34}\b',  # Legacy BTC
                r'\bbc1[a-z0-9]{39,59}\b',  # Bech32 BTC
            ]
            total = 0
            for p in patterns:
                compiled = re.compile(p, flags=re.IGNORECASE)
                masked_text, num = compiled.subn(REPLACERS[pii_type], masked_text)
                total += num
            if total:
                detected[pii_type] = detected.get(pii_type, 0) + total
            continue

        compiled = re.compile(pattern, flags=re.IGNORECASE)
        matches: List[str] = compiled.findall(masked_text)
        if matches:
            detected[pii_type] = detected.get(pii_type, 0) + len(matches)
            masked_text = compiled.sub(REPLACERS[pii_type], masked_text)

    # Fallback for Ethereum-like addresses without word boundaries
    eth_fallback = re.compile(r'0x[a-fA-F0-9]{40}', flags=re.IGNORECASE)
    masked_text, num = eth_fallback.subn(REPLACERS['crypto_wallet'], masked_text)
    if num:
        # Merge or set detection count
        existing = next((d for d in detected_list if d['type'] == 'crypto_wallet'), None) if 'detected_list' in locals() else None
        if existing:
            existing['count'] += num
        else:
            detected_list = ([{"type": k, "count": v} for k, v in detected.items()]
                             if 'detected_list' not in locals() else detected_list)
            detected_list.append({"type": 'crypto_wallet', "count": num})

    detected_list = [
        {"type": k, "count": v} for k, v in detected.items()
    ]

    return {
        'masked_text': masked_text,
        'detected_pii': detected_list,
    }


