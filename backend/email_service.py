import os
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

def send_welcome_email(to_email: str):
    """
    Sends a welcome email to the user.
    If SMTP env vars are not set, logs to console instead (Simulation).
    """
    smtp_server = os.getenv("SMTP_SERVER")
    smtp_port = os.getenv("SMTP_PORT", "587")
    smtp_user = os.getenv("SMTP_USER")
    smtp_password = os.getenv("SMTP_PASSWORD")
    sender_email = os.getenv("SENDER_EMAIL", "noreply@venturemind.ai")

    subject = "Welcome to VentureMind.AI – Let's Build the Future"
    
    body = f"""
    <html>
    <head>
        <style>
            body {{ font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; background-color: #f3f4f6; padding: 20px; }}
            .container {{ max-width: 600px; margin: 0 auto; background: white; padding: 40px; border-radius: 12px; box-shadow: 0 4px 6px rgba(0,0,0,0.1); }}
            h1 {{ color: #111827; font-size: 24px; margin-bottom: 10px; }}
            p {{ color: #4b5563; font-size: 16px; line-height: 1.6; }}
            .btn {{ display: inline-block; background-color: #2563eb; color: white !important; padding: 12px 24px; text-decoration: none; border-radius: 6px; font-weight: bold; margin-top: 20px; }}
            .footer {{ margin-top: 30px; font-size: 12px; color: #9ca3af; text-align: center; border-top: 1px solid #e5e7eb; padding-top: 20px; }}
        </style>
    </head>
    <body>
        <div class="container">
            <h1>Welcome to VentureMind.AI 🚀</h1>
            <p>Hi there,</p>
            <p>You've just taken the first step towards building your next big venture. VentureMind is your 24/7 AI Co-Founder designed to turn rough ideas into actionable business plans in seconds.</p>
            
            <h3>What you can do now:</h3>
            <ul>
                <li><strong>Generate Startup Packs:</strong> Get instant Pitch Decks, Financial Models, and Strategies.</li>
                <li><strong>Design Brand Identity:</strong> Create professional logos and color palettes automatically.</li>
                <li><strong>Understand Your Market:</strong> Get deep insights into TAM, SAM, and Competitors.</li>
            </ul>
            
            <a href="http://localhost:8080" class="btn">Launch App</a>
            
            <br><br>
            <p>We believe that execution is everything, but a great plan is the spark. We're here to provide that spark.</p>
            <p>Happy Building!</p>
            <p><strong>The VentureMind Team</strong></p>
            
            <div class="footer">
                &copy; 2025 VentureMind.AI Inc. All rights reserved.<br>
                This is a simulated SaaS notification.
            </div>
        </div>
    </body>
    </html>
    """

    if not (smtp_server and smtp_user and smtp_password):
        print(f"\n[EMAIL SERVICE] 📧 Simulation: Sending Welcome Email to {to_email}")
        print("-" * 60)
        print(f"Subject: {subject}")
        # Print a preview of the body (stripped of tags for readability in log)
        preview = body.replace("<br>", "\n").replace("</p>", "\n").replace("</li>", "\n")
        import re
        text_only = re.sub('<[^<]+?>', '', preview)
        print(text_only[:500] + "...\n[End of Email Preview]")
        print("-" * 60 + "\n")
        return True

    try:
        msg = MIMEMultipart()
        msg["From"] = sender_email
        msg["To"] = to_email
        msg["Subject"] = subject
        msg.attach(MIMEText(body, "html"))

        server = smtplib.SMTP(smtp_server, int(smtp_port))
        server.starttls()
        server.login(smtp_user, smtp_password)
        server.sendmail(sender_email, to_email, msg.as_string())
        server.quit()
        print(f"[EMAIL SERVICE] Sent Welcome Email to {to_email}")
        return True
    except Exception as e:
        print(f"[EMAIL SERVICE] Error sending email: {e}")
        return False
