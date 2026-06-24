# Internship Weekly Log: Week 3

**Developer:** Anurag Debnath & Abhilash Ghosh \
**Date:** June 18, 2026  

---

## Day 1: June 18, 2026

### Part 1: Intelligent Robotics — SLAMTEC RPLIDAR C1 Integration  
**Hardware:** SLAMTEC RPLIDAR C1  
**Environment:** macOS (M1)

#### ✅ What I Did
1. **Connected RPLIDAR C1 to MacBook:** - Identified the CP2102 chip as the USB-to-UART converter.
   - Located the device at `/dev/cu.SLAB_USBtoUART` on Mac.
   - Configured baud rate to `460800` (different from older RPLIDAR models).
2. **Diagnosed Library Incompatibility:** - Encountered a `Descriptor length mismatch` error using `rplidar-roboticia`. 
   - Determined the library was built for the A1/A2 series, not the C1. Pivoted to raw serial communication.
3. **Decoded RPLIDAR Protocol Manually:**
   - Sent `GET_INFO` command: `0xA5 0x50`.
   - Received a 27-byte response confirming the C1 device.
   - Decoded the 5-byte scan packets (quality, angle_low, angle_high, dist_low, dist_high).
4. **Built Live 2D Visualizer:**
   - Developed a real-time visualization tool using a `matplotlib` polar plot.
   - Configured 3600 slots for a 0.1° angular resolution.
   - Implemented a Plasma colormap (purple=near, yellow=far) and a quality filter to remove noise.
5. **Set Up VS Code Environment:**
   - Created a strict `.venv` isolated environment inside the LiDAR project folder.
   - Installed dependencies: `pyserial`, `matplotlib`, `numpy`.


#### 📸 Visual Evidence

<table>
  <tr>
    <td align="center"><b>1. Numerical Terminal Output</b></td>
    <td align="center"><b>2. Live 2D Polar Plot Visualization</b></td>
  </tr>
  <tr>
    <td align="center"><img src="/Daily_Logs/assets/week3_numerical_data_LiDAR.png" width="400" alt="Terminal output showing numerical data of LiDAR points"></td>
    <td align="center"><img src="/Daily_Logs/assets/week3_matplotlib_2d_LiDAR.png" width="400" alt="Matplotlib polar plot showing the live 2D room scan"></td>
  </tr>
</table>

#### 📊 Results
| Metric | Value |
|--------|-------|
| **Points collected (one session)** | 49,172 |
| **Angular resolution** | 0.1° (3600 slots) |
| **Max range tested** | ~5000mm |
| **Visualization FPS** | ~10 FPS |

#### 🧠 Key Learnings
- **Protocol Shifts:** The RPLIDAR C1 relies on a raw serial protocol, unsupported by common older Python libraries.
- **Environment Management:** Virtual environments (`.venv`) use hardcoded paths and break if moved after creation.
- **System Permissions:** `dmesg` requires `sudo` on Ubuntu, whereas `lsusb` does not.
- **VM Hardware Bridging:** UTM requires manual USB passthrough for serial devices to work.

#### ❌ Issues Faced & Solutions
| Issue | Cause | Solution |
|-------|-------|----------|
| `dmesg: Operation not permitted` | Needs sudo privileges | Ran `sudo dmesg` |
| LiDAR missing from `lsusb` in VM | USB not passed through to VM | Bypassed VM and used Mac Terminal directly |
| `Descriptor length mismatch` | Incompatible library for C1 | Shifted to raw serial at 460800 baud |
| `externally-managed-environment` | macOS pip restriction | Created and activated `.venv` |
| Scattering in visualization | Too few points per frame | Increased to 3600 slots & read all bytes |

#### 📁 Files Created
- [lidar_raw_numerical_data.py](../LiDAR/lidar_raw_numerical_data.py) — Raw LiDAR data stream
- [lidar_2d_visualizer.py](../LiDAR/lidar_2d_visualizer.py) — Optimal live 2D visualizer.

