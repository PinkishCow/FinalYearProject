import cv2
import numpy
import csv
import os
import sys
import asyncio
import tools.config as config
from timeit import default_timer as timer


def server_cascade_setup():
    recog = CascadeRecognition(config.cfg['pi']['cascade']['scale'],
                               config.cfg['pi']['cascade']['neighbours'])
    recog.add_classifier(config.cfg['pi']['cascade']['cascades']['can'], "can")
    recog.add_classifier(config.cfg['pi']['cascade']['cascades']['cereal'], "cereal")
    recog.add_classifier(config.cfg['pi']['cascade']['cascades']['butter'], "butter")
    recog.add_classifier(config.cfg['pi']['cascade']['cascades']['crisp1'], "crisp1")
    recog.add_classifier(config.cfg['pi']['cascade']['cascades']['crisp2'], "crisp2")
    recog.add_classifier(config.cfg['pi']['cascade']['cascades']['milk'], "milk")
    recog.add_classifier(config.cfg['pi']['cascade']['cascades']['spray'], "spray")
    return recog


def clean_results(matches):
    # https://puu.sh/F8xbG/6e6441ce24.png Layout of the value matches
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


async def accuracy_test():
    classifier_file = "D:\\Desktop\\Dissertation\\images\\cas\\can_cas\\cascade404020s.xml"
    image_csv = "D:\\Desktop\\Dissertation\\images\\test_images_coco_spray_can\\vott-csv-export\\TestSet-export.csv"
    image_folder = "D:\\Desktop\\Dissertation\\images\\test_images_coco_spray_can\\vott-csv-export"
    output_file = "D:\\Desktop\\Dissertation\\images\\cascade404020stats.csv"

    recogniser_scale_values = [1.5, 1.4, 1.3, 1.25, 1.2, 1.15, 1.1, 1.05, 1.04, 1.03, 1.02, 1.01]
    recogniser_neighbour_values = [1, 3, 5, 7, 10, 15, 20, 30]

    test_results = []
    for scale in recogniser_scale_values:
        for nbr in recogniser_neighbour_values:
            start = timer()
            print(str(scale) + ": " + str(nbr))

            recog = CascadeRecognition(scale, nbr)
            recog.toggle_clean(False)

            recog.add_classifier(classifier_file, "Can")
            false_positive = 0
            false_negative = 0
            true_positive = 0
            image_count = 0
            with open(image_csv, newline='') as file_in:
                reader = csv.reader(file_in, quoting=csv.QUOTE_NONNUMERIC)
                next(reader)
                for row in reader:
                    if row[5] != "Can":
                        continue
                    print(row[0])
                    image_count += 1
                    image_path = os.path.join(image_folder, row[0])
                    image = cv2.imread(image_path)
                    matches = recog.recognise(image)
                    item_found = False
                    for match in matches:
                        boxes = match[1]
                        # Improve false negative logic to allow for images with no item to be mixed in
                        for (x, y, w, h) in boxes[0]:

                            if abs(x - [row[1]]) <= 100 and abs(y - row[2]) <= 100 and abs(
                                    w - (row[3] - row[1])) <= 100 and \
                                    abs(h - (row[4] - row[2])) <= 100:
                                if item_found:
                                    continue
                                true_positive += 1
                                item_found = True
                            else:
                                false_positive += 1
                    if not item_found:
                        false_negative += 1
            end = timer()
            test_results.append([false_positive, false_negative, true_positive, image_count, scale, nbr, (end - start)])
    with open(output_file, 'x', newline='') as file_out:
        writer = csv.writer(file_out, quoting=csv.QUOTE_NONNUMERIC)
        writer.writerow(["False positive", "False negative", "True positive", "Image count", "Cascade scaling",
                         "Cascade neighbours", "Time taken"])
        for item in test_results:
            writer.writerow(item)


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


def invalid():
    print("Not a valid choice")


def test_menu():
    # Add other tests
    choices = {"1": ('Can test', can_test),
               "Z": ('Exit', exit)}

    for key in sorted(choices.keys()):
        print(key + ":" + choices[key][0])
    print("Please select a task")
    choices.get(input(), [None, invalid])[1]()


asyncio.run(can_test())
