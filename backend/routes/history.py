"""
Indian Currency Detection - History Routes
"""
from datetime import datetime
from typing import Optional
from fastapi import APIRouter, Depends, Query, HTTPException
from bson import ObjectId

from utils.auth import get_current_user
from database.connection import get_database

router = APIRouter(prefix="/api", tags=["History"])


@router.get("/history")
async def get_detection_history(
    page: int = Query(1, ge=1),
    limit: int = Query(20, ge=1, le=100),
    detection_type: Optional[str] = Query(None, pattern="^(upload|live|multi)$"),
    current_user: dict = Depends(get_current_user),
):
    """Get detection history for the authenticated user"""
    db = get_database()
    if db is None:
        raise HTTPException(status_code=500, detail="Database not connected")

    # Build query
    query = {"user_id": current_user["user_id"]}
    if detection_type:
        query["detection_type"] = detection_type

    # Get total count
    total = await db.detection_history.count_documents(query)

    # Fetch results with pagination
    skip = (page - 1) * limit
    cursor = db.detection_history.find(query).sort("date", -1).skip(skip).limit(limit)

    history = []
    async for doc in cursor:
        history.append({
            "id": str(doc["_id"]),
            "prediction": doc.get("prediction", 0),
            "confidence": round(doc.get("confidence", 0.0), 4),
            "ocr_text": doc.get("ocr_text", ""),
            "is_fake": doc.get("is_fake", False),
            "detection_type": doc.get("detection_type", "upload"),
            "date": doc.get("date", datetime.utcnow()).isoformat(),
            "image_path": doc.get("image_path", ""),
        })

    return {
        "success": True,
        "data": {
            "history": history,
            "total": total,
            "page": page,
            "limit": limit,
            "pages": (total + limit - 1) // limit,
        },
    }


@router.delete("/history/{history_id}")
async def delete_history_item(
    history_id: str,
    current_user: dict = Depends(get_current_user),
):
    """Delete a detection history item"""
    db = get_database()
    if db is None:
        raise HTTPException(status_code=500, detail="Database not connected")

    try:
        result = await db.detection_history.delete_one({
            "_id": ObjectId(history_id),
            "user_id": current_user["user_id"],
        })
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid history ID")

    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="History item not found")

    return {"success": True, "message": "History item deleted"}


@router.delete("/history")
async def clear_history(
    current_user: dict = Depends(get_current_user),
):
    """Clear all detection history for the user"""
    db = get_database()
    if db is None:
        raise HTTPException(status_code=500, detail="Database not connected")

    result = await db.detection_history.delete_many({"user_id": current_user["user_id"]})

    return {
        "success": True,
        "message": f"Deleted {result.deleted_count} history items",
    }


@router.get("/stats")
async def get_detection_stats(
    current_user: dict = Depends(get_current_user),
):
    """Get detection statistics for the user"""
    db = get_database()
    if db is None:
        raise HTTPException(status_code=500, detail="Database not connected")

    user_id = current_user["user_id"]

    # Total detections
    total = await db.detection_history.count_documents({"user_id": user_id})

    # By type
    upload_count = await db.detection_history.count_documents(
        {"user_id": user_id, "detection_type": "upload"}
    )
    live_count = await db.detection_history.count_documents(
        {"user_id": user_id, "detection_type": "live"}
    )

    # Average confidence
    pipeline_agg = [
        {"$match": {"user_id": user_id}},
        {"$group": {
            "_id": None,
            "avg_confidence": {"$avg": "$confidence"},
            "max_confidence": {"$max": "$confidence"},
        }},
    ]
    stats_cursor = db.detection_history.aggregate(pipeline_agg)
    stats = await stats_cursor.to_list(length=1)

    avg_conf = stats[0]["avg_confidence"] if stats else 0
    max_conf = stats[0]["max_confidence"] if stats else 0

    # Denomination distribution
    denom_pipeline = [
        {"$match": {"user_id": user_id}},
        {"$group": {"_id": "$prediction", "count": {"$sum": 1}}},
        {"$sort": {"_id": 1}},
    ]
    denom_cursor = db.detection_history.aggregate(denom_pipeline)
    denom_dist = {}
    async for doc in denom_cursor:
        denom_dist[str(doc["_id"])] = doc["count"]

    # Fake detections
    fake_count = await db.detection_history.count_documents(
        {"user_id": user_id, "is_fake": True}
    )

    return {
        "success": True,
        "data": {
            "total_detections": total,
            "upload_detections": upload_count,
            "live_detections": live_count,
            "average_confidence": round(avg_conf, 4),
            "max_confidence": round(max_conf, 4),
            "denomination_distribution": denom_dist,
            "fake_detections": fake_count,
        },
    }
