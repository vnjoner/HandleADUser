import csv
import datetime
import splunk.Intersplunk


SPLUNK_HOME="/opt/splunk"
APP = SPLUNK_HOME + "/etc/apps/adaction"


def write_csv (file,fields):
        with open(file, "a") as csv_file:
                writer = csv.writer(csv_file)
                writer.writerow(fields)


def read_csv (file):
        with open(file, "r") as csv_file:
                reader = csv.reader(csv_file)
                data = list()
                for line in reader:
                        data.append(line)
                return data


if __name__ == '__main__':
        keyword, argvals = splunk.Intersplunk.getKeywordsAndOptions()

	host = argvals.get("host", None)
        user_dn = argvals.get("user_dn", None)
        minutes = argvals.get("minutes", None)

        current_time = datetime.datetime.now()

        fields = [current_time, minutes, host, user_dn]
        file = APP + "/lookups/ad_whitelist.csv"

        write_csv(file, fields)
