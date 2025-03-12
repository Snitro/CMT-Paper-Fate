import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText


class Mail:
    def __init__(self, sender_email, sender_password, receiver_email, smtp_server, smtp_port=465):
        """
        Initialize the Mail class with email credentials and server settings.

        :param sender_email: Sender's email address
        :param sender_password: Sender's email password
        :param receiver_email: Recipient's email address
        :param smtp_server: SMTP server address
        :param smtp_port: SMTP server port (default is 465 for SSL)
        """
        self.__sender_email = sender_email
        self.__sender_password = sender_password
        self.__receiver_email = receiver_email
        self.__smtp_server = smtp_server
        self.__smtp_port = smtp_port

    def send_email(self, subject, content):
        """
        Sends an email notification.

        :param subject: Email subject
        :param content: Email body content
        """
        msg = MIMEMultipart()
        msg["From"] = self.__sender_email
        msg["To"] = self.__receiver_email
        msg["Subject"] = subject
        msg.attach(MIMEText(content, "plain"))

        try:
            with smtplib.SMTP_SSL(self.__smtp_server, self.__smtp_port) as server:
                server.login(self.__sender_email, self.__sender_password)
                server.sendmail(self.__sender_email, self.__receiver_email, msg.as_string())
            print("✅ Email sent successfully!")
        except Exception as e:
            print(f"❌ Failed to send email: {e}")
