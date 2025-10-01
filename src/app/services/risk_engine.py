from typing import Dict, List
import re


RED_FLAG_PATTERNS = {
    'financial': {
        'direct_money_request': {
            'keywords': [
                'send money', 'need cash', 'wire transfer', 'help financially', '$', 'dollars',
                '송금', '입금', '돈 보내', '보내주세요', '보내 줄래', '지원해줘', '급히 돈', '긴급 자금',
                '이체', '충전', '보증금', '페이로 보내', '소액만', '계좌로', '도와주면', '갚을게'
            ],
            'weight': 0.35
        },
        'gift_card_request': {
            'keywords': ['gift card', 'itunes', 'steam card', 'google play', '기프트카드', '아이튠즈', '구글플레이'],
            'weight': 0.35
        },
        'crypto_wallet': {
            'regex': r'\b(0x[a-fA-F0-9]{40}|bc1[a-z0-9]{39,59})\b',
            'weight': 0.4
        },
        'investment_scheme': {
            'keywords': [
                'investment opportunity', 'trading', 'crypto profit', 'guaranteed return',
                '투자', '수익 보장', '보장 수익', '고수익', '거래로 수익', '원금 보장', '신호', '리딩', '리딩방',
                '수익내드릴게요', '수익 내드릴게요', '수익 드릴게요', '따라하세요', '시키는대로', '시키는 대로', '지시대로',
                '거래소', '입금', '출금', '코인', '카피 트레이딩', '카피트레이딩'
            ],
            'weight': 0.35
        },
        'guaranteed_profit_daily': {
            'keywords': [
                'guaranteed', 'profit daily', '12% profit', 'guaranteed profit', 'no risk', 'risk-free',
                '무위험', '확실한 수익', '100% 수익', 'guaranteed return'
            ],
            'weight': 0.35
        },
        'minimum_deposit': {
            'regex': r'(start|begin|minimum|min)\s+(with|deposit|amount)?\s*\$?\d+',
            'weight': 0.3
        },
        'registration_fee': {
            'keywords': [
                'registration fee', 'sign-up fee', 'signup fee', 'joining fee', 'membership fee',
                '등록비', '가입비', '회원비'
            ],
            'weight': 0.35
        },
        'activation_fee': {
            'keywords': ['activation fee', 'activate your account', 'account activation', '활성화 비용'],
            'weight': 0.3
        },
        'earn_per_day': {
            'regex': r'(earn|make|get)\s*\$?\d+\s*[/-]\s*(day|daily|per day)',
            'weight': 0.35
        },
        'fees_documents': {
            'keywords': ['customs fee', 'visa fee', 'lawyer fee', 'processing fee', 'clearance', '수수료', '비용', '관세', '서류비', '배송비', '보관료'],
            'weight': 0.35
        },
        'exchange_deposit': {
            'keywords': ['거래소', '입금', '충전', '지갑으로 보내', '코인 보내', 'VIP 방', '입장료'],
            'weight': 0.35
        },
        'promise_withdrawal': {
            'keywords': ['출금 줄게', '출금 줄게요', '출금 해줄게', '출금 가능', '출금 도와줄게'],
            'weight': 0.25
        },
        'prize_scam': {
            'keywords': ['당첨', '축하합니다', '경품', '스마트폰 당첨', '복권', 'congratulations', 'you won', 'prize'],
            'weight': 0.3
        },
        'account_restriction': {
            'keywords': ['계좌 제한', '계정 잠금', '동결', '차단', 'account locked', 'suspended', '복구', '인증 필요'],
            'weight': 0.35
        }
    },
    'relationship': {
        'love_bombing': {
            'keywords': ['soulmate', 'destiny', 'love of my life', 'meant to be', 'i love you', 'my dear'],
            'weight': 0.25
        },
        'meeting_avoidance': {
            'keywords': ['camera broken', 'bad connection', 'next week', 'soon', 'working away', '통화 어려워', '통화 안돼', '카메라 고장', '영상 통화 나중에'],
            'weight': 0.25
        },
        'rush_intimacy': {
            'keywords': ['marry me', 'our future', 'our kids', 'grow old together'],
            'weight': 0.25
        },
        'platform_switch': {
            'keywords': ['whatsapp', 'telegram', 'private email', 'another app'],
            'weight': 0.2
        }
    },
    'identity': {
        'military_claim': {
            'keywords': ['soldier', 'deployed', 'military base', 'overseas mission', '파병', '해외 파병', '군인', '군 복무'],
            'weight': 0.25
        },
        'oil_rig_claim': {
            'keywords': ['oil rig', 'offshore', 'north sea', 'drilling platform'],
            'weight': 0.25
        },
        'doctor_engineer': {
            'keywords': ['surgeon', 'un doctor', 'civil engineer abroad', 'contractor'],
            'weight': 0.15
        },
        'authority_impersonation': {
            'keywords': ['검찰', '경찰', '수사관', '국세청', '검사', '형사', '세무서', 'prosecutor', 'detective', 'tax office'],
            'weight': 0.4
        },
        'delivery_impersonation': {
            'keywords': ['택배', '관세', '배송 보류', '국제특송', 'customs', 'delivery suspended', '반송'],
            'weight': 0.35
        },
        'tech_support_impersonation': {
            'keywords': ['ms 보안팀', '마이크로소프트', '애플 보안', '원격 접속', 'remote access', 'anydesk', 'teamviewer'],
            'weight': 0.35
        },
        'document_request': {
            'keywords': ['passport', 'id copy', 'account verification', 'verification copy', '신분증', '주민등록증', '계좌 인증'],
            'weight': 0.3
        },
        'family_impersonation': {
            'keywords': ['엄마', '아빠', '폰 고장', '폰 바꿨어', '급한 돈', '병원 수납', '사고났어'],
            'weight': 0.4
        },
        'inconsistent_details': {
            'detection': 'contradiction_analysis',
            'weight': 0.3
        }
    },
    'behavioral': {
        'isolation_attempt': {
            'keywords': ["don't tell", 'secret', "they don't understand", 'trust me only', '나만 믿어', '믿으세요'],
            'weight': 0.25
        },
        'time_pressure': {
            'keywords': [
                'urgent', 'today', 'right now', 'deadline', 'expire', 'within 1 hour', 'one hour', 'limited time', 'spot will be given',
                '긴급', '지금', '오늘', '바로', '급히', '오늘만', '30분 안에', '10분 내', '시간 없어', '마지막 기회'
            ],
            'weight': 0.25
        },
        'small_test_request': {
            'keywords': ['small favor', 'just $20', 'prove you care', '소액', '작게 먼저', '테스트로 조금', '소액만'],
            'weight': 0.15
        },
        'follow_orders': {
            'keywords': ['시키는대로', '시키는 대로', '지시대로', '따라만 하세요', '말대로만 하세요', '입력하세요', '지금 처리하세요'],
            'weight': 0.25
        },
        'threat': {
            'keywords': ['체포영장', '계좌 동결', '영구 잠금', '손해', '큰일', '후회', '반송', 'arrest warrant', 'account freeze'],
            'weight': 0.35
        },
        'phishing_link': {
            'regex': r'(bit\.ly|goo\.gl|tinyurl|[a-z0-9-]+\.(kr|com)/[a-z0-9-]{6,})',
            'weight': 0.4
        }
    }
}


