#!/usr/bin/env python3

import smtplib
import csv
import os
import sys
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.utils import formataddr
import time
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

class PeerSphereEmailSender:
    def __init__(self):
        # Load environment variables from .env file
        load_dotenv()
        
        # Email SMTP configuration
        self.smtp_server = "smtp.gmail.com"
        self.smtp_port = 587
        self.sender_email = os.getenv('EMAIL_ADDRESS', "")
        self.sender_password = os.getenv('APP_PASSWORD', "")
        self.sender_name = os.getenv('SENDER_NAME', "Sahyadri PeerSphere")
        
        # Files config
        self.subject = os.getenv('EMAIL_SUBJECT', "Mock Interview Scheduled - PeerSphere")
        self.template_file = os.getenv('TEMPLATE_FILE', "template.html")
        self.recipients_file = os.getenv('RECIPIENTS_FILE', "recipients.csv")
        
        # Statistics trackers
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
        """Load recipients from the updated CSV format matching your columns"""
        recipients = []
        try:
            with open(self.recipients_file, 'r', encoding='utf-8') as file:
                reader = csv.DictReader(file)
                for row in reader:
                    if row.get('email') and row.get('name'):
                        recipients.append({
                            'name': row['name'].strip(),
                            'email': row['email'].strip().lower(),
                            'time': row['time'].strip(),
                            'pannel_name': row['pannel_name'].strip(),
                            'gmeet_link': row['gmeet_link'].strip()
                        })
            logger.info(f"Loaded {len(recipients)} recipients from {self.recipients_file}")
            return recipients
        except FileNotFoundError:
            logger.error(f"Recipients file {self.recipients_file} not found!")
            return []
        except Exception as e:
            logger.error(f"Error loading recipients: {str(e)}")
            return []
    
    def create_email(self, recipient, html_template):
        """Create personalized email message using CSV data fields"""
        # Replace the placeholders with matching data
        personalized_html = html_template
        personalized_html = personalized_html.replace("{{NAME}}", recipient['name'])
        personalized_html = personalized_html.replace("{{time}}", recipient['time'])
        personalized_html = personalized_html.replace("{{Pannel name}}", recipient['pannel_name'])
        personalized_html = personalized_html.replace("{{Name}}", recipient['name']) # Match join name requirement
        personalized_html = personalized_html.replace("{{G_MEET_LINK}}", recipient['gmeet_link'])
        
        # Assemble message container
        msg = MIMEMultipart('alternative')
        msg['From'] = formataddr((self.sender_name, self.sender_email))
        msg['To'] = recipient['email']
        msg['Subject'] = self.subject
        
        html_part = MIMEText(personalized_html, 'html', 'utf-8')
        msg.attach(html_part)
        
        return msg
    
    def setup_smtp_connection(self):
        """Setup SMTP connection with Gmail"""
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
            msg = self.create_email(recipient, html_template)
            text = msg.as_string()
            server.sendmail(self.sender_email, recipient['email'], text)
            self.sent_emails += 1
            logger.info(f"✓ Email sent to {recipient['name']} ({recipient['email']})")
            return True
        except Exception as e:
            self.failed_emails += 1
            logger.error(f"✗ Failed to send email to {recipient['name']} ({recipient['email']}): {str(e)}")
            return False
    
    def send_bulk_emails(self, test_mode=False, batch_size=40, delay_between_batches=60):
        """Send emails to all loaded recipients in safe batches"""
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
            recipients = recipients[:2]
            logger.info("Running in TEST MODE - sending to first 2 recipients only")
        
        logger.info(f"Starting bulk email send to {len(recipients)} recipients")
        
        server = self.setup_smtp_connection()
        if not server:
            return False
        
        try:
            for i, recipient in enumerate(recipients, 1):
                self.send_single_email(server, recipient, html_template)
                
                # Small anti-spam delay between individual consecutive emails
                time.sleep(1.5)
                
                # Dynamic batch reset to protect connection limits
                if i % batch_size == 0 and i < len(recipients):
                    logger.info(f"Completed batch of {batch_size} emails. Cool-down break for {delay_between_batches}s...")
                    server.quit()
                    time.sleep(delay_between_batches)
                    server = self.setup_smtp_connection()
                    if not server:
                        logger.error("Failed to reconnect to SMTP server mid-batch")
                        break
                
                if i % 10 == 0:
                    logger.info(f"Progress: {i}/{len(recipients)} records processed")
            
            if server:
                server.quit()
                
        except Exception as e:
            logger.error(f"Error during bulk processing loop: {str(e)}")
            if server:
                server.quit()
            return False
        
        logger.info("\n" + "="*50)
        logger.info("EMAIL DISPATCH RUN SUMMARY")
        logger.info(f"Total entries: {len(recipients)}")
        logger.info(f"Dispatched successfully: {self.sent_emails}")
        logger.info(f"Failed dispatches: {self.failed_emails}")
        logger.info("="*50)
        return True

def main():
    sender = PeerSphereEmailSender()
    
    if not os.path.exists(sender.recipients_file):
        print(f"Error: '{sender.recipients_file}' not found. Please place your CSV file here.")
        return
        
    if not sender.sender_email or not sender.sender_password:
        print("Missing Credentials! Verify your .env setup config details.")
        return

    test_mode = input("\nRun a dry-run test? (Sends to first 2 rows only) [y/N]: ").lower().startswith('y')
    
    recipients = sender.load_recipients()
    count = min(2, len(recipients)) if test_mode else len(recipients)
    
    confirm = input(f"Proceeding to dispatch emails to {count} recipient(s). Continue? [y/N]: ").lower().startswith('y')
    if confirm:
        sender.send_bulk_emails(test_mode=test_mode)
    else:
        print("Aborted.")

if __name__ == "__main__":
    main()