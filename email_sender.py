#!/usr/bin/env python3

import smtplib
import csv
import os
import sys
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.image import MIMEImage
from email.utils import formataddr
import time
from datetime import datetime
import logging
from dotenv import load_dotenv

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('email_sending.log'),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)

class VAAEmailSender:
    def __init__(self):
        # Load environment variables from .env file
        load_dotenv()
        
        # Email configuration
        self.smtp_server = "smtp.gmail.com"
        self.smtp_port = 587
        self.sender_email = os.getenv('EMAIL_ADDRESS', "")
        self.sender_password = os.getenv('APP_PASSWORD', "")
        self.sender_name = os.getenv('SENDER_NAME', "")
        
        # Email content
        self.subject = os.getenv('EMAIL_SUBJECT', "")
        self.template_file = os.getenv('TEMPLATE_FILE', "")
        self.recipients_file = os.getenv('RECIPIENTS_FILE', "")
        
        # Statistics
        self.total_emails = 0
        self.sent_emails = 0
        self.failed_emails = 0
        
    def load_email_template(self):
        """Load the HTML email template"""
        try:
            with open(self.template_file, 'r', encoding='utf-8') as file:
                return file.read()
        except FileNotFoundError:
            logger.error(f"Template file {self.template_file} not found!")
            return None
        except Exception as e:
            logger.error(f"Error loading template: {str(e)}")
            return None
    
    def load_recipients(self):
        """Load recipients from CSV file"""
        recipients = []
        try:
            with open(self.recipients_file, 'r', encoding='utf-8') as file:
                reader = csv.DictReader(file)
                for row in reader:
                    if row.get('email') and row.get('name'):
                        recipients.append({
                            'name': row['name'].strip(),
                            'email': row['email'].strip().lower()
                        })
            logger.info(f"Loaded {len(recipients)} recipients from {self.recipients_file}")
            return recipients
        except FileNotFoundError:
            logger.error(f"Recipients file {self.recipients_file} not found!")
            return []
        except Exception as e:
            logger.error(f"Error loading recipients: {str(e)}")
            return []
    
    def load_image(self, image_path):
        """Load image file for email attachment"""
        try:
            with open(image_path, 'rb') as file:
                return file.read()
        except FileNotFoundError:
            logger.warning(f"Image file {image_path} not found!")
            return None
        except Exception as e:
            logger.warning(f"Error loading image {image_path}: {str(e)}")
            return None
    
    def create_email(self, recipient_name, recipient_email, html_template):
        """Create personalized email message"""
        # Personalize the template
        personalized_html = html_template.replace("{{NAME}}", recipient_name)
        
        # Create message
        msg = MIMEMultipart('related')
        msg['From'] = formataddr((self.sender_name, self.sender_email))
        msg['To'] = recipient_email
        msg['Subject'] = self.subject
        
        # Add HTML content
        html_part = MIMEText(personalized_html, 'html', 'utf-8')
        msg.attach(html_part)
        
        # Add images (if available)
        self.attach_images(msg)
        
        return msg
    
    def attach_images(self, msg):
        """Attach images to email"""
        # List of images to attach
        images = [
            ('banner_image', 'vaadigest.gif'),  # Main banner in center
            ('wkc_logo', 'WKC.png'),            # Left side logo (local backup)
            ('vaa_logo', 'image.png'),          # Right side logo (local backup)
            # Add more images as needed for person photos
            # ('karan_photo', 'photos/karan.jpg'),
            # ('navami_photo', 'photos/navami.jpg'),
            # etc.
        ]
        
        for cid, filepath in images:
            image_data = self.load_image(filepath)
            if image_data:
                image = MIMEImage(image_data)
                image.add_header('Content-ID', f'<{cid}>')
                image.add_header('Content-Disposition', 'inline')
                msg.attach(image)
    
    def setup_smtp_connection(self):
        """Setup SMTP connection"""
        try:
            server = smtplib.SMTP(self.smtp_server, self.smtp_port)
            server.starttls()
            server.login(self.sender_email, self.sender_password)
            logger.info("SMTP connection established successfully")
            return server
        except Exception as e:
            logger.error(f"Failed to setup SMTP connection: {str(e)}")
            return None
    
    def send_single_email(self, server, recipient, html_template):
        """Send email to a single recipient"""
        try:
            msg = self.create_email(recipient['name'], recipient['email'], html_template)
            text = msg.as_string()
            server.sendmail(self.sender_email, recipient['email'], text)
            self.sent_emails += 1
            logger.info(f"✓ Email sent to {recipient['name']} ({recipient['email']})")
            return True
        except Exception as e:
            self.failed_emails += 1
            logger.error(f"✗ Failed to send email to {recipient['name']} ({recipient['email']}): {str(e)}")
            return False
    
    def send_bulk_emails(self, test_mode=False, batch_size=50, delay_between_batches=60):
        """Send emails to all recipients"""
        # Load template and recipients
        html_template = self.load_email_template()
        if not html_template:
            logger.error("Cannot proceed without email template")
            return False
        
        recipients = self.load_recipients()
        if not recipients:
            logger.error("Cannot proceed without recipients")
            return False
        
        self.total_emails = len(recipients)
        
        if test_mode:
            # In test mode, send only to first 3 recipients
            recipients = recipients[:3]
            logger.info("Running in TEST MODE - sending to first 3 recipients only")
        
        logger.info(f"Starting bulk email send to {len(recipients)} recipients")
        
        # Setup SMTP connection
        server = self.setup_smtp_connection()
        if not server:
            return False
        
        try:
            # Send emails in batches
            for i, recipient in enumerate(recipients, 1):
                success = self.send_single_email(server, recipient, html_template)
                
                # Add small delay between emails to avoid rate limiting
                time.sleep(1)
                
                # Batch processing with breaks
                if i % batch_size == 0 and i < len(recipients):
                    logger.info(f"Completed batch of {batch_size} emails. Taking a {delay_between_batches}s break...")
                    server.quit()  # Close current connection
                    time.sleep(delay_between_batches)
                    server = self.setup_smtp_connection()  # Reconnect
                    if not server:
                        logger.error("Failed to reconnect to SMTP server")
                        break
                
                # Progress update every 25 emails
                if i % 25 == 0:
                    logger.info(f"Progress: {i}/{len(recipients)} emails processed")
            
            server.quit()
            
        except Exception as e:
            logger.error(f"Error during bulk email sending: {str(e)}")
            if server:
                server.quit()
            return False
        
        # Final statistics
        logger.info("\n" + "="*50)
        logger.info("EMAIL SENDING COMPLETED")
        logger.info(f"Total recipients: {len(recipients)}")
        logger.info(f"Successfully sent: {self.sent_emails}")
        logger.info(f"Failed: {self.failed_emails}")
        logger.info(f"Success rate: {(self.sent_emails/len(recipients)*100):.1f}%")
        logger.info("="*50)
        
        return True
    
    def setup_credentials(self):
        """Setup email credentials from environment variables"""
        print("\n=== VAA Email Newsletter Setup ===")
        print("Loading email credentials from environment variables...")
        
        if not self.sender_email or not self.sender_password:
            print("Error: Email credentials not found in environment variables!")
            print("Please ensure your .env file contains:")
            print("EMAIL_ADDRESS=your_email@gmail.com")
            print("APP_PASSWORD=your_app_password")
            return False
        
        print(f"Email loaded: {self.sender_email}")
        print("App password loaded successfully")
        return True

