#!/usr/bin/env python3.8

import time
import os
import string

# Suppress tensorflow noncritical warnings
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '2'

from nodes.usage_table import UsageTableNode


def ignore_punctuation_marks(sentence):
    result = sentence.translate(str.maketrans('', '', string.punctuation))
    return result


if __name__ == "__main__":
    usage_node = UsageTableNode()

    while 1:
        # Wait for commands
        if usage_node.command_arrived:
            usage_node.command_arrived = False
            command = ignore_punctuation_marks(usage_node.command).lower()

            if command == "przywieź mi herbatę" or ("bring" in command and "tea" in command):
                if usage_node.handle_give_tea_command() != 0:
                    usage_node.abort_task()
            elif command == "odwieź kubek do kuchni" or ("take" in command and "empty" in command):
                if usage_node.handle_drop_mug_command() != 0:
                    usage_node.abort_task()
            else:
                pass

        time.sleep(1)
