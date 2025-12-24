from typing import Any

from dify_plugin import ToolProvider
from dify_plugin.errors.tool import ToolProviderCredentialValidationError
from tools.send_mail import SendMailTool


class DifyPluginEmailHtmlProProvider(ToolProvider):
    def _validate_credentials(self, credentials: dict[str, Any]) -> None:
        try:
            # Validate required credentials are present
            required_fields = ["smtp_server", "smtp_port", "email_account", "email_password", "encrypt_method"]
            for field in required_fields:
                if not credentials.get(field):
                    raise ToolProviderCredentialValidationError(f"{field} is required")
            
            # Validate smtp_port is a valid integer
            try:
                int(credentials.get("smtp_port", ""))
            except ValueError:
                raise ToolProviderCredentialValidationError("smtp_port must be a valid integer")
            
            # Validate encrypt_method is valid
            encrypt_method = credentials.get("encrypt_method", "").upper()
            if encrypt_method not in ["NONE", "SSL", "TLS"]:
                raise ToolProviderCredentialValidationError("encrypt_method must be NONE, SSL, or TLS")
            
            # Test the credentials by sending a test email to the sender
            for _ in SendMailTool.from_credentials(credentials, user_id="").invoke(
                tool_parameters={
                    "subject": "Email HTML Pro - Setup Verification",
                    "email_content": "Your Email HTML Pro plugin has been configured successfully!",
                    "send_to": credentials.get("email_account")
                }
            ):
                pass
                
        except ToolProviderCredentialValidationError:
            raise
        except Exception as e:
            raise ToolProviderCredentialValidationError(str(e))
