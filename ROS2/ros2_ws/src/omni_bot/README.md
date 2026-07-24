# omni_bot — Simulated 3-Wheel Omni Robot

Simulates the real triangular-chassis, 3-omni-wheel Arduino robot from
your photos, using the same single-package layout style as `my_bot`.

## ⚠️ Assumptions to fix first

The dimensions in `description/robot_core.xacro` are **estimates** from
photos, not real measurements:

| Property | Current guess | Replace with |
|---|---|---|
| `triangle_side` | 0.30 m | Real edge length of your chassis |
| `wall_height` | 0.10 m | Real height of the side panels |
| `wheel_radius` | 0.03 m | Real omni wheel radius |
| `wheel_width` | 0.025 m | Real wheel thickness |

All of these are `xacro:property` values at the top of
`robot_core.xacro` — one place to edit, everything else recalculates
automatically (circumradius, wheel placement, etc).

## Why no per-wheel physics?

Simulating individual omni-wheel roller friction in Gazebo is advanced
and most tutorials skip it. Instead, this uses the **`PlanarMove`**
Gazebo plugin, which reads `/cmd_vel` (a Twist with vx, vy, and
angular.z) and moves the whole robot body directly — no wheel slip
physics, but full holonomic motion (strafing + independent rotation),
which is what actually matters for testing navigation logic.

The real 3-wheel kinematics (how much *each individual wheel* should
spin) are **not** needed for this simulation — but they ARE needed for
the real Arduino robot. That math is worked out separately in
[`OMNI_KINEMATICS.md`](./OMNI_KINEMATICS.md), so it's ready to reuse
once you're back at college with the real hardware.

## Folder structure

Matches `my_bot`'s conventions:
```
omni_bot/
├── description/
│   ├── robot_core.xacro       <- chassis + wheels + PlanarMove plugin
│   ├── inertial_macros.xacro  <- reusable inertia math (copied from my_bot)
│   └── robot.urdf.xacro       <- master file
├── launch/
│   ├── rsp.launch.py          <- robot_state_publisher (for RViz)
│   └── launch_sim.launch.py   <- full Gazebo sim + bridge
├── worlds/
│   └── empty.world
├── CMakeLists.txt
└── package.xml
```

## Setup

1. Copy this whole `omni_bot/` folder into your workspace's `src/`:
   ```bash
   cp -r omni_bot ~/Documents/AI-HCI-LAB-Internship-2026/ROS2/ros2_ws/src/
   ```

2. Build:
   ```bash
   cd ~/Documents/AI-HCI-LAB-Internship-2026/ROS2/ros2_ws
   colcon build --symlink-install --packages-select omni_bot
   source install/setup.bash
   ```

3. Launch:
   ```bash
   ros2 launch omni_bot launch_sim.launch.py
   ```

4. Drive it around (any terminal, holonomic-capable teleop):
   ```bash
   ros2 run teleop_twist_keyboard teleop_twist_keyboard
   ```
   Since this robot can strafe, standard `teleop_twist_keyboard` only
   drives forward/back/rotate by default (WASD-style) — sideways strafe
   needs different keys in that tool (check its help text with `h` once
   it's running) or a joystick. This is fine for a first test; the
   `/cmd_vel` topic itself supports full vx/vy/wz regardless.

5. Visualize in RViz2 (separate terminal):
   ```bash
   rviz2
   ```
   Set **Fixed Frame** to `odom`, add a **RobotModel** display with
   **Description Topic** set to `/robot_description` (same fix as
   `my_bot` — don't forget this dropdown).

## Next steps

- [ ] Measure real chassis dimensions, update the properties in
      `robot_core.xacro`.
- [ ] Confirm sim strafing/rotation looks right via `teleop_twist_keyboard`
      or a keyboard/joystick teleop that exposes vx/vy/wz separately.
- [ ] Once at college: measure `L` and `R` for
      [`OMNI_KINEMATICS.md`](./OMNI_KINEMATICS.md), write the Arduino
      serial-listener sketch using those formulas.
- [ ] Bridge `/cmd_vel` from this same sim (or from Nav2) over serial to
      the real Arduino, so sim motion and real motion happen together.
