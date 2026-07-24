# Internship Weekly Log: Week 7

**Developer:** Anurag Debnath and Abhilash Ghosh
**Date:** July 15, 2026

---

## Day 1: July 15, 2026

## Robotics — Custom URDF Robot (`my_bot`) with Simulated LIDAR in RViz2 & Gazebo Harmonic

**Hardware (attempted, real):** SLAMTEC RPLIDAR C1 (CP2102N USB-to-UART bridge)
**Environment:** Apple Silicon (M1) Mac, UTM (QEMU), Ubuntu guest, ROS 2 Jazzy, Gazebo Harmonic (`gz sim` v8.11.0)

### ✅ What I Did
 
**1. Built a Custom Single-Package Robot Description (`my_bot`)**
* Followed the Articulated Robotics "How do we add LIDAR to a ROS robot?" workflow, adapted to a simpler single-package layout (rather than a 3-package split) since this is a solo project on one robot.
* Structure created inside `ros2_ws/src/my_bot/`:
  * `description/robot_core.xacro` — chassis (`base_link`, `chassis` box link, materials, inertia).
  * `description/lidar.xacro` — RPLIDAR C1 model (`laser_frame` cylinder link) + Gazebo sensor plugin.
  * `description/inertial_macros.xacro` — reusable box/cylinder/sphere inertia macros.
  * `description/robot.urdf.xacro` — master file combining the above via `xacro:include`.
  * `launch/rsp.launch.py` — robot_state_publisher launch (RViz-ready).
  * `launch/launch_sim.launch.py` — full Gazebo simulation launch (Gazebo + spawn + ROS↔GZ bridge).
  * `worlds/empty.world` — custom SDF world (needed to explicitly declare the `Sensors` system plugin).
  * `config/bridge_parameters.yaml` — explicit `ros_gz_bridge` topic mapping for `/scan`.

**2. RViz2 Visualization — Successful**
* Verified the URDF parses correctly (`check_urdf`), confirmed the 3-link tree: `base_link → chassis → laser_frame`.
* Initial issue: RobotModel display showed nothing despite `Status: Ok`. Root cause was that RViz's **Description Topic** field was not explicitly set to `/robot_description`, even with Description Source correctly set to `Topic`.
* Fix: manually selected `/robot_description` in the Description Topic dropdown — chassis (white box) and LIDAR (black cylinder) rendered correctly.

**3. Gazebo Harmonic Simulation — Robot Spawns Successfully**
* Built `launch_sim.launch.py` reusing `rsp.launch.py`, launching Gazebo via `ros_gz_sim`, and spawning the robot from the live `/robot_description` topic.
* Robot consistently spawns and appears correctly in the Gazebo Entity Tree alongside `ground_plane` and `sun`.

**4. Simulated LIDAR — Extensive Debugging, Eventually Resolved**
* **The Issue:** `/scan` topic existed and had a registered publisher (`ros_gz_bridge`), but produced zero actual messages — `ros2 topic hz /scan` hung indefinitely with `does not appear to be published yet`.
* **Ruled out (in order):** GPU vs CPU rendering, missing `Sensors` system plugin (confirmed loaded via `-v 4` verbose logs), malformed world SDF (a missing closing `</sdf>` tag was found and fixed along the way), `ogre` vs `ogre2` render engine, GUI-vs-headless rendering contention, inline bridge argument syntax vs explicit YAML config (`bridge_parameters.yaml`).
* **Root Cause Found:** A Gazebo warning buried in the log revealed it directly: `Sensor type LIDAR not supported yet. Try using a GPU LIDAR instead.` The sensor's `type="lidar"` (CPU raycasting) is **not implemented** in this Gazebo Harmonic build — it silently registers the topic but never produces data.
* **The Fix:** Switched the sensor definition back to `type="gpu_lidar"`. Once combined with the already-fixed world file (Sensors plugin + `ogre2`) and the YAML-based bridge config, real scan data began publishing immediately — confirmed via `ros2 topic echo /scan --once`, which showed a correctly formed `LaserScan` message (`frame_id: my_bot/base_link/lidar`, full ±π sweep, `range_max: 12.0`) with real (non-infinite) range values where the sensor detected a test obstacle.

**5. Added a Test Obstacle & Confirmed Live Detection**
* Added a static red box (`box_obstacle`) to `empty.world` near the robot's spawn point.
* Confirmed via `ros2 topic echo /scan --once --field ranges | grep -v inf` that the sensor returns real, non-infinite distance values corresponding to the box's position — proving the full pipeline (URDF → Gazebo physics → sensor → `ros_gz_bridge` → ROS 2 topic) works correctly end-to-end.

