import argparse
import urllib
import ldap3
import datetime
import pymsteams
import json, datetime
from pypsrp.client import Client

import random

from ad_lib.ad_action_const import *
from ad_lib.handle_csv import *
from ad_lib.my_encrypt import *
from ad_lib.handle_syn_csv import *


class GenerateToken:

	def __init__(self):
		self.token = None

		self.identify = random.randint(1,99999999999999999)
		self.time = datetime.datetime.now().__str__()

	def whitelist_field(self, host, user_dn, minutes, webhook):
		fields = dict()

		fields["host"] = host
		fields["user_dn"] = user_dn
		fields["minutes"] = minutes
		fields["webhook"] = webhook
		fields["identify"] = self.identify
		fields["time"] = self.time

		self.token = json.dumps(fields)
		
	def enable_field(self, host, user_dn, webhook):
		fields = dict()

		fields["host"] = host
		fields["user_dn"] = user_dn
		fields["webhook"] = webhook
		fields["identify"] = self.identify
		fields["time"] = self.time

		self.token = json.dumps(fields)

	def create_token(self):
		rsa = RSACipher(PUBLIC_KEY, PRIVATE_KEY)
		aes = AESCipher(open(AES_KEY).read())

		aes_en_token = aes.encrypt(self.token)
		rsa_en_token = rsa.encrypt_data(aes_en_token)

		token = rsa_en_token.decode("utf-8")
		token_url = urllib.parse.quote(token)

		return token_url


class GenerateURL:

	def __init__(self, ip_addr, port):
		self.ip_addr = ip_addr
		self.port = port

	def whitelist_url(self, action, host, user_dn, minutes, webhook):
		gen_token = GenerateToken()
		gen_token.whitelist_field(host, user_dn, minutes, webhook)
		token = gen_token.create_token()

		url = "https://{0}:{1}/{2}?host={3}&user_dn={4}&minutes={5}&webhook={6}&token={7}" \
				.format(self.ip_addr, self.port, action, host, user_dn, minutes, webhook, token)
		return url

	def enable_user_url(self, action, host, user_dn, webhook):
		gen_token = GenerateToken()
		gen_token.enable_field(host, user_dn, webhook)
		token = gen_token.create_token()

		url = "https://{0}:{1}/{2}?host={3}&user_dn={4}&webhook={5}&token={6}" \
				.format(self.ip_addr, self.port, action, host, user_dn, webhook, token)
		return url


class AlertToMsteam():

	def __init__(self, webhook, title, message):
		self.webhook = webhook
		self.title = title
		self.message = message
		self.potential_action = list()

	def append_btn (self, name_btn, btn_url):
		action = {"@type": "HttpPOST", "name": name_btn, "target": btn_url}
		self.potential_action.append(action)

	def send_alert(self):
		msteams = pymsteams.connectorcard(self.webhook)
		msteams.title(self.title)
		msteams.text(self.message)
		msteams.payload["potentialAction"] = self.potential_action
		msteams.send()
		return msteams.last_http_status.status_code


