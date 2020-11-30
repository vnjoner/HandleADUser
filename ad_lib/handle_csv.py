import csv


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


def delete_row_csv (file, condition):
        lines = read_csv (file)
        for line in lines:
                if line[2] == condition:
                        lines.remove(line)
        with open(file, "w") as override_file:
                writer = csv.writer(override_file)
                writer.writerows (lines) 
		
