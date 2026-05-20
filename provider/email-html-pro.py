import smtplib
import ssl
from typing import Any

from dify_plugin import ToolProvider
from dify_plugin.errors.tool import ToolProviderCredentialValidationError
from tools.send_mail import SendMailTool


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
            
            if email_account and email_password:
                # Mode 1: With authentication - send a test email to verify credentials
                send_to = sender_address or email_account
                for _ in SendMailTool.from_credentials(credentials, user_id="").invoke(
                    tool_parameters={
                        "subject": "Email HTML Pro - Setup Verification",
                        "email_content": "Your Email HTML Pro plugin has been configured successfully!",
                        "send_to": send_to
                    }
                ):
                    pass
            else:
                # Mode 2: Without authentication - test SMTP connection only
                timeout = 30
                ctx = ssl.create_default_context()
                if encrypt_method == "SSL":
                    with smtplib.SMTP_SSL(smtp_server, smtp_port, context=ctx, timeout=timeout) as server:
                        server.ehlo()
                else:
                    with smtplib.SMTP(smtp_server, smtp_port, timeout=timeout) as server:
                        if encrypt_method == "TLS":
                            server.starttls(context=ctx)
                        server.ehlo()
                
        except ToolProviderCredentialValidationError:
            raise
        except Exception as e:
            raise ToolProviderCredentialValidationError(str(e))
