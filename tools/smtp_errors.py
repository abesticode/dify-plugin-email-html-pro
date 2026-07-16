"""Utilities to translate low-level smtplib/socket exceptions into
human-readable, actionable error messages.

This module centralizes the mapping of common SMTP error codes (e.g. the
enhanced status codes returned by Microsoft 365 / Exchange Online) to plain
English explanations, so that both the tool invocations and the provider
credential validation surface the *real* SMTP error instead of a generic or
misleading "success" message.
"""

import re
import smtplib
import socket
import ssl
from typing import Optional

# Mapping of "<smtp_code> <enhanced_status_code>" (or bare smtp code) to a
# human readable explanation of what the error means and how to resolve it.
#
# Key format: build the key the same way `translate_smtp_error` does below,
# i.e. f"{smtp_code} {enhanced_status_code}" (e.g. "535 5.7.139"), where the
# enhanced status code is the RFC 3463 "x.y.z" code found in the server's
# response text. If a server does not return an enhanced status code, fall
# back to a bare `str(smtp_code)` key (e.g. "530"). To add support for a new
# provider-specific error, capture the real `smtp_code`/response text from a
# failing call and add an entry here with a plain-English explanation and,
# where applicable, remediation steps.
SMTP_ERROR_EXPLANATIONS = {
    "535 5.7.139": (
        "SMTP AUTH is disabled on the recipient's Microsoft 365 tenant. "
        "This is a tenant policy setting, not a credentials issue. Ask the "
        "tenant admin to enable SMTP AUTH, or use an alternative sending "
        "method (e.g., Graph API)."
    ),
    "535 5.7.3": "Authentication unsuccessful: the account or password is incorrect.",
}

_ENHANCED_CODE_RE = re.compile(r"\b\d\.\d+\.\d+\b")


def _decode(value) -> str:
    if isinstance(value, bytes):
        return value.decode("utf-8", errors="replace")
    return str(value)


def _extract_enhanced_code(raw_text: str) -> Optional[str]:
    match = _ENHANCED_CODE_RE.search(raw_text)
    return match.group(0) if match else None


class SMTPSendError(Exception):
    """Raised when an SMTP operation (login/send) fails.

    Carries the real SMTP status code and server response (when available)
    so callers can surface the actual error to the user/log instead of a
    generic message.
    """

    def __init__(self, message: str, code: Optional[str] = None, response: Optional[str] = None,
                 category: str = "smtp"):
        super().__init__(message)
        self.code = code
        self.response = response
        # category is one of: "auth", "smtp", "network", "unknown"
        self.category = category

    def __str__(self) -> str:
        return super().__str__()


def translate_smtp_error(exc: Exception) -> SMTPSendError:
    """Translate an smtplib/socket exception into an SMTPSendError carrying
    the real SMTP code/response plus a human-readable explanation when one
    is known.
    """
    if isinstance(exc, (smtplib.SMTPAuthenticationError, smtplib.SMTPResponseException)):
        code = getattr(exc, "smtp_code", None)
        raw = _decode(getattr(exc, "smtp_error", b""))
        enhanced = _extract_enhanced_code(raw)
        if code is not None and enhanced:
            key = f"{code} {enhanced}"
        elif code is not None:
            key = str(code)
        else:
            key = "unknown"
        explanation = SMTP_ERROR_EXPLANATIONS.get(key)

        is_auth = isinstance(exc, smtplib.SMTPAuthenticationError)
        prefix = "SMTP authentication failed" if is_auth else "SMTP server rejected the request"
        message = f"{prefix} ({key}): {raw}"
        if explanation:
            message += f" — {explanation}"
        return SMTPSendError(message, code=key, response=raw, category="auth" if is_auth else "smtp")

    if isinstance(exc, smtplib.SMTPException):
        return SMTPSendError(f"SMTP error: {exc}", category="smtp")

    if isinstance(exc, (socket.timeout, TimeoutError)):
        return SMTPSendError(
            f"Network/connectivity error: connection to the SMTP server timed out ({exc}).",
            category="network",
        )

    if isinstance(exc, ssl.SSLError):
        return SMTPSendError(
            f"TLS/SSL error while establishing a secure connection to the SMTP server ({exc}).",
            category="network",
        )

    if isinstance(exc, (ConnectionError, OSError, socket.error)):
        return SMTPSendError(
            f"Network/connectivity error: could not reach the SMTP server ({exc}).",
            category="network",
        )

    return SMTPSendError(str(exc), category="unknown")
