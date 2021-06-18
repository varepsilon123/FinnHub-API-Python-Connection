import email, smtplib, ssl

from email import encoders
from email.header import Header
from email.mime.base import MIMEBase
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

from shutil import copyfile
import os

def send(date, testing):
    subject = "Daily RS Rating Update"
    body = f"{date} Daily RS Rating Update on HK stocks, DOW, S&P500, NASDAQ stocks"
    sender_email = "mrakmrakmrakmrak1@gmail.com"
    if testing:
        receiver_email = ["mrakmrakmrakmrak1@gmail.com"]
    else:
        receiver_email = ["mrakmrakmrakmrak1@gmail.com", "philipforcsgo@gmail.com"]
    password = "@qw121212" # input("Type your password and press enter:")
    
    # Create a multipart message and set headers
    message = MIMEMultipart()
    message["From"] = str(Header('Mrak Minorvini <mrakmrakmrakmrak1@gmail.com>'))
    message["To"] = ", ".join(receiver_email)
    message["Subject"] = subject
    # message["Bcc"] = ", ".join(receiver_email)  # Recommended for mass emails
    
    # Add body to email
    message.attach(MIMEText(body, "plain"))
    
    filename = f"ScreenOutput_{date}.xlsx" # In same directory as script
    copyfile(f"output/{filename}", filename) # copy the output to same dir
    
    
    # Open PDF file in binary mode
    with open(filename, "rb") as attachment:
        # Add file as application/octet-stream
        # Email client can usually download this automatically as attachment
        part = MIMEBase("application", "octet-stream")
        part.set_payload(attachment.read())
    
    # Encode file in ASCII characters to send by email    
    encoders.encode_base64(part)
    
    # Add header as key/value pair to attachment part
    part.add_header(
        "Content-Disposition",
        f"attachment; filename= {filename}",
    )
    
    
    # Add attachment to message and convert message to string
    message.attach(part)
    text = message.as_string()
    
    # Log in to server using secure context and send email
    context = ssl.create_default_context()
    with smtplib.SMTP_SSL("smtp.gmail.com", 465, context=context) as server:
        server.login(sender_email, password)
        server.sendmail(sender_email, receiver_email, text)
        
    os.remove(filename)

if __name__ == '__main__':
    # send()
    pass