import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

class EmailAutomationSystem:
    def __init__(self, smtp_server, port, username, password):
        self.smtp_server = smtp_server
        self.port = port
        self.username = username
        self.password = password

    def send_email(self, to_email, subject, body):
        msg = MIMEMultipart()
        msg['From'] = self.username
        msg['To'] = to_email
        msg['Subject'] = subject
        msg.attach(MIMEText(body, 'plain'))
        with smtplib.SMTP(self.smtp_server, self.port) as server:
            server.starttls()
            server.login(self.username, self.password)
            server.sendmail(self.username, to_email, msg.as_string())
        print(f"Email sent to {to_email}")

if __name__ == "__main__":
    print("Email Automation System Demo")
    # system = EmailAutomationSystem('smtp.example.com', 587, 'user@example.com', 'password')
    # system.send_email('recipient@example.com', 'Test Subject', 'Hello from Python!')