def detect_red_flags(messages: List[Dict]) -> Dict:
    detected: Dict[str, Dict[str, Dict[str, int]]] = {}
    for idx, msg in enumerate(messages):
        content = msg.get('content') or msg.get('text') or ''
        lowered = content.lower()
        for category, flags in RED_FLAG_PATTERNS.items():
            for flag, spec in flags.items():
                count = 0
                if 'keywords' in spec:
                    for kw in spec['keywords']:
                        if kw in lowered:
                            count += 1
                if 'regex' in spec:
                    if re.search(spec['regex'], content, flags=re.IGNORECASE):
                        count += 1
                if count > 0:
                    detected.setdefault(category, {}).setdefault(flag, {"count": 0})
                    detected[category][flag]["count"] += count
    return detected


def calculate_risk_score(detected_flags: Dict, conversation_context: Dict) -> float:
    base_score = 0.0
    for category, flags in detected_flags.items():
        for flag, details in flags.items():
            weight = RED_FLAG_PATTERNS[category][flag]['weight']
            frequency = details['count']
            base_score += weight * min(frequency / 3, 1.0)

    # Context multipliers
    if conversation_context.get('message_count', 0) < 10:
        if 'relationship' in detected_flags and 'love_bombing' in detected_flags['relationship']:
            base_score *= 1.3

    if conversation_context.get('financial_flags_count', 0) > 2:
        base_score *= 1.4

    # Complex combo boosters
    types = set()
    for cat_flags in detected_flags.values():
        types.update(cat_flags.keys())

    # Boost 1: Money + urgency + untraceable method
    if (types & {'direct_money_request', 'gift_card_request', 'crypto_wallet'}) and ('time_pressure' in types):
        base_score += 0.25

    # Boost 2: Investment fraud combo (guaranteed return + deposit instruction + obedience)
    if (types & {'guaranteed_profit_daily', 'investment_scheme'}) and (types & {'exchange_deposit', 'minimum_deposit'}) and ('follow_orders' in types):
        base_score += 0.3

    # Boost 3: Employment scam (earn high + upfront fee + deadline)
    if ('earn_per_day' in types) and (types & {'registration_fee', 'activation_fee'}) and ('time_pressure' in types):
        base_score += 0.28

    # Boost 4: Identity theft setup (document request + upfront payment)
    if ('document_request' in types) and (types & {'registration_fee', 'activation_fee', 'fees_documents'}):
        base_score += 0.2

    return min(max(base_score, 0.0), 1.0)


