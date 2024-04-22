import numpy as np
import ros_numpy

from sensor_msgs.msg import Image
from std_msgs.msg import Bool, String, Header, Int32
from geometry_msgs.msg import PoseStamped
from tiago_msgs.msg import SaySentenceActionGoal

from debug.debug import *


def prepare_bool_msg(val):
    if type(val) is bool:
        msg = Bool()
        msg.data = val
        return msg


def prepare_string_msg(val):
    if type(val) is str:
        msg = String()
        msg.data = val
        return msg


def prepare_int32_msg(val):
    if type(val) is Int32 or type(val) is int:
        msg = Int32()
        msg.data = val
        return msg


def prepare_image_msg(header_str, val):
    if type(header_str) is str and type(val) is np.ndarray:
        try:
            msg = ros_numpy.msgify(Image, val, encoding="mono8")
            msg.header = Header()
            msg.header.frame_id = header_str
        except:
            debug(DBGLevel.ERROR, "Unsuccessfull image parsing")
            return None
        return msg


def prepare_pose_stamped_msg(frame_id="map", pos_x=0.0, pos_y=0.0, pos_z=0.0, rot_x=0.0, rot_y=0.0, rot_z=0.0,
                             rot_w=1.0):
    if type(frame_id) is str and type(pos_x) is float and type(pos_y) is float and type(pos_z) is float and type(
            rot_x) is float and type(rot_y) is float and type(rot_z) is float and type(rot_w) is float:
        msg = PoseStamped()
        msg.header.frame_id = frame_id
        msg.pose.position.x = pos_x
        msg.pose.position.y = pos_y
        msg.pose.position.z = pos_z
        msg.pose.orientation.x = rot_x
        msg.pose.orientation.y = rot_y
        msg.pose.orientation.z = rot_z
        msg.pose.orientation.w = rot_w
        return msg


def prepare_sentence_action_goal(string):
    if type(string) is str:
        msg = SaySentenceActionGoal()
        msg.goal.sentence = string
        return msg