**6. Added `DiffDrive` Plugin & Keyboard Teleop**
* Added a `gz-sim-diff-drive-system` plugin to `robot_core.xacro`, subscribing to `/cmd_vel`.
* Installed `ros-jazzy-teleop-twist-keyboard` to drive the robot manually.
* **Note for future reference:** my keyboard layout uses **I / J / K / L / M** for movement controls (not the default WASD scheme referenced in most tutorials).
* *(Robot does not yet have wheel links/joints — `DiffDrive` plugin is wired up but has no physical wheels to actuate yet; movement testing is a pending next step.)*

**7. Attempted Real Hardware LIDAR Connection — Unsuccessful Today**
* Attempted to connect the physical SLAMTEC RPLIDAR C1 to the Ubuntu VM to begin real-hardware testing (as a parallel track to the simulation work).
* `ls /dev/ttyUSB*` returned `No such file or directory` — the VM is not detecting the LIDAR's USB-serial bridge.
* Not yet resolved today. Most likely cause (per Week 6 log precedent): USB device needs to be attached via UTM's toolbar *after* the VM has already booted, rather than being connected before/during boot. To be retried and confirmed next session.
<br>

### Folder Structure Explained

```python
ros2_ws/
└── src/
    └── my_bot/
        ├── description/                 <-  What does my robot look like?
        │   ├── robot_core.xacro
        │   ├── lidar.xacro
        │   ├── inertial_macros.xacro
        │   └── robot.urdf.xacro
        ├── launch/                      <- How do I turn it on?
        │   ├── rsp.launch.py
        │   └── launch_sim.launch.py
        ├── worlds/                      <- Where does it exist (in simulation)?
        │   └── empty.world
        ├── CMakeLists.txt
        └── package.xml
```

### 📸 Visual Evidence
<table>
  <tr>
    <td align="center" width="50%" valign="middle">
      <b>1. RViz2 — Robot Model</b><br>
      Custom <code>my_bot</code> URDF (chassis + LIDAR link) rendered correctly via the <code>/robot_description</code> topic.<br><br>
      <img src="./assets/week7_rviz_model.png" width="100%" alt="RViz2 showing the my_bot chassis and LIDAR link">
    </td>
    <td align="center" width="50%" valign="middle">
      <b>2. Gazebo Harmonic — Robot Spawn</b><br>
      <code>my_bot</code> spawned successfully in the Gazebo Entity Tree alongside <code>ground_plane</code> and the test obstacle.<br><br>
      <img src="./assets/week7_gazebo_spawn.png" width="100%" alt="Gazebo Harmonic showing my_bot spawned in the empty world">
    </td>
  </tr>
  <tr>
    <td align="center" width="50%" valign="middle">
      <b>3. Simulated LIDAR — Obstacle Detection</b><br>
      Live <code>/scan</code> data (post <code>gpu_lidar</code> fix) showing non-infinite range values against the test obstacle box.<br><br>
      <img src="./assets/week7_scan_obstacle.png" width="100%" alt="Gazebo/RViz view of LIDAR scan detecting the red obstacle box">
    </td>
    <td align="center" width="50%" valign="middle">
      <b>4. Terminal — Bridge & Debugging</b><br>
      <code>ros2 topic echo /scan --once</code> confirming a correctly formed <code>LaserScan</code> message after the world/sensor/bridge fixes.<br><br>
      <img src="./assets/week7_terminal_scan.png" width="100%" alt="Terminal output showing a valid LaserScan message on /scan">
    </td>
  </tr>
</table>

Video evidence: [Week 7 my_bot driving demo](./assets/week7_my_bot_driving.mp4)

<br>

### 📊 Results

| Metric | Value |
|--------|-------|
| **Package** | `my_bot` (single ROS 2 package) |
| **Simulator** | Gazebo Harmonic (`gz sim` v8.11.0) |
| **Sensor Type (working)** | `gpu_lidar` (`type="lidar"` confirmed unsupported in this build) |
| **Scan Topic** | `/scan` (bridged GZ → ROS 2 via `ros_gz_bridge` + YAML config) |
| **Scan Range** | `range_min: 0.05 m`, `range_max: 12.0 m` |
| **Scan Sweep** | Full 360° (`-π` to `π`) |
| **RViz Visualization** | ✅ Working (chassis + LIDAR render correctly) |
| **Gazebo Spawn** | ✅ Working (robot + obstacle spawn correctly) |
| **Live Obstacle Detection** | ✅ Confirmed (non-infinite ranges match obstacle position) |
| **Real Hardware LIDAR (UTM passthrough)** | ❌ Not detected — `/dev/ttyUSB*` empty, unresolved today |
| **Wheel Actuation** | ⏳ Pending — `DiffDrive` plugin added, no wheel links yet |

