"""
=============================================================================
PhD Paper 2 — Script P2_02: Learning Trajectory Classification (RQ2)
Uncovering Learning Patterns and Behavioral Trajectories in Continuous
Assessment Beyond Average Performance
Author  : Mariyan J Rooban
College : Kristu Jayanti College, Bengaluru
Date    : March 2026
=============================================================================

RESEARCH QUESTION:
  RQ2 — What learning trajectories do students follow across the semester in
         their continuous assessment performance, and how prevalent is each
         trajectory type?

METHODOLOGY:
  Trajectory computation:
    - For each student-course, fit a linear regression on percentage_score
      (0–100 scale) ordered by attempt_start (chronological quiz sequence)
    - Slope = rate of change per quiz across the semester
    - Minimum 3 quizzes required for meaningful trajectory analysis

  Slope threshold (data-driven, mean ± 1 SD):
    - Compute slope for all eligible students
    - Improver  : slope > (mean_slope + 1 SD)
    - Decliner  : slope < (mean_slope − 1 SD)
    - Stable    : slope within mean_slope ± 1 SD

  Trajectory classification (avg score + slope combination):
    ┌─────────────────────────┬──────────────────┬────────────────┐
    │ Trajectory              │ Avg Score        │ Slope          │
    ├─────────────────────────┼──────────────────┼────────────────┤
    │ Steady High Performer   │ ≥ 60.0           │ Stable         │
    │ Stable Average          │ 40.0 – 59.99     │ Stable         │
    │ Consistently Struggling │ < 40.0           │ Stable         │
    │ Improver                │ Any              │ > mean + 1 SD  │
    │ Decliner                │ Any              │ < mean − 1 SD  │
    └─────────────────────────┴──────────────────┴────────────────┘
    NOTE: Slope takes priority — Improver/Decliner override stable categories.

ELIGIBILITY:
  Students with < 3 quizzes are EXCLUDED from trajectory analysis (RQ2)
  but remain in engagement profile analysis (RQ1).

INPUTS:
  data/processed/students_clean.csv
  data/processed/quizzes_clean.csv
  data/processed/paper2/engagement_profiles.csv  (from P2_01)

OUTPUTS:
  data/processed/paper2/learning_trajectories.csv  — eligible students only
  data/processed/paper2/student_profiles_master.csv — merged RQ1+RQ2+ESE
                                                       (input for RQ3 & RQ4)
  results/paper2/rq2_trajectory_distribution.csv
  results/paper2/rq2_slope_thresholds.csv
  results/paper2/figures/rq2_slope_distribution.png
  results/paper2/figures/rq2_trajectory_distribution.png
  results/paper2/figures/rq2_trajectory_score_progression.png
=============================================================================
"""

import pandas as pd
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import seaborn as sns
from pathlib import Path
from datetime import datetime
from scipy import stats
import warnings
warnings.filterwarnings('ignore')

pd.set_option('display.max_columns', None)
pd.set_option('display.float_format', '{:.4f}'.format)

# ── PATHS ─────────────────────────────────────────────────────────────────────
PROJECT_ROOT = Path(__file__).parent
DATA_PROCESSED  = PROJECT_ROOT / "data" / "processed"
P2_PROCESSED    = DATA_PROCESSED / "paper2"
P2_RESULTS      = PROJECT_ROOT / "results" / "paper2"
P2_FIGURES      = P2_RESULTS / "figures"

for d in [P2_PROCESSED, P2_RESULTS, P2_FIGURES]:
    d.mkdir(parents=True, exist_ok=True)

START_TIME = datetime.now()

print("=" * 80)
print("PAPER 2 — SCRIPT P2_02 : LEARNING TRAJECTORY CLASSIFICATION  (RQ2)")
print(f"Started : {START_TIME.strftime('%Y-%m-%d %H:%M:%S')}")
print("=" * 80)

# ─────────────────────────────────────────────────────────────────────────────
# STEP 1 — LOAD DATA
# ─────────────────────────────────────────────────────────────────────────────
print("\n[STEP 1] LOADING DATA")
print("-" * 80)

required = {
    'students'   : DATA_PROCESSED / 'students_clean.csv',
    'quizzes'    : DATA_PROCESSED / 'quizzes_clean.csv',
    'engagement' : P2_PROCESSED   / 'engagement_profiles.csv',
}

