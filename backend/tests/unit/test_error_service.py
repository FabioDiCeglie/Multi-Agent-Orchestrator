from services.error_service import ErrorService


class FakeProviderError(Exception):
    def __init__(self, message: str) -> None:
        super().__init__(message)
        self.message = message


def test_clean_error_extracts_provider_message() -> None:
    payload = (
        'AnthropicException - {"type":"error","error":{"type":"invalid_request_error",'
        '"message":"Your credit balance is too low to access the Anthropic API."}}'
    )
    exc = FakeProviderError(payload)

    assert ErrorService.clean_provider_error(exc) == (
        "Your credit balance is too low to access the Anthropic API."
    )


def test_clean_error_returns_plain_message_when_no_json_suffix() -> None:
    exc = RuntimeError("Connection refused")

    assert ErrorService.clean_provider_error(exc) == "Connection refused"


def test_clean_error_returns_raw_when_json_is_invalid() -> None:
    exc = FakeProviderError("AnthropicException - not-json")

    assert ErrorService.clean_provider_error(exc) == "AnthropicException - not-json"
