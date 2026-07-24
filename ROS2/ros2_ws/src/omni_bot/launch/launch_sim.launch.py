import os

from ament_index_python.packages import get_package_share_directory

from launch import LaunchDescription
from launch.actions import IncludeLaunchDescription
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch_ros.actions import Node


def generate_launch_description():
    package_name = 'omni_bot'

    rsp = IncludeLaunchDescription(
        PythonLaunchDescriptionSource([
            os.path.join(get_package_share_directory(package_name), 'launch', 'rsp.launch.py')
        ])
    )

    gazebo = IncludeLaunchDescription(
        PythonLaunchDescriptionSource([
            os.path.join(get_package_share_directory('ros_gz_sim'), 'launch', 'gz_sim.launch.py')
        ]),
        launch_arguments={
            'gz_args': '-r -v 4 ' + os.path.join(
                get_package_share_directory(package_name), 'worlds', 'empty.world'
            )
        }.items()
    )

    spawn_entity = Node(
        package='ros_gz_sim',
        executable='create',
        arguments=['-topic', 'robot_description', '-name', 'omni_bot'],
        output='screen'
    )

    # Only cmd_vel needs bridging ROS -> GZ. /odom and /tf are now
    # published directly in ROS by fake_planar_move.py (see below) —
    # this Gazebo Harmonic build doesn't ship the PlanarMove plugin
    # that would normally have produced them.
    bridge = Node(
        package='ros_gz_bridge',
        executable='parameter_bridge',
        arguments=[
            '/cmd_vel@geometry_msgs/msg/Twist]gz.msgs.Twist',
        ],
        output='screen'
    )

    # Stand-in for the missing PlanarMove plugin: integrates /cmd_vel
    # and moves the robot directly via Gazebo's set_pose service.
    fake_planar_move = Node(
        package='omni_bot',
        executable='fake_planar_move.py',
        parameters=[{
            'world_name': 'empty',
            'model_name': 'omni_bot',
            'update_rate_hz': 12.0,
        }],
        output='screen'
    )

    return LaunchDescription([
        rsp,
        gazebo,
        spawn_entity,
        bridge,
        fake_planar_move,
    ])