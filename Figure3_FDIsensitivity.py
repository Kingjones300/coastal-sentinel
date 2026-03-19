"""
Figure S1: FDI Threshold Sensitivity Analysis
Coastal Sentinel - Supplementary Information Figure
Generates ROC-style sensitivity plot showing detection rate vs. false-positive
rate across FDI thresholds 0.03-0.08, plus debris area and scene detection curves.
"""

import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec
from matplotlib.patches import FancyArrowPatch, Rectangle
from matplotlib.lines import Line2D

# ── Locked validated data from Table S2 ──────────────────────────────────────
thresholds    = [0.03, 0.04, 0.05, 0.06, 0.07, 0.08]
scs_detections = [1842, 1287, 847,  612,  401,  218]
bob_detections = [1654, 1134, 762,  548,  365,  197]
total_det      = [3496, 2421, 1609, 1160, 766,  415]
scs_area       = [3210, 2640, 1890, 1420, 940,  490]
bob_area       = [2890, 2310, 1650, 1180, 790,  410]

# Estimated false-positive rates (% of detections attributable to sun-glint/foam)
# derived from visual inspection of 50 known debris / non-debris scenes
fp_rate = [0.42, 0.28, 0.09, 0.04, 0.02, 0.01]   # fraction
tp_rate = [0.95, 0.92, 0.88, 0.72, 0.51, 0.29]   # true positive fraction (sensitivity)

# ── Figure layout ─────────────────────────────────────────────────────────────
fig = plt.figure(figsize=(14, 10), facecolor='white')
fig.patch.set_facecolor('white')
gs = gridspec.GridSpec(2, 2, figure=fig, hspace=0.42, wspace=0.38,
                       left=0.09, right=0.97, top=0.91, bottom=0.09)

BLUE   = '#1A4F8A'
ORANGE = '#D4711A'
GREEN  = '#2A7A4B'
GRAY   = '#555555'
SELECT = '#C0392B'
LBLUE  = '#4A90C4'
LORANGE= '#E8A04A'
PANEL_BG = '#F7F9FC'

def style_ax(ax, title):
    ax.set_facecolor(PANEL_BG)
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    ax.spines['left'].set_color('#CCCCCC')
    ax.spines['bottom'].set_color('#CCCCCC')
    ax.tick_params(colors=GRAY, labelsize=9)
    ax.set_title(title, fontsize=10.5, fontweight='bold', color='#1A1A2E', pad=8)
    ax.grid(True, linestyle='--', linewidth=0.5, color='#DDDDDD', alpha=0.8)
    ax.set_axisbelow(True)

def add_selected_line(ax, x_val, label_y_frac=0.92):
    ax.axvline(x=x_val, color=SELECT, linewidth=1.5, linestyle='--', alpha=0.85, zorder=5)
    ymin, ymax = ax.get_ylim()
    y_pos = ymin + (ymax - ymin) * label_y_frac
    ax.text(x_val + 0.003, y_pos, 'Selected\n(0.05)', color=SELECT,
            fontsize=7.5, fontweight='bold', va='top')

# ── Panel A: Detection counts by basin ───────────────────────────────────────
ax1 = fig.add_subplot(gs[0, 0])
style_ax(ax1, '(A) Scene Detection Count by Basin')
ax1.plot(thresholds, scs_detections, 'o-', color=BLUE,   linewidth=2, markersize=7,
         label='SCS', zorder=4)
ax1.plot(thresholds, bob_detections, 's-', color=ORANGE, linewidth=2, markersize=7,
         label='BoB', zorder=4)
ax1.plot(thresholds, total_det,      '^--', color=GREEN, linewidth=1.5, markersize=6,
         label='Total', zorder=3, alpha=0.75)
ax1.scatter([0.05], [scs_detections[2]], s=120, color=SELECT, zorder=6, edgecolors='white', linewidth=1.5)
ax1.scatter([0.05], [bob_detections[2]], s=120, color=SELECT, zorder=6, edgecolors='white', linewidth=1.5)
ax1.set_xlabel('FDI Threshold', fontsize=9, color=GRAY)
ax1.set_ylabel('Scene Detections (n)', fontsize=9, color=GRAY)
ax1.set_xticks(thresholds)
ax1.legend(fontsize=8, framealpha=0.8, loc='upper right')
ax1.set_ylim(0, 4000)
add_selected_line(ax1, 0.05, 0.88)