class HandleActiveDirectoryUser:

	def __init__(self, host_name, ad_ip, webhook):
		self.host_name = host_name
		self.ad_ip = ad_ip
		self.webhook = webhook

	def ad_connect(self, ad_user, ad_pass):
		server = ldap3.Server(self.ad_ip)
		self.conn = ldap3.Connection(server, read_only=False, user=ad_user, password=ad_pass, version=3, client_strategy="SYNC")
		status = self.conn.bind()
		return status

	def check_whitelist(self, path, user_dn):
		whitelist = read_csv(path)
		for line in whitelist:
				if line[3] == user_dn:
					return True
		return False

	def ad_disable_user(self, user_dn, reason="None"):
		user_dn = user_dn.replace("'", '')
		user_dn = user_dn.replace ('"', '')
		self.conn.search(search_base=user_dn, search_filter='(objectClass=*)', search_scope=ldap3.BASE, attributes=['cn', 'userAccountControl'])
		data = self.conn.response

		curr_acc_ctrl = data[0]['attributes']['userAccountControl']

		if curr_acc_ctrl == USER_DISABLE_STATE or self.check_whitelist(FILE_WHITELIST,user_dn) or self.check_whitelist(FILE_GROUP_WHITELIST, user_dn):
			self.conn.unbind()
		else:
			changes = {'userAccountControl': [(ldap3.MODIFY_REPLACE, USER_DISABLE_STATE)]}
			status = True#self.conn.modify(dn=user_dn, changes=changes)
			self.conn.unbind()

			if status != True:
				return False

			time = datetime.datetime.now()	
			fields = [time ,self.host_name , user_dn, self.webhook]
			write_syn_csv(FILE_BLOCK_USERS, fields)

			if self.webhook != None:
				title = DISABLE_USER_TITLE.format(self.host_name)
				msg = DISABLE_USER_MSG.format(user_dn, reason)

				gen_url = GenerateURL(IP_SERVICE, PORT_SERVICE)
				enable_btn = gen_url.enable_user_url("ad_enable_user", self.host_name, user_dn, self.webhook)
				whitelist_1h_btn = gen_url.whitelist_url("ad_whitelist", self.host_name, user_dn, 60, self.webhook)
				whitelist_2h_btn = gen_url.whitelist_url("ad_whitelist", self.host_name, user_dn, 2*60, self.webhook)
				whitelist_8h_btn = gen_url.whitelist_url("ad_whitelist", self.host_name, user_dn, 8*60, self.webhook)

				msteam = AlertToMsteam(self.webhook, title, msg)
				msteam.append_btn(name_btn="Enabled User", btn_url=enable_btn)
				msteam.append_btn(name_btn="Whitelist 1h", btn_url=whitelist_1h_btn)
				msteam.append_btn(name_btn="Whitelist 2h", btn_url=whitelist_2h_btn)
				msteam.append_btn(name_btn="whitelist 8h", btn_url=whitelist_8h_btn)

				msteam.send_alert()

		return True

	def ad_enable_user(self, user_dn):
		user_dn = user_dn.replace("'", '')
		user_dn = user_dn.replace ('"', '')
		self.conn.search(search_base=user_dn, search_filter='(objectClass=*)', search_scope=ldap3.BASE, attributes=['cn', 'userAccountControl'])
		data = self.conn.response

		curr_acc_ctrl = data[0]['attributes']['userAccountControl']

		if curr_acc_ctrl == USER_ENABLE_STATE:
			self.conn.unbind()
		else:
			changes = {'userAccountControl': [(ldap3.MODIFY_REPLACE, USER_ENABLE_STATE)]}
			status = self.conn.modify(dn=user_dn, changes=changes)
			self.conn.unbind()

			if status != True:
				return False

			delete_syn_row_csv(FILE_BLOCK_USERS, user_dn)

			if self.webhook != None:
				title = ENABLE_USER_TITLE.format(self.host_name)
				msg = ENABLE_USER_MSG.format(user_dn)
				msteam = AlertToMsteam(self.webhook, title, msg)
				msteam.send_alert()

		return True
	
	def ad_forcechange_pwd_user (self, user_dn, new_pwd, issue):
		user_dn = user_dn.replace("'", '')
		user_dn = user_dn.replace ('"', '')	
		with Client(self.host_name, username="cp\splunksrun", password="spk#0511", ssl=False) as client:
			shell = "dsmod user '{}' -pwd {}".format(user_dn, new_pwd)
			output, streams, had_errors = client.execute_ps(shell)
		if had_errors == True:
			return False

		force_change_pwd = {"pwdLastSet": (ldap3.MODIFY_REPLACE, [0])}
		status = self.conn.modify(dn=user_dn, changes=force_change_pwd)
		self.conn.unbind()

		if self.webhook != None:
			title = FORCECHANGE_PWD_TITLE.format(self.host_name)
			msg = FORCECHANGE_PWD_MSG.format(user_dn, issue)
			msteam = AlertToMsteam (self.webhook, title, msg)
			msteam.send_alert()
		return status
		
