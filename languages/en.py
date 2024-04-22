from item.item import ItemType, ItemPlacement
from nodes.node_core import NodeStatus
from nodes.table import TableStatus

##### Node #####
nodeStatusTranslationDictionary = {
        NodeStatus.unknown:            "Unknown",
        NodeStatus.initializing:       "Initializing",
        NodeStatus.working:            "Working",

        NodeStatus.crashed:            "Crashed unknown",
        NodeStatus.crashed_internal:   "Crashed internal",
        NodeStatus.crashed_connection: "Crashed communication",
        NodeStatus.crashed_ros:        "Crashed ROS",

        TableStatus.table_off:         "Working off",
        TableStatus.table_working:     "Working on",
        TableStatus.table_calibrating: "Working calibrating",
}
##### Node #####

##### Table Node #####
itemTranslationDict = {
        ItemType.book:        "Book",
        ItemType.food_tray:   "Food tray",
        ItemType.mug_any:     "Mug",
        ItemType.mug_full:    "Full mug",
        ItemType.mug_empty:   "Empty mug",
        ItemType.plate_any:   "Plate",
        ItemType.plate_full:  "Full plate",
        ItemType.plate_empty: "Empty plate",
        ItemType.phone:       "Phone",
        ItemType.drug:        "Drugs",
        ItemType.hand_any:    "Hand",
        ItemType.hand_light:  "Light touch",
        ItemType.hand_mid:    "Normal touch",
        ItemType.hand_hard:   "Hard touch",
        ItemType.none:        "Nothing",
        ItemType.unknown:     "Unknown",
}

itemPlacementTranslationDict = {
        ItemPlacement.center:        "Center of table",
        ItemPlacement.side:          "Side of table",
        ItemPlacement.edge:          "Edge of table",
        ItemPlacement.partially_out: "Out of table",
        ItemPlacement.unknown:       "Nothing",
}
##### Table Node #####

##### Usage of table node #####
usageIntelligentTableDictionary = {
        # Locations
        "kitchen_D": "the kitchen ",
        "table_D": "the table ",
        "dock_D": "the docking station ",
        "default_D": "the default position ",
        "idk_D": "somewhere ",

        # Objects
        "tea_B": "tea ",
        "dish_B": "empty dish ",
        "sth_B": "something ",

        # Informative
        "drive": "I go to ",
        "arrived": "I arrived to ",
        "not_arrived": "Cannot arrive to ",
        "not_placed": "The object was not placed on the table ",
        "thanks": "Thank you ",

        # Requests
        "position": "Please correct the position of the object ",
        "weight": "The item has an incorrect weight ",
        "give": "Could you give me ",
        "take": "Please take ",

        # Tasks
        "deliver_tea": "The tea has been delivered ",
        "deliver_dish": "The dish has been delivered ",
        "abort": "Task aborted ",
}
##### Usage of table node #####
