import os
import logging
import csv

# logger = logging.getLogger(__name__)
# logger.info("Loading")


def start():
    file = input("Please input path to csv")
    name = input("Please input name to save csv as")
    output_dir = os.path.basename(file)
    image_path = input("Please input path to image folders")
    lines = []
    if not (os.path.exists(file)):
        logging.error("File not found")
        return
    else:
        with open(file, newline='') as x:
            reader = csv.reader(x, quoting=csv.QUOTE_NONNUMERIC)
            next(reader)
            for row in reader:
                full_path = os.path.join(image_path, row[0])
                new_x = abs(row[1] - 1024)
                new_y = abs(row[2] - 768)
                height = row[3] - row[1]
                width = row[4] - row[2]
                lines.append((full_path, new_x, new_y, height, width, row[5]))
        with open(os.path.join(os.path.dirname(file), name), 'w', newline='') as z:
            writer = csv.writer(z, quoting=csv.QUOTE_NONNUMERIC)
            for item in lines:
                writer.writerow(item)
    exit()


start()
