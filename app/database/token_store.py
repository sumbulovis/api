from __future__ import annotations

from typing import Optional
import json

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, delete
from google.oauth2.credentials import Credentials

from app.database.models import YouTubeToken


class YouTubeTokenStore:
    """Async token store for persisting a single YouTube OAuth credential set.

    We store exactly one row; new writes replace existing data.
    """

    def __init__(self, session: AsyncSession):
        self.session = session

    async def read_credentials(self, scopes: list[str]) -> Optional[Credentials]:
        query = select(YouTubeToken).limit(1)
        result = await self.session.execute(query)
        row = result.scalar_one_or_none()
        if not row:
            return None
        info = json.loads(row.credentials_json)
        return Credentials.from_authorized_user_info(info, scopes)

    async def write_credentials(self, credentials: Credentials) -> None:
        # Replace the single row
        await self.session.execute(delete(YouTubeToken))
        self.session.add(YouTubeToken(credentials_json=credentials.to_json()))
        await self.session.commit()


