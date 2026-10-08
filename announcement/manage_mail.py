import smtplib
from email.mime.text import MIMEText

EMAIL = "hashupal25@gmail.com"
APP_PASSWORD = "lricrhsxjtjljirt"  # paste locally, never commit this

msg = MIMEText("This is a test from raw smtplib.")
msg["Subject"] = "SMTP test"
msg["From"] = EMAIL
msg["To"] = EMAIL  # send to yourself first

with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
    server.login(EMAIL, APP_PASSWORD)
    server.sendmail(EMAIL, [EMAIL], msg.as_string())

print("Sent successfully")