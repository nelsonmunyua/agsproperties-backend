from flask import current_app
from flask_mail import Message
import socket
from threading import Thread
import smtplib

class MailService:

    @staticmethod
    def send_email(subject, recipients, html_body):
        # Send email with timeout handling
        # Check if mail is configured before trying to send
        mail_server = current_app.config["MAIL_SERVER"]
        mail_username = current_app.config["MAIL_USERNAME"]

        if not mail_server or not mail_username:
            print(f"Email not configured. Skipping email: {subject} to {recipients}")
            return False

        mail = current_app.extensions.get("mail")

        if not mail:
            print("Flask-Mail not initialized. Skipping email.")
            return False

        # Create message
        msg = Message(
            subject=subject,
            recipients=recipients,
            html=html_body,
            sender=current_app.config["MAIL_DEFAULT_SENDER"]
        )

        # Capture the app so the background thread can create an app context
        app = current_app._get_current_object()

        # Send email in a separate thread to prevent blocking the main request
        def _send_async():
            with app.app_context():
                try:
                    # set a short timeout to prevent hanging
                    socket.setdefaulttimeout(5)
                    with mail.connect() as connection:
                        connection.send(msg)
                    print(f"Email sent successfully: {subject} to {recipients}")
                except socket.timeout:
                    print(f"Email failed (timeout): {subject} to {recipients}")
                except smtplib.SMTPException as e:
                    print(f"Email failed (STMP error): {subject} to {recipients} - {str(e)}")
                except Exception as e:
                    print(f"Email failed (error): {subject} to {recipients} - {str(e)}")

        try:
            # Start email sending in background thread
            thread = Thread(target=_send_async)
            thread.daemon = True
            thread.start()
            return True
        except Exception as e:
            print(f"Failed to start email thread: {str(e)}")
            return False

    @staticmethod
    def send_verification(user, token_value):
        frontend = current_app.config["FRONTEND_URL"]

        verification_url = f"{frontend}/verify-email?token={token_value}"

        html = f"""
                <html>
                <body style="font-family: Arial, sans-serif; line-height:1.6;">
                
                <h2>Verify Your Email</h2>
                
                <p>Hello {user.first_name},</p>
                
                <p>
                Thank you for creating your account.
                Please verify your email address by clicking the button below.
                </p>

                <p>
                <a href="{verification_url}"
                style="
                background:#2563eb;
                color:white;
                padding:12px 24px;
                text-decoration:none;
                border-radius:6px;
                display:inline-block;
                ">
                Verify Email
                </a>
                </p>
                
                <p>
                This verification link will expire in one hour.
                </p>
                
                <p>
                If you didn't create this account, you can safely ignore this email.
                </p>
                
                </body>
                </html>
                """

        MailService.send_email(
            subject="Verify Your Email",
            recipients=[user.email],
            html_body=html
        )

    @staticmethod
    def send_password_reset(user, token):
        frontend = current_app.config["FRONTEND_URL"]

        reset_url = f"{frontend}/reset-password?token={token}"

        html = f"""
                <html>
                <body style="font-family: Arial, sans-serif; line-height:1.6;">

                <h2>Reset Your Password</h2>

                <p>Hello {user.first_name},</p>

                <p>
                We received a request to reset the password for your account.
                Click the button below to choose a new password.
                </p>

                <p>
                <a href="{reset_url}"
                style="
                background:#2563eb;
                color:white;
                padding:12px 24px;
                text-decoration:none;
                border-radius:6px;
                display:inline-block;
                ">
                Reset Password
                </a>
                </p>

                <p>
                This reset link will expire in 15 minutes.
                </p>

                <p>
                If you didn't request a password reset, you can safely ignore this email.
                </p>

                </body>
                </html>
                """

        MailService.send_email(
            subject="Reset Your Password",
            recipients=[user.email],
            html_body=html
        )
