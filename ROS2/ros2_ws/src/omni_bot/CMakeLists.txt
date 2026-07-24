cmake_minimum_required(VERSION 3.8)
project(omni_bot)

find_package(ament_cmake REQUIRED)

install(
  DIRECTORY description launch worlds
  DESTINATION share/${PROJECT_NAME}
)

install(
  PROGRAMS scripts/fake_planar_move.py
  DESTINATION lib/${PROJECT_NAME}
)

ament_package()
