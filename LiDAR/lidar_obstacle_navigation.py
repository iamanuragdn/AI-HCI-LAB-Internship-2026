"""
RPLIDAR C1 — Final Navigation System
NIT Agartala ILAB Internship 2026
Anurag Debnath
"""
import serial, time, numpy as np
import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec
import matplotlib.patches as mpatches
from scipy.spatial import cKDTree

PORT      = '/dev/cu.SLAB_USBtoUART'
BAUD      = 460800
DANGER    = 500
WARNING   = 1000
CAUTION   = 1500
SLOTS     = 3600

dist_history = np.full((SLOTS, 6), np.nan)
hist_idx     = np.zeros(SLOTS, dtype=int)
angles_arr   = np.arange(SLOTS) * (2 * np.pi / SLOTS)

ser = serial.Serial(PORT, BAUD, timeout=0.1)
time.sleep(0.1)
ser.write(b'\xA5\x25')
time.sleep(0.1)
ser.reset_input_buffer()
ser.write(b'\xA5\x20')
time.sleep(0.1)
ser.read(7)

def get_direction(a):
    a = a % 360
    for lo, hi, name in [
        (0,22.5,"FRONT"),(22.5,67.5,"FRONT-RIGHT"),
        (67.5,112.5,"RIGHT"),(112.5,157.5,"BACK-RIGHT"),
        (157.5,202.5,"BACK"),(202.5,247.5,"BACK-LEFT"),
        (247.5,292.5,"LEFT"),(292.5,337.5,"FRONT-LEFT"),
        (337.5,360,"FRONT")]:
        if lo <= a < hi: return name
    return "FRONT"

def find_safe_direction(pa, ds):
    best_a, best_c = 0, 0
    for start in range(0, 360, 15):
        m = ((pa >= start) & (pa < start+15))
        c = np.min(ds[m]) if m.sum() > 0 else 2000
        if c > best_c:
            best_c = c
            best_a = start + 7.5
    return best_a, best_c

def clean_points(xs, ys):
    if len(xs) < 5: return xs, ys
    tree   = cKDTree(np.column_stack((xs, ys)))
    counts = tree.query_ball_point(np.column_stack((xs, ys)),
                                   r=150, return_length=True)
    return xs[counts >= 2], ys[counts >= 2]

# ── Layout ──────────────────────────────────────────────
fig = plt.figure(figsize=(16, 9), facecolor='#050a05')
gs  = gridspec.GridSpec(1, 2, width_ratios=[1.6, 1],
                         wspace=0.04)
ax_map  = fig.add_subplot(gs[0], facecolor='#050a05')
ax_info = fig.add_subplot(gs[1], facecolor='#070d07')
plt.ion()

# ── Header bar ──────────────────────────────────────────
fig.text(0.5, 0.97,
         'RPLIDAR C1  ·  Obstacle Navigation System  ·  NIT Agartala ILAB',
         color='#3a8a3a', fontsize=11, ha='center', va='top',
         fontweight='bold')

print("Final Navigation System started.")
print("GREEN ARROW = safest direction.  Press Ctrl+C to save + exit.\n")

