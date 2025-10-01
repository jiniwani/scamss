from fastapi import APIRouter
from pydantic import BaseModel
from typing import Literal, Optional
import json
import os
from datetime import datetime
from pathlib import Path


router = APIRouter()


class FeedbackRequest(BaseModel):
    analysis_id: str
    rating: int  # 1-5
    actual_tier: Optional[Literal["low", "medium", "high"]] = None
    comments: Optional[str] = None
    conversation_text: str
    predicted_tier: str
    predicted_score: float


FEEDBACK_DIR = Path("data/feedback")
FEEDBACK_DIR.mkdir(parents=True, exist_ok=True)


@router.post("/feedback")
def submit_feedback(body: FeedbackRequest):
    """
    사용자 피드백 수집 및 저장
    """
    # 피드백 파일명: feedback_YYYYMMDD_HHMMSS_rating.json
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"feedback_{timestamp}_rating{body.rating}.json"
    filepath = FEEDBACK_DIR / filename
    
    # 익명화된 데이터 저장
    feedback_data = {
        "timestamp": datetime.now().isoformat(),
        "analysis_id": body.analysis_id,
        "rating": body.rating,
        "predicted_tier": body.predicted_tier,
        "predicted_score": body.predicted_score,
        "actual_tier": body.actual_tier,
        "comments": body.comments,
        "conversation_text": body.conversation_text[:500],  # 최대 500자만 저장
        "is_low_rating": body.rating <= 2,
    }
    
    with open(filepath, 'w', encoding='utf-8') as f:
        json.dump(feedback_data, f, ensure_ascii=False, indent=2)
    
    return {
        "status": "success",
        "message": "피드백이 저장되었습니다. 개선에 활용하겠습니다.",
        "feedback_id": filename
    }


@router.get("/feedback/stats")
def get_feedback_stats():
    """
    피드백 통계 조회 (관리자용)
    """
    if not FEEDBACK_DIR.exists():
        return {"total": 0, "by_rating": {}, "low_rating_cases": []}
    
    feedbacks = []
    for filepath in FEEDBACK_DIR.glob("feedback_*.json"):
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                feedbacks.append(json.load(f))
        except Exception:
            continue
    
    # 별점별 집계
    by_rating = {i: 0 for i in range(1, 6)}
    for fb in feedbacks:
        rating = fb.get('rating', 3)
        by_rating[rating] = by_rating.get(rating, 0) + 1
    
    # 낮은 별점 케이스 (1~2점)
    low_rating_cases = [
        {
            "timestamp": fb['timestamp'],
            "rating": fb['rating'],
            "predicted_tier": fb['predicted_tier'],
            "actual_tier": fb.get('actual_tier'),
            "comments": fb.get('comments'),
            "conversation_preview": fb['conversation_text'][:100]
        }
        for fb in feedbacks if fb.get('rating', 3) <= 2
    ]
    
    # 정확도 계산 (actual_tier가 있는 경우만)
    accurate_count = 0
    total_with_actual = 0
    for fb in feedbacks:
        if fb.get('actual_tier'):
            total_with_actual += 1
            if fb['predicted_tier'] == fb['actual_tier']:
                accurate_count += 1
    
    accuracy = (accurate_count / total_with_actual * 100) if total_with_actual > 0 else None
    
    return {
        "total": len(feedbacks),
        "by_rating": by_rating,
        "low_rating_count": len(low_rating_cases),
        "low_rating_cases": low_rating_cases[:10],  # 최근 10개만
        "accuracy": accuracy,
        "accurate_count": accurate_count,
        "total_with_actual": total_with_actual
    }

