from app.core.config import get_settings


def assert_private_storage_disabled_by_default() -> None:
    settings = get_settings()
    if settings.store_private_documents:
        raise RuntimeError("Private document storage must stay disabled by default")
