from app.core.config import get_settings


class S3TemporaryStorage:
    def __init__(self) -> None:
        self.settings = get_settings()

    def assert_configured(self) -> None:
        if not self.settings.s3_temp_bucket:
            raise RuntimeError("S3_TEMP_BUCKET is not configured")
