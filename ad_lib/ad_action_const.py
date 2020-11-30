SPLUNK_HOME = "/home/splunk"
APP = SPLUNK_HOME + "/etc/apps/splunk_app_for_cp"


BIN = APP + "/bin"
PUBLIC_KEY = BIN + "/receiver.pem"
PRIVATE_KEY = BIN + "/private.pem"
AES_KEY = BIN + "/aes.key"
ACTIVATE = BIN + "/ad_api/bin/activate_this.py"


LOOKUPS = APP + "/lookups"
FILE_BLOCK_USERS = LOOKUPS + "/ad_block_users.csv"
FILE_WHITELIST = LOOKUPS +  "/ad_disable_whitelist.csv"
FILE_GROUP_WHITELIST = LOOKUPS + "/ad_whitelist.csv"
FILE_TOKEN = LOOKUPS + "/ad_token.csv"
FILE_CREDS = LOOKUPS + "/ad_server.csv"


WHITELIST_TITLE = "[{0}] User have been added to whitelist"
WHITELIST_MSG = "<b>User DN:</b> {0}<br/><b>Minutes:</b> {1}"
ENABLE_USER_TITLE = "[{0}] User have been enabled"
ENABLE_USER_MSG = "<b>User DN:</b> {0}"
DISABLE_USER_TITLE = "[{0}] User have been disabled"
DISABLE_USER_MSG = "<b>User DN:</b> {0}<br/><b>Reason:</b> {1}"
FORCECHANGE_PWD_TITLE = "[{0}] User have been force change password"
FORCECHANGE_PWD_MSG = "<b>User DN:</b> {0}<br/><b>Reason:</b> {1}"



USER_DISABLE_STATE = 514
USER_ENABLE_STATE = 512

EMAIL_USERNAME = "mnhat1119@gmail.com"
EMAIL_PASSWORD = "minhnhat1999"
EMAIL_SUBJECT = "[ADMIN] NEW PASSWORD"
EMAIL_MSG = "Hello, this email send from ADMIN.\nYour password is: {}"


IP_SERVICE = "cpv-splunk-sh.cp.com.vn"
PORT_SERVICE = "8080"
EXPIRE_TOKEN_TIME = 60*24*3
