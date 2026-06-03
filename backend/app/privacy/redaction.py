def assert_no_content_logging(value: str) -> None:
    if value:
        raise RuntimeError("Sensitive content must not be passed to logs")
