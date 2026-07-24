# 3-Wheel Omni Drive — Kinematics Reference

This is the math that converts a desired robot motion `(vx, vy, ω)` into
individual wheel speeds. The simulation doesn't need this (it uses the
`PlanarMove` plugin to move the whole body directly), but **your real
Arduino robot does** — this is the formula you'll put in the Arduino
serial-listener sketch.

## Setup

- `vx` — forward/backward speed (m/s), robot's local +X
- `vy` — sideways/strafe speed (m/s), robot's local +Y
- `ω`  — rotation speed (rad/s), positive = counter-clockwise
- `R`  — wheel radius (m)
- `L`  — distance from robot center to each wheel (m) — the "circumradius"
- `θᵢ` — the mounting angle of wheel `i`, measured from the robot's +X axis

For 3 wheels spaced 120° apart, if wheel 1 is at angle `θ₁`, then:
```
θ₂ = θ₁ + 120°
θ₃ = θ₁ + 240°
```

## The Formula

For a wheel mounted tangentially (standard omni/kiwi drive), the wheel's
angular speed is:

```
ωᵢ = ( -sin(θᵢ) · vx  +  cos(θᵢ) · vy  +  L · ω ) / R
```

Do this once per wheel (i = 1, 2, 3) using each wheel's own `θᵢ`.
`ωᵢ` comes out in **rad/s** — multiply by `60 / (2π)` if your motor
driver wants RPM instead.

## Worked Example (matching this sim's defaults)

Using `wheel_angle_offset = 90°` from `robot_core.xacro`:
```
θ₁ = 90°
θ₂ = 210°
θ₃ = 330°
```

So:
```
ω1 = ( -sin(90°)  · vx + cos(90°)  · vy + L·ω ) / R  =  ( -vx        + L·ω ) / R
ω2 = ( -sin(210°) · vx + cos(210°) · vy + L·ω ) / R  =  ( 0.5·vx - 0.866·vy + L·ω ) / R
ω3 = ( -sin(330°) · vx + cos(330°) · vy + L·ω ) / R  =  ( 0.5·vx + 0.866·vy + L·ω ) / R
```

## Measuring L and R on the real robot

- `R` = radius of one omni wheel, measured with calipers/ruler across
  the wheel (not including the rollers sticking out).
- `L` = distance from the triangle's true geometric center to the
  center of any one wheel's axle. Easiest way: measure the triangle's
  edge length `side`, then:
  ```
  L = side / sqrt(3)   (for an equilateral triangle, circumradius)
  ```

## What changes between sim and real

| | Simulation (`omni_bot`) | Real robot (Arduino) |
|---|---|---|
| Input | `/cmd_vel` (Twist: vx, vy, wz) | Same `/cmd_vel`, relayed over serial |
| Kinematics applied? | No — `PlanarMove` moves the body directly | **Yes** — Arduino must run this formula |
| Output | Whole-body pose in Gazebo | 3 individual PWM/speed values to motor driver |

**Action item once you're at college:** measure your real robot's
`side` (triangle edge length) and wheel radius `R`, plug them into this
sheet, and we'll write the exact Arduino code using these formulas.
