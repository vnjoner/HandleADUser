#!/home/splunk/etc/apps/splunk_app_for_cp/bin/dhcpsapi/bin/python

import os
os.chdir("/home/splunk/etc/apps/splunk_app_for_cp/bin")

import random
import string
import base64
import hashlib
from Crypto import Random
from Crypto.Cipher import AES, PKCS1_OAEP
from Crypto.PublicKey import RSA
import json
import cherrypy
import subprocess
import csv
import os
import urllib.parse
import pymsteams

SPLUNK_HOME = "/home/splunk"
APP = SPLUNK_HOME + "/etc/apps/splunk_app_for_cp"
ACTIVATE = APP + "/bin/ad_api/bin/activate_this.py"

class AESCipher(object):
    def __init__(self, key):
        self.bs = 32
        self.key = hashlib.sha256(key.encode()).digest()

    def encrypt(self, raw):
        raw = self._pad(raw)
        iv = Random.new().read(AES.block_size)
        cipher = AES.new(self.key, AES.MODE_CBC, iv)
        return base64.b64encode(iv + cipher.encrypt(raw.encode()))

    def decrypt(self, enc):
        enc = base64.b64decode(enc)
        iv = enc[:AES.block_size]
        cipher = AES.new(self.key, AES.MODE_CBC, iv)
        return self._unpad(cipher.decrypt(enc[AES.block_size:])).decode('utf-8')

    def _pad(self, s):
        return s + (self.bs - len(s) % self.bs) * chr(self.bs - len(s) % self.bs)

    @staticmethod
    def _unpad(s):
        return s[:-ord(s[len(s)-1:])]


class RSACipher(object):
    def __init__(self, pub_key_file, pri_key_file):
        self.pub_key = RSA.import_key(open(pub_key_file).read())
        self.pri_key = RSA.import_key(open(pri_key_file).read())

    def encrypt_data(self, data):
        cipher_rsa = PKCS1_OAEP.new(self.pub_key)
        encode_data = cipher_rsa.encrypt(data)
        return base64.b64encode(encode_data)

    def decrypt_data(self, encode_data):
        enc = base64.b64decode(encode_data)
        cipher_rsa = PKCS1_OAEP.new(self.pri_key)
        data = cipher_rsa.decrypt(enc).decode("utf-8")
        return data

def get_csv_header(path):
        with open(path, "r") as f:
            return next(csv.reader(f))

def remove_token(path_file_token, token):
    with open(path_file_token) as file_save:
        reader = csv.DictReader(file_save)
        with open("temp_token.csv", 'w', newline='') as temp_file:
            fieldnames = get_csv_header(path_file_token)
            writer = csv.DictWriter(temp_file, fieldnames=fieldnames)
            writer.writeheader()
            for row in reader:
                if urllib.parse.quote(token) != row["token"]:
                    writer.writerow(row)
    os.remove(path_file_token)
    os.rename("temp_token.csv", path_file_token)

def check_token(path_file_token, token):
    with open(path_file_token) as file_save:
        reader = csv.DictReader(file_save)  
        for row in reader:
            if urllib.parse.quote(token) == row["token"]:
                return True
    return False

def msteam_send(webhook, title, message):
    msteams = pymsteams.connectorcard(webhook)
    msteams.title(title)
    msteams.text(message)
    msteams.send()
    return msteams.last_http_status.status_code