missing = [k for k, v in required.items() if not v.exists()]
if missing:
    print(f"\n  ERROR: Missing files: {missing}")
    if 'engagement' in missing:
        print("  Please run P2_01_engagement_profiles.py first.")
    exit(1)

s = pd.read_csv(required['students'],   low_memory=False)
q = pd.read_csv(required['quizzes'],    low_memory=False)
ep = pd.read_csv(required['engagement'], low_memory=False)

print(f"  students_clean        : {len(s):>7,} rows")
print(f"  quizzes_clean         : {len(q):>7,} rows")
print(f"  engagement_profiles   : {len(ep):>7,} rows")

# Parse dates and sort chronologically
q['attempt_start'] = pd.to_datetime(q['attempt_start'], errors='coerce')
q = q.sort_values(['student_id', 'course_id', 'attempt_start']).reset_index(drop=True)

# ─────────────────────────────────────────────────────────────────────────────
# STEP 2 — FILTER: MINIMUM 3 QUIZZES
# ─────────────────────────────────────────────────────────────────────────────
print("\n[STEP 2] FILTERING — MINIMUM 3 QUIZZES")
print("-" * 80)

MIN_QUIZZES = 3

quiz_counts = (
    q.groupby(['student_id', 'course_id'])
     .size()
     .reset_index(name='quiz_count')
)

eligible = quiz_counts[quiz_counts['quiz_count'] >= MIN_QUIZZES].copy()
ineligible = quiz_counts[quiz_counts['quiz_count'] < MIN_QUIZZES].copy()

print(f"  Total student-course pairs with quizzes : {len(quiz_counts):,}")
print(f"  Eligible   (≥ {MIN_QUIZZES} quizzes)          : {len(eligible):,} "
      f"({len(eligible)/len(quiz_counts)*100:.1f}%)")
print(f"  Ineligible (< {MIN_QUIZZES} quizzes)          : {len(ineligible):,} "
      f"({len(ineligible)/len(quiz_counts)*100:.1f}%)")
print(f"  NOTE: Ineligible pairs remain in RQ1 (engagement profiles)")
print(f"        but are excluded from RQ2 (trajectory analysis)")

# Filter quiz data to eligible pairs only
eligible_set = set(zip(eligible['student_id'], eligible['course_id']))
q_elig = q[q.apply(lambda r: (r['student_id'], r['course_id']) in eligible_set, axis=1)].copy()

# ─────────────────────────────────────────────────────────────────────────────
# STEP 3 — COMPUTE LINEAR REGRESSION SLOPE PER STUDENT-COURSE
# ─────────────────────────────────────────────────────────────────────────────
print("\n[STEP 3] COMPUTING TRAJECTORY SLOPES (Linear Regression)")
print("-" * 80)
print(f"  Method : OLS linear regression of percentage_score vs quiz_sequence")
print(f"  Scale  : percentage_score is 0–100")
print(f"  Sequence : chronological order by attempt_start")

trajectory_list = []

for (sid, cid), grp in q_elig.groupby(['student_id', 'course_id']):
    scores = grp['percentage_score'].values
    n      = len(scores)

    # Quiz sequence: 1, 2, 3, ...
    seq = np.arange(1, n + 1)

    # Linear regression: slope of score vs quiz sequence
    slope, intercept, r_value, p_value, std_err = stats.linregress(seq, scores)

    avg_score = scores.mean()

    trajectory_list.append({
        'student_id'         : sid,
        'course_id'          : cid,
        'quiz_count'         : n,
        'avg_score'          : round(avg_score, 4),
        'slope'              : round(slope, 6),
        'intercept'          : round(intercept, 4),
        'r_squared'          : round(r_value**2, 4),
        'p_value_slope'      : round(p_value, 6),
        'score_sequence'     : ','.join([str(round(x, 2)) for x in scores]),
    })

traj_df = pd.DataFrame(trajectory_list)

print(f"\n  Trajectories computed : {len(traj_df):,}")
print(f"  Slope statistics (raw, before thresholding):")
print(f"    Mean   : {traj_df['slope'].mean():.4f}")
print(f"    Median : {traj_df['slope'].median():.4f}")
print(f"    Std    : {traj_df['slope'].std():.4f}")
print(f"    Min    : {traj_df['slope'].min():.4f}")
print(f"    Max    : {traj_df['slope'].max():.4f}")

