#!/usr/bin/env python3.8

import time
import os
import string

# Suppress tensorflow noncritical warnings
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '2'

from nodes.box_carring import BoxCarringNode


def ignore_punctuation_marks(sentence):
    result = sentence.translate(str.maketrans('', '', string.punctuation))
    return result


if __name__ == "__main__":
    usage_node = BoxCarringNode()

    while 1:
        # Wait for commands
        if usage_node.command_arrived:
            usage_node.command_arrived = False
            command = ignore_punctuation_marks(usage_node.command).lower()

            if command == "zanieś to do kuchni" or ("take" in command and "this" in command):
                if usage_node.handle_carring_box() != 0:
                    usage_node.abort_task()
                usage_node.go_to_position("dock")
            else:
                pass

        time.sleep(1)
