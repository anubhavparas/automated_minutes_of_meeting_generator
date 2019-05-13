import smtplib

subject = 'Innovation Mail Test'
msg = 'Hello!'

server = smtplib.SMTP_SSL('email-smtp.us-east-1.amazonaws.com', 465, timeout=120)