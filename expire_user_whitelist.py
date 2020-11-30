import csv
import datetime


SPLUNK_HOME="/home/splunk"
APP = SPLUNK_HOME + "/etc/apps/splunk_app_for_cp"

def read_csv (file):
        with open(file, "r") as csv_file:
                reader = csv.reader(csv_file)
                data = list()
                for line in reader:
                        data.append(line)
                return data


def expire_whitelist (file):
        whitelist = read_csv(file)
        curr_time = datetime.datetime.now()

        for user in whitelist:

                if user == None:
                        continue

                if user[0] == "start_time":
                        continue

                if user[1] == '0':
                        continue

                whitelist_time = datetime.datetime.strptime(user[0], '%Y-%m-%d %H:%M:%S.%f')
                expire = datetime.timedelta(minutes=int(user[1]))
                if curr_time - whitelist_time > expire:
                        whitelist.remove(user)

        with open(file, "w") as override_file:
                writer = csv.writer(override_file)
                writer.writerows(whitelist)


if __name__ == '__main__':
        file = APP + "/lookups/ad_whitelist.csv"
        expire_whitelist (file)

