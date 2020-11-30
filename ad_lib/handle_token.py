from ad_lib.ad_action_const import *
from ad_lib.handle_syn_csv import read_syn_csv, write_syn_csv, write_syn_full_csv
import datetime


class HandleToken:

	def __init__(self, file_token, payload, token):
		self.file_token = file_token
		self.payload = payload
		self.token = token

	def check_expire_token (self, time_expire):
		now = datetime.datetime.now()
		expire = datetime.timedelta(minutes=time_expire)
		time_create_token = datetime.datetime.strptime(self.payload["time"], "%Y-%m-%d %H:%M:%S.%f")
		if now - time_create_token > expire:
			return True
		return False

	def check_using_token (self):
		using_tokens = read_syn_csv(self.file_token)	
		for using_token in using_tokens:
			if str(using_token[0]) == str(self.payload["time"]) and str(using_token[1]) == str(self.payload["identify"]):
				return True
		fields = [self.payload["time"], self.payload["identify"]]
		write_syn_csv(self.file_token, fields)
		return False


class HandleExpireToken:

    def __init__(self, file_token):
        self.file_token = file_token
        self.current_time = datetime.datetime.now()

    def check_expire_token (self, time_create_token, time_expire):
        expire = datetime.timedelta(minutes=time_expire)
        time_create_token = datetime.datetime.strptime(time_create_token, "%Y-%m-%d %H:%M:%S.%f")
        if self.current_time - time_create_token > expire:
            return True
        return False

    def delete_expire_token (self):
        tokens = read_syn_csv(self.file_token) 
        file_del_expire_token = list()
        for token in tokens:
            if token == None:
                continue

            if token[0] == "time" or token[1] == "identify":
                file_del_expire_token.append(token)
                continue

            if self.check_expire_token(token[0], EXPIRE_TOKEN_TIME) == False:
                file_del_expire_token.append(token)

        write_syn_full_csv(self.file_token, file_del_expire_token)
