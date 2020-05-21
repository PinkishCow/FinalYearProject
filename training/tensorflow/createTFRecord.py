
import random
import tensorflow as tf
import csv
import os
import glob

from object_detection.utils import dataset_util


# D:\Desktop\Dissertation\images\can_bedroom_shelf_2\\vott-csv-export\Can-Pics-export.csv
# only works for single item images
def start():
    eval_percentage = 0.2

    folders = ["D:\\Desktop\\Dissertation\\images\\butter\\vott-csv-export",
               "D:\\Desktop\\Dissertation\\images\\can_bedroom_shelf_2\\vott-csv-export",
               "D:\\Desktop\\Dissertation\\images\\coco_bedroom_shelf\\vott-csv-export",
               "D:\\Desktop\\Dissertation\\images\\crisps\\vott-csv-export",
               "D:\\Desktop\\Dissertation\\images\\crisps-2\\vott-csv-export",
               "D:\\Desktop\\Dissertation\\images\\milk-red\\vott-csv-export",
               "D:\\Desktop\\Dissertation\\images\\spray_bedroom_shelf\\vott-csv-export"]

    item_ids = {"Butter": 1, "Can": 2, "Cereal": 3, "Crisps-1": 4, "Crisps-2": 5, "Milk": 6, "Spray": 7}
    train_examples = []
    eval_examples = []
    name = "D:\\Desktop\\Dissertation\\images\\Tensorflow-TFRecord-All-Items"

    for folder in folders:
        item_count = len(glob.glob1(folder, "*.jpg"))
        eval_count = int(item_count * eval_percentage)

        temp_train = []
        temp_eval = []
        file = os.path.join(folder, glob.glob1(folder, "*.csv")[0])
        print(file)
        if not (os.path.exists(file)):
            print("File not found..")
            return
        else:
            with open(file, newline='') as x:
                reader = csv.reader(x, quoting=csv.QUOTE_NONNUMERIC)
                next(reader)
                for row in reader:
                    print(row[0])
                    if row[5] not in item_ids:
                        print("item_ids broken")
                        exit()
                    image_path = os.path.join(folder, row[0])
                    encoded_image = open(image_path, 'rb').read()
                    temp_train.append(
                        create_tf_example(bytes(image_path, encoding='utf8'), encoded_image, [row[1] / 1024],
                                          [row[2] / 768], [row[3] / 1024],
                                          [row[4] / 768], [bytes(row[5], encoding='utf8')], [item_ids[row[5]]]))

        for x in range(eval_count):
            item = random.choice(temp_train)
            temp_eval.append(item)
            temp_train.remove(item)

        train_examples += temp_train
        eval_examples += temp_eval

    train_writer = tf.python.python_io.TFRecordWriter("D:\\Desktop\\Dissertation\\Tensorflow-TFRecord-All-Items")
    for example in train_examples:
        train_writer.write(example.SerializeToString())

    eval_writer = tf.python.python_io.TFRecordWriter("D:\\Desktop\\Dissertation\\Tensorflow-TFRecord-All-Items-EVAL")
    for example in eval_examples:
        eval_writer.write(example.SerializeToString())


# From TD obj examples
# https://github.com/tensorflow/models/blob/master/research/object_detection/g3doc/using_your_own_dataset.md
def create_tf_example(filename, image_data, xmins, ymins, xmaxs, ymaxs, classes_text, classes_id):
    tf_example = tf.python.train.Example(features=tf.python.train.Features(feature={
        'image/height': dataset_util.int64_feature(768),
        'image/width': dataset_util.int64_feature(1024),
        'image/filename': dataset_util.bytes_feature(filename),
        'image/source_id': dataset_util.bytes_feature(filename),
        'image/encoded': dataset_util.bytes_feature(image_data),
        'image/format': dataset_util.bytes_feature(b'jpeg'),
        'image/object/bbox/xmin': dataset_util.float_list_feature(xmins),
        'image/object/bbox/xmax': dataset_util.float_list_feature(xmaxs),
        'image/object/bbox/ymin': dataset_util.float_list_feature(ymins),
        'image/object/bbox/ymax': dataset_util.float_list_feature(ymaxs),
        'image/object/class/text': dataset_util.bytes_list_feature(classes_text),
        'image/object/class/label': dataset_util.int64_list_feature(classes_id),
    }))
    return tf_example


start()
