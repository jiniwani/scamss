from typing import Dict, List
import re


# Currency normalization
CURRENCY_PATTERNS = {
    'usd': r'\$\s*(\d+(?:,\d{3})*(?:\.\d{2})?)',
    'krw': r'(\d+(?:,\d{3})*)\s*(?:원|won)',
    'eur': r'€\s*(\d+(?:,\d{3})*(?:\.\d{2})?)',
    'gbp': r'£\s*(\d+(?:,\d{3})*(?:\.\d{2})?)',
    'cny': r'¥\s*(\d+(?:,\d{3})*)',
    'generic': r'\b(\d+)\s*(?:dollars?|bucks?|euros?|pounds?)\b',
}


def extract_money_amounts(messages: List[Dict]) -> List[Dict]:
    """
    Extract all money mentions with normalized amounts in USD.
    """
    amounts = []
    
    for i, msg in enumerate(messages):
        # Handle both dict and Pydantic model
        if hasattr(msg, 'content'):
            content = msg.content
            sender = msg.sender
        else:
            content = msg.get('content') or msg.get('text') or ''
            sender = msg.get('sender', 'contact')
        
        for currency, pattern in CURRENCY_PATTERNS.items():
            matches = re.findall(pattern, content, re.IGNORECASE)
            for match in matches:
                # Remove commas and convert to float
                clean_amount = match.replace(',', '')
                try:
                    value = float(clean_amount)
                    # Normalize to USD (rough conversion)
                    if currency == 'krw':
                        value = value / 1300  # KRW to USD
                    elif currency == 'eur':
                        value = value * 1.1
                    elif currency == 'gbp':
                        value = value * 1.3
                    elif currency == 'cny':
                        value = value / 7
                    
                    amounts.append({
                        'turn': i,
                        'sender': sender,
                        'amount_usd': value,
                        'original': match,
                        'currency': currency
                    })
                except ValueError:
                    continue
    
    return amounts


def detect_escalation_pattern(amounts: List[Dict]) -> Dict:
    """
    Detect progressive amount escalation (testing boundaries).
    """
    if len(amounts) < 2:
        return {
            'has_escalation': False,
            'pattern': None,
            'first_amount': amounts[0]['amount_usd'] if amounts else 0,
            'max_amount': amounts[0]['amount_usd'] if amounts else 0
        }
    
    # Sort by turn order
    sorted_amounts = sorted(amounts, key=lambda x: x['turn'])
    values = [a['amount_usd'] for a in sorted_amounts]
    
    # Check if amounts are generally increasing
    increasing_count = 0
    for i in range(1, len(values)):
        if values[i] > values[i-1]:
            increasing_count += 1
    
    is_escalating = increasing_count >= len(values) // 2
    
    # Small test pattern: starts with < $50, then jumps to > $200
    small_test = any(v < 50 for v in values[:2]) and any(v > 200 for v in values)
    
    return {
        'has_escalation': is_escalating,
        'small_test_then_large': small_test,
        'first_amount': values[0],
        'max_amount': max(values),
        'escalation_ratio': max(values) / values[0] if values[0] > 0 else 1.0,
        'amount_count': len(amounts)
    }


def analyze_money_patterns(messages: List[Dict]) -> Dict:
    """
    Comprehensive money pattern analysis.
    """
    amounts = extract_money_amounts(messages)
    escalation = detect_escalation_pattern(amounts)
    
    suspicion_signals = []
    
    # Signal 1: Small test then large request
    if escalation.get('small_test_then_large'):
        suspicion_signals.append({
            'type': 'small_test_escalation',
            'severity': 'high',
            'detail': f"Small amount (${escalation['first_amount']:.0f}) then large (${escalation['max_amount']:.0f})"
        })
    
    # Signal 2: Rapid escalation (5x or more)
    if escalation.get('escalation_ratio', 1) >= 5:
        suspicion_signals.append({
            'type': 'rapid_escalation',
            'severity': 'high',
            'detail': f"{escalation['escalation_ratio']:.1f}x amount increase"
        })
    
    # Signal 3: Multiple money requests
    if escalation.get('amount_count', 0) >= 3:
        suspicion_signals.append({
            'type': 'multiple_requests',
            'severity': 'medium',
            'detail': f"{escalation['amount_count']} separate money requests"
        })
    
    return {
        'amounts': amounts,
        'escalation': escalation,
        'suspicion_signals': suspicion_signals
    }


def calculate_money_pattern_risk_boost(money_analysis: Dict) -> float:
    """
    Calculate risk boost based on money request patterns.
    """
    boost = 0.0
    
    for signal in money_analysis.get('suspicion_signals', []):
        if signal['severity'] == 'high':
            boost += 0.2
        elif signal['severity'] == 'medium':
            boost += 0.1
    
    return min(boost, 0.4)

