# Privacy Policy

## Overview
Email HTML Pro is a Dify plugin that enables sending emails via SMTP. This privacy policy explains how we handle your data.

## Data Collection
This plugin collects the following data only during email sending operations:
- **SMTP Credentials**: Server address, port, email account, and password (stored encrypted in Dify)
- **Email Content**: Subject, body, and attachments are processed in-memory only
- **Recipient Information**: Email addresses for sending purposes only

## Data Processing
- All email data is processed in real-time and is **not stored** by the plugin
- SMTP credentials are used only for authentication with your configured email server
- Email content is transmitted directly to your SMTP server and then discarded

## Third-Party Services
This plugin connects to your configured SMTP server (e.g., Gmail, AWS SES, custom SMTP servers). Please refer to your SMTP provider's privacy policy for how they handle your data:
- [Google Privacy Policy](https://policies.google.com/privacy) (for Gmail SMTP)
- [AWS Privacy Policy](https://aws.amazon.com/privacy/) (for AWS SES)

## Data Retention
- **No data is retained by this plugin**
- All email content is processed in-memory and immediately discarded after sending
- Credentials are managed by Dify's secure credential storage system

## Security
- All SMTP connections support TLS/SSL encryption
- Passwords are handled as secrets and never logged or exposed
- No email content is cached or stored

## User Rights
Users have the right to:
- Remove their SMTP credentials at any time through Dify settings
- Choose which encryption method to use for SMTP connections
- Control all data sent through the plugin

## Contact Information
For privacy-related inquiries, please contact the plugin author through GitHub or the Dify marketplace.

**Last updated**: December 2024