try:
    frame = 0
    while True:
        waiting = ser.in_waiting
        if waiting < 5:
            time.sleep(0.01)
            continue

        n = (min(waiting, 10000) // 5) * 5
        raw   = ser.read(n)

        for i in range(0, len(raw)-4, 5):
            b0,b1,b2,b3,b4 = raw[i:i+5]
            angle    = ((b1|(b2<<8))>>1) / 64.0
            distance = (b3|(b4<<8)) / 4.0
            quality  = b0 >> 2
            if 0 < distance < 6000 and quality > 12:
                idx = int(angle*10) % SLOTS
                dist_history[idx, hist_idx[idx]] = distance
                hist_idx[idx] = (hist_idx[idx]+1) % 6

        if frame % 3 == 0:
            dists = np.nanmedian(dist_history, axis=1)
            mask  = ~np.isnan(dists)

            if mask.sum() > 10:
                xs = dists[mask] * np.cos(angles_arr[mask])
                ys = dists[mask] * np.sin(angles_arr[mask])
                xs, ys = clean_points(xs, ys)
                ds = np.sqrt(xs**2 + ys**2)
                pa = np.degrees(np.arctan2(ys, xs)) % 360

                safe_angle, safe_clear = find_safe_direction(pa, ds)
                safe_rad = np.radians(safe_angle)
                min_idx  = np.argmin(ds)
                min_dist = ds[min_idx]
                min_dir  = get_direction(pa[min_idx])

                n_danger  = int(np.sum(ds < DANGER))
                n_warning = int(np.sum((ds >= DANGER)  & (ds < WARNING)))
                n_caution = int(np.sum((ds >= WARNING) & (ds < CAUTION)))
                n_safe    = int(np.sum(ds >= CAUTION))

                colors = np.where(ds < DANGER,  '#ff2020',
                         np.where(ds < WARNING, '#ff8c00',
                         np.where(ds < CAUTION, '#ffd700', '#39ff14')))
                sizes  = np.where(ds < DANGER,  14,
                         np.where(ds < WARNING,   8,
                         np.where(ds < CAUTION,   4, 2)))

                # ════════════════════════════════
                # LEFT — MAP
                # ════════════════════════════════
                ax_map.clear()
                ax_map.set_facecolor('#050a05')

                # Zone fills
                for r, c in [(DANGER,'#ff202018'),
                              (WARNING,'#ff8c0010'),
                              (CAUTION,'#ffd70008')]:
                    ax_map.add_patch(plt.Circle((0,0),r,
                        color=c,fill=True,zorder=1))
                    ax_map.add_patch(plt.Circle((0,0),r,
                        color=c.replace('18','55').replace('10','44').replace('08','33'),
                        fill=False,linewidth=1,zorder=1))

                # Range rings
                for r in [500,1000,1500,2000,2500,3000]:
                    ax_map.add_patch(plt.Circle((0,0),r,
                        color='#0d2a0d',fill=False,
                        linewidth=0.5,linestyle='--'))
                    ax_map.text(r+40,40,f'{r/1000:.1f}m',
                                color='#1a4a1a',fontsize=6.5)

                # Safe cone
                cone_w = np.radians(40)
                ca     = np.linspace(safe_rad-cone_w/2,
                                     safe_rad+cone_w/2, 50)
                cr     = min(safe_clear*0.85, 3000)
                cx     = np.concatenate([[0], cr*np.cos(ca), [0]])
                cy     = np.concatenate([[0], cr*np.sin(ca), [0]])
                ax_map.fill(cx, cy, color='#39ff14',
                            alpha=0.13, zorder=2)
                ax_map.plot(cx, cy, color='#39ff1444',
                            linewidth=0.8, zorder=2)

                # Crosshair + cardinals
                ax_map.axhline(0,color='#0d2a0d',linewidth=0.4)
                ax_map.axvline(0,color='#0d2a0d',linewidth=0.4)
                for deg,lbl in [(90,'N'),(270,'S'),(0,'E'),(180,'W')]:
                    a = np.radians(deg)
                    ax_map.text(3300*np.cos(a),3300*np.sin(a),lbl,
                                color='#2a6a2a',fontsize=9,
                                ha='center',va='center',
                                fontweight='bold')

                # Points
                ax_map.scatter(xs,ys,s=sizes,c=colors,
                               alpha=0.95,linewidths=0,zorder=3)

                # GO arrow
                al = min(safe_clear*0.75, 2800)
                ax_map.annotate('',
                    xy=(al*np.cos(safe_rad), al*np.sin(safe_rad)),
                    xytext=(0,0),
                    arrowprops=dict(arrowstyle='->',
                        color='#39ff14',lw=3,
                        mutation_scale=28))
                lx = (al+260)*np.cos(safe_rad)
                ly = (al+260)*np.sin(safe_rad)
                ax_map.text(lx,ly,
                    f'GO\n{safe_clear/1000:.1f}m',
                    color='#39ff14',fontsize=10,
                    ha='center',va='center',
                    fontweight='bold',
                    bbox=dict(boxstyle='round,pad=0.4',
                              facecolor='#050a05',
                              edgecolor='#39ff14',lw=1.5))

                # Danger arrow
                if min_dist < WARNING:
                    da = np.radians(pa[min_idx])
                    ax_map.annotate('',
                        xy=(min_dist*0.65*np.cos(da),
                            min_dist*0.65*np.sin(da)),
                        xytext=(0,0),
                        arrowprops=dict(arrowstyle='->',
                            color='#ff2020',lw=2,
                            mutation_scale=18))

                # Origin
                ax_map.plot(0,0,'o',color='#ffffff',
                            markersize=12,zorder=6)
                ax_map.plot(0,0,'o',color='#ff4444',
                            markersize=6,zorder=7)

                # Title
                if   min_dist < DANGER:
                    tc='#ff2020'; tt=f'⚠  DANGER — {min_dir}  ({min_dist/1000:.2f}m)'
                elif min_dist < WARNING:
                    tc='#ff8c00'; tt=f'⚡  WARNING — {min_dir}  ({min_dist/1000:.2f}m)'
                elif min_dist < CAUTION:
                    tc='#ffd700'; tt=f'◈  CAUTION — {min_dir}  ({min_dist/1000:.2f}m)'
                else:
                    tc='#39ff14'; tt=f'✓  CLEAR — nearest {min_dist/1000:.2f}m'

                ax_map.set_title(tt,color=tc,fontsize=14,
                                 fontweight='bold',pad=10)
                ax_map.text(0,-3600,
                    f'▲ Safest: {get_direction(safe_angle)}'
                    f'  ({safe_clear/1000:.1f}m)',
                    color='#39ff14',fontsize=11,
                    ha='center',va='top',fontweight='bold')

                ax_map.set_aspect('equal')
                ax_map.set_xlim(-3700,3700)
                ax_map.set_ylim(-3800,3700)
                ax_map.tick_params(colors='#1a4a1a',labelsize=7)
                for sp in ax_map.spines.values():
                    sp.set_edgecolor('#0d2a0d')

                # ════════════════════════════════
                # RIGHT — INFO PANEL
                # ════════════════════════════════
                ax_info.clear()
                ax_info.set_xlim(0,10)
                ax_info.set_ylim(0,10)
                ax_info.axis('off')
                ax_info.set_facecolor('#070d07')

                # Section: Zone stats
                ax_info.text(5,9.7,'Zone Statistics',
                             color='#5aff5a',fontsize=12,
                             ha='center',va='top',fontweight='bold')

                y = 9.1
                for count, label, color, rng in [
                    (n_danger,  'DANGER',  '#ff2020', '< 0.5m'),
                    (n_warning, 'WARNING', '#ff8c00', '0.5–1.0m'),
                    (n_caution, 'CAUTION', '#ffd700', '1.0–1.5m'),
                    (n_safe,    'SAFE',    '#39ff14', '> 1.5m'),
                ]:
                    # Bar
                    bar_w = min(count/25, 7.5)
                    ax_info.barh(y, bar_w, height=0.38,
                                 left=1.2, color=color, alpha=0.75)
                    # Zone label
                    ax_info.text(1.0, y, label,
                                 color=color, fontsize=9,
                                 ha='right', va='center',
                                 fontweight='bold')
                    # Range
                    ax_info.text(1.3, y-0.24, rng,
                                 color=color, fontsize=7,
                                 ha='left', va='center', alpha=0.7)
                    # Count
                    ax_info.text(1.2+bar_w+0.2, y, str(count),
                                 color=color, fontsize=9,
                                 va='center', fontweight='bold')
                    y -= 0.78

                # Divider
                y -= 0.1
                ax_info.plot([0.5, 9.5], [y, y],
                             color='#1a3a1a', linewidth=0.8)
                y -= 0.35

                # Section: Closest obstacle
                ax_info.text(5, y, 'Closest Obstacle',
                             color='#5aff5a', fontsize=11,
                             ha='center', va='top', fontweight='bold')
                y -= 0.55
                ax_info.text(5, y,
                    f'{min_dist/1000:.2f} m  —  {min_dir}',
                    color=tc, fontsize=13,
                    ha='center', va='top', fontweight='bold')
                y -= 0.55
                ax_info.text(5, y,
                    f'Total scan points: {len(ds)}',
                    color='#3a6a3a', fontsize=9,
                    ha='center', va='top')

                # Divider
                y -= 0.45
                ax_info.plot([0.5,9.5],[y,y],
                             color='#1a3a1a',linewidth=0.8)
                y -= 0.35

                # Section: Active alerts
                ax_info.text(5, y, 'Active Alerts',
                             color='#5aff5a', fontsize=11,
                             ha='center', va='top', fontweight='bold')
                y -= 0.55

                alerted = False
                for threshold, color, prefix in [
                    (DANGER,  '#ff2020', '⛔  DANGER'),
                    (WARNING, '#ff8c00', '⚡  WARNING'),
                    (CAUTION, '#ffd700', '◈  CAUTION'),
                ]:
                    dirs = list(set([
                        get_direction(a)
                        for a in pa[ds < threshold]
                    ]))
                    for d in dirs[:3]:
                        ax_info.text(5, y,
                            f'{prefix}  →  {d}',
                            color=color, fontsize=10,
                            ha='center', va='top',
                            fontweight='bold' if threshold==DANGER else 'normal')
                        y -= 0.5
                        alerted = True
                    if alerted and threshold == DANGER:
                        break

                if not alerted:
                    ax_info.text(5, y, '✓  All clear',
                                 color='#39ff14', fontsize=13,
                                 ha='center', va='top',
                                 fontweight='bold')
                    y -= 0.5

                # Divider
                y -= 0.3
                ax_info.plot([0.5,9.5],[y,y],
                             color='#1a3a1a',linewidth=0.8)
                y -= 0.35

                # Section: Safe path
                ax_info.text(5, y, 'Safe Path',
                             color='#5aff5a', fontsize=11,
                             ha='center', va='top', fontweight='bold')
                y -= 0.55
                safe_color = ('#ff2020' if safe_clear < DANGER else
                              '#ff8c00' if safe_clear < WARNING else
                              '#ffd700' if safe_clear < CAUTION else
                              '#39ff14')
                ax_info.text(5, y,
                    f'▲  {get_direction(safe_angle)}',
                    color='#39ff14', fontsize=14,
                    ha='center', va='top', fontweight='bold')
                y -= 0.55
                ax_info.text(5, y,
                    f'Clearance: {safe_clear/1000:.2f} m',
                    color=safe_color, fontsize=11,
                    ha='center', va='top')

                # Legend at bottom
                for lx2, ly2, lc, ll in [
                    (1.0,0.8,'#ff2020','< 0.5m  DANGER'),
                    (1.0,0.4,'#ff8c00','< 1.0m  WARNING'),
                    (5.5,0.8,'#ffd700','< 1.5m  CAUTION'),
                    (5.5,0.4,'#39ff14','> 1.5m  SAFE'),
                ]:
                    ax_info.plot(lx2, ly2,'s',
                                 color=lc,markersize=7,alpha=0.8)
                    ax_info.text(lx2+0.3, ly2, ll,
                                 color=lc,fontsize=8,va='center')

                plt.pause(0.001)

        frame += 1

except KeyboardInterrupt:
    plt.savefig('lidar_final.png',
                facecolor='#050a05',dpi=200,
                bbox_inches='tight')
    print("\nSaved lidar_final.png ✅")
finally:
    ser.write(b'\xA5\x25')
    ser.close()
