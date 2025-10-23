import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from tools.keys import get_secret

def send_email(to_email, subject, body):
    gmail_user = get_secret("GMAIL_USER")
    gmail_pass = get_secret("GMAIL_APP_PASSWORD")

    msg = MIMEMultipart()
    msg["From"] = gmail_user
    msg["To"] = "ywcharles21@gmail.com" # TODO: to_email
    msg["Subject"] = subject

    msg.attach(MIMEText(body, "plain"))

    try:
        with smtplib.SMTP("smtp.gmail.com", 587) as server:
            server.starttls()  # Secure connection
            server.login(gmail_user, gmail_pass)
            server.send_message(msg)
            print(f"✅ Email sent to {to_email}")
            return True
    except Exception as e:
        print(f"❌ Failed to send email to {to_email}: {e}")
        return False
