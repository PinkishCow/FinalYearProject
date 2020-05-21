import numpy as np
import os
import sys
import tensorflow as tf
import time
import cv2
import csv
from object_detection.utils import label_map_util

#  Heavily adapted from https://gilberttanner.com/blog/live-object-detection

sys.path.append("..")
from object_detection.utils import ops as utils_ops

# Path to frozen detection graph. This is the actual model that is used for the object detection.
PATH_TO_MODEL_FOLDER = "/home/pi/FinalYearProject/TFgraphs"

# List of the strings that is used to add correct label for each box.
PATH_TO_LABELS = "/home/pi/models/research/object_detection/data/mscoco_complete_label_map.pbtxt"

TEST_COUNT = 10


def run_inference_for_single_image(image, graph):
    if 'detection_masks' in tensor_dict:
        # The following processing is only for single image
        detection_boxes = tf.squeeze(tensor_dict['detection_boxes'], [0])
        detection_masks = tf.squeeze(tensor_dict['detection_masks'], [0])
        # Reframe is required to translate mask from box coordinates to image coordinates and fit the image size.
        real_num_detection = tf.cast(tensor_dict['num_detections'][0], tf.int32)
        detection_boxes = tf.slice(detection_boxes, [0, 0], [real_num_detection, -1])
        detection_masks = tf.slice(detection_masks, [0, 0, 0], [real_num_detection, -1, -1])
        detection_masks_reframed = utils_ops.reframe_box_masks_to_image_masks(
            detection_masks, detection_boxes, image.shape[0], image.shape[1])
        detection_masks_reframed = tf.cast(
            tf.greater(detection_masks_reframed, 0.5), tf.uint8)
        # Follow the convention by adding back the batch dimension
        tensor_dict['detection_masks'] = tf.expand_dims(
            detection_masks_reframed, 0)
    image_tensor = tf.get_default_graph().get_tensor_by_name('image_tensor:0')

    # Run inference
    print("infer")
    output_dict = sess.run(tensor_dict,
                           feed_dict={image_tensor: np.expand_dims(image, 0)})
    print("end infer")
    return output_dict


for MODEL in os.listdir(PATH_TO_MODEL_FOLDER):
    if MODEL.endswith(".csv"):
        continue
    if MODEL.endswith(".py"):
        continue
    results = []
    print(MODEL)
    counter = 0
    while counter < TEST_COUNT:
        cap = cv2.VideoCapture(0)
        print(counter)
        counter += 1
        PATH_TO_FROZEN_GRAPH = os.path.join(PATH_TO_MODEL_FOLDER, MODEL, "frozen_inference_graph.pb")

        detection_graph = tf.Graph()
        with detection_graph.as_default():
            od_graph_def = tf.GraphDef()
            with tf.gfile.GFile(PATH_TO_FROZEN_GRAPH, 'rb') as fid:
                serialized_graph = fid.read()
                od_graph_def.ParseFromString(serialized_graph)
                tf.import_graph_def(od_graph_def, name='')

        category_index = label_map_util.create_category_index_from_labelmap(PATH_TO_LABELS, use_display_name=True)

        try:
            with detection_graph.as_default():
                with tf.Session() as sess:
                    # Get handles to input and output tensors
                    ops = tf.get_default_graph().get_operations()
                    all_tensor_names = {output.name for op in ops for output in op.outputs}
                    tensor_dict = {}
                    for key in [
                        'num_detections', 'detection_boxes', 'detection_scores',
                        'detection_classes', 'detection_masks'
                    ]:
                        tensor_name = key + ':0'
                        if tensor_name in all_tensor_names:
                            tensor_dict[key] = tf.get_default_graph().get_tensor_by_name(
                                tensor_name)

                        ret, image_np = cap.read()
                        # Expand dimensions since the model expects images to have shape: [1, None, None, 3]
                        image_np_expanded = np.expand_dims(image_np, axis=0)
                        # Actual detection.
                        print(ret)
                        start_time = time.time()
                        print(start_time)
                        output_dict = run_inference_for_single_image(image_np, detection_graph)
                        run_time = time.time() - start_time
                        results.append([MODEL, counter, run_time])
                        print(run_time)
                        # Visualization of the results of a detection.
                        if cv2.waitKey(25) & 0xFF == ord('q'):
                            cap.release()
                            cv2.destroyAllWindows()
                            break
        except Exception as e:
            print(e)
            cap.release()
        cap.release()
    for row in results:
        print(row)
    with open(os.path.join(PATH_TO_MODEL_FOLDER, "TFspeedResults.csv"), 'a', newline='') as file_out:
        writer = csv.writer(file_out, quoting=csv.QUOTE_NONNUMERIC)
        for row in results:
            writer.writerow(row)