class WebService(object):
    @cherrypy.expose
    def dhcp_remove_deny(self, host, MAC, token):
        rsa = RSACipher("receiver.pem", "private.pem")
        aes = AESCipher(open("aes.key").read())
        rsa_de = rsa.decrypt_data(token)
        aes_de = aes.decrypt(rsa_de)
        payload = json.loads(aes_de)
        print(payload["host"] + ":" +
              payload["MAC"] + ":" + payload["webhook"])
        if check_token("../lookups/dhcp_tokens.csv", token) == False:
            msteam_send(payload["webhook"], "You have already pressed this button.", 'A "Remove Deny" button can only be pressed once. You have already pressed this button.')
            return """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Document</title>
</head>
<body>
    <script>
        window.addEventListener('load', function () {
            window.open('', '_parent', '');
            window.close();
        })
    </script>
</body>
</html>"""
        if host == payload["host"] and MAC == payload["MAC"]:
            command = "/home/splunk/etc/apps/splunk_app_for_cp/bin/dhcpsapi/bin/python dhcp_allow.py -host {} -mac {} -wh {}".format(
                payload["host"], payload["MAC"], payload["webhook"])
            process = subprocess.Popen(command.split(), stdout=subprocess.PIPE)
            output, error = process.communicate()
            remove_token("../lookups/dhcp_tokens.csv", token)
        return """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Document</title>
</head>
<body>
    <script>
        window.addEventListener('load', function () {
            window.open('', '_parent', '');
            window.close();
        })
    </script>
</body>
</html>"""

    @cherrypy.expose
    def ad_enable_user(self, host, user_dn, webhook, token):
        rsa = RSACipher("receiver.pem", "private.pem")
        aes = AESCipher(open("aes.key").read())

        rsa_de = rsa.decrypt_data(token)
        aes_de = aes.decrypt(rsa_de)
        payload = json.loads(aes_de)

        with open(ACTIVATE) as f:
            code = compile(f.read(), ACTIVATE, 'exec')
            exec(code, dict(__file__=ACTIVATE))
        from ad_lib.handle_ad_user import HandleActiveDirectoryUser
        from ad_lib.ad_action_const import FILE_CREDS, EXPIRE_TOKEN_TIME, FILE_TOKEN, FILE_WHITELIST
        from ad_lib.handle_csv import read_csv
        from ad_lib.handle_token import HandleToken

        handle_token = HandleToken(FILE_TOKEN, payload, token)


        if payload["host"] == host and payload["user_dn"] \
            and payload["webhook"] == webhook \
            and handle_token.check_expire_token(EXPIRE_TOKEN_TIME) == False:
            if handle_token.check_using_token() == False:

                list_creds = read_csv(FILE_CREDS)
                for cred in list_creds:
                    if cred[0] == host:
                        ad_ip = cred[1]
                        username = cred[2]
                        password = cred[3]

                handle_user = HandleActiveDirectoryUser(host, ad_ip, webhook)
                handle_user.ad_connect(username, password)
                handle_user.ad_enable_user(user_dn)

        return """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Document</title>
</head>
<body>
    <script>
        window.addEventListener('load', function () {
            window.open('', '_parent', '');
            window.close();
        })
    </script>
</body>
</html>"""

    @cherrypy.expose
    def ad_whitelist(self, host, user_dn, minutes, webhook, token):
        rsa = RSACipher("receiver.pem", "private.pem")
        aes = AESCipher(open("aes.key").read())

        rsa_de = rsa.decrypt_data(token)
        aes_de = aes.decrypt(rsa_de)
        payload = json.loads(aes_de)

        with open(ACTIVATE) as f:
            code = compile(f.read(), ACTIVATE, 'exec')
            exec(code, dict(__file__=ACTIVATE))
        from ad_lib.handle_ad_user import HandleActiveDirectoryUser
        from ad_lib.ad_action_const import FILE_WHITELIST, EXPIRE_TOKEN_TIME, FILE_TOKEN, FILE_CREDS
        from ad_lib.handle_whitelist import whitelist
        from ad_lib.handle_token import HandleToken
        from ad_lib.handle_csv import read_csv


        handle_token = HandleToken(FILE_TOKEN, payload, token)

        if payload["host"] == host and payload["user_dn"] \
            and payload["webhook"] == webhook and payload["minutes"] == int(minutes) \
            and handle_token.check_expire_token(EXPIRE_TOKEN_TIME) == False:
            if handle_token.check_using_token() == False:
                list_creds = read_csv(FILE_CREDS)
                for cred in list_creds:
                    if cred[0] == host:
                        ad_ip = cred[1]
                        username = cred[2]
                        password = cred[3]

                handle_user = HandleActiveDirectoryUser(host, ad_ip, webhook)
                handle_user.ad_connect(username, password)
                handle_user.ad_enable_user(user_dn)

                whitelist = whitelist(FILE_WHITELIST)
                whitelist.append_user_dn(host, user_dn, minutes, webhook)
                whitelist.add()

        return """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Document</title>
</head>
<body>
    <script>
        window.addEventListener('load', function () {
            window.open('', '_parent', '');
            window.close();
        })
    </script>
</body>
</html>"""

if __name__ == '__main__':
    cherrypy.config.update({'server.socket_host': '0.0.0.0'})
    cherrypy.server.ssl_module = 'builtin'
    cherrypy.server.ssl_certificate = "Spkunk_CP.pem"
    cherrypy.server.ssl_private_key = "Spkunk_CP.pem"
    cherrypy.quickstart(WebService())

