import os
import logging
import csv

# logger = logging.getLogger(__name__)
# logger.info("Loading")


def start():
    file = input("Please input path to csv")
    name = input("Please input name to save csv as")
    output_dir = os.path.basename(file)
    lines = []
    if not (os.path.exists(file)):
        logging.error("File not found")
        return
    else:
        with open(file, newline='') as x:
            reader = csv.reader(x, quoting=csv.QUOTE_NONNUMERIC)
            next(reader)
            for row in reader:
                full_path = row[0]
                new_x = int(row[1])
                new_y = int(row[2])
                height = int(row[3] - row[1])
                width = int(row[4] - row[2])
                lines.append((full_path, 1, new_x, new_y, height, width, row[5]))#Remove row[5] for anything except the test set
        with open(os.path.join(os.path.dirname(file), name), 'w', newline='') as z:
            writer = csv.writer(z)#Space delim for all non mixed
            for item in lines:
                writer.writerow(item)
    exit()


start()
