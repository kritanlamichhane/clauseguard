from typing import List, Dict, Any
from fastapi import APIRouter, HTTPException, Depends, status

from backend.core.models import HistorySummaryItem, HistoryDetailResponse
from backend.core.database import get_user_history, get_history_detail, delete_history_item
from backend.core.dependencies import get_current_user

router = APIRouter(prefix="/history", tags=["History"])


@router.get("", response_model=List[HistorySummaryItem])
def list_history(current_user: Dict[str, Any] = Depends(get_current_user)):
    """Returns the list of previously analyzed documents for the authenticated user."""
    history_items = get_user_history(current_user["id"])
    return history_items


@router.get("/{history_id}", response_model=HistoryDetailResponse)
def get_history_item(history_id: int, current_user: Dict[str, Any] = Depends(get_current_user)):
    """Returns the complete analysis report for a specific past document audit."""
    item = get_history_detail(history_id, current_user["id"])
    if not item:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="History item not found or unauthorized access."
        )
    return item


@router.delete("/{history_id}")
def delete_history(history_id: int, current_user: Dict[str, Any] = Depends(get_current_user)):
    """Deletes a past document audit record from the user's history."""
    deleted = delete_history_item(history_id, current_user["id"])
    if not deleted:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="History item not found or unauthorized access."
        )
    return {"message": "Document audit deleted from history successfully.", "id": history_id}
