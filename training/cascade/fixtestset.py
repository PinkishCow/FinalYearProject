import os
import csv


def start():
    file = input("Please input path to csv")
    name = input("Please input name to save csvs as")
    output_dir = os.path.basename(file)
    can_lines = []
    cereal_lines = []
    spray_lines = []
    if not (os.path.exists(file)):
        print("File not found")
        return
    else:
        with open(file, newline='') as x:
            reader = csv.reader(x)
            next(reader)
            for row in reader:
                full_path = row[0]
                new_x = int(row[2])
                new_y = int(row[3])
                height = int(row[4])
                width = int(row[5])
                if row[6] == "Can":
                    can_lines.append((full_path, 1, new_x, new_y, height, width))
                elif row[6] == "Cereal":
                    cereal_lines.append((full_path, 1, new_x, new_y, height, width))
                elif row[6] == "Deodorant":
                    spray_lines.append((full_path, 1, new_x, new_y, height, width))
        with open(os.path.join(os.path.dirname(file), name + "Can.txt"), 'w', newline='') as z:
            writer = csv.writer(z, delimiter=" ")
            for item in can_lines:
                writer.writerow(item)
        with open(os.path.join(os.path.dirname(file), name + "Cereal.txt"), 'w', newline='') as z:
            writer = csv.writer(z, delimiter=" ")
            for item in cereal_lines:
                writer.writerow(item)
        with open(os.path.join(os.path.dirname(file), name + "Spray.txt"), 'w', newline='') as z:
            writer = csv.writer(z, delimiter=" ")
            for item in spray_lines:
                writer.writerow(item)
    exit()