# ─────────────────────────────────────────────────────────────────────────────
# STEP 4 — COMPUTE DATA-DRIVEN SLOPE THRESHOLDS (mean ± 1 SD)
# ─────────────────────────────────────────────────────────────────────────────
print("\n[STEP 4] COMPUTING SLOPE THRESHOLDS (Data-Driven: mean ± 1 SD)")
print("-" * 80)

mean_slope = traj_df['slope'].mean()
std_slope  = traj_df['slope'].std()

IMPROVER_THRESHOLD = mean_slope + std_slope
DECLINER_THRESHOLD = mean_slope - std_slope

print(f"  Mean slope           : {mean_slope:+.4f}")
print(f"  Std of slopes        : {std_slope:.4f}")
print(f"  Improver threshold   : slope > {IMPROVER_THRESHOLD:+.4f}  (mean + 1 SD)")
print(f"  Decliner threshold   : slope < {DECLINER_THRESHOLD:+.4f}  (mean − 1 SD)")
print(f"  Stable range         : {DECLINER_THRESHOLD:+.4f} to {IMPROVER_THRESHOLD:+.4f}")

# Save thresholds for methodological transparency
thresh_df = pd.DataFrame({
    'parameter'   : ['mean_slope', 'std_slope', 'improver_threshold',
                     'decliner_threshold', 'stable_lower', 'stable_upper',
                     'min_quizzes_required'],
    'value'       : [mean_slope, std_slope, IMPROVER_THRESHOLD,
                     DECLINER_THRESHOLD, DECLINER_THRESHOLD, IMPROVER_THRESHOLD,
                     MIN_QUIZZES],
    'description' : [
        'Mean slope across all eligible student-course pairs',
        'Standard deviation of slopes',
        'Threshold above which student is classified as Improver (mean + 1 SD)',
        'Threshold below which student is classified as Decliner (mean − 1 SD)',
        'Lower bound of Stable range',
        'Upper bound of Stable range',
        'Minimum quizzes required for trajectory analysis',
    ]
})
thresh_df.to_csv(P2_RESULTS / 'rq2_slope_thresholds.csv', index=False)
print(f"\n  Thresholds saved to rq2_slope_thresholds.csv")

# ─────────────────────────────────────────────────────────────────────────────
# STEP 5 — CLASSIFY TRAJECTORIES
# ─────────────────────────────────────────────────────────────────────────────
print("\n[STEP 5] CLASSIFYING LEARNING TRAJECTORIES")
print("-" * 80)
print("  Classification rules (slope takes priority over avg score):")
print("  ┌─────────────────────────┬──────────────────┬──────────────────────┐")
print("  │ Trajectory              │ Avg Score        │ Slope                │")
print("  ├─────────────────────────┼──────────────────┼──────────────────────┤")
print("  │ Steady High Performer   │ ≥ 60             │ Stable               │")
print("  │ Stable Average          │ 40–59.99         │ Stable               │")
print("  │ Consistently Struggling │ < 40             │ Stable               │")
print("  │ Improver                │ Any              │ > mean + 1 SD        │")
print("  │ Decliner                │ Any              │ < mean − 1 SD        │")
print("  └─────────────────────────┴──────────────────┴──────────────────────┘")

def classify_trajectory(row):
    slope     = row['slope']
    avg_score = row['avg_score']

    # Slope takes priority
    if slope > IMPROVER_THRESHOLD:
        return 'Improver'
    elif slope < DECLINER_THRESHOLD:
        return 'Decliner'
    else:
        # Stable — classify by average score level
        if avg_score >= 60.0:
            return 'Steady High Performer'
        elif avg_score >= 40.0:
            return 'Stable Average'
        else:
            return 'Consistently Struggling'

traj_df['trajectory_label'] = traj_df.apply(classify_trajectory, axis=1)

# Ordered category
TRAJ_ORDER = [
    'Steady High Performer',
    'Stable Average',
    'Improver',
    'Decliner',
    'Consistently Struggling'
]
traj_df['trajectory_label'] = pd.Categorical(
    traj_df['trajectory_label'],
    categories=TRAJ_ORDER,
    ordered=True
)

