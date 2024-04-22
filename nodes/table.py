import time
import numpy as np

import rospkg
from sensor_msgs.msg import Image
from std_msgs.msg import Bool, String, Int32

from keras.models import load_model

from nodes.messages import prepare_bool_msg, prepare_image_msg, prepare_string_msg, prepare_int32_msg
from nodes.node_core import NodeStatus, Topic, Node
from sensor.params import ImageMask
from sensor.data_parsing import flatten
from item.item import Item, ItemPlacement, ItemType
from item.classifier.position_recognition import recognise_position
from item.classifier.weight_estimation import estimate_weight, estimate_weight_with_model, \
    mean_absolute_percentage_square_error
from item.classifier.image_recognition import Classifier
from debug.debug import *


class TableStatus(NodeStatus, Enum):
    table_working = 101
    table_calibrating = 102
    table_off = 103


class TableNode(Node):
    sensor = None

    on_flag = False
    calibrate_flag = False
    new_image_flag = False

    mask = ImageMask()
    actual_item = None
    item_cnt = 1

    item_classifier = None
    classifier_model_path = None

    weight_calculation_mode = None
    weight_model_path = None
    weight_model = None

    # weight_calculation: "internal", "neuron"
    def __init__(self,
                 node_name="SmartTable",
                 language="en",
                 model_path="item/classifier/models/classifier_model.keras",
                 topic_prefix="/table",
                 weight_calculation_mode="internal",
                 weight_calculation_model_path="item/classifier/models/weight_model.keras",
                 default_turn_on=False
                 ):
        # Set status
        self.node_status = TableStatus.initializing

        # Setup subscribed topics
        subscribed_topics = []
        ret = Topic(topic_prefix + "/sgn_on", Bool, callback=self.sgn_on_callback)
        subscribed_topics.append(ret)
        ret = Topic(topic_prefix + "/sgn_calibrate", Bool, callback=self.sgn_calibrate_callback)
        subscribed_topics.append(ret)

        # Setup published topics
        published_topics = []
        ret = Topic(topic_prefix + "/raw_image", Image)
        published_topics.append(ret)
        ret = Topic(topic_prefix + "/status", String)
        published_topics.append(ret)
        ret = Topic(topic_prefix + "/is_placed", Bool)
        published_topics.append(ret)
        ret = Topic(topic_prefix + "/weight", Int32)
        published_topics.append(ret)
        ret = Topic(topic_prefix + "/predicted_item", String)
        published_topics.append(ret)
        ret = Topic(topic_prefix + "/location", String)
        published_topics.append(ret)

        # Localize path to resources
        rp = rospkg.RosPack()
        share_path = rp.get_path('smart_table') + '/'

        # Item classifier model initialization section
        self.classifier_model_path = share_path + model_path
        self.item_classifier = Classifier()
        self.item_classifier.import_model(self.classifier_model_path)

        # Item weight variants
        if weight_calculation_mode == "neuron":
            self.weight_calculation_mode = weight_calculation_mode
            self.weight_model_path = share_path + weight_calculation_model_path
            self.weight_model = load_model(self.weight_model_path, custom_objects={
                'mean_absolute_percentage_square_error': mean_absolute_percentage_square_error})
        else:
            self.weight_calculation_mode = "internal"

        # Run node
        self.topic_prefix = topic_prefix
        super(TableNode, self).__init__(node_name, subscribed_topics, published_topics, language=language)
        if default_turn_on:
            self.on_flag = default_turn_on
            self.node_status = TableStatus.table_working
        else:
            self.node_status = TableStatus.table_off
        debug(DBGLevel.CRITICAL, "Table node has been initialized")

    def set_sensor(self, sensor):
        self.sensor = sensor
        self.sensor.set_parent_node(self)

    def sgn_on_callback(self, data=None):
        if type(data) is Bool:
            self.on_flag = data.data
            self.new_image_flag = False

        if self.on_flag and self.node_status is TableStatus.table_off:
            self.node_status = TableStatus.table_working
        if not self.on_flag and (
                self.node_status is TableStatus.table_working or self.node_status is TableStatus.table_calibrating):
            self.node_status = TableStatus.table_off

    def sgn_calibrate_callback(self, data=None):
        if type(data) is Bool:
            self.calibrate_flag = data.data

        if self.calibrate_flag and self.node_status is TableStatus.table_working:
            self.node_status = TableStatus.table_calibrating
        if not self.calibrate_flag:
            if self.on_flag:
                self.node_status = TableStatus.table_working
            else:
                self.node_status = TableStatus.table_off

    def get_calibration_flag(self):
        return self.calibrate_flag

    def get_on_flag(self):
        return self.on_flag

    def publish_is_placed(self, boolean):
        self.publish_msg_on_topic(self.topic_prefix + "/is_placed", prepare_bool_msg(boolean))

    def publish_status(self, string):
        self.publish_msg_on_topic(self.topic_prefix + "/status", prepare_string_msg(string))

    def publish_predicted_item(self, string):
        self.publish_msg_on_topic(self.topic_prefix + "/predicted_item", prepare_string_msg(string))

    def publish_location(self, string):
        self.publish_msg_on_topic(self.topic_prefix + "/location", prepare_string_msg(string))

    def publish_weight(self, int32):
        self.publish_msg_on_topic(self.topic_prefix + "/weight", prepare_int32_msg(int32))

    def publish_image(self, image):
        self.publish_msg_on_topic(self.topic_prefix + "/raw_image", prepare_image_msg("Smart table node", image))

    def new_image_from_sensor(self):
        self.new_image_flag = True

    def is_item_placed(self):
        for i in flatten(self.actual_item.getExtractedImage()):
            if i > 10:
                return True
        else:
            return False

    def get_predicted_item(self):
        if self.actual_item.type is not ItemType.none:
            return self.translation.itemTranslationDict[self.actual_item.type]
        else:
            return self.translation.itemTranslationDict[ItemType.none]

    def get_predicted_location(self):
        if self.actual_item.placement is not ItemPlacement.unknown:
            return self.translation.itemPlacementTranslationDict[self.actual_item.placement]
        else:
            return self.translation.itemPlacementTranslationDict[ItemPlacement.unknown]

    def get_predicted_weight(self):
        if self.actual_item.weight > 0.0:
            return int(round(self.actual_item.weight))
        else:
            return 0

    def exstract_image_from_sensor_data(self):
        # Calibration image is not nessecarry, because sensor calibrated this data on its own
        self.actual_item = Item(self.mask.getMask())
        self.actual_item.image = self.sensor.image_actual_calibrated
        self.actual_item.image_extracted_raw = self.sensor.image_actual_calibrated_raw
        self.actual_item.setExtractedImage()
        self.actual_item.id = self.item_cnt
        self.item_cnt += 1

    def make_recognition_of_image(self):
        if self.is_item_placed():
            self.actual_item.placement = recognise_position(self.actual_item.getExtractedImage(), self.mask.getMask(),
                                                            [1.5, 2.5])

            if self.weight_calculation_mode == "internal":
                self.actual_item.weight = estimate_weight(self.actual_item.image_extracted_raw)
            elif self.weight_calculation_mode == "neuron":
                weight_estimated = estimate_weight_with_model(self.weight_model,
                                                              np.array([self.actual_item.getExtractedImage()]))
                self.actual_item.weight = int(weight_estimated[0])
            else:
                self.actual_item.weight = 0

            if self.item_classifier is not None:
                prediction = self.item_classifier.predict_items_with_confidence(
                    np.array([self.actual_item.getExtractedImage()]), 0.75, self.item_classifier.output_types)
                self.actual_item.type = prediction[0]
            else:
                self.actual_item.type = ItemType.unknown

    def check_node_work_properly(self):
        # Check status of connection
        if self.sensor.get_usb_connected() is False:
            self.node_status = TableStatus.crashed_connection
            return False

        # Connection has been resetted (have to be after connection check)
        if self.node_status == TableStatus.crashed_connection:
            self.node_status = TableStatus.table_off
            return False

        # Node is turned off by user
        if self.on_flag is False:
            self.node_status = TableStatus.table_off
            return False

        return True

    def run(self):
        i = 0
        while not self.exitFlag:
            time.sleep(0.01)

            if self.check_node_work_properly():
                # Check for new image and handle it
                if self.new_image_flag:
                    if self.calibrate_flag:
                        self.sensor.calibrate_sensor(self.sensor.image_actual)
                    self.exstract_image_from_sensor_data()
                    self.make_recognition_of_image()

                    #####
                    self.publish_image(self.sensor.image_actual)
                    self.publish_is_placed(self.is_item_placed())
                    self.publish_predicted_item(self.get_predicted_item())
                    self.publish_location(self.get_predicted_location())
                    self.publish_weight(self.get_predicted_weight())
                    #####

                    self.new_image_flag = False

            # TODO Make it simpler and better (slow down publishing status msgs)
            i += 1
            if i == 10:
                self.publish_status(self.get_node_status())
                i = 0
