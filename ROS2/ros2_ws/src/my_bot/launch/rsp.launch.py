# import os # this is a Python library that lets us manipulate files and folders. 

# from ament_index_python.packages import get_package_share_directory  # this is a ROS2 library that lets us find the location of our package.
# from launch import LaunchDescription  # this is a ROS2 library that lets us create a launch file.
# from launch.substitutions import Command  # this is a ROS2 library that lets us run a command in the terminal and use its output.
# from launch_ros.actions import Node # this is a ROS2 library that lets us launch a ROS2 node.


# def generate_launch_description(): #Everything inside here is the "to-do list" for startup.

#     pkg_path = get_package_share_directory('my_bot') # Find the path to our package.
#     xacro_file = os.path.join(pkg_path, 'description', 'robot.urdf.xacro') # Find the path to our xacro file. os.path.join() is a Python function that combines folder names into a full path.
#     robot_description = Command(['xacro ', xacro_file])     # Run the command "xacro <path to xacro file>" in the terminal, and store the output (the URDF) in a variable called robot_description.

#     node_robot_state_publisher = Node( 
#         package='robot_state_publisher', #Tells ROS to look in the official 'robot_state_publisher' package...
#         executable='robot_state_publisher', #Tells ROS to run the 'robot_state_publisher' program...
#         name='robot_state_publisher', #Tells ROS to name this node 'robot_state_publisher' (this is how other nodes will refer to it)...
#         output='screen', #Tells ROS to print the output (like errors) of this node to the terminal...
#         parameters=[{'robot_description': robot_description}] #Tells ROS to give this node a parameter called 'robot_description', and sets its value to the URDF we generated from the xacro file.
#     )

#     return LaunchDescription([ # Packages up our configured node (and any others we might add later) into a final list.
#         node_robot_state_publisher # Hands the final to-do list back to ROS 2 to actually execute and start the robot!
#     ])

import os

from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.substitutions import Command
from launch_ros.actions import Node
from launch_ros.parameter_descriptions import ParameterValue


def generate_launch_description():

    pkg_path = get_package_share_directory('my_bot')
    xacro_file = os.path.join(pkg_path, 'description', 'robot.urdf.xacro')
    robot_description = ParameterValue(Command(['xacro ', xacro_file]), value_type=str)

    node_robot_state_publisher = Node(
        package='robot_state_publisher',
        executable='robot_state_publisher',
        output='screen',
        parameters=[{'robot_description': robot_description}]
    )

    return LaunchDescription([
        node_robot_state_publisher
    ])