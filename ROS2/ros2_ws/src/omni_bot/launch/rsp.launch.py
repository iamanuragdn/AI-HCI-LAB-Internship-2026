import os

from ament_index_python.packages import get_package_share_directory

from launch import LaunchDescription
from launch.substitutions import LaunchConfiguration
from launch_ros.actions import Node

import xacro


def generate_launch_description():

    package_name = 'omni_bot'

    xacro_file = os.path.join(
        get_package_share_directory(package_name), 'description', 'robot.urdf.xacro'
    )
    robot_description_config = xacro.process_file(xacro_file)
    robot_description = robot_description_config.toxml()

    node_robot_state_publisher = Node(
        package='robot_state_publisher',
        executable='robot_state_publisher',
        output='screen',
        parameters=[{
            'robot_description': robot_description,
            'use_sim_time': True
        }]
    )

    return LaunchDescription([
        node_robot_state_publisher
    ])