# ─────────────────────────────────────────────────────────────────────────────
# STEP 6 — TRAJECTORY DISTRIBUTION (answers RQ2)
# ─────────────────────────────────────────────────────────────────────────────
print("\n[STEP 6] TRAJECTORY DISTRIBUTION — RQ2 ANSWER")
print("-" * 80)

total_elig = len(traj_df)

traj_dist = (
    traj_df.groupby('trajectory_label', observed=True)
           .agg(
               n              = ('student_id', 'count'),
               mean_avg_score = ('avg_score', 'mean'),
               mean_slope     = ('slope', 'mean'),
               median_slope   = ('slope', 'median'),
           )
           .reset_index()
)
traj_dist['pct'] = (traj_dist['n'] / total_elig * 100).round(2)

# Merge ESE for preliminary view
traj_with_ese = traj_df.merge(
    s[['student_id', 'course_id', 'ese_percentage']].drop_duplicates(),
    on=['student_id', 'course_id'], how='left'
)
ese_by_traj = (
    traj_with_ese.groupby('trajectory_label', observed=True)['ese_percentage']
                 .mean().reset_index().rename(columns={'ese_percentage': 'mean_ese_pct'})
)
traj_dist = traj_dist.merge(ese_by_traj, on='trajectory_label')

print(f"\n  Total eligible student-course pairs : {total_elig:,}")
print(f"\n  {'Trajectory':<26} {'n':>6} {'%':>7}  {'Avg Score':>10}  "
      f"{'Mean Slope':>11}  {'Mean ESE%':>10}")
print(f"  {'-'*78}")
for _, row in traj_dist.iterrows():
    print(f"  {str(row['trajectory_label']):<26} {int(row['n']):>6} {row['pct']:>6.1f}%  "
          f"{row['mean_avg_score']:>10.2f}  {row['mean_slope']:>+11.4f}  "
          f"{row['mean_ese_pct']:>10.2f}")

# ─────────────────────────────────────────────────────────────────────────────
# STEP 7 — SAVE OUTPUTS
# ─────────────────────────────────────────────────────────────────────────────
print("\n[STEP 7] SAVING OUTPUTS")
print("-" * 80)

# Save learning trajectories
traj_df.to_csv(P2_PROCESSED / 'learning_trajectories.csv', index=False)
print(f"  learning_trajectories.csv         : {len(traj_df):,} rows")

# Save trajectory distribution
traj_dist.to_csv(P2_RESULTS / 'rq2_trajectory_distribution.csv', index=False)
print(f"  rq2_trajectory_distribution.csv saved")

# ── Build student_profiles_master.csv (merged RQ1 + RQ2 + ESE) ──────────────
print("\n  Building student_profiles_master.csv (input for RQ3 & RQ4)...")

master = ep.merge(
    traj_df[['student_id', 'course_id', 'quiz_count', 'avg_score',
             'slope', 'r_squared', 'trajectory_label']],
    on=['student_id', 'course_id'],
    how='left'
)

# Flag trajectory-ineligible students
master['trajectory_eligible'] = master['trajectory_label'].notna()

master_path = P2_PROCESSED / 'student_profiles_master.csv'
master.to_csv(master_path, index=False)

eligible_master   = master['trajectory_eligible'].sum()
ineligible_master = (~master['trajectory_eligible']).sum()

print(f"  student_profiles_master.csv       : {len(master):,} rows total")
print(f"    With trajectory label            : {eligible_master:,}  (RQ2, RQ3, RQ4 ready)")
print(f"    Without trajectory label         : {ineligible_master:,}  (RQ1 only, < 3 quizzes)")

# ─────────────────────────────────────────────────────────────────────────────
# STEP 8 — FIGURES
# ─────────────────────────────────────────────────────────────────────────────
print("\n[STEP 8] GENERATING FIGURES")
print("-" * 80)

TRAJ_COLORS = {
    'Steady High Performer'  : '#27AE60',
    'Stable Average'         : '#3498DB',
    'Improver'               : '#F39C12',
    'Decliner'               : '#E74C3C',
    'Consistently Struggling': '#8E44AD',
}

plt.rcParams.update({
    'font.family'    : 'sans-serif',
    'font.size'      : 11,
    'axes.titlesize' : 13,
    'axes.labelsize' : 11,
    'savefig.dpi'    : 300,
    'savefig.bbox'   : 'tight',
})

