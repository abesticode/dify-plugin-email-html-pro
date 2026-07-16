import logging
import smtplib
import ssl
from contextlib import contextmanager
from datetime import datetime, timezone
from typing import Any

from dify_plugin import ToolProvider
from dify_plugin.errors.tool import ToolProviderCredentialValidationError

from tools.smtp_errors import translate_smtp_error


@contextmanager
def _smtp_connection(smtp_server: str, smtp_port: int, encrypt_method: str, timeout: int):
    """Open an SMTP connection (SSL/TLS/plain) and perform EHLO/STARTTLS as
    needed, yielding a ready-to-use server object."""
    ctx = ssl.create_default_context()
    if encrypt_method == "SSL":
        with smtplib.SMTP_SSL(smtp_server, smtp_port, context=ctx, timeout=timeout) as server:
            server.ehlo()
            yield server
    else:
        with smtplib.SMTP(smtp_server, smtp_port, timeout=timeout) as server:
            server.ehlo()
            if encrypt_method == "TLS":
                server.starttls(context=ctx)
                server.ehlo()
            yield server


class DifyPluginEmailHtmlProProvider(ToolProvider):
    def _validate_credentials(self, credentials: dict[str, Any]) -> None:
        try:
            # Validate required credentials are present
            required_fields = ["smtp_server", "smtp_port", "encrypt_method"]
            for field in required_fields:
                if not credentials.get(field):
                    raise ToolProviderCredentialValidationError(f"{field} is required")

            # Validate smtp_port is a valid integer
            try:
                smtp_port = int(credentials.get("smtp_port", ""))
            except ValueError:
                raise ToolProviderCredentialValidationError("smtp_port must be a valid integer")

            # Validate encrypt_method is valid
            encrypt_method = credentials.get("encrypt_method", "").upper()
            if encrypt_method not in ["NONE", "SSL", "TLS"]:
                raise ToolProviderCredentialValidationError("encrypt_method must be NONE, SSL, or TLS")

            email_account = credentials.get("email_account", "")
            email_password = credentials.get("email_password", "")
            sender_address = credentials.get("sender_address", "")
            smtp_server = credentials.get("smtp_server", "")

            # If no email_account is provided, sender_address is required
            if not email_account and not sender_address:
                raise ToolProviderCredentialValidationError(
                    "Sender Address is required when Email Account is not provided "
                    "(e.g., for relay servers without authentication)"
                )

            timeout = 30

            try:
                if email_account and email_password:
                    # Mode 1: With authentication - perform a lightweight
                    # EHLO/STARTTLS + AUTH handshake to verify the credentials
                    # actually work. We deliberately do NOT send a real email
                    # here so that saving credentials never has the side
                    # effect of delivering mail.
                    with _smtp_connection(smtp_server, smtp_port, encrypt_method, timeout) as server:
                        server.login(email_account, email_password)
                else:
                    # Mode 2: Without authentication - test SMTP connection only
                    with _smtp_connection(smtp_server, smtp_port, encrypt_method, timeout):
                        pass
            except (smtplib.SMTPException, ssl.SSLError, OSError) as e:
                smtp_error = translate_smtp_error(e)
                logging.error(
                    "Credential verification failed | server=%s account=%s category=%s code=%s "
                    "response=%s time=%s",
                    smtp_server,
                    email_account or sender_address,
                    smtp_error.category,
                    smtp_error.code,
                    smtp_error.response,
                    datetime.now(timezone.utc).isoformat(),
                )
                # Block saving and surface the real SMTP error/code, never a
                # generic "invalid credentials" message.
                raise ToolProviderCredentialValidationError(str(smtp_error)) from e

            logging.info(
                "Credential verification succeeded | server=%s account=%s verified_at=%s",
                smtp_server,
                email_account or sender_address,
                datetime.now(timezone.utc).isoformat(),
            )

        except ToolProviderCredentialValidationError:
            raise
        except Exception as e:
            raise ToolProviderCredentialValidationError(str(e))
