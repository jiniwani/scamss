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


class FeedbackAction(BaseModel):
    feedback_id: str
    action: Literal["confirm_scam", "mark_safe", "delete", "ignore"]
    admin_notes: Optional[str] = None


FEEDBACK_DIR = Path("data/feedback")
FEEDBACK_DIR.mkdir(parents=True, exist_ok=True)

TRAINING_DATA_DIR = Path("data/training")
TRAINING_DATA_DIR.mkdir(parents=True, exist_ok=True)


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


@router.post("/feedback/action")
def process_feedback_action(body: FeedbackAction):
    """
    관리자의 피드백 처리 액션
    - confirm_scam: 스캠 확정 → 학습 데이터로 저장
    - mark_safe: 정상 대화 → 학습 데이터로 저장 (오탐 개선용)
    - delete: 삭제 (스팸/장난)
    - ignore: 무시
    """
    feedback_path = FEEDBACK_DIR / body.feedback_id
    
    if not feedback_path.exists():
        return {"status": "error", "message": "피드백을 찾을 수 없습니다"}
    
    with open(feedback_path, 'r', encoding='utf-8') as f:
        feedback_data = json.load(f)
    
    if body.action == "delete":
        feedback_path.unlink()
        return {"status": "success", "message": "피드백이 삭제되었습니다"}
    
    elif body.action == "confirm_scam":
        # 학습 데이터로 저장 (scam)
        training_file = TRAINING_DATA_DIR / f"scam_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        training_data = {
            "text": feedback_data['conversation_text'],
            "label": "scam",
            "predicted_tier": feedback_data['predicted_tier'],
            "admin_confirmed": True,
            "admin_notes": body.admin_notes,
            "original_feedback_id": body.feedback_id,
            "timestamp": datetime.now().isoformat()
        }
        with open(training_file, 'w', encoding='utf-8') as f:
            json.dump(training_data, f, ensure_ascii=False, indent=2)
        feedback_path.unlink()  # 처리 완료 후 삭제
        return {"status": "success", "message": "스캠으로 확정되어 학습 데이터에 추가되었습니다"}
    
    elif body.action == "mark_safe":
        # 학습 데이터로 저장 (safe)
        training_file = TRAINING_DATA_DIR / f"safe_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        training_data = {
            "text": feedback_data['conversation_text'],
            "label": "safe",
            "predicted_tier": feedback_data['predicted_tier'],
            "admin_confirmed": True,
            "admin_notes": body.admin_notes,
            "original_feedback_id": body.feedback_id,
            "timestamp": datetime.now().isoformat()
        }
        with open(training_file, 'w', encoding='utf-8') as f:
            json.dump(training_data, f, ensure_ascii=False, indent=2)
        feedback_path.unlink()  # 처리 완료 후 삭제
        return {"status": "success", "message": "정상 대화로 확정되어 학습 데이터에 추가되었습니다"}
    
    else:  # ignore
        return {"status": "success", "message": "무시되었습니다"}


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
                data = json.load(f)
                data['feedback_id'] = filepath.name
                feedbacks.append(data)
        except Exception:
            continue
    
    # 별점별 집계
    by_rating = {i: 0 for i in range(1, 6)}
    for fb in feedbacks:
        rating = fb.get('rating', 3)
        by_rating[rating] = by_rating.get(rating, 0) + 1
    
    # 낮은 별점 케이스 (1~2점) - 전체 대화 포함
    low_rating_cases = [
        {
            "feedback_id": fb['feedback_id'],
            "timestamp": fb['timestamp'],
            "rating": fb['rating'],
            "predicted_tier": fb['predicted_tier'],
            "actual_tier": fb.get('actual_tier'),
            "comments": fb.get('comments'),
            "conversation_preview": fb['conversation_text'][:100],
            "conversation_full": fb['conversation_text'],  # 전체 대화
            "predicted_score": fb.get('predicted_score', 0)
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
        "low_rating_cases": low_rating_cases,  # 전체 반환
        "accuracy": accuracy,
        "accurate_count": accurate_count,
        "total_with_actual": total_with_actual
    }