<br>

### 🧠 Key Learnings

- **A working topic registration does not mean working data.** `ros2 topic hz` hanging with no output (rather than an error) was the key signal that the sensor was structurally fine but functionally producing nothing — worth checking early rather than assuming a config/bridge problem first.
- **Gazebo will silently accept unsupported SDF values.** `type="lidar"` parsed without any fatal error and only printed a warning (`Sensor type LIDAR not supported yet`) buried among many other startup log lines — a strong reminder to scan *all* warnings in verbose (`-v 4`) logs, not just errors, when a sensor produces no data.
- **Simulation debugging benefits from isolating variables one at a time**: world file correctness, render engine, sensor type, and bridge configuration were each independently verified before the real cause was found — even though this made the process long, it ruled out every alternative explanation with certainty.
- **RViz's "Description Source: Topic" being set does not guarantee "Description Topic" is populated** — this is a separate field that can be silently empty even when the source type looks correctly configured.
- **A missing closing tag (`</sdf>`) can be silently tolerated** by some parsers while still causing unpredictable downstream behavior — worth validating world/URDF files structurally, not just visually.
- **Keyboard teleop tools assume WASD by default** — worth checking/remapping key bindings before assuming a control scheme isn't working.

<br>

### ❌ Issues Faced & Solutions

| Issue | Cause | Solution |
|-------|-------|----------|
| RViz `RobotModel` showed nothing despite `Status: Ok` | `Description Topic` field not explicitly set to `/robot_description` | Manually selected `/robot_description` in the dropdown |
| `/scan` topic existed but never published data | `type="lidar"` (CPU LIDAR) not supported in this Gazebo Harmonic build | Switched sensor to `type="gpu_lidar"` |
| Gazebo process died with `exit code -2` on first launches | Software rendering (`kms_swrast`) instability in the VM, intermittent | Retried launch; not fully deterministic, but resolved once world file + sensor type were both corrected |
| Custom world file loaded but sensors never activated | World SDF was missing a required `gz-sim-sensors-system` plugin declaration | Added explicit `<plugin filename="gz-sim-sensors-system" ...>` block to `empty.world` |
| World file accepted with no error but behaved inconsistently | Missing closing `</sdf>` tag at end of file | Added the missing `</sdf>` closing tag |
| `ros_gz_bridge` inline argument string produced an unclear registration state | Single-string bridge argument syntax | Switched to an explicit `bridge_parameters.yaml` config file for the `/scan` mapping |
| Real RPLIDAR C1 not detected in VM (`/dev/ttyUSB*` empty) | Likely USB not attached via UTM after VM boot (per Week 6 precedent) | Not yet resolved — to retry next session |

<br>

### 📁 Files Created / Modified

- `ros2_ws/src/my_bot/description/robot_core.xacro` — chassis links, materials, inertia, `DiffDrive` Gazebo plugin.
- `ros2_ws/src/my_bot/description/lidar.xacro` — LIDAR link + `gpu_lidar` Gazebo sensor plugin.
- `ros2_ws/src/my_bot/description/inertial_macros.xacro` — reusable inertia macros.
- `ros2_ws/src/my_bot/description/robot.urdf.xacro` — master robot file.
- `ros2_ws/src/my_bot/launch/rsp.launch.py` — robot_state_publisher launch.
- `ros2_ws/src/my_bot/launch/launch_sim.launch.py` — Gazebo simulation launch (Gazebo + spawn + bridge).
- `ros2_ws/src/my_bot/worlds/empty.world` — custom SDF world with explicit `Sensors` plugin + test obstacle.
- `ros2_ws/src/my_bot/config/bridge_parameters.yaml` — `ros_gz_bridge` topic mapping.
- `ros2_ws/src/my_bot/CMakeLists.txt` / `package.xml` — updated install directories and dependencies (`xacro`, `robot_state_publisher`, `ros_gz_sim`, `ros_gz_bridge`).

**Next Steps:**
1. Retry real RPLIDAR C1 USB passthrough in UTM (attach after VM boot, per Week 6 process).
2. Add wheel links/joints so the existing `DiffDrive` plugin has something to actuate; verify keyboard teleop (I/J/K/L/M) actually moves the robot in Gazebo.
3. Once real hardware LIDAR is confirmed working, compare real `/scan` output against the simulated one for consistency.
4. Move toward SLAM Toolbox integration once both simulated and real robot control are functional.

<br>
