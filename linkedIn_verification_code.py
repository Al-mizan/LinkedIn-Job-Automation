import imaplib
import email
import re
import os
from dotenv import load_dotenv
from email.header import decode_header

class LinkedInVerification:
    def __init__(self):
        load_dotenv()
        self.gmail_user = os.getenv("GMAIL_USER")
        self.gmail_password = os.getenv("GMAIL_APP_PASSWORD")

    def connect_to_gmail(self):
        """Connect to Gmail IMAP server"""
        try:
            mail = imaplib.IMAP4_SSL("imap.gmail.com")
            mail.login(self.gmail_user, self.gmail_password)
            return mail
        except Exception as e:
            print(f"Connection failed: {str(e)}")
            return None

    def extract_code(self, subject):
        """Extract 6-digit code from subject"""
        match = re.search(r'(?:verification code is|code:|code is|Here\'s your verification code)\s*(\d{6})', subject,
                          re.IGNORECASE)
        return match.group(1) if match else None

    def get_latest_verification_email(self, mail):
        """Fetch the single latest LinkedIn verification email"""
        try:
            mail.select("inbox")
            status, messages = mail.search(
                None,
                '(FROM "linkedin.com" SUBJECT "verification")'
            )
            if status != "OK" or not messages[0]:
                return None

            latest_email_id = messages[0].split()[-1]
            status, data = mail.fetch(latest_email_id, "(RFC822)")
            if status != "OK":
                return None

            msg = email.message_from_bytes(data[0][1])
            subject = decode_header(msg["Subject"])[0][0]
            subject = subject.decode() if isinstance(subject, bytes) else subject
            code = self.extract_code(subject)

            return {
                "subject": subject,
                "code": code
            } if code else None

        except Exception as e:
            print(f"Error: {str(e)}")
            return None

    def get_verification_code(self):
        mail = self.connect_to_gmail()
        if not mail:
            return ""

        email_data = self.get_latest_verification_email(mail)
        code = ""

        if email_data:
            print("Latest verification email:")
            print(f"Subject: {email_data['subject']}")
            print(f"Code: {email_data['code']}")
            code = email_data['code']
        else:
            print("No matching verification email found")

        mail.close()
        mail.logout()
        return code