def determine_risk_tier(score: float, red_flags_list: List[Dict]) -> Dict:
    if score >= 0.8:
        base_tier = 'high'
    elif score >= 0.5:
        base_tier = 'medium'
    else:
        base_tier = 'low'

    severe_flags = [f for f in red_flags_list if f.get('severity') == 'severe']
    if len(severe_flags) >= 2 and base_tier == 'medium':
        base_tier = 'high'

    has_financial_flag = any(f.get('category') == 'financial' for f in red_flags_list)
    if base_tier == 'high':
        if len(red_flags_list) == 1 and score < 0.9:
            base_tier = 'medium'
        if not has_financial_flag and score < 0.85:
            base_tier = 'medium'

    # Tier escalation based on pattern combos
    types = {f.get('type') for f in red_flags_list}
    categories = {f.get('category') for f in red_flags_list}

    # Rule 1: Investment fraud pattern (deposit + obedience)
    if {'investment_scheme'} & types and (types & {'exchange_deposit', 'follow_orders'}):
        if base_tier == 'low':
            base_tier = 'medium'
        elif base_tier == 'medium':
            base_tier = 'high'

    # Rule 2: Multiple categories = cross-cutting manipulation
    if len(categories) >= 3 and score >= 0.4:
        base_tier = 'high'
    elif len(categories) >= 2 and score >= 0.5:
        if base_tier == 'low':
            base_tier = 'medium'

    # Rule 3: Upfront fee + time pressure (job/investment scam)
    if (types & {'registration_fee', 'activation_fee', 'minimum_deposit'}) and ('time_pressure' in types):
        if base_tier == 'low':
            base_tier = 'medium'

    # Rule 4: Money + urgency + untraceable method = classic scam
    if (types & {'direct_money_request', 'gift_card_request', 'crypto_wallet'}) and ('time_pressure' in types):
        if score >= 0.5:
            base_tier = 'high'
        elif base_tier == 'low':
            base_tier = 'medium'

    # Rule 5: Guaranteed profit + upfront fee + document = compound fraud
    if (types & {'guaranteed_profit_daily', 'earn_per_day'}) and (types & {'registration_fee', 'activation_fee', 'minimum_deposit'}):
        if ('document_request' in types):
            base_tier = 'high'
        elif base_tier == 'low':
            base_tier = 'medium'

    # Rule 6: Any severe financial flag + behavioral manipulation = high concern
    severe_financial = [f for f in red_flags_list if f.get('category') == 'financial' and f.get('severity') == 'severe']
    behavioral_present = any(f.get('category') == 'behavioral' for f in red_flags_list)
    if len(severe_financial) >= 1 and behavioral_present and score >= 0.5:
        if base_tier == 'medium':
            base_tier = 'high'

    return {
        'tier': base_tier,
        'confidence': calculate_confidence(score, red_flags_list),
        'override_applied': False,
    }


def calculate_confidence(score: float, red_flags_list: List[Dict]) -> float:
    n = len(red_flags_list)
    return min(1.0, 0.5 + 0.5 * score + 0.05 * n)


