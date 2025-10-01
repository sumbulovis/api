from typing import Optional, List

from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException, status
from pydantic import BaseModel, Field

from app.services.youtube_shorts_uploader import YouTubeShortsUploader
from app.database.db import get_session
from sqlalchemy.ext.asyncio import AsyncSession
from app.database.token_store import YouTubeTokenStore


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


async def _perform_upload(payload: UploadShortRequest, session: AsyncSession) -> dict:
    token_store = YouTubeTokenStore(session)
    creds = await token_store.read_credentials(scopes=YouTubeShortsUploader().scopes)
    uploader = YouTubeShortsUploader(credentials=creds)
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
async def upload_short(payload: UploadShortRequest, background_tasks: BackgroundTasks, session: AsyncSession = Depends(get_session)):
    # Quick check to fail early on missing files
    try:
        # schedule background upload with DB session
        background_tasks.add_task(_perform_upload, payload, session)
        return UploadShortResponse(status="scheduled")
    except FileNotFoundError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:  # noqa: BLE001
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@router.post("/auth/youtube", status_code=status.HTTP_200_OK)
async def auth_youtube(session: AsyncSession = Depends(get_session)):
    """Explicitly perform OAuth and save credentials into the database.

    This will open a local browser window on the server (run_local_server). Use in
    environments where an interactive login is possible.
    """
    try:
        uploader = YouTubeShortsUploader()
        creds = uploader._interactive_login()  # interactive login; returns Credentials
        token_store = YouTubeTokenStore(session)
        await token_store.write_credentials(creds)
        return {"status": "ok"}
    except Exception as e:  # noqa: BLE001
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))

