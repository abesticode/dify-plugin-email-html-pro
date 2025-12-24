<p align="center">
  <img src="_assets/icon.svg" alt="Email HTML Pro" width="80" height="80">
</p>

# Email HTML Pro

**Author:** abesticode  
**Version:** 0.0.1  
**Type:** Tool Plugin
**Repo:** https://github.com/abesticode/dify-plugin-email-html-pro

## Description

Email HTML Pro is a professional Dify plugin for sending HTML emails via SMTP with comprehensive template support. It enables seamless integration with AI workflows for sending transactional emails, marketing communications, and business notifications.

## Features

- 📧 **SMTP Support**: Compatible with Gmail, AWS SES, and any standard SMTP server
- 🎨 **Raw HTML Templates**: Send pre-built HTML templates without modification
- 📝 **Markdown to HTML**: Automatically convert markdown content to beautiful HTML emails
- 📎 **File Attachments**: Attach multiple files to your emails
- 👥 **Multiple Recipients**: Send to multiple recipients with batch sending
- 📋 **CC/BCC Support**: Include carbon copy and blind carbon copy recipients
- ↩️ **Reply-To**: Set custom reply-to addresses
- 🔐 **Encryption**: Support for SSL, TLS, or no encryption

## Installation

1. Navigate to the Dify Marketplace
2. Search for "Email HTML Pro"
3. Click "Install"
4. Configure your SMTP credentials

## Configuration

Configure the following credentials in Dify:

| Field | Description | Required |
|-------|-------------|----------|
| SMTP Server | Your SMTP server address (e.g., smtp.gmail.com) | ✅ |
| SMTP Port | SMTP port (25, 465, or 587) | ✅ |
| Email Account | Your email account for authentication | ✅ |
| Email Password | Your email password or app password | ✅ |
| Encryption Method | NONE, SSL, or TLS | ✅ |
| Sender Address | Custom sender address (optional, for AWS SES) | ❌ |

### Common SMTP Configurations

**Gmail:**
- Server: `smtp.gmail.com`
- Port: `587`
- Encryption: `TLS`
- Note: Use an [App Password](https://support.google.com/accounts/answer/185833)

**AWS SES:**
- Server: `email-smtp.{region}.amazonaws.com`
- Port: `587`
- Encryption: `TLS`
- Note: Use IAM SMTP credentials

## Tools

### Send Email
Send a single email to one recipient.

**Parameters:**
- `send_to` (required): Recipient email address
- `subject` (required): Email subject line
- `email_content` (required): Email body content
- `convert_to_html`: Convert markdown to HTML (default: false)
- `is_raw_html`: Send content as raw HTML (default: false)
- `reply_to`: Custom reply-to address
- `cc`: CC recipients as JSON array
- `bcc`: BCC recipients as JSON array
- `attachments`: Files to attach

### Send Batch Email
Send emails to multiple recipients at once.

**Parameters:**
- `send_to` (required): JSON array of recipient emails
- `subject` (required): Email subject line
- `email_content` (required): Email body content
- Other parameters same as Send Email

## Usage Examples

### Send Plain Text Email
```
send_to: user@example.com
subject: Hello World
email_content: This is a plain text email.
```

### Send Markdown Email
```
send_to: user@example.com
subject: Weekly Report
email_content: |
  # Weekly Report
  
  ## Highlights
  - Task 1 completed
  - Task 2 in progress
  
  **Next Steps:**
  1. Review documentation
  2. Deploy to production
convert_to_html: true
```

### Send Raw HTML Template
```
send_to: user@example.com
subject: Welcome to Our Service
email_content: |
  <!DOCTYPE html>
  <html>
  <body style="font-family: Arial, sans-serif;">
    <h1 style="color: #333;">Welcome!</h1>
    <p>Thank you for joining us.</p>
  </body>
  </html>
is_raw_html: true
```

### Send to Multiple Recipients
```
send_to: ["user1@example.com", "user2@example.com"]
subject: Team Announcement
email_content: Important team update...
cc: ["manager@example.com"]
```

## Troubleshooting

### Authentication Failed
- Verify your email and password are correct
- For Gmail, ensure you're using an App Password
- Check if your SMTP server requires specific security settings

### Connection Timeout
- Verify the SMTP server address is correct
- Check if the port is open and not blocked by firewall
- Try different encryption methods

### Emails Not Received
- Check recipient's spam folder
- Verify sender address is valid
- For AWS SES, ensure recipient is verified in sandbox mode

## Contributing

Contributions are welcome! Please submit issues and pull requests on GitHub.

## License

MIT License
