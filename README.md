## Smart table node
- **Smart table** have to run on system that has a physical sensor connected to it
- **Smart table** need to have access to proper USB port to work `sudo chmod 777 /dev/ttyUSB0` (or other USB number, depends on configuration)
- **Smart table** is turned on by default right now but signal to turn it on manually might be usefull `rostopic pub /table/sgn_on std_msgs/Bool "data: true"`

```
python3 ./smart_table.py
```
```
rosrun smart_table smart_table.py
```

If it don't die with **Ctrl+C** use **Ctrl+\\**.

## Scenario manager node
- **Scenario manager** need *dialog* node to running `roslaunch dialog websocket.launch`
- **Scenario manager** need **smart_table** to work properly. **Smart table** can be launched later or restarted when **scenario manager** works.

```
python3 ./scenario_manager.py
```
```
rosrun smart_table scenario_manager.py
```

## Rico docking
<details>
  <summary>Undock robot</summary>
  
```
rostopic pub /undocker_server/goal laser_servoing_msgs/UndockActionGoal "header:
  seq: 0
  stamp:
    secs: 0
    nsecs: 0
  frame_id: ''
goal_id:
  stamp:
    secs: 0
    nsecs: 0
  id: ''
goal: {}"
```
</details>

<details>
  <summary>Dock robot</summary>
  
```
rostopic pub /go_and_dock/goal dock_charge_sm_msgs/GoAndDockActionGoal "header:
  seq: 0
  stamp:
    secs: 0
    nsecs: 0
  frame_id: ''
goal_id:
  stamp:
    secs: 0
    nsecs: 0
  id: ''
goal:
  retry_delay:
    secs: 0
    nsecs: 0
  use_current_pose: true"
```
</details>

## Caution
During development of this code and tensorflow models I stumble upon this [issue](https://github.com/keras-team/keras-core/issues/855). To go through it I worked with tensorflow in version 2.12. If you will have problems with models try to use this version of tensorflow.

To don't mess your global workspace I recommend to use **venv** and **python 3.8**. Also I created script to setup this venv. This script creates venv in directory of executing.
```
sudo apt-get install python3.8-venv
source ./venv_setup.sh
```
