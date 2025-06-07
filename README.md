# VAA Digest Email Newsletter Sender

A Python-based email newsletter sender for the VAA (Visual Arts Association) Digest. This tool sends personalized HTML emails to a list of recipients with embedded images and professional formatting.

## Features

- 📧 **Automated Email Sending**: Send bulk emails to multiple recipients
- 🎨 **HTML Email Templates**: Rich HTML email content with embedded images
- 🔐 **Secure Credential Management**: Uses environment variables for email credentials
- 📊 **Progress Tracking**: Real-time progress updates and statistics
- 🧪 **Test Mode**: Send to limited recipients for testing
- 📝 **Comprehensive Logging**: Detailed logs of email sending process
- 🔄 **Batch Processing**: Handles large recipient lists with rate limiting
- 🖼️ **Image Embedding**: Automatically embeds logos and images in emails

## Prerequisites

- Python 3.x
- Gmail account with App Password enabled
- Linux/Ubuntu system (tested on Ubuntu 24.04)

## Installation

1. **Clone or download the project files**

2. **Install required Python packages**:

   ```bash
   sudo apt update
   sudo apt install python3-dotenv -y
   ```

3. **Set up your email credentials**:
   - Copy `.env.example` to `.env`
   - Edit `.env` with your email credentials:
   ```bash
   cp .env.example .env
   ```

## Configuration

### Environment Variables (.env file)

Create a `.env` file in the project directory with the following variables:

```env
EMAIL_ADDRESS=your_email@gmail.com
APP_PASSWORD=your_app_password
SENDER_NAME=VAA Digest Team
EMAIL_SUBJECT=VAA Digest - Special Issue: May 2022
TEMPLATE_FILE=email_template.html
RECIPIENTS_FILE=recipients.csv
```

### Gmail App Password Setup

1. Enable 2-Factor Authentication on your Gmail account
2. Go to [Google App Passwords](https://myaccount.google.com/apppasswords)
3. Generate a new app password for "Mail"
4. Use this 16-character password in your `.env` file

### Recipients File

Create a `recipients.csv` file with the following format:

```csv
name,email
John Doe,john.doe@example.com
Jane Smith,jane.smith@example.com
```

## Project Structure

```
email sending/
├── email_sender.py          # Main Python script
├── email_template.html      # HTML email template
├── recipients.csv          # List of email recipients
├── .env                   # Environment variables (not in git)
├── .env.example          # Example environment file
├── README.md            # This documentation
├── email_sending.log   # Log file (generated)
├── vaadigest.gif      # Main banner image
├── WKC.png           # Left logo
├── image.png         # Right logo
└── .gitignore       # Git ignore file
```

## Usage

### Basic Usage

1. **Prepare your recipients**:

   ```bash
   # Edit the recipients.csv file with actual email addresses
   nano recipients.csv
   ```

2. **Run the email sender**:

   ```bash
   python3 email_sender.py
   ```

3. **Choose test mode** (recommended for first run):
   - Select 'y' to send to first 3 recipients only
   - Select 'n' to send to all recipients

### Command Line Options

The script provides interactive prompts for:

- **Test Mode**: Send to first 3 recipients only
- **Confirmation**: Final confirmation before sending

### Test Mode

Always run in test mode first to verify your setup:

```bash
python3 email_sender.py
# Choose 'y' when asked about test mode
```

## Email Template Customization

The `email_template.html` file contains the email layout. Key features:

- **Personalization**: Use `{{NAME}}` placeholder for recipient names
- **Embedded Images**: Images are automatically embedded using Content-ID
- **Responsive Design**: Optimized for both desktop and mobile
- **Professional Styling**: Clean, newsletter-style layout

### Available Image Placeholders

- `cid:banner_image` - Main banner (vaadigest.gif)
- `cid:wkc_logo` - Left logo (WKC.png)
- `cid:vaa_logo` - Right logo (image.png)

## Monitoring and Logs

### Log Files

- **email_sending.log**: Detailed logs of all email operations
- **Console Output**: Real-time progress and status updates

### Statistics Tracked

- Total recipients
- Successfully sent emails
- Failed emails
- Success rate percentage
- Processing time

## Security Best Practices

1. **Never commit `.env` file**: Contains sensitive credentials
2. **Use App Passwords**: Never use your regular Gmail password
3. **Regular credential rotation**: Update app passwords periodically
4. **Secure file permissions**: Ensure `.env` file is not readable by others
   ```bash
   chmod 600 .env
   ```

## Rate Limiting and Performance

The script includes built-in rate limiting:

- **1-second delay** between individual emails
- **Batch processing** with 60-second breaks every 50 emails
- **Progress updates** every 25 emails

## Troubleshooting

### Common Issues

1. **"No module named dotenv"**:

   ```bash
   sudo apt install python3-dotenv
   ```

2. **"Authentication failed"**:

   - Verify your Gmail App Password
   - Ensure 2FA is enabled on your Google account
   - Check your email address in `.env`

3. **"Template file not found"**:

   - Ensure `email_template.html` exists in the project directory
   - Check the `TEMPLATE_FILE` variable in `.env`

4. **"Recipients file not found"**:
   - Create `recipients.csv` with proper format
   - Check the `RECIPIENTS_FILE` variable in `.env`

### Debugging

Enable verbose logging by checking the `email_sending.log` file:

```bash
tail -f email_sending.log
```

## Development

### Adding New Images

1. Add image files to the project directory
2. Update the `images` list in `attach_images()` method:
   ```python
   images = [
       ('banner_image', 'vaadigest.gif'),
       ('new_image', 'new_image.png'),  # Add new image
   ]
   ```
3. Reference in HTML template: `<img src="cid:new_image" />`

### Customizing Email Content

Edit `email_template.html` to modify:

- Email layout and design
- Content sections
- Styling and colors
- Image placement

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly with test mode
5. Submit a pull request

## License

This project is created for the VAA (Visual Arts Association) newsletter system.

## Support

For support or questions:

- Check the log files for detailed error messages
- Verify your `.env` configuration
- Test with a small recipient list first
- Ensure all image files are present

## Version History

- **v1.0**: Initial release with basic email sending
- **v1.1**: Added environment variable support
- **v1.2**: Improved error handling and logging
- **v1.3**: Added batch processing and rate limiting

---

**Note**: Always test the email sender with a small group of recipients before sending to your entire list.
