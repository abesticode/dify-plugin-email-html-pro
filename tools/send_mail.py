import json
import re
from typing import Any, Generator

from dify_plugin import Tool
from dify_plugin.entities.tool import ToolInvokeMessage
from dify_plugin.file.file import File
from tools.markdown_utils import convert_markdown_to_html

from tools.send import SendEmailToolParameters, send_mail


class SendMailTool(Tool):
    def _invoke(
        self, tool_parameters: dict[str, Any]

    ) -> Generator[ToolInvokeMessage, None, None]:
        """
        Send an email to a single recipient
        """
        sender = self.runtime.credentials.get("email_account", "")
        email_rgx = re.compile("^[a-zA-Z0-9._-]+@[a-zA-Z0-9_-]+(\.[a-zA-Z0-9_-]+)+$")
        password = self.runtime.credentials.get("email_password", "")
        smtp_server = self.runtime.credentials.get("smtp_server", "")
        if not smtp_server:
            yield self.create_text_message("please input smtp server")
            return

        smtp_port = self.runtime.credentials.get("smtp_port", "")
        try:
            smtp_port = int(smtp_port)
        except ValueError:
            yield self.create_text_message("Invalid parameter smtp_port(should be int)")
            return

            
        if not sender:
            yield self.create_text_message("please input email account (SMTP username)")
            return
        
        # Get sender address - this must be a valid email for the "From" header
        sender_address = self.runtime.credentials.get("sender_address", "") or sender
        
        # Only validate sender_address if it's supposed to be an email
        # For AWS SES and similar services, sender_address must be a verified email
        if sender_address and not email_rgx.match(sender_address):
            yield self.create_text_message(
                f"Invalid sender address '{sender_address}'. The sender address must be a valid email format. "
                f"For AWS SES, please set the 'Sender Address' field in credentials to your verified email."
            )
            return

        receiver_email = tool_parameters["send_to"]
        if not receiver_email:
            yield self.create_text_message("please input receiver email")
            return

        if not email_rgx.match(receiver_email):
            yield self.create_text_message(
                f"Invalid parameter receiver email, the receiver email({receiver_email}) is not a mailbox"
            )
            return

        email_content = tool_parameters.get("email_content", "")
        if not email_content:
            yield self.create_text_message("please input email content")
            return

        subject = tool_parameters.get("subject", "")
        if not subject:
            yield self.create_text_message("please input email subject")
            return

        encrypt_method = self.runtime.credentials.get("encrypt_method", "")
        if not encrypt_method:
            yield self.create_text_message("please input encrypt method")
            return
            
        # Process CC recipients
        cc_email = tool_parameters.get('cc', '')
        cc_email_list = []
        if cc_email:
            try:
                cc_email_list = json.loads(cc_email)
                for cc_email_item in cc_email_list:
                    if not email_rgx.match(cc_email_item):
                        yield self.create_text_message(
                            f"Invalid parameter cc email, the cc email({cc_email_item}) is not a mailbox"
                        )
                        return
            except json.JSONDecodeError:
                yield self.create_text_message("Invalid JSON format for CC list")
                return
                
        # Process BCC recipients
        bcc_email = tool_parameters.get('bcc', '')
        bcc_email_list = []
        if bcc_email:
            try:
                bcc_email_list = json.loads(bcc_email)
                for bcc_email_item in bcc_email_list:
                    if not email_rgx.match(bcc_email_item):
                        yield self.create_text_message(
                            f"Invalid parameter bcc email, the bcc email({bcc_email_item}) is not a mailbox"
                        )
                        return
            except json.JSONDecodeError:
                yield self.create_text_message("Invalid JSON format for BCC list")
                return
        
        # Check if markdown to HTML conversion is requested
        convert_to_html = tool_parameters.get("convert_to_html", False)
        
        # Check if raw HTML mode is enabled (overrides convert_to_html)
        is_raw_html = tool_parameters.get("is_raw_html", False)
        
        # Store original plain text content before any conversion
        plain_text_content = email_content
        
        # Handle content processing based on mode
        if is_raw_html:
            # Raw HTML mode: send content as-is without any processing
            # The email_content is already HTML and should not be modified
            pass  # No conversion needed, content stays as-is
        elif convert_to_html:
            # Convert content to HTML using shared utility
            email_content, plain_text_content = convert_markdown_to_html(email_content)
        
        # Get attachments from parameters (if any)
        attachments = tool_parameters.get("attachments", None)
        
        # Convert single attachment to list if needed
        if attachments is not None and not isinstance(attachments, list):
            attachments = [attachments]
        
        # Note: sender_address is already retrieved and validated at the beginning of this method
        
        # Get reply-to address if provided
        reply_to = tool_parameters.get("reply_to", None)
            
        # Create email parameters with all fields
        send_email_params = SendEmailToolParameters(
            smtp_server=smtp_server,
            smtp_port=smtp_port,
            email_account=sender,
            email_password=password,
            sender_address=sender_address,
            sender_to=[receiver_email],  # Single recipient as list
            subject=subject,
            email_content=email_content,
            plain_text_content=plain_text_content if convert_to_html and not is_raw_html else None,
            encrypt_method=encrypt_method,
            is_html=convert_to_html or is_raw_html,
            is_raw_html=is_raw_html,
            attachments=attachments,
            cc_recipients=cc_email_list,
            bcc_recipients=bcc_email_list,
            reply_to_address=reply_to
        )
        
        # Send the email and get result
        result = send_mail(send_email_params)
        
        # Process result
        if result:
            # If there are error results
            error_messages = []
            for key, (integer_value, bytes_value) in result.items():
                error_messages.append(f"{key}: {integer_value} {bytes_value.decode('utf-8')}")
            yield self.create_text_message(f"Email sending failed: {', '.join(error_messages)}")
        else:
            # Success
            msg = f"Email sent successfully to {receiver_email}"
            if cc_email_list:
                msg += f", CC: {', '.join(cc_email_list)}"
            if bcc_email_list:
                msg += f", BCC: {', '.join(bcc_email_list)}"
            if attachments:
                msg += f" with {len(attachments)} attachment(s)"
            yield self.create_text_message(msg)
