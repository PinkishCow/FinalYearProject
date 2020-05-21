import asyncio
import random
import time

import cv2
import numpy
import csv
import os


# import pyodbc

def clean_results(matches):
    # Visual layout of the value matches is in the report appendix
    # Each "match" is a list of the item type and its recognition data
    # Its data is made up of; "0" The bounding boxes and "2" the certainty for each box
    # Possibly way way overdone, but it works, finally
    for counter, match in enumerate(matches):  # Enumerate returns the counter thank god
        data = match[1]
        boxes = data[0]
        if len(boxes) <= 1:
            return matches
        for i in range(len(boxes)):
            for j in range(len(boxes)):
                if i == j:
                    continue
                # Xi right of Xj, Yi under Yj
                # width not outside
                # height not outside
                if (boxes[i][0] >= boxes[j][0] and boxes[i][1] >= boxes[j][1]
                        and boxes[i][0] + boxes[i][2] <= boxes[j][0] + boxes[j][2]
                        and boxes[i][1] + boxes[i][3] <= boxes[j][1] + boxes[j][3]):
                    if data[2][i] > data[2][j]:
                        matches[counter][1][2][j] = matches[counter][1][2][i]
                    matches[counter][1][2][i] = 0  # Remove smaller rectangle value from confidence values
                    matches[counter][1][0][i] = 0  # Remove smaller rectangle from list of bounding boxes
        for xcount, x in enumerate(match[1]):
            if 0 in x:
                for zcount, z in enumerate(x):
                    if z.all() == 0:
                        matches[counter][1][xcount] = numpy.delete(matches[counter][1][xcount], zcount, 0)
    return matches


class CascadeRecognition:
    # Add max recognitions
    def __init__(self, scale, neighbours):
        self.classifiers = []
        self.scale = scale
        self.neighbours = neighbours
        self.latest_image = None
        self.clean = True

    @staticmethod
    def id(self):
        return 1

    def toggle_clean(self, x: bool):
        self.clean = x

    def recognise(self, image):
        self.latest_image = image
        matches = []
        for classifier in self.classifiers:
            matches.append([classifier[0],
                            list((classifier[1].detectMultiScale3(image, self.scale, self.neighbours,
                                                                  outputRejectLevels=True)))])
        if self.clean:
            return clean_results(matches)
        return matches

    def add_classifier(self, classifier, name):
        self.classifiers.append((name, cv2.CascadeClassifier(classifier)))

    def load_test(self):
        for classifier in self.classifiers:
            print(classifier[0])
            print(classifier[1].empty())

    def present_image(self, matches):
        for match in matches:
            name = match[0]
            box = match[1]
            for (count, rect) in enumerate(box[0]):
                x = rect[0]
                y = rect[1]
                w = rect[2]
                h = rect[3]
                cv2.rectangle(self.latest_image, (x, y), (x + w, y + h), (255, 255, 0), 2)
                cv2.putText(self.latest_image, name + ": " + str(box[2][count]), (x, y - 10), cv2.FONT_HERSHEY_SIMPLEX,
                            0.9, (255, 255, 0), 2)


