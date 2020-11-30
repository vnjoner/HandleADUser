import smtplib
import poplib
import getpass
import base64
import random
import string


def sendemail(mail):
    SMTP_SERVER = "smtp.gmail.com"
    SMTP_PORT = 465
    #Connect to server GOOGLE, 465 is port
    server = smtplib.SMTP_SSL(SMTP_SERVER,SMTP_PORT)
    #Login to server GOOGLE
    server.login(mail["mail_sender"], mail["pass_sender"])
    # Send mail
    try:
        # Join things into BODY
        BODY = '\r\n'.join(['To: %s' % mail["mail_receiver"],
                            'From: %s' % mail["mail_sender"],
                            'Subject: %s' % mail["subject"],
                            '', mail["message"]])
        # Send.....
        server.sendmail(
            mail["mail_sender"],
            mail["mail_receiver"],  # Mail Receive
            BODY  # Mail's Body
        )
    except:
        print("Something wrong!?")
    finally:
        return

def get_random_password(length):
    letters_and_digits = string.ascii_letters + string.digits + "!@#$%^&*()?"
    result_str = ''.join((random.choice(letters_and_digits) for i in range(length)))
    return result_str
