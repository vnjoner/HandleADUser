import csv
import time
import portalocker


def write_syn_csv (file,fields):
    while (True):
        try:
            with open(file, "a") as csv_file:
                portalocker.lock(csv_file, portalocker.LOCK_EX | portalocker.LOCK_NB)

                writer = csv.writer(csv_file)
                writer.writerow(fields)

                portalocker.unlock(csv_file)
            break
        except portalocker.LockException:
            time.sleep(0.5)


def read_syn_csv (file):
    while (True):
        try:
            with open(file, "r") as csv_file:
                portalocker.lock(csv_file, portalocker.LOCK_EX | portalocker.LOCK_NB)

                reader = csv.reader(csv_file)
                portalocker.unlock(csv_file)

                data = list()
                for line in reader:
                    data.append(line)
            return data
        except portalocker.LockException:
            time.sleep(0.5)


def write_syn_full_csv (file, data):
    while (True):
        try:
            with open(file, "w") as csv_file:
                portalocker.lock(csv_file, portalocker.LOCK_EX | portalocker.LOCK_NB)

                writer = csv.writer(csv_file)
                writer.writerows(data)

                portalocker.unlock(csv_file)
            break
        except portalocker.LockException:
            time.sleep(0.5)

def delete_syn_row_csv (file, condition):
	lines = read_syn_csv(file)
	for line in lines:
		if line[2] == condition:
			lines.remove(line)
	write_syn_full_csv(file, lines)


