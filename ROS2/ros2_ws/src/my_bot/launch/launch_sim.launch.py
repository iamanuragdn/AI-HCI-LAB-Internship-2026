import os
from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import IncludeLaunchDescription
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch_ros.actions import Node

def generate_launch_description():
    package_name = 'my_bot'
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
            'gz_args': '-r -v 4 ' + os.path.join(get_package_share_directory('my_bot'), 'worlds', 'empty.world')
        }.items()
    )

    spawn_entity = Node(
        package='ros_gz_sim',
        executable='create',
        arguments=['-topic', 'robot_description', '-name', 'my_bot'],
        output='screen'
    )

    # Bridges the LIDAR scan topic from Gazebo's internal transport into ROS 2
    bridge = Node(
        package='ros_gz_bridge',
        executable='parameter_bridge',
        arguments=[
            '/scan@sensor_msgs/msg/LaserScan[gz.msgs.LaserScan',
            '/cmd_vel@geometry_msgs/msg/Twist]gz.msgs.Twist',
            '/model/my_bot/odometry@nav_msgs/msg/Odometry[gz.msgs.Odometry',
            '/model/my_bot/tf@tf2_msgs/msg/TFMessage[gz.msgs.Pose_V',
        ],
        remappings=[
            ('/model/my_bot/odometry', '/odom'),
            ('/model/my_bot/tf', '/tf'),
        ],
        output='screen'
    )

    # Twist mux: merges Nav2 and (future) joystick commands into one /cmd_vel stream
    twist_mux_params = os.path.join(
        get_package_share_directory('my_bot'), 'config', 'twist_mux.yaml'
    )
    twist_mux = Node(
        package='twist_mux',
        executable='twist_mux',
        parameters=[twist_mux_params, {'use_sim_time': True}],
        remappings=[('/cmd_vel_out', '/cmd_vel')]
    )

    return LaunchDescription([
        rsp,
        gazebo,
        spawn_entity,
        bridge,
        twist_mux,
    ])