# ── Panel B: Debris area by basin ────────────────────────────────────────────
ax2 = fig.add_subplot(gs[0, 1])
style_ax(ax2, '(B) Cumulative Debris Area by Basin')
ax2.fill_between(thresholds, scs_area, alpha=0.18, color=BLUE)
ax2.fill_between(thresholds, bob_area, alpha=0.18, color=ORANGE)
ax2.plot(thresholds, scs_area, 'o-', color=BLUE,   linewidth=2, markersize=7, label='SCS')
ax2.plot(thresholds, bob_area, 's-', color=ORANGE, linewidth=2, markersize=7, label='BoB')
ax2.scatter([0.05], [scs_area[2]], s=120, color=SELECT, zorder=6, edgecolors='white', linewidth=1.5)
ax2.scatter([0.05], [bob_area[2]], s=120, color=SELECT, zorder=6, edgecolors='white', linewidth=1.5)
ax2.set_xlabel('FDI Threshold', fontsize=9, color=GRAY)
ax2.set_ylabel('Debris Area (km²)', fontsize=9, color=GRAY)
ax2.set_xticks(thresholds)
ax2.legend(fontsize=8, framealpha=0.8, loc='upper right')
ax2.set_ylim(0, 3800)
add_selected_line(ax2, 0.05, 0.88)

# ── Panel C: ROC-style curve (TPR vs FPR) ────────────────────────────────────
ax3 = fig.add_subplot(gs[1, 0])
style_ax(ax3, '(C) ROC-Style Curve: Sensitivity vs. False-Positive Rate')
# Add random classifier diagonal
ax3.plot([0, 1], [0, 1], '--', color='#AAAAAA', linewidth=1, label='Random classifier', zorder=1)
ax3.plot(fp_rate, tp_rate, 'o-', color=LBLUE, linewidth=2.5, markersize=8, zorder=4,
         label='FDI thresholds (0.03→0.08)')
# Label each point with threshold
for i, (fp, tp, thr) in enumerate(zip(fp_rate, tp_rate, thresholds)):
    offset = (0.015, 0.01) if thr != 0.05 else (0.015, -0.04)
    col = SELECT if thr == 0.05 else GRAY
    ax3.annotate(f'{thr}', (fp, tp), xytext=(fp + offset[0], tp + offset[1]),
                 fontsize=8, color=col, fontweight='bold' if thr == 0.05 else 'normal')
# Highlight selected threshold
ax3.scatter([fp_rate[2]], [tp_rate[2]], s=160, color=SELECT, zorder=6,
            edgecolors='white', linewidth=2, label='Selected: 0.05')
# Shade "good" quadrant
ax3.axvspan(0, 0.15, alpha=0.06, color='green')
ax3.text(0.02, 0.15, 'High specificity\nregion', fontsize=7, color='#2A7A4B', alpha=0.7)
ax3.set_xlabel('False-Positive Rate', fontsize=9, color=GRAY)
ax3.set_ylabel('True-Positive Rate (Sensitivity)', fontsize=9, color=GRAY)
ax3.set_xlim(-0.02, 0.50)
ax3.set_ylim(0.20, 1.02)
ax3.legend(fontsize=8, framealpha=0.8, loc='lower right')

# ── Panel D: Detection efficiency ratio ──────────────────────────────────────
ax4 = fig.add_subplot(gs[1, 1])
style_ax(ax4, '(D) Detection Efficiency (TPR / FPR Ratio)')
efficiency = [tp / max(fp, 0.005) for tp, fp in zip(tp_rate, fp_rate)]
bar_colors = [SELECT if t == 0.05 else LBLUE for t in thresholds]
bars = ax4.bar([str(t) for t in thresholds], efficiency, color=bar_colors,
               edgecolor='white', linewidth=1.2, zorder=4)
ax4.set_xlabel('FDI Threshold', fontsize=9, color=GRAY)
ax4.set_ylabel('TPR / FPR (Efficiency Ratio)', fontsize=9, color=GRAY)
for bar, val in zip(bars, efficiency):
    ax4.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.3,
             f'{val:.1f}', ha='center', va='bottom', fontsize=8, color=GRAY)
ax4.set_ylim(0, max(efficiency) * 1.18)
legend_elements = [
    Line2D([0], [0], marker='s', color='w', markerfacecolor=SELECT, markersize=10, label='Selected (0.05)'),
    Line2D([0], [0], marker='s', color='w', markerfacecolor=LBLUE,  markersize=10, label='Other thresholds'),
]
ax4.legend(handles=legend_elements, fontsize=8, framealpha=0.8)

# ── Main title ────────────────────────────────────────────────────────────────
fig.suptitle(
    'Figure S1. FDI Threshold Sensitivity Analysis (Thresholds 0.03–0.08)\n'
    'Coastal Sentinel | South China Sea & Bay of Bengal | January 2019 – December 2023',
    fontsize=11, fontweight='bold', color='#0D2D5E', y=0.975
)

# ── Save ──────────────────────────────────────────────────────────────────────
plt.savefig('Figure_S1_FDI_Sensitivity.png',  dpi=300, bbox_inches='tight',
            facecolor='white', edgecolor='none')
plt.savefig('Figure_S1_FDI_Sensitivity.tiff', dpi=600, bbox_inches='tight',
            facecolor='white', edgecolor='none')
plt.close()
print("Saved: Figure_S1_FDI_Sensitivity.png (300 dpi) and .tiff (600 dpi)")
