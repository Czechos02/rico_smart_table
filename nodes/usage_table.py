import time
import os

# Suppress tensorflow noncritical warnings
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '2'

from std_msgs.msg import Bool, String, Int32
from geometry_msgs.msg import PoseStamped
from move_base_msgs.msg import MoveBaseActionResult
from tiago_msgs.msg import SaySentenceActionGoal

from nodes.node_core import Node, Topic
from nodes.messages import prepare_pose_stamped_msg, prepare_sentence_action_goal
from debug.debug import debug, DBGLevel
from item.item import ItemPlacement


class UsageTableNode(Node):
    item_placed_status = False
    item_weight = 0
    item_prediction = ""
    item_location = ""
    move_status = 0
    command_arrived = False
    command = ""

    language_usage_table = "en"
    translation_usage_table = Node
    language_table = "en"
    translation_table = Node

    def __init__(self,
                 node_name="UsageIntelligentTable",
                 language_usage_table="en",
                 language_table="en"
                 ):
        # Initialize internal variables
        self.item_placed_status = False
        self.item_weight = 0
        self.item_prediction = ""
        self.item_location = ""
        self.move_status = 0
        self.command_arrived = False
        self.command = ""

        # Setup subscribed topics
        subscribed_topics = []
        ret = Topic("/table/is_placed", Bool, callback=self.item_placed_callback)
        subscribed_topics.append(ret)
        ret = Topic("/table/weight", Int32, callback=self.item_weight_callback)
        subscribed_topics.append(ret)
        ret = Topic("/table/predicted_item", String, callback=self.item_predicted_callback)
        subscribed_topics.append(ret)
        ret = Topic("/table/location", String, callback=self.item_location_callback)
        subscribed_topics.append(ret)
        ret = Topic("/move_base/result", MoveBaseActionResult, callback=self.move_status_callback)
        subscribed_topics.append(ret)
        ret = Topic("/rico_hear", String, callback=self.rico_heard_callback)  # Rico heard that thing
        subscribed_topics.append(ret)

        # Setup published topics
        published_topics = []
        # TODO publish status of this node
        # nie status, tylko opublikować wiadomość raz, po wykonaniu/failu zadania
        # ret = Topic(topic_prefix + "/status", String)
        # published_topics.append(ret)
        ret = Topic("/move_base_simple/goal", PoseStamped)
        published_topics.append(ret)
        ret = Topic("/rico_says/goal", SaySentenceActionGoal)  # Rico will say that thing
        published_topics.append(ret)

        # Language of messages that robot says
        self.language_usage_table = language_usage_table
        if self.language_usage_table == "en":
            from languages import en as translation
            self.translation_usage_table = translation
        elif self.language_usage_table == "pl":
            from languages import pl as translation
            self.translation_usage_table = translation
        else:
            from languages import en as translation
            self.translation_usage_table = translation

        # Language of messages incoming from table
        self.language_table = language_usage_table
        if self.language_table == "en":
            from languages import en as translation
            self.translation_table = translation
        else:
            from languages import en as translation
            self.translation_table = translation

        # Run node
        super(UsageTableNode, self).__init__(node_name, subscribed_topics, published_topics)
        debug(DBGLevel.CRITICAL, "Usage table node has been initialized")

    def item_placed_callback(self, data=None):
        if type(data) is Bool:
            self.item_placed_status = data.data
        else:
            self.item_placed_status = False
            self.item_weight = 0
            self.item_prediction = ""
            self.item_location = ""

    def item_weight_callback(self, data=None):
        if type(data) is Int32:
            self.item_weight = data.data
        else:
            self.item_weight = 0

    def item_predicted_callback(self, data=None):
        if type(data) is String:
            self.item_prediction = data.data
        else:
            self.item_prediction = ""

    def item_location_callback(self, data=None):
        if type(data) is String:
            self.item_location = data.data
        else:
            self.item_location = ""

    def move_status_callback(self, data=None):
        # MoveBaseActionResult.status.status (Enum)
        # uint8 PENDING=0
        # uint8 ACTIVE=1
        # uint8 PREEMPTED=2
        # uint8 SUCCEEDED=3
        # uint8 ABORTED=4
        # uint8 REJECTED=5
        # uint8 PREEMPTING=6
        # uint8 RECALLING=7
        # uint8 RECALLED=8
        # uint8 LOST=9

        if type(data) is MoveBaseActionResult:
            self.move_status = data.status.status
        else:
            self.move_status = 0

    def rico_heard_callback(self, data=None):
        if type(data) is String:
            debug(DBGLevel.INFO, "Rico heard: " + data.data)
            self.command = data.data
            self.command_arrived = True
        else:
            self.command = ""
            self.command_arrived = False

    # TODO positions to json or xml
    @staticmethod
    def get_pose_kitchen():
        pose = prepare_pose_stamped_msg(pos_x=16.85, pos_y=8.05, rot_z=-0.1, rot_w=0.0)
        return pose

    @staticmethod
    def get_pose_docker():
        pose = prepare_pose_stamped_msg(pos_x=11.28, pos_y=6.9, rot_z=-0.7, rot_w=0.71)
        return pose

    @staticmethod
    def get_pose_table():
        pose = prepare_pose_stamped_msg(pos_x=9.91, pos_y=8.14, rot_z=-0.54, rot_w=0.84)
        return pose

    @staticmethod
    def get_pose_default():
        pose = prepare_pose_stamped_msg(pos_x=11.28, pos_y=6.9, rot_z=0.68, rot_w=0.75)
        return pose

    def go_to_position(self, position):
        # TODO enum with possible Poses
        if position == "kitchen":
            position_translate = self.translation_usage_table.usageIntelligentTableDictionary["kitchen_D"]
            goal = self.get_pose_kitchen()
        elif position == "table":
            position_translate = self.translation_usage_table.usageIntelligentTableDictionary["table_D"]
            goal = self.get_pose_table()
        elif position == "dock":
            position_translate = self.translation_usage_table.usageIntelligentTableDictionary["dock_D"]
            goal = self.get_pose_docker()
        elif position == "default":
            position_translate = self.translation_usage_table.usageIntelligentTableDictionary["default_D"]
            goal = self.get_pose_default()
        else:
            position_translate = self.translation_usage_table.usageIntelligentTableDictionary["idk_D"]
            goal = self.get_pose_default()

        debug(DBGLevel.INFO, "I go to the " + position)
        self.robot_say_sth(self.translation_usage_table.usageIntelligentTableDictionary["drive"] + position_translate)

        self.publish_msg_on_topic("/move_base_simple/goal", goal)
        self.move_status = 0  # Have to reset move status after publishing message

        while 1:
            # Move ended
            if self.move_status != 0:
                # Success
                if self.move_status == 3:
                    debug(DBGLevel.INFO, "I arrived to the " + position)
                    return 0
                # Failure
                else:
                    self.robot_say_sth(
                        self.translation_usage_table.usageIntelligentTableDictionary[
                            "not_arrived"] + position_translate)
                    debug(DBGLevel.ERROR, "Cannot arrive to the " + position + " Code: " + str(self.move_status))
                    return 1

            time.sleep(1)

    def task_completed_behaviour(self, message):
        self.robot_say_sth(message)
        debug(DBGLevel.ERROR, message)
        if self.go_to_position("default"):
            return -1
        return 0

    def robot_say_sth(self, text_to_say):
        self.publish_msg_on_topic("/rico_says/goal", prepare_sentence_action_goal(text_to_say))
        return 0

    def check_item_inside_table(self, item):
        if self.item_location == self.translation_table.itemPlacementTranslationDict[ItemPlacement.center] or \
                self.item_location == self.translation_table.itemPlacementTranslationDict[ItemPlacement.side]:
            debug(DBGLevel.INFO, "Item " + item + " has been placed")
            return 0
        elif self.item_location == self.translation_table.itemPlacementTranslationDict[ItemPlacement.edge]:
            debug(DBGLevel.WARN,
                  "Item " + item + " has been placed on the edge of the table - correct its position")
            self.robot_say_sth(self.translation_usage_table.usageIntelligentTableDictionary["position"])
            time.sleep(5)
            return 1
        else:
            debug(DBGLevel.ERROR, "Item " + item + " couldn't be placed od the table")
            self.robot_say_sth(self.translation_usage_table.usageIntelligentTableDictionary["not_placed"])
            return 2

    def check_item_in_weight_range(self, item):
        if item == "tea":
            expected_weight = 800
        elif item == "empty dish":
            expected_weight = 500
        else:
            return 0

        if expected_weight * 0.6 < self.item_weight < expected_weight * 1.5:
            return 0
        else:
            self.robot_say_sth(self.translation_usage_table.usageIntelligentTableDictionary["weight"])
            debug(DBGLevel.ERROR, "Item " + item + " have wrong weight: " + str(self.item_weight))
            time.sleep(5)
            return 1

    def wait_for_item_placed(self, item):
        if item == "tea":
            item_translate = self.translation_usage_table.usageIntelligentTableDictionary["tea_B"]
        elif item == "empty dish":
            item_translate = self.translation_usage_table.usageIntelligentTableDictionary["dish_B"]
        else:
            item_translate = self.translation_usage_table.usageIntelligentTableDictionary["sth_B"]

        debug(DBGLevel.INFO, "I wait for " + item + " to be placed")
        self.robot_say_sth(self.translation_usage_table.usageIntelligentTableDictionary["give"] + item_translate)

        # TODO check weight and item type
        i = 0
        while 1:
            time.sleep(1)
            if self.item_placed_status:
                # Drop first measurement
                if i == 0:
                    i = 1
                    continue
                i = 0
                if self.check_item_inside_table(item) != 0:
                    continue
                if self.check_item_in_weight_range(item) != 0:
                    continue

                self.robot_say_sth(self.translation_usage_table.usageIntelligentTableDictionary["thanks"])
                time.sleep(2)
                return 0

    def wait_for_item_taken(self, item):
        if item == "tea":
            item_translate = self.translation_usage_table.usageIntelligentTableDictionary["tea_B"]
        elif item == "empty dish":
            item_translate = self.translation_usage_table.usageIntelligentTableDictionary["dish_B"]
        else:
            item_translate = self.translation_usage_table.usageIntelligentTableDictionary["sth_B"]

        debug(DBGLevel.INFO, "I wait for " + item + " to be taken")
        self.robot_say_sth(self.translation_usage_table.usageIntelligentTableDictionary["take"] + item_translate)

        while 1:
            if self.item_placed_status is False:
                debug(DBGLevel.INFO, "Item " + item + " has been taken")

                self.robot_say_sth(self.translation_usage_table.usageIntelligentTableDictionary["thanks"])
                time.sleep(2)
                return 0
            time.sleep(1)

    def handle_give_tea_command(self):
        # Go to kitchen
        if self.go_to_position("kitchen") != 0:
            return -1

        # Get mug of tea
        if self.wait_for_item_placed("tea") != 0:
            return -1

        # Go to task giver
        if self.go_to_position("table") != 0:
            return -1

        # Acknowledge tea take off
        if self.wait_for_item_taken("tea") != 0:
            return -1

        # End task
        if self.task_completed_behaviour(
                self.translation_usage_table.usageIntelligentTableDictionary["deliver_tea"]) != 0:
            return -1
        return 0

    def handle_drop_mug_command(self):
        # Go to task giver
        if self.go_to_position("table") != 0:
            return -1

        # Take mug from task giver
        if not self.wait_for_item_placed("empty dish"):
            return -1

        # Go to kitchen
        if self.go_to_position("kitchen") != 0:
            return -1

        # Acknowledge mug take off
        if not self.wait_for_item_taken("empty dish"):
            return -1

        # End task
        if self.task_completed_behaviour(
                self.translation_usage_table.usageIntelligentTableDictionary["deliver_dish"]) != 0:
            return -1
        return 0

    def abort_task(self):
        self.task_completed_behaviour(self.translation_usage_table.usageIntelligentTableDictionary["abort"])