def create_sample_recipients_file():
    """Create a sample recipients CSV file"""
    sample_data = [
        {'name': 'Ramnath Sharma', 'email': 'ramnath@example.com'},
        {'name': 'Priya Nayak', 'email': 'priya.nayak@example.com'},
        {'name': 'Kiran Pai', 'email': 'kiran.pai@example.com'},
        {'name': 'Anita Shenoy', 'email': 'anita.shenoy@example.com'},
        {'name': 'Vikram Rao', 'email': 'vikram.rao@example.com'},
    ]
    
    filename = 'recipients.csv'
    with open(filename, 'w', newline='', encoding='utf-8') as file:
        writer = csv.DictWriter(file, fieldnames=['name', 'email'])
        writer.writeheader()
        writer.writerows(sample_data)
    
    print(f"Sample recipients file '{filename}' created with {len(sample_data)} entries.")
    print("Please edit this file with your actual recipient data before sending emails.")

def main():
    sender = VAAEmailSender()
    
    # Check if recipients file exists
    if not os.path.exists('recipients.csv'):
        print("Recipients file not found. Creating sample file...")
        create_sample_recipients_file()
        print("\nPlease edit 'recipients.csv' with your actual recipient data and run the script again.")
        return
    
    # Setup credentials
    if not sender.setup_credentials():
        return
    
    # Ask for test mode
    test_mode = input("\nRun in test mode? (sends to first 3 recipients only) [y/N]: ").lower().startswith('y')
    
    # Confirm before sending
    recipients = sender.load_recipients()
    count = min(3, len(recipients)) if test_mode else len(recipients)
    
    print(f"\nReady to send emails to {count} recipients.")
    confirm = input("Do you want to proceed? [y/N]: ").lower().startswith('y')
    
    if confirm:
        sender.send_bulk_emails(test_mode=test_mode)
    else:
        print("Email sending cancelled.")

if __name__ == "__main__":
    main()
