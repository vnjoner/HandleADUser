import argparse
from ad_lib.handle_ad_user import HandleActiveDirectoryUser
from ad_lib.handle_csv import read_csv
from ad_lib.ad_action_const import *


if __name__ == '__main__':
        parser = argparse.ArgumentParser()
        parser.add_argument('-n', '--name', required=True)
        parser.add_argument('-dn', '--user_dn', required=True)
        parser.add_argument('-w', '--webhook')
        parser.add_argument('-is', '--issue')
        args = parser.parse_args()

        host = args.name
        user_dn = args.user_dn
        webhook = args.webhook
        issue = args.issue

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
        ok = handle_user.ad_connect(username, password)
        status = handle_user.ad_disable_user(user_dn, issue)
        print (status)