# ── Figure 1: Slope distribution with threshold lines ────────────────────────
fig, ax = plt.subplots(figsize=(10, 5))

ax.hist(traj_df['slope'], bins=60, color='steelblue',
        edgecolor='white', alpha=0.80, zorder=2, label='Slope values')

ax.axvspan(traj_df['slope'].min(), DECLINER_THRESHOLD,
           alpha=0.10, color='#E74C3C', zorder=1)
ax.axvspan(IMPROVER_THRESHOLD, traj_df['slope'].max(),
           alpha=0.10, color='#27AE60', zorder=1)

ax.axvline(IMPROVER_THRESHOLD, color='#27AE60', lw=2, ls='--', zorder=3,
           label=f'Improver threshold ({IMPROVER_THRESHOLD:+.3f})')
ax.axvline(DECLINER_THRESHOLD, color='#E74C3C', lw=2, ls='--', zorder=3,
           label=f'Decliner threshold ({DECLINER_THRESHOLD:+.3f})')
ax.axvline(mean_slope, color='navy', lw=1.5, ls=':', zorder=3,
           label=f'Mean slope ({mean_slope:+.3f})')

ax.set_title('Slope Distribution with Data-Driven Thresholds  [RQ2]',
             fontweight='bold', pad=12)
ax.set_xlabel('Slope (score change per quiz, 0–100 scale)')
ax.set_ylabel('Number of Student-Course Pairs')
ax.legend(fontsize=9)

ymax = ax.get_ylim()[1]
ax.text(traj_df['slope'].min() + std_slope * 0.3, ymax * 0.85,
        'Decliners', color='#C0392B', fontsize=10, fontweight='bold')
ax.text(IMPROVER_THRESHOLD + std_slope * 0.1, ymax * 0.85,
        'Improvers', color='#1E8449', fontsize=10, fontweight='bold')

plt.tight_layout()
plt.savefig(P2_FIGURES / 'rq2_slope_distribution.png')
plt.close()
print(f"  rq2_slope_distribution.png saved")

# ── Figure 2: Trajectory distribution (bar + box) ────────────────────────────
fig, axes = plt.subplots(1, 2, figsize=(14, 6))
fig.suptitle('Learning Trajectory Distribution  [RQ2]',
             fontsize=14, fontweight='bold', y=1.01)

traj_order_str = TRAJ_ORDER
colors_ordered = [TRAJ_COLORS[t] for t in traj_order_str]

traj_dist_sorted = traj_dist.set_index('trajectory_label').reindex(traj_order_str).reset_index()

short_labels = ['Steady\nHigh', 'Stable\nAverage', 'Improver', 'Decliner', 'Consistently\nStruggling']

bars = axes[0].bar(short_labels,
                   traj_dist_sorted['n'],
                   color=colors_ordered,
                   edgecolor='white', linewidth=1.2, alpha=0.90)
for bar, (_, row) in zip(bars, traj_dist_sorted.iterrows()):
    axes[0].text(bar.get_x() + bar.get_width() / 2,
                 bar.get_height() + total_elig * 0.003,
                 f"n={int(row['n'])}\n({row['pct']:.1f}%)",
                 ha='center', va='bottom', fontsize=9, fontweight='bold')
axes[0].set_title('Trajectory Counts')
axes[0].set_xlabel('Learning Trajectory')
axes[0].set_ylabel('Number of Student-Course Pairs')
axes[0].set_ylim(0, traj_dist_sorted['n'].max() * 1.20)

# Box plot — ESE % by trajectory
data_by_traj = [
    traj_with_ese[traj_with_ese['trajectory_label'] == t]['ese_percentage'].dropna().values
    for t in traj_order_str
]
bp = axes[1].boxplot(data_by_traj,
                     labels=short_labels,
                     patch_artist=True,
                     medianprops={'color': 'black', 'linewidth': 2})
for patch, t in zip(bp['boxes'], traj_order_str):
    patch.set_facecolor(TRAJ_COLORS[t])
    patch.set_alpha(0.75)
axes[1].set_title('ESE % by Trajectory\n(Preliminary — full analysis in RQ4)')
axes[1].set_xlabel('Learning Trajectory')
axes[1].set_ylabel('ESE Percentage (%)')

