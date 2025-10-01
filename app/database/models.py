from typing import Optional

from sqlmodel import SQLModel, Field


class YouTubeToken(SQLModel, table=True):
    __tablename__ = "youtube_tokens"

    id: Optional[int] = Field(default=None, primary_key=True)
    # Store credentials JSON as string
    credentials_json: str = Field(index=False, nullable=False)


