import os
import pathlib
from typing import Optional, Dict, Any

from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from googleapiclient.http import MediaFileUpload
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow

from app.config import conf


class YouTubeShortsUploader:
    """
    Uploads local videos to YouTube as Shorts.

    This class manages OAuth2 credentials and performs a resumable upload to the
    YouTube Data API. It sets the #Shorts tag automatically and allows passing
    additional metadata.
    """

    def __init__(
        self,
        client_secrets_file: Optional[str] = None,
        token_storage_path: Optional[str] = None,
        scopes: Optional[list[str]] = None,
        default_privacy_status: Optional[str] = None,
        default_category_id: Optional[str] = None,
    ) -> None:
        self.client_secrets_file = client_secrets_file or conf.YOUTUBE_CLIENT_SECRETS_FILE
        self.token_storage_path = token_storage_path or conf.YOUTUBE_TOKEN_STORAGE
        self.scopes = scopes or conf.YOUTUBE_OAUTH_SCOPES
        self.default_privacy_status = default_privacy_status or conf.YOUTUBE_PRIVACY_STATUS
        self.default_category_id = default_category_id or conf.YOUTUBE_CATEGORY_ID

        self._credentials: Optional[Credentials] = None

    def _load_credentials(self) -> Credentials:
        token_path = pathlib.Path(self.token_storage_path)
        creds: Optional[Credentials] = None

        if token_path.exists():
            creds = Credentials.from_authorized_user_file(str(token_path), self.scopes)

        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                creds.refresh(Request())
            else:
                flow = InstalledAppFlow.from_client_secrets_file(
                    self.client_secrets_file, self.scopes
                )
                # For server environments without browser, use run_local_server with a port
                creds = flow.run_local_server(port=0)

            # Save the credentials for the next run
            token_path.parent.mkdir(parents=True, exist_ok=True)
            with open(token_path, "w") as token_file:
                token_file.write(creds.to_json())

        self._credentials = creds
        return creds

    def _get_service(self):
        creds = self._credentials or self._load_credentials()
        return build("youtube", "v3", credentials=creds)

    def upload(
        self,
        video_path: str,
        title: str,
        description: str | None = None,
        tags: Optional[list[str]] = None,
        privacy_status: Optional[str] = None,
        category_id: Optional[str] = None,
        made_for_kids: bool = False,
        publish_at_rfc3339: Optional[str] = None,
        additional_snippet_fields: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """
        Upload a local video to YouTube as a Short (vertical, <=60s).

        Note: You are responsible for providing a valid file that conforms to
        YouTube Shorts constraints (vertical aspect, <= 60 seconds). This method
        will automatically add the "#Shorts" tag if not present.
        """

        if not os.path.exists(video_path):
            raise FileNotFoundError(f"Video file not found: {video_path}")

        # Ensure #Shorts tag is present
        tags = tags[:] if tags else []
        shorts_tag = "#Shorts"
        if all(t.lower() != shorts_tag.lower() for t in tags):
            tags.append(shorts_tag)

        privacy_status = privacy_status or self.default_privacy_status
        category_id = category_id or self.default_category_id

        snippet: Dict[str, Any] = {
            "title": title,
            "description": description or "",
            "tags": tags,
            "categoryId": category_id,
        }
        if additional_snippet_fields:
            snippet.update(additional_snippet_fields)

        status_body: Dict[str, Any] = {
            "privacyStatus": privacy_status,
            "selfDeclaredMadeForKids": made_for_kids,
        }
        if publish_at_rfc3339 and privacy_status == "private":
            # Scheduled publish requires private + publishAt
            status_body["publishAt"] = publish_at_rfc3339

        body = {
            "snippet": snippet,
            "status": status_body,
        }

        media = MediaFileUpload(video_path, chunksize=-1, resumable=True)

        service = self._get_service()
        request = service.videos().insert(
            part=",".join(["snippet", "status"]), body=body, media_body=media
        )

        try:
            response = None
            while response is None:
                status, response = request.next_chunk()
                # Optionally, you can log progress here using `status.progress()`
            return {
                "id": response.get("id"),
                "url": f"https://www.youtube.com/watch?v={response.get('id')}",
                "response": response,
            }
        except HttpError as err:
            raise RuntimeError(
                f"YouTube upload failed: {err.status_code} {err.error_details if hasattr(err, 'error_details') else err}"
            ) from err


