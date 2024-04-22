#!/usr/bin/env python3.8

import time
import os
import argparse

# Suppress tensorflow noncritical warnings
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '2'

from nodes.table import TableNode
from sensor.sensor import Sensor
from connection.connection import Serial

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("-p", metavar="PORT", help="USB port where intelligent skin is connected",
                        default=Serial.default_port_name())
    args = parser.parse_args()

    sensor = Sensor(args.p)
    sensor.connect_to_controller()
    node = TableNode(weight_calculation_mode="neuron", default_turn_on=True)
    node.set_sensor(sensor)

    while 1:
        time.sleep(60)
