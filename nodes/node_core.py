from enum import Enum
from PyQt5 import QtCore

import rospy

from debug.debug import *


class Topic:
    def __init__(self, name, msg_type, callback=None, queue_size=10):
        self.name = name
        self.msg_type = msg_type
        self.callback = callback
        self.queue_size = queue_size


class NodeStatus(Enum):
    unknown = 0
    initializing = 1
    working = 2

    crashed = 20
    crashed_internal = 21
    crashed_connection = 22
    crashed_ros = 23


class Node(QtCore.QThread):
    language = "en"
    translation = None

    node_status = NodeStatus.unknown

    subscribed_topics = []
    published_topics = []
    subscribers = []
    publishers = []

    def __init__(self, node_name, subscribed_topics=None, published_topics=None, language="en"):
        # Set status
        self.node_status = NodeStatus.initializing

        # Initialize
        super(Node, self).__init__()
        rospy.init_node(node_name)

        # Place where you should import all translations
        self.language = language
        if self.language == "en":
            from languages import en as translation
            self.translation = translation
        else:
            from languages import en as translation
            self.translation = translation

        # Setup subscribed topics
        if subscribed_topics is not None:
            self.subscribed_topics = subscribed_topics

        # Setup published topics
        if published_topics is not None:
            self.published_topics = published_topics

        # Initialize all topics
        for topic in self.subscribed_topics:
            sub = self.Subscriber(topic)
            self.subscribers.append(sub)
        for topic in self.published_topics:
            pub = self.Publisher(topic)
            self.publishers.append(pub)

        self.exitFlag = False
        self.start()

    def publish_msg_on_topic(self, topic_name, msg):
        for pub in self.publishers:
            if pub.topic.name == topic_name:
                pub.publish(msg)

    def get_node_status(self):
        return self.translation.nodeStatusTranslationDictionary[self.node_status]

    class Subscriber:
        topic = None
        callback_function = None

        def __init__(self, topic):
            self.topic = topic
            self.callback_function = topic.callback
            self.sub = rospy.Subscriber(self.topic.name, self.topic.msg_type, self.subscriber_callback)

        def subscriber_callback(self, data):
            self.callback_function(data)

    class Publisher:
        topic = None

        def __init__(self, topic):
            self.topic = topic
            self.pub = rospy.Publisher(topic.name, topic.msg_type, queue_size=topic.queue_size)

        def publish(self, message):
            if type(message) is self.topic.msg_type:
                self.pub.publish(message)
            else:
                debug(DBGLevel.WARN,
                      "Invalid publish message type, expected: " + str(self.topic.msg_type) + ", received: " + str(
                          message) + ".")
