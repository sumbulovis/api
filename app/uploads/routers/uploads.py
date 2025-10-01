from typing import Optional, List

from fastapi import APIRouter, BackgroundTasks, HTTPException, status
from pydantic import BaseModel, Field

from app.services.youtube_shorts_uploader import YouTubeShortsUploader


router = APIRouter(
    prefix="/uploads",
    tags=["uploads"],
    responses={404: {"description": "Not found"}},
)


class UploadShortRequest(BaseModel):
    video_path: str = Field(..., description="Absolute path to local video file")
    title: str
    description: Optional[str] = ""
    tags: Optional[List[str]] = None
    privacy_status: Optional[str] = None  # private|unlisted|public
    category_id: Optional[str] = None
    made_for_kids: bool = False
    publish_at_rfc3339: Optional[str] = None


class UploadShortResponse(BaseModel):
    id: Optional[str] = None
    url: Optional[str] = None
    status: str
    message: Optional[str] = None


def _perform_upload(payload: UploadShortRequest) -> dict:
    uploader = YouTubeShortsUploader()
    return uploader.upload(
        video_path=payload.video_path,
        title=payload.title,
        description=payload.description,
        tags=payload.tags,
        privacy_status=payload.privacy_status,
        category_id=payload.category_id,
        made_for_kids=payload.made_for_kids,
        publish_at_rfc3339=payload.publish_at_rfc3339,
    )


@router.post("/shorts", response_model=UploadShortResponse, status_code=status.HTTP_202_ACCEPTED)
async def upload_short(payload: UploadShortRequest, background_tasks: BackgroundTasks):
    # Quick check to fail early on missing files
    try:
        # schedule background upload
        background_tasks.add_task(_perform_upload, payload)
        return UploadShortResponse(status="scheduled")
    except FileNotFoundError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:  # noqa: BLE001
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


