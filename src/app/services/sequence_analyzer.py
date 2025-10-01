from typing import Dict, List
import re


# Define typical scam sequence stages
SCAM_SEQUENCE_STAGES = {
    'greeting': {
        'keywords': ['hello', 'hi', 'hey', 'nice to meet', 'pleased to meet', '안녕', '반가워', '처음 뵙겠습니다'],
        'expected_turn_range': (0, 5)
    },
    'love_bombing': {
        'keywords': ['love', 'beautiful', 'gorgeous', 'soulmate', 'destiny', 'connection', '사랑', '아름다워', '운명'],
        'expected_turn_range': (3, 15)
    },
    'video_avoidance': {
        'keywords': ['camera broken', 'video not working', 'bad connection', 'no webcam', 'later', 'soon', '카메라 고장', '통화 안돼'],
        'expected_turn_range': (5, 30)
    },
    'emergency_story': {
        'keywords': ['emergency', 'urgent', 'sick', 'accident', 'hospital', 'crisis', '응급', '긴급', '사고', '병원'],
        'expected_turn_range': (10, 50)
    },
    'money_request': {
        'keywords': ['money', 'send', 'help financially', 'transfer', 'gift card', '돈', '송금', '보내줘', '기프트카드'],
        'expected_turn_range': (12, 60)
    }
}


def detect_scam_sequence(messages: List[Dict]) -> Dict:
    """
    Detect if conversation follows typical romance scam sequence pattern.
    """
    detected_stages = {}
    
    for stage_name, stage_spec in SCAM_SEQUENCE_STAGES.items():
        first_occurrence = None
        
        for i, msg in enumerate(messages):
            # Handle both dict and Pydantic model
            if hasattr(msg, 'content'):
                content = msg.content.lower()
            else:
                content = (msg.get('content') or msg.get('text') or '').lower()
            
            if any(kw in content for kw in stage_spec['keywords']):
                first_occurrence = i
                break
        
        if first_occurrence is not None:
            detected_stages[stage_name] = {
                'turn': first_occurrence,
                'within_expected_range': stage_spec['expected_turn_range'][0] <= first_occurrence <= stage_spec['expected_turn_range'][1]
            }
    
    # Check if stages appear in order
    stage_order = ['greeting', 'love_bombing', 'video_avoidance', 'emergency_story', 'money_request']
    detected_order = [s for s in stage_order if s in detected_stages]
    
    # Calculate sequence match score
    sequence_match = 0
    for i in range(len(detected_order) - 1):
        curr_stage = detected_order[i]
        next_stage = detected_order[i + 1]
        curr_turn = detected_stages[curr_stage]['turn']
        next_turn = detected_stages[next_stage]['turn']
        
        # Stages should appear in order
        if next_turn > curr_turn:
            sequence_match += 1
    
    # Perfect sequence: all 5 stages in order
    is_classic_sequence = (len(detected_order) >= 4 and 
                          sequence_match >= len(detected_order) - 1 and
                          'money_request' in detected_order)
    
    return {
        'detected_stages': detected_stages,
        'stage_count': len(detected_stages),
        'is_classic_sequence': is_classic_sequence,
        'sequence_match_score': sequence_match / max(len(detected_order) - 1, 1) if len(detected_order) > 1 else 0
    }


def calculate_sequence_risk_boost(sequence_result: Dict) -> float:
    """
    Calculate risk boost based on scam sequence pattern matching.
    """
    boost = 0.0
    
    # Classic 5-stage sequence = very high suspicion
    if sequence_result.get('is_classic_sequence'):
        boost += 0.35
    
    # Partial sequence (3-4 stages in order)
    elif sequence_result.get('stage_count', 0) >= 3:
        match_score = sequence_result.get('sequence_match_score', 0)
        if match_score >= 0.7:
            boost += 0.2
    
    # Money request without proper relationship building
    stages = sequence_result.get('detected_stages', {})
    if 'money_request' in stages and 'greeting' in stages:
        greeting_turn = stages['greeting']['turn']
        money_turn = stages['money_request']['turn']
        gap = money_turn - greeting_turn
        
        # Very quick money request (within 10 turns)
        if gap < 10:
            boost += 0.25
        elif gap < 20:
            boost += 0.15
    
    return min(boost, 0.4)

