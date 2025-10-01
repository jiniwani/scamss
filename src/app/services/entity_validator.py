from typing import Dict, List, Set
import re


def extract_entities(messages: List[Dict]) -> Dict:
    """
    Extract named entities (names, locations, occupations, ages) from conversation.
    """
    entities = {
        'names': set(),
        'locations': set(),
        'occupations': set(),
        'ages': set(),
        'family_mentions': set(),
    }
    
    for msg in messages:
        # Handle both dict and Pydantic model
        if hasattr(msg, 'content'):
            content = msg.content
        else:
            content = msg.get('content') or msg.get('text') or ''
        
        # Extract self-introduced names (simple heuristic)
        name_patterns = [
            r"(?:my name is|i'm|i am|call me)\s+([A-Z][a-z]+(?:\s+[A-Z][a-z]+)?)",
            r"(?:제 이름은|저는)\s+([가-힣]{2,4})",
        ]
        for pattern in name_patterns:
            matches = re.findall(pattern, content, re.IGNORECASE)
            entities['names'].update(m.strip() for m in matches if m)
        
        # Extract locations
        location_patterns = [
            r"(?:in|from|live in|based in)\s+([A-Z][a-z]+(?:\s+[A-Z][a-z]+)?)",
            r"(?:에 살아|에서 왔어|거주)\s+([가-힣]{2,10})",
        ]
        for pattern in location_patterns:
            matches = re.findall(pattern, content, re.IGNORECASE)
            entities['locations'].update(m.strip() for m in matches if m)
        
        # Extract occupations
        occupation_keywords = [
            'engineer', 'doctor', 'surgeon', 'soldier', 'military', 'oil rig', 'contractor',
            'businessman', 'CEO', 'manager', '엔지니어', '의사', '군인', '사업가'
        ]
        for occ in occupation_keywords:
            if occ.lower() in content.lower():
                entities['occupations'].add(occ.lower())
        
        # Extract ages
        age_pattern = r"\b(\d{2})\s*(?:years old|year old|살|세)\b"
        age_matches = re.findall(age_pattern, content, re.IGNORECASE)
        entities['ages'].update(age_matches)
        
        # Extract family mentions
        family_keywords = ['mother', 'father', 'grandmother', 'son', 'daughter', 'wife', 'husband', 
                          '엄마', '아빠', '할머니', '아들', '딸', '아내', '남편']
        for fam in family_keywords:
            if fam.lower() in content.lower():
                entities['family_mentions'].add(fam.lower())
    
    return {k: list(v) for k, v in entities.items()}


def detect_inconsistencies(messages: List[Dict]) -> Dict:
    """
    Detect contradictions in self-reported information across messages.
    """
    entities = extract_entities(messages)
    inconsistencies = []
    
    # Check for multiple names
    if len(entities['names']) > 1:
        inconsistencies.append({
            'type': 'multiple_names',
            'severity': 'high',
            'detail': f"Multiple names mentioned: {', '.join(entities['names'])}",
            'entities': entities['names']
        })
    
    # Check for multiple locations (if mentioned in short timeframe)
    if len(entities['locations']) > 2:
        inconsistencies.append({
            'type': 'multiple_locations',
            'severity': 'medium',
            'detail': f"Multiple locations claimed: {', '.join(entities['locations'])}",
            'entities': entities['locations']
        })
    
    # Check for multiple ages
    if len(entities['ages']) > 1:
        ages_int = [int(a) for a in entities['ages']]
        if max(ages_int) - min(ages_int) > 2:
            inconsistencies.append({
                'type': 'conflicting_ages',
                'severity': 'high',
                'detail': f"Different ages mentioned: {', '.join(entities['ages'])}",
                'entities': entities['ages']
            })
    
    # Check for suspicious occupation claims
    suspicious_occupations = ['oil rig', 'military', 'soldier', 'surgeon', 'un doctor']
    found_suspicious = [occ for occ in entities['occupations'] if occ in suspicious_occupations]
    if found_suspicious:
        inconsistencies.append({
            'type': 'suspicious_occupation',
            'severity': 'medium',
            'detail': f"Stereotypical scam occupation: {', '.join(found_suspicious)}",
            'entities': found_suspicious
        })
    
    return {
        'entities': entities,
        'inconsistencies': inconsistencies,
        'inconsistency_count': len(inconsistencies)
    }


def calculate_entity_risk_boost(validation_result: Dict) -> float:
    """
    Calculate risk boost based on entity inconsistencies.
    """
    boost = 0.0
    
    for incon in validation_result.get('inconsistencies', []):
        if incon['severity'] == 'high':
            boost += 0.2
        elif incon['severity'] == 'medium':
            boost += 0.1
    
    return min(boost, 0.5)  # Cap at 0.5

