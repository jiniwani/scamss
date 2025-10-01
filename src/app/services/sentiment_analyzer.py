from typing import Dict, List
import re


# Emotional manipulation patterns
GUILT_TRIP_PATTERNS = [
    "i thought you cared",
    "you don't love me",
    "if you really loved",
    "prove you care",
    "thought you were different",
    "disappointed in you",
    "expected more",
    "나는 널 믿었는데",
    "실망했어",
    "사랑한다면",
    "증명해봐",
]

ISOLATION_PATTERNS = [
    "don't tell",
    "keep it secret",
    "between us",
    "they won't understand",
    "your family doesn't know",
    "don't ask them",
    "trust me only",
    "비밀로",
    "말하지 마",
    "가족에게 말하지",
    "나만 믿어",
]

LOVE_INTENSITY_KEYWORDS = [
    'love', 'soul', 'destiny', 'forever', 'soulmate', 'meant to be',
    '사랑', '운명', '영원', '소울메이트'
]

DESPERATION_KEYWORDS = [
    'desperate', 'emergency', 'urgent', 'dying', 'life or death', 'critical',
    '절박', '긴급', '위급', '생사'
]


def analyze_emotional_manipulation(messages: List[Dict]) -> Dict:
    """
    Detect guilt-tripping, isolation attempts, and emotional intensity patterns.
    """
    guilt_trips = []
    isolation_attempts = []
    love_intensity_by_turn = []
    desperation_count = 0
    
    for i, msg in enumerate(messages):
        # Handle both dict and Pydantic model
        if hasattr(msg, 'content'):
            content = msg.content
            sender = msg.sender
        else:
            content = msg.get('content') or msg.get('text') or ''
            sender = msg.get('sender', 'contact')
        
        lowered = content.lower()
        
        # Detect guilt-tripping
        for pattern in GUILT_TRIP_PATTERNS:
            if pattern in lowered:
                guilt_trips.append({
                    'turn': i,
                    'sender': sender,
                    'pattern': pattern,
                    'text': content[:100]
                })
        
        # Detect isolation attempts
        for pattern in ISOLATION_PATTERNS:
            if pattern in lowered:
                isolation_attempts.append({
                    'turn': i,
                    'sender': sender,
                    'pattern': pattern,
                    'text': content[:100]
                })
        
        # Measure love intensity per turn
        love_score = sum(1 for kw in LOVE_INTENSITY_KEYWORDS if kw in lowered)
        love_intensity_by_turn.append(love_score)
        
        # Desperation count
        if any(kw in lowered for kw in DESPERATION_KEYWORDS):
            desperation_count += 1
    
    # Calculate love bombing intensity (early messages with high love score)
    early_love_intensity = sum(love_intensity_by_turn[:10]) if len(love_intensity_by_turn) >= 10 else sum(love_intensity_by_turn)
    
    return {
        'guilt_trips': guilt_trips,
        'isolation_attempts': isolation_attempts,
        'love_intensity_early': early_love_intensity,
        'desperation_count': desperation_count,
        'has_guilt_trip': len(guilt_trips) > 0,
        'has_isolation': len(isolation_attempts) > 0,
        'excessive_early_love': early_love_intensity >= 5
    }


def calculate_emotional_risk_boost(sentiment_result: Dict) -> float:
    """
    Calculate risk boost based on emotional manipulation patterns.
    """
    boost = 0.0
    
    # Guilt-tripping is a strong manipulation tactic
    if sentiment_result.get('has_guilt_trip'):
        boost += 0.2 * min(len(sentiment_result['guilt_trips']), 3) / 3
    
    # Isolation is a severe warning sign
    if sentiment_result.get('has_isolation'):
        boost += 0.25 * min(len(sentiment_result['isolation_attempts']), 3) / 3
    
    # Excessive early love bombing
    if sentiment_result.get('excessive_early_love'):
        boost += 0.15
    
    # Desperation tactics
    if sentiment_result.get('desperation_count', 0) >= 2:
        boost += 0.1
    
    return min(boost, 0.5)