plt.tight_layout()
plt.savefig(P2_FIGURES / 'rq2_trajectory_distribution.png')
plt.close()
print(f"  rq2_trajectory_distribution.png saved")

# ── Figure 3: Score progression by trajectory (mean quiz score per position) ─
print("  Building score progression plot...")

q_elig_traj = q_elig.merge(
    traj_df[['student_id', 'course_id', 'trajectory_label']],
    on=['student_id', 'course_id'], how='inner'
)

q_elig_traj['quiz_seq'] = (
    q_elig_traj.groupby(['student_id', 'course_id']).cumcount() + 1
)

# Limit to quiz positions 1–6 for clarity
max_pos = 6
q_prog = q_elig_traj[q_elig_traj['quiz_seq'] <= max_pos].copy()

prog_summary = (
    q_prog.groupby(['trajectory_label', 'quiz_seq'], observed=True)['percentage_score']
          .agg(['mean', 'sem'])
          .reset_index()
)

fig, ax = plt.subplots(figsize=(10, 6))

for traj in traj_order_str:
    sub = prog_summary[prog_summary['trajectory_label'] == traj]
    if len(sub) == 0:
        continue
    ax.plot(sub['quiz_seq'], sub['mean'],
            marker='o', linewidth=2, markersize=7,
            color=TRAJ_COLORS[traj], label=traj)
    ax.fill_between(sub['quiz_seq'],
                    sub['mean'] - sub['sem'],
                    sub['mean'] + sub['sem'],
                    alpha=0.12, color=TRAJ_COLORS[traj])

ax.axhline(60, color='gray', ls='--', lw=1, alpha=0.6, label='High threshold (60%)')
ax.axhline(40, color='gray', ls=':',  lw=1, alpha=0.6, label='Low threshold (40%)')

ax.set_title('Mean Quiz Score Progression by Trajectory  [RQ2]',
             fontweight='bold', pad=12)
ax.set_xlabel('Quiz Sequence Number')
ax.set_ylabel('Mean Quiz Score (%)')
ax.set_xticks(range(1, max_pos + 1))
ax.set_ylim(0, 105)
ax.legend(fontsize=9, loc='lower right')
ax.grid(axis='y', alpha=0.3)

plt.tight_layout()
plt.savefig(P2_FIGURES / 'rq2_trajectory_score_progression.png')
plt.close()
print(f"  rq2_trajectory_score_progression.png saved")

# ─────────────────────────────────────────────────────────────────────────────
# FINAL SUMMARY
# ─────────────────────────────────────────────────────────────────────────────
elapsed = (datetime.now() - START_TIME).seconds

print("\n" + "=" * 80)
print("SCRIPT P2_02 COMPLETE — RQ2 ANSWERED")
print("=" * 80)
print(f"\n  Eligible student-course pairs : {total_elig:,} (≥ {MIN_QUIZZES} quizzes)")
print(f"\n  SLOPE THRESHOLDS (data-driven):")
print(f"    Mean slope           : {mean_slope:+.4f}")
print(f"    Std of slopes        : {std_slope:.4f}")
print(f"    Improver threshold   : slope > {IMPROVER_THRESHOLD:+.4f}")
print(f"    Decliner threshold   : slope < {DECLINER_THRESHOLD:+.4f}")
print(f"\n  TRAJECTORY DISTRIBUTION:")
for _, row in traj_dist_sorted.iterrows():
    print(f"    {str(row['trajectory_label']):<26} : "
          f"n={int(row['n']):>5,}  ({row['pct']:.1f}%)  "
          f"mean_ese={row['mean_ese_pct']:.1f}%")
print(f"\n  OUTPUTS SAVED:")
print(f"    data/processed/paper2/learning_trajectories.csv")
print(f"    data/processed/paper2/student_profiles_master.csv  ← input for RQ3 & RQ4")
print(f"    results/paper2/rq2_trajectory_distribution.csv")
print(f"    results/paper2/rq2_slope_thresholds.csv")
print(f"    results/paper2/figures/rq2_slope_distribution.png")
print(f"    results/paper2/figures/rq2_trajectory_distribution.png")
print(f"    results/paper2/figures/rq2_trajectory_score_progression.png")
print(f"\n  Time elapsed : {elapsed}s")
print(f"\n  NEXT : python scripts/P2_03_statistical_analysis.py  (RQ3 & RQ4)")
print("=" * 80)