# async def accuracy_test():
#     classifier_folder = "D:\\Desktop\\Dissertation\\images\\cas"
#     image_csv = "D:\\Desktop\\Dissertation\\images\\testingImages\\vott-csv-export\\TestingImages-export.csv"
#     image_folder = "D:\\Desktop\\Dissertation\\images\\testingImages\\vott-csv-export"
#     output_folder = "D:\\Desktop\\Dissertation\\images\\FinalResultsOutput"
#
#     recogniser_scale_values = [1.5, 1.4, 1.3, 1.25, 1.2, 1.15, 1.1, 1.05, 1.04, 1.03, 1.02, 1.01]
#     recogniser_neighbour_values = [1, 3, 5, 7, 10, 15, 20, 25, 30]
#
#     image_data_in = []
#
#     with open(image_csv, newline='') as csv_in:
#         reader = csv.reader(csv_in, quoting=csv.QUOTE_NONNUMERIC)
#         next(reader)
#         image_data_in = list(reader)
#
#     # True pos, True Neg, False Pos, False Neg, mAP, IoU>50, IoU>75
#     conn = pyodbc.connect(
#         r'Driver={Microsoft Access Driver (*.mdb, *.accdb)};DBQ=D:\Desktop\Dissertation\images\FinalResultsCas.accdb;')
#     cursor = conn.cursor()
#     print("connected")
#     for size_name in os.listdir(classifier_folder):
#         for item_name in os.listdir(os.path.join(classifier_folder, size_name)):
#             for scale in recogniser_scale_values:
#                 for nbr in recogniser_neighbour_values:
#                     recog = CascadeRecognition(scale, nbr)
#                     recog.toggle_clean(False)
#                     recog.add_classifier(os.path.join(classifier_folder, size_name, item_name, "cascade.xml"),
#                                          item_name)
#                     for image_file in os.listdir(image_folder):
#                         if not image_file.endswith(".jpg"):
#                             continue
#                         print(image_file + ", " + size_name + ", " + item_name + ", " + str(scale) + ", " + str(nbr))
#                         # Cannot have "True Negative" because every test image contains something that should be recognised
#                         true_pos = 0  # At least 1 bounding box with Iou >= 50
#                         false_pos = 0  # Bounding box with IoU < 50
#                         false_neg = 0  # No bounding box with IoU >= 50
#                         iou50 = 0
#                         iou75 = 0
#
#                         contains_item = False
#                         item_found = False
#
#                         image_items = {item_name, image_file}
#                         # https://stackoverflow.com/questions/1658505/searching-within-nested-list-in-python
#                         image_gt = None
#                         try:
#                             if next(subl for subl in image_data_in if image_items.issubset(subl)):
#                                 image_gt = next(subl for subl in image_data_in if image_items.issubset(subl))
#                                 contains_item = True
#                         except StopIteration:
#                             pass
#                         image = cv2.imread(os.path.join(image_folder, image_file))
#                         matches = recog.recognise(image)
#                         if contains_item:
#                             # https://www.pyimagesearch.com/2016/11/07/intersection-over-union-iou-for-object-detection/
#                             for match in matches:
#                                 # 1 = xmin, 2 = ymin, 3 = xmax, 4 = ymax
#                                 for (x, y, w, h) in match[1][0]:
#                                     # Intersection
#                                     xA = max(x, image_gt[1])
#                                     yA = max(y, image_gt[2])
#                                     xB = min(x + w, image_gt[3])
#                                     yB = min(y + h, image_gt[4])
#
#                                     intersection_area = max(0, xB - xA + 1) * max(0, yB - yA + 1)
#
#                                     # Union
#                                     resultArea = ((x + w) - x + 1) * ((y + h) - y + 1)
#                                     truthArea = (image_gt[3] - image_gt[1] + 1) * (image_gt[4] - image_gt[2] + 1)
#
#                                     # IoU
#                                     iou = intersection_area / float(resultArea + truthArea - intersection_area)
#
#                                     if iou >= 0.5:
#                                         iou50 += 1
#                                         if iou >= 0.75:
#                                             iou75 += 1
#                                         if not item_found:
#                                             true_pos += 1
#                                             item_found = True
#                                     else:
#                                         false_pos += 1
#                             if not item_found:
#                                 false_neg += 1
#                         else:
#                             for match in matches:
#                                 false_pos += 1
#
#                         cursor.execute('''
#                         INSERT INTO Results ( Filename, True_Positive, False_Positive, False_Negative, IoU50, IoU75, Cascade_Size, Cascade_Item, Cascade_Scale, Cascade_Neighbours )
#                         VALUES(?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
#                         ''', (
#                             image_file, true_pos, false_pos, false_neg, iou50, iou75, size_name, item_name, scale, nbr))
#                         conn.commit()


async def can_test():
    # classifier_file = input("Please enter classifier path")
    # image_csv = input("Please enter image csv path")
    # image_folder = input("Please enter image folder")
    classifier_file = "D:\\Desktop\\Dissertation\\images\\cas\\can_cas\\cascade404020s.xml"
    image_csv = "D:\\Desktop\\Dissertation\\images\\test_images_coco_spray_can\\vott-csv-export\\TestSet-export.csv"
    image_folder = "D:\\Desktop\\Dissertation\\images\\test_images_coco_spray_can\\vott-csv-export"
    recog = CascadeRecognition(1.05, 10)

    recog.add_classifier(classifier_file, "Can")
    with open(image_csv, newline='') as file_in:
        reader = csv.reader(file_in, quoting=csv.QUOTE_NONNUMERIC)
        next(reader)
        for row in reader:
            if row[5] != "Can":
                continue
            image_path = os.path.join(image_folder, row[0])
            image = cv2.imread(image_path)
            matches = recog.recognise(image)
            recog.present_image(matches)
            cv2.imshow("img", image)
            k = cv2.waitKey(0) & 0xff
            if k == 27:
                cv2.destroyAllWindows()
                break
            elif k == 78:
                continue


