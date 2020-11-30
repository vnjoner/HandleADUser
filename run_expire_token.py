import subprocess

SPLUNK_HOME = "/home/splunk"
APP = SPLUNK_HOME + "/etc/apps/splunk_app_for_cp/bin/ad_api"
ACTIVATE = APP + "/bin/activate_this.py"

with open(ACTIVATE) as f:
        code = compile(f.read(), ACTIVATE, 'exec') 
        exec (code, dict(__file__=ACTIVATE))

if __name__ == "__main__":
	subprocess.run(["python3", APP + "/expire_token.py"])
		

