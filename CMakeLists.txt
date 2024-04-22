cmake_minimum_required(VERSION 3.0.2)
project(smart_table)

find_package(catkin REQUIRED)

catkin_package(
#  INCLUDE_DIRS include
#  LIBRARIES smart_table
#  CATKIN_DEPENDS other_catkin_pkg
#  DEPENDS system_lib
)


include_directories(
# include
# ${catkin_INCLUDE_DIRS}
)

# catkin_python_setup()

install(
  DIRECTORY   item/classifier/models/
  DESTINATION ${CATKIN_PACKAGE_SHARE_DESTINATION}/models/
)