def cascade_speed_test():
    classifier_folder = "./cas"
    image_csv = "./boxes.csv"
    image_folder = "./images/testingImages"
    output_file = "./newSpeedResults.csv"

    recogniser_scale_values = [1.5, 1.4, 1.3, 1.25, 1.2, 1.15, 1.1, 1.05, 1.04, 1.03, 1.02, 1.01]
    recogniser_neighbour_values = [1, 3, 5, 7, 10, 15, 20, 25, 30]

    image_data_in = []

    test_image_count = 10

    results = []

    with open(image_csv, newline='') as csv_in:
        reader = csv.reader(csv_in, quoting=csv.QUOTE_NONNUMERIC)
        next(reader)
        image_data_in = list(reader)

    for size_name in os.listdir(classifier_folder):
        for item_name in os.listdir(os.path.join(classifier_folder, size_name)):
            for scale in recogniser_scale_values:
                for nbr in recogniser_neighbour_values:
                    recog = CascadeRecognition(scale, nbr)
                    recog.add_classifier(os.path.join(classifier_folder, size_name, item_name, "cascade.xml"),
                                         item_name)
                    val = 0
                    while val < test_image_count:
                        image_file = random.choice(os.listdir(image_folder))
                        start_time = time.time()
                        if not image_file.endswith(".jpg"):
                            continue
                        val += 1
                        print(str(val) + ", " + size_name + ", " + item_name + ", " + str(scale) + ", " + str(nbr))
                        # Cannot have "True Negative" because every test image contains something that should be recognised
                        true_pos = 0  # At least 1 bounding box with Iou >= 50
                        false_pos = 0  # Bounding box with IoU < 50
                        false_neg = 0  # No bounding box with IoU >= 50
                        iou50 = 0
                        iou75 = 0

                        contains_item = False
                        item_found = False

                        image_items = {item_name, image_file}
                        # https://stackoverflow.com/questions/1658505/searching-within-nested-list-in-python
                        image_gt = None
                        try:
                            if next(subl for subl in image_data_in if image_items.issubset(subl)):
                                image_gt = next(subl for subl in image_data_in if image_items.issubset(subl))
                                contains_item = True
                        except StopIteration:
                            pass
                        image = cv2.imread(os.path.join(image_folder, image_file))
                        matches = recog.recognise(image)
                        if contains_item:
                            # https://www.pyimagesearch.com/2016/11/07/intersection-over-union-iou-for-object-detection/
                            for match in matches:
                                # 1 = xmin, 2 = ymin, 3 = xmax, 4 = ymax
                                for (x, y, w, h) in match[1][0]:
                                    # Intersection
                                    xA = max(x, image_gt[1])
                                    yA = max(y, image_gt[2])
                                    xB = min(x + w, image_gt[3])
                                    yB = min(y + h, image_gt[4])

                                    intersection_area = max(0, xB - xA + 1) * max(0, yB - yA + 1)

                                    # Union
                                    resultArea = ((x + w) - x + 1) * ((y + h) - y + 1)
                                    truthArea = (image_gt[3] - image_gt[1] + 1) * (image_gt[4] - image_gt[2] + 1)

                                    # IoU
                                    iou = intersection_area / float(resultArea + truthArea - intersection_area)

                                    if iou >= 0.5:
                                        iou50 += 1
                                        if iou >= 0.75:
                                            iou75 += 1
                                        if not item_found:
                                            true_pos += 1
                                            item_found = True
                                    else:
                                        false_pos += 1
                            if not item_found:
                                false_neg += 1
                        else:
                            for match in matches:
                                false_pos += 1
                        taken_time = time.time() - start_time
                        results.append([item_name, size_name, scale, nbr, taken_time])

    with open(output_file, 'a', newline='') as file_out:
        writer = csv.writer(file_out, quoting=csv.QUOTE_NONNUMERIC)
        for item in results:
            writer.writerow(item)


def invalid():
    print("Not a valid choice")

# Change as needed

# asyncio.run(accuracy_test())
