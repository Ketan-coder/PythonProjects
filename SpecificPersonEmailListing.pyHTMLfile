import imaplib
import email
from email.header import decode_header
import webbrowser
import os
from tqdm import tqdm

# account credentials
username = "email"
password = "password"

# prompt user for sender email and fetch mode
sender_email = input("Enter the email of the sender: ")
fetch_mode = input("Fetch all emails or only new emails since last run? (all/new): ")

# create an IMAP4 class with SSL 
imap = imaplib.IMAP4_SSL("imap.gmail.com")

# authenticate
imap.login(username, password)

# select the mailbox you want to delete in
imap.select("Inbox")

# search for specific mails by sender
if fetch_mode == "new":
    status, messages = imap.search(None, 'FROM', f'"{sender_email}"', "UNSEEN")
else:
    status, messages = imap.search(None, 'FROM', f'"{sender_email}"')

# convert messages to a list of email IDs
messages = messages[0].split(b' ')

if len(messages) > 0:
    # create an html file to save the emails
    with open(f"emails_{sender_email}.html", "a",encoding="utf-8") as f:
        f.write("<html><head>")
        f.write("<style>")
        f.write("body { font-family: Arial, sans-serif; }")
        f.write("h1 { text-align: center; }")
        f.write(".email { border: 1px solid #ddd; margin: 10px; padding: 10px; }")
        f.write(".subject { font-size: 18px; font-weight: bold; }")
        f.write(".date { font-size: 14px; color: #999; margin-bottom: 10px; }")
        f.write("</style>")
        f.write("</head><body>")
        f.write(f"<h1>Emails from {sender_email}</h1>")

        # iterate over each email
        for i, mail in enumerate(tqdm(messages, desc="Saving emails", unit="email")):
            _, msg = imap.fetch(mail, "(RFC822)")

            # loop over the returned bytes to get the message
            for response in msg:
                if isinstance(response, tuple):
                    msg = email.message_from_bytes(response[1])

                    # decode the email subject
                    subject = decode_header(msg["Subject"])[0][0]
                    if isinstance(subject, bytes):
                        # if it's a bytes type, decode to str
                        subject = subject.decode()

                    # get the email date
                    date = msg["Date"]

                    # get the email sender
                    sender = msg.get("From")

                    # get the email body
                    body = ""
                    if msg.is_multipart():
                        for part in msg.walk():
                            content_type = part.get_content_type()
                            content_disposition = str(part.get("Content-Disposition"))
                            try:
                                # get the email body
                                body = part.get_payload(decode=True).decode()
                            except:
                                pass
                            if content_type == "text/plain" and "attachment" not in content_disposition:
                                # print text/plain emails and skip attachments
                                body += body + "\n"
                    else:
                        # extract content type of email
                        content_type = msg.get_content_type()
                        # get the email body
                        body = msg.get_payload(decode=True).decode()
                        if content_type == "text/plain":
                            # print only text email parts
                            body += body + "\n"

                    # save the email as an html file
                    f.write(f"<div class='email'>")
                    f.write(f"<div class='subject'>{i+1}. {subject}</div>")
                    f.write(f"<div class='date'>{date}</div>")
                    f.write(body)
                    f.write("</div>")

        f.write("</body></html>")

    # close the connection and logout
    imap.close()
    imap.logout()

    # open the file in the browser
    filename = os.path.abspath(f"emails_{sender_email}.html")
    webbrowser.open(f"file://{filename}")
else:
    print(f"No emails found from {sender_email}.")
