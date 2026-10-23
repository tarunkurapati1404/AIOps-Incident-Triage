"""Email the AI triage report to the on-call engineer (you!)."""

import os
import smtplib
import sys
from email.message import EmailMessage
from pathlib import Path

SMTP_SERVER = "smtp.gmail.com"
SMTP_PORT = 465
REPORT_PATH = Path("triage-report.md")


def main() -> None:
    sender = os.getenv("GMAIL_ADDRESS")
    password = os.getenv("GMAIL_APP_PASSWORD")
    if not sender or not password:
        sys.exit("❌ Set GMAIL_ADDRESS and GMAIL_APP_PASSWORD first.")

    if not REPORT_PATH.exists():
        sys.exit("❌ triage-report.md not found — run the analyzer first.")

    msg = EmailMessage()
    msg["From"] = sender
    msg["To"] = sender          # on-call engineer = you
    msg["Subject"] = "🚨 AI Triage Report: CI failure detected"
    msg.set_content(REPORT_PATH.read_text())

    with smtplib.SMTP_SSL(SMTP_SERVER, SMTP_PORT) as smtp:
        smtp.login(sender, password)
        smtp.send_message(msg)

    print("📧 Triage report emailed successfully.")


if __name__ == "__main__":
    main()