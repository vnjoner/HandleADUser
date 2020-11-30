import subprocess
import splunk.Intersplunk

SPLUNK_HOME = "/home/splunk"
APP = SPLUNK_HOME + "/etc/apps/splunk_app_for_cp/bin/ad_api"
ACTIVATE = APP + "/bin/activate_this.py"

with open(ACTIVATE) as f:
        code = compile(f.read(), ACTIVATE, 'exec') 
        exec (code, dict(__file__=ACTIVATE))

if __name__ == "__main__":
	keywords, argvals = splunk.Intersplunk.getKeywordsAndOptions()
	host = argvals.get("host", None)
	user_dn = argvals.get("user_dn", None)
	webhook = argvals.get("webhook", None)

	if webhook == None:
		subprocess.run(["python3", APP + "/enable_user.py", "--name", host, "--user_dn", user_dn])
	else:
		subprocess.run(["python3", APP + "/enable_user.py", "--name", host, "--user_dn", user_dn, "--webhook", webhook])
		

