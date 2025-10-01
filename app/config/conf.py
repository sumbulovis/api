import os
from dotenv import load_dotenv


load_dotenv()

DB_HOST = os.environ.get("DB_HOST")
DB_PORT = int(os.environ.get("DB_PORT", 5432))
DB_NAME = os.environ.get("DB_NAME")
DB_PASSWORD = os.environ.get("DB_PASSWORD")
DB_USER = os.environ.get("DB_USER")

# YouTube / Google OAuth settings
YOUTUBE_CLIENT_SECRETS_FILE = os.environ.get("YOUTUBE_CLIENT_SECRETS_FILE", "client_secret.json")
YOUTUBE_OAUTH_SCOPES = [
    "https://www.googleapis.com/auth/youtube.upload",
]
YOUTUBE_TOKEN_STORAGE = os.environ.get("YOUTUBE_TOKEN_STORAGE", ".youtube_token.json")
YOUTUBE_CATEGORY_ID = os.environ.get("YOUTUBE_CATEGORY_ID", "22")  # 22 = People & Blogs default
YOUTUBE_PRIVACY_STATUS = os.environ.get("YOUTUBE_PRIVACY_STATUS", "public")  # private|unlisted|public
