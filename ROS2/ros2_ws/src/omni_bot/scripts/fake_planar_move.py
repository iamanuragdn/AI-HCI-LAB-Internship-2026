#!/usr/bin/env python3
"""
fake_planar_move.py

Your installed Gazebo Harmonic build doesn't ship the `PlanarMove`
system plugin (confirmed: "Failed to load system plugin
[gz-sim-planar-move-system] : Could not find shared library.").

This node does the same job in plain Python/ROS 2 instead:
  1. Subscribes to /cmd_vel (geometry_msgs/Twist)
  2. Integrates (vx, vy, wz) into an (x, y, yaw) pose over time
  3. Calls Gazebo's `/world/<world>/set_pose` service to move the
     model directly to that pose every tick.

This is a stand-in for the missing plugin — not as smooth/high-rate
as a native C++ system, but functionally equivalent for testing
navigation logic in sim.
"""

import math
import subprocess
import time

import rclpy
from rclpy.node import Node
from geometry_msgs.msg import Twist, TransformStamped
from nav_msgs.msg import Odometry
from tf2_ros import TransformBroadcaster


class FakePlanarMove(Node):
    def __init__(self):
        super().__init__('fake_planar_move')

        self.declare_parameter('world_name', 'empty')
        self.declare_parameter('model_name', 'omni_bot')
        self.declare_parameter('update_rate_hz', 12.0)
        self.declare_parameter('z_height', 0.055)
        self.declare_parameter('odom_frame', 'odom')
        self.declare_parameter('base_frame', 'base_link')

        self.world_name = self.get_parameter('world_name').value
        self.model_name = self.get_parameter('model_name').value
        rate_hz = self.get_parameter('update_rate_hz').value
        self.z_height = self.get_parameter('z_height').value
        self.odom_frame = self.get_parameter('odom_frame').value
        self.base_frame = self.get_parameter('base_frame').value

        self.x = 0.0
        self.y = 0.0
        self.yaw = 0.0
        self.vx = 0.0
        self.vy = 0.0
        self.wz = 0.0

        self.last_time = time.monotonic()
        self.pending_proc = None  # tracks an in-flight (non-blocking) pose-set call

        self.odom_pub = self.create_publisher(Odometry, '/odom', 10)
        self.tf_broadcaster = TransformBroadcaster(self)

        self.create_subscription(Twist, '/cmd_vel', self.cmd_vel_cb, 10)
        self.timer = self.create_timer(1.0 / rate_hz, self.update)

        self.get_logger().info(
            f"fake_planar_move running for model '{self.model_name}' "
            f"in world '{self.world_name}' at {rate_hz} Hz "
            "(stand-in for the unavailable PlanarMove plugin)"
        )

    def cmd_vel_cb(self, msg: Twist):
        self.vx = msg.linear.x
        self.vy = msg.linear.y
        self.wz = msg.angular.z

    def update(self):
        now = time.monotonic()
        dt = now - self.last_time
        self.last_time = now

        # Integrate body-frame (vx, vy) into world-frame x,y using current yaw
        self.x += (self.vx * math.cos(self.yaw) - self.vy * math.sin(self.yaw)) * dt
        self.y += (self.vx * math.sin(self.yaw) + self.vy * math.cos(self.yaw)) * dt
        self.yaw += self.wz * dt

        qz = math.sin(self.yaw / 2.0)
        qw = math.cos(self.yaw / 2.0)

        req = (
            f"name: '{self.model_name}' "
            f"position: {{x: {self.x:.5f}, y: {self.y:.5f}, z: {self.z_height:.5f}}} "
            f"orientation: {{x: 0, y: 0, z: {qz:.5f}, w: {qw:.5f}}}"
        )

        # --- Non-blocking pose update ---
        # Previously this used subprocess.run() (blocking) and waited for
        # each "gz service" call to fully complete — a fresh process every
        # tick, each paying a real discovery/connection cost (~50-150ms).
        # At 20Hz that regularly exceeded the 50ms tick budget, causing
        # skipped/delayed updates (the choppiness you saw).
        #
        # Fix: fire the call with Popen and DON'T wait for it. If a
        # previous call from an earlier tick hasn't finished yet, skip
        # this tick entirely rather than piling up overlapping processes
        # (which was likely making things worse, not better).
        if self.pending_proc is not None and self.pending_proc.poll() is None:
            # previous call still running — skip this tick, don't stack up
            self.publish_odom_and_tf(qz, qw)
            return

        self.pending_proc = subprocess.Popen(
            [
                'gz', 'service', '-s', f'/world/{self.world_name}/set_pose',
                '--reqtype', 'gz.msgs.Pose',
                '--reptype', 'gz.msgs.Boolean',
                '--timeout', '200',
                '--req', req,
            ],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
        )

        self.publish_odom_and_tf(qz, qw)

    def publish_odom_and_tf(self, qz, qw):
        now = self.get_clock().now().to_msg()

        odom = Odometry()
        odom.header.stamp = now
        odom.header.frame_id = self.odom_frame
        odom.child_frame_id = self.base_frame
        odom.pose.pose.position.x = self.x
        odom.pose.pose.position.y = self.y
        odom.pose.pose.position.z = self.z_height
        odom.pose.pose.orientation.z = qz
        odom.pose.pose.orientation.w = qw
        odom.twist.twist.linear.x = self.vx
        odom.twist.twist.linear.y = self.vy
        odom.twist.twist.angular.z = self.wz
        self.odom_pub.publish(odom)

        t = TransformStamped()
        t.header.stamp = now
        t.header.frame_id = self.odom_frame
        t.child_frame_id = self.base_frame
        t.transform.translation.x = self.x
        t.transform.translation.y = self.y
        t.transform.translation.z = self.z_height
        t.transform.rotation.z = qz
        t.transform.rotation.w = qw
        self.tf_broadcaster.sendTransform(t)


def main():
    rclpy.init()
    node = FakePlanarMove()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        rclpy.shutdown()


if __name__ == '__main__':
    main()