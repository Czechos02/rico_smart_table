from connection.connection import Serial
import copy

from sensor.data_parsing import parse_data_to_np_image, cast_data_to_uint8, compensate_raw_image
from sensor.params import Params
from debug.debug import *


class Sensor:
    ser = None
    usb_port = ""
    usb_connected = False

    field_params = None

    parent_node = None

    image_calibrated = None
    image_calibrated_raw = None
    image_actual = None
    image_actual_raw = None
    image_actual_calibrated = None
    image_actual_calibrated_raw = None

    def __init__(self, usb_port="/dev/ttyUSB0", field_params=Params):
        self.usb_port = usb_port
        self.field_params = field_params
        self.ser = Serial()
        self.ser.set_data_receiver(self.new_data_received)

    def set_usb_port(self, usb_port):
        self.usb_port = usb_port

    def connect_to_controller(self):
        if self.ser.connect_to_controller(self.usb_port) == 0:
            self.usb_connected = True
        else:
            self.usb_connected = False

    def connection_crashed(self):
        # TODO make usage of this function
        self.usb_connected = False

    def set_parent_node(self, node):
        self.parent_node = node

    def get_usb_connected(self):
        return self.usb_connected

    def new_data_received(self, n_rows, n_columns, new_pressure_map):
        # TODO sometimes incoming data are corrupted (values like 4). It has to be filtered out
        # It is no longer a problem when reading from USB is no longer clogged
        self.image_actual_raw = new_pressure_map
        self.image_actual = parse_data_to_np_image(n_rows, n_columns, new_pressure_map)

        if self.image_calibrated is None:
            self.image_calibrated = self.image_actual.copy()
            self.image_calibrated_raw = copy.deepcopy(self.image_actual_raw)
            return
        self.image_actual_calibrated_raw = compensate_raw_image(n_rows, n_columns, self.image_actual_raw,
                                                                self.image_calibrated_raw)
        self.image_actual_calibrated = parse_data_to_np_image(n_rows, n_columns, self.image_actual_calibrated_raw)
        debug(DBGLevel.INFO, "New data received from controller")

        if self.parent_node is not None:
            self.parent_node.new_image_from_sensor()

    def calibrate_sensor(self, raw_data):
        debug(DBGLevel.INFO, "Calibrate sensor")
        self.image_calibrated = raw_data
