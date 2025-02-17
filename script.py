import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.image import MIMEImage
import os
from dotenv import load_dotenv
from typing import Dict, List
import logging
from pathlib import Path
import ssl

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class CIDEmailSender:
    def __init__(self):
        # Load environment variables
        load_dotenv()
        
        # Email configuration
        self.smtp_server = os.getenv("SMTP_SERVER", "smtp.gmail.com")
        self.smtp_port = int(os.getenv("SMTP_PORT", "587"))
        self.sender_email = os.getenv("EMAIL_SENDER")
        self.sender_password = os.getenv("EMAIL_PASSWORD")
        
        # Validate required environment variables
        if not all([self.sender_email, self.sender_password]):
            raise ValueError("Missing required environment variables: EMAIL_SENDER and EMAIL_PASSWORD")
        
        # SSL Context for secure connection
        self.ssl_context = ssl.create_default_context()

    def create_email_message(self, recipient: Dict[str, str], template_path: str, images: Dict[str, str]) -> MIMEMultipart:
        """
        Create email message with HTML template and embedded images
        
        Args:
            recipient (Dict[str, str]): Dictionary containing recipient details
            template_path (str): Path to HTML template file
            images (Dict[str, str]): Dictionary mapping image IDs to file paths
            
        Returns:
            MIMEMultipart: Prepared email message
        """
        msg = MIMEMultipart('related')
        msg['From'] = self.sender_email
        msg['To'] = recipient["email"]
        msg['Subject'] = f"Welcome {recipient['name']} to Tinkering Lab!"
        
        try:
            with open(template_path, 'r', encoding='utf-8') as template_file:
                html_content = template_file.read()
                
            # Personalize template
            html_content = html_content.replace('{{name}}', recipient['name'])
            html_content = html_content.replace('{{role}}', recipient['role'])
            
            # Create the HTML part
            html_part = MIMEText(html_content, "html")
            msg.attach(html_part)
            
            # Attach images with Content-ID
            for image_id, image_path in images.items():
                with open(image_path, 'rb') as img_file:
                    img = MIMEImage(img_file.read())
                    img.add_header('Content-ID', f'<{image_id}>')
                    msg.attach(img)
            
        except FileNotFoundError:
            logger.error(f"Template file not found: {template_path}")
            raise
        except Exception as e:
            logger.error(f"Error creating email message: {str(e)}")
            raise
            
        return msg

    def send_email(self, recipient: Dict[str, str], template_path: str, images: Dict[str, str]) -> bool:
        """
        Send email to a single recipient
        
        Args:
            recipient (Dict[str, str]): Dictionary containing recipient details
            template_path (str): Path to HTML template file
            images (Dict[str, str]): Dictionary mapping image IDs to file paths
            
        Returns:
            bool: True if email sent successfully, False otherwise
        """
        try:
            msg = self.create_email_message(recipient, template_path, images)
            
            with smtplib.SMTP(self.smtp_server, self.smtp_port) as server:
                server.starttls(context=self.ssl_context)
                server.login(self.sender_email, self.sender_password)
                server.send_message(msg)
                
            logger.info(f"Email sent successfully to {recipient['email']}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to send email to {recipient['email']}: {str(e)}")
            return False

    def send_bulk_emails(self, recipients: List[Dict[str, str]], template_path: str, images: Dict[str, str]) -> Dict[str, List[str]]:
        """
        Send emails to multiple recipients
        
        Args:
            recipients (List[Dict[str, str]]): List of recipient dictionaries
            template_path (str): Path to HTML template file
            images (Dict[str, str]): Dictionary mapping image IDs to file paths
            
        Returns:
            Dict[str, List[str]]: Dictionary containing successful and failed email addresses
        """
        results = {
            "success": [],
            "failed": []
        }
        
        for recipient in recipients:
            if self.send_email(recipient, template_path, images):
                results["success"].append(recipient["email"])
            else:
                results["failed"].append(recipient["email"])
                
        return results

def main():
    # Example usage
    recipients = [  # Changed to a list of dictionaries
        

        # Add more recipients as needed
    ]
    
    images = {
        "logo": "./images/logo.png",
        "instagram2x": "./images/instagram2x.png",
        "linkedin2x": "./images/linkedin2x.png",
        "website2x": "./images/website2x.png",
        "662b71d6-f351-4098-842f-8c5f50a34709": "./images/662b71d6-f351-4098-842f-8c5f50a34709.jpg",
        "bfd":"./images/bfd.jpg",
    }
    
    template_path = Path("./new-email.html")
    
    try:
        sender = CIDEmailSender()
        results = sender.send_bulk_emails(recipients, template_path, images)
        
        logger.info(f"Successfully sent emails to: {', '.join(results['success'])}")
        if results['failed']:
            logger.warning(f"Failed to send emails to: {', '.join(results['failed'])}")
            
    except Exception as e:
        logger.error(f"Application error: {str(e)}")

if __name__ == "__main__":
    main()