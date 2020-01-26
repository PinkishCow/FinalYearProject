import cv2
import numpy
import csv
import os


class CascadeRecognition:

    def __init__(self, scale, neighbours):
        self.classifiers = []
        self.scale = scale
        self.neighbours = neighbours

    def recognise(self, image):
        matches = []
        for classifier in self.classifiers:
            matches.append(classifier.detectMultiScale(image, self.scale, self.neighbours))
        return matches

    def add_classifier(self, classifier):
        self.classifiers.append(classifier)


class CascadeTest:

    def can_test(self, classifier_file, image_csv, image_folder):
        recog = CascadeRecognition(1, 5)

        recog.add_classifier(classifier_file)
        with open(image_csv, newline='') as file_in:
            reader = csv.reader(file_in, quoting=csv.QUOTE_NONNUMERIC)
            next(reader)
            for row in reader:
                image_path = os.path.join(image_folder, row[0])
                image = cv2.imread(image_path)
                matches = recog.recognise(image)
                for (x, y, w, h) in matches:
                    cv2.rectangle(image, (x, y), (x+w, y+h), (255, 255, 0), 2)
                cv2.imshow("img", image)
                k = cv2.waitKey(0) & 0xff
                if k == 27:
                    break
                elif k == 78:
                    continue



