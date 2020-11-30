import argparse

from ad_lib.handle_ad_user import HandleActiveDirectoryUser
from ad_lib.handle_csv import read_csv
from ad_lib.ad_action_const import *
from ad_lib.send_mail import get_random_password, sendemail


if __name__ == '__main__':
        parser = argparse.ArgumentParser()
        parser.add_argument('-n', '--name', required=True)
        parser.add_argument('-dn', '--user_dn', required=True)
        parser.add_argument('-m', '--mail', required=True)
        parser.add_argument('-w', '--webhook')
        parser.add_argument('-is', '--issue')
        args = parser.parse_args()

        host = args.name
        user_dn = args.user_dn
        mail_receiver = args.mail
        issue = args.issue
        webhook = args.webhook

        server = None
        username = None
        password = None

        list_creds = read_csv(FILE_CREDS)
        for cred in list_creds:
                if cred[0] == host:
                        server = cred[1]
                        username = cred[2]
                        password = cred[3]
                        break

        handle_user = HandleActiveDirectoryUser(host, server, webhook)
        handle_user.ad_connect(username, password)
        new_pwd = get_random_password(15)
        status = handle_user.ad_forcechange_pwd_user(user_dn, new_pwd, issue)

        email = dict()
        email["mail_receiver"] = mail_receiver
        email["mail_sender"] = EMAIL_USERNAME
        email["pass_sender"] = EMAIL_PASSWORD
        email["subject"] = EMAIL_SUBJECT
        email["message"] = EMAIL_MSG.format(new_pwd)
        sendemail(email)
        print (status)