#### 🔜 Next Steps
- [ ] Add obstacle detection (highlight nearest object).
- [ ] Save scan data to CSV.
- [ ] Try mapping a full room.
- [ ] Explore ROS integration.

---

### Part 2: Serverless Web Architecture — Custom HTML Form Integration  
**Task:** Develop a custom HTML frontend form and establish a serverless connection to a Google Sheet database using Google Forms as the backend handler.

#### ✅ What I Did
1. **Frontend Development:** Created a custom user interface using HTML and CSS for a data collection form featuring fields for *Name*, *Roll Number*, and *Address*.
2. **Backend Configuration:** Configured a Google Form to act as a hidden backend endpoint and linked it directly to a Google Sheet.
3. **Endpoint Interception:** Extracted the specific `formResponse` URL from the Google Form to handle incoming `POST` requests.
4. **Data Mapping:** Mapped the custom HTML `<input>` fields to the Google Form's database columns by extracting and assigning the correct `entry.ID` values to the `name` attributes.
5. **Redirection Bypass:** Implemented an `iframe` workaround to intercept the Google Form submission response, preventing default page redirection.

#### 📸 Visual Evidence

<table>
  <tr>
    <td align="center"><b>1. Custom HTML Frontend</b></td>
    <td align="center"><b>2. Hidden Google Form (Backend)</b></td>
    <td align="center"><b>3. Live Google Sheet (Database)</b></td>
  </tr>
  <tr>
    <td align="center"><img src="assets/week3_html_frontend.png" width="260" alt="Custom HTML Form"></td>
    <td align="center"><img src="assets/week3_google_form.png" width="260" alt="Google Form Backend"></td>
    <td align="center"><img src="assets/week3_google_sheet.png" width="260" alt="Google Sheet Database"></td>
  </tr>
</table>

#### 📊 Results
- **Seamless Data Flow:** Successfully submitted user data from a standalone, custom HTML page directly into a designated Google Sheet in real-time.
- **UX Preservation:** Kept the user on the custom webpage post-submission, triggering a local Javascript success alert rather than routing them to the native Google Forms confirmation UI.

#### 🧠 Key Learnings
- **Endpoint Modification:** Changing a Google Form's URL endpoint from `viewform` to `formResponse` allows it to accept external `POST` requests.
- **Data Mapping via Pre-fill:** Google Forms' "pre-filled link" feature exposes hidden `entry.ID` variables (e.g., `entry.205096224`) inside the URL query string, essential for mapping frontend inputs.
- **Redirection Handling:** Setting the form's `target` attribute to a hidden iframe absorbs the cross-origin redirect forced by Google, allowing custom `onload` JavaScript to handle the success state cleanly.

#### ❌ Issues Faced & Solutions
| Issue | Solution |
|-------|----------|
| **Missing Field IDs:** Unable to locate the exact field IDs required to link HTML inputs to the database. | Generated a pre-filled link with dummy data ("TEST"). Analyzed the URL parameters to isolate the exact `entry.ID` numbers corresponding to Name, Roll, and Address. |
| **Forced Redirect:** Submitting data forced a browser redirect to a native Google "Thank You" page, breaking the custom UX. | Implemented a hidden iframe (`<iframe name="hidden_iframe" style="display:none;"></iframe>`) and set the form to target it. Added an `onsubmit` trigger for a local JS alert and page reload. |

#### 📁 Files & Assets Created
- [google_sheet.html](../google_sheet.html) — The frontend file containing the form structure, inline CSS styling, and submission handling scripts.
- **Google Form (Backend Handler)** — Configured to passively receive incoming `POST` requests.
link- https://docs.google.com/forms/d/e/1FAIpQLSey9LJ_Sox9OaQ68d3NkIbKOP22GahAGBNsT5whcQqVpM8iGg/viewform?usp=header
- **Google Sheet (Database)** — Linked to the form to capture and structure all mapped input data.
link- https://docs.google.com/spreadsheets/d/1R5YrLAylg-sIwPQ3gqetaLpbTemMlXkRSD7oacnirao/edit?usp=sharing
