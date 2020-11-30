from ad_lib.ad_action_const import *
from ad_lib.handle_ad_user import AlertToMsteam
from ad_lib.handle_syn_csv import *
import csv
import datetime

class whitelist:
	
	def __init__(self, file_whitelist):
		self.file_whitelist = file_whitelist
		self.list_user_dn = list()

	def append_user_dn (self, host, user_dn, minutes, webhook):
		obj = {"user_dn": user_dn, "minutes": minutes, "host": host, "webhook": webhook}
		self.list_user_dn.append(obj)

	def add(self):
		for obj in self.list_user_dn:
			now = datetime.datetime.now()
			fields = [now, obj["minutes"], obj["host"], obj["user_dn"]]
			write_syn_csv(self.file_whitelist, fields)

			title = WHITELIST_TITLE.format(obj["host"])
			msg = WHITELIST_MSG.format(obj["user_dn"], obj["minutes"])
			msteam = AlertToMsteam(obj["webhook"], title, msg)
			status = msteam.send_alert()
			print(status)

