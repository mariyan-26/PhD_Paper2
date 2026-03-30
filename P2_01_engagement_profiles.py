"""
=============================================================================
PhD Paper 2 — Script P2_01: Engagement Profile Classification (RQ1)
Uncovering Learning Patterns and Behavioral Trajectories in Continuous
Assessment Beyond Average Performance
Author  : Mariyan J Rooban
College : Kristu Jayanti College, Bengaluru
Date    : March 2026
=============================================================================

RESEARCH QUESTION:
  RQ1 — What distinct engagement profiles exist among students in online
         continuous assessment, and how are they distributed across the cohort?

METHODOLOGY:
  Engagement is operationalised as a composite score combining:
    - Participation Rate  (60% weight) : quizzes attempted / max quizzes in
                                         course × 100
    - Avg Quiz Score %   (40% weight) : mean percentage_score across all
                                         attempted quizzes (already 0–100)

  Composite Engagement Score = 0.6 × participation_rate + 0.4 × avg_quiz_score_pct

  Max quizzes per course is derived EMPIRICALLY from the data:
    max_quizzes_in_course = maximum distinct quiz attempts by any student
                            in that course (data-driven, not hardcoded)

  Students with ZERO quiz attempts are INCLUDED with:
    participation_rate = 0, avg_quiz_score_pct = 0, engagement_score = 0

PROFILE THRESHOLDS:
  Low    : 0.00 – 39.99   (Fail/Disengaged)
  Medium : 40.00 – 59.99  (Moderate Engagement)
  High   : 60.00 – 100.00 (Active Engagement)

INPUTS  (from Paper 1 cleaned outputs):
  data/processed/students_clean.csv  — valid student-course enrollments
  data/processed/quizzes_clean.csv   — best attempt per student per quiz

OUTPUTS:
  data/processed/paper2/engagement_profiles.csv  — one row per student-course
  results/paper2/rq1_profile_distribution.csv    — profile counts and %
  results/paper2/figures/rq1_engagement_histogram.png
  results/paper2/figures/rq1_profile_distribution.png
  results/paper2/figures/rq1_profile_by_course_heatmap.png
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
import warnings
warnings.filterwarnings('ignore')

pd.set_option('display.max_columns', None)
pd.set_option('display.float_format', '{:.2f}'.format)

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
print("PAPER 2 — SCRIPT P2_01 : ENGAGEMENT PROFILE CLASSIFICATION  (RQ1)")
print(f"Started : {START_TIME.strftime('%Y-%m-%d %H:%M:%S')}")
print("=" * 80)

# ─────────────────────────────────────────────────────────────────────────────
# STEP 1 — LOAD CLEANED DATA (from Paper 1 Script 01 outputs)
# ─────────────────────────────────────────────────────────────────────────────
print("\n[STEP 1] LOADING CLEANED DATA")
print("-" * 80)

required = {
    'students' : DATA_PROCESSED / 'students_clean.csv',
    'quizzes'  : DATA_PROCESSED / 'quizzes_clean.csv',
}

missing = [k for k, v in required.items() if not v.exists()]
if missing:
    print(f"\n  ERROR: Missing files: {missing}")
    print(f"  Please run Script 01 first to generate cleaned data.")
    exit(1)

s = pd.read_csv(required['students'], low_memory=False)
q = pd.read_csv(required['quizzes'],  low_memory=False)

print(f"  students_clean : {len(s):>7,} rows | {s.shape[1]} cols")
print(f"  quizzes_clean  : {len(q):>7,} rows | {q.shape[1]} cols")

# Parse attempt_start for sorting
q['attempt_start'] = pd.to_datetime(q['attempt_start'], errors='coerce')

# ─────────────────────────────────────────────────────────────────────────────
# STEP 2 — COMPUTE MAX QUIZZES PER COURSE (empirical denominator)
# ─────────────────────────────────────────────────────────────────────────────
print("\n[STEP 2] COMPUTING MAX QUIZZES PER COURSE (empirical)")
print("-" * 80)

# Each row in quizzes_clean is the best attempt per student per quiz.
# Count distinct quizzes per student per course, then take the max per course.
quizzes_per_student_course = (
    q.groupby(['student_id', 'course_id'])
     .size()
     .reset_index(name='quizzes_attempted')
)

max_quizzes_per_course = (
    quizzes_per_student_course
    .groupby('course_id')['quizzes_attempted']
    .max()
    .reset_index()
    .rename(columns={'quizzes_attempted': 'max_quizzes_in_course'})
)

print(f"  Courses with quiz data     : {len(max_quizzes_per_course):,}")
print(f"  Max quizzes distribution:")
print(f"    Min  : {max_quizzes_per_course['max_quizzes_in_course'].min()}")
print(f"    Max  : {max_quizzes_per_course['max_quizzes_in_course'].max()}")
print(f"    Mean : {max_quizzes_per_course['max_quizzes_in_course'].mean():.1f}")
print(f"    Mode : {max_quizzes_per_course['max_quizzes_in_course'].mode().iloc[0]}")

# ─────────────────────────────────────────────────────────────────────────────
# STEP 3 — COMPUTE AVERAGE QUIZ SCORE % PER STUDENT-COURSE
# ─────────────────────────────────────────────────────────────────────────────
print("\n[STEP 3] COMPUTING AVERAGE QUIZ SCORE PER STUDENT-COURSE")
print("-" * 80)

# percentage_score is already 0–100 in quizzes_clean
avg_quiz_scores = (
    q.groupby(['student_id', 'course_id'])['percentage_score']
     .mean()
     .reset_index()
     .rename(columns={'percentage_score': 'avg_quiz_score_pct'})
)

avg_quiz_scores['avg_quiz_score_pct'] = avg_quiz_scores['avg_quiz_score_pct'].round(4)

print(f"  Student-course pairs with quiz data : {len(avg_quiz_scores):,}")
print(f"  Avg quiz score stats:")
print(f"    Mean   : {avg_quiz_scores['avg_quiz_score_pct'].mean():.2f}%")
print(f"    Median : {avg_quiz_scores['avg_quiz_score_pct'].median():.2f}%")
print(f"    Std    : {avg_quiz_scores['avg_quiz_score_pct'].std():.2f}%")

# ─────────────────────────────────────────────────────────────────────────────
# STEP 4 — BUILD ENROLLMENT BASE (all valid student-course pairs from s)
# ─────────────────────────────────────────────────────────────────────────────
print("\n[STEP 4] BUILDING ENROLLMENT BASE")
print("-" * 80)

# Start with all valid enrollments
id_cols = ['student_id', 'course_id', 'ese_percentage', 'programme_level',
           'Group', 'course_name', 'course_code']
id_cols = [c for c in id_cols if c in s.columns]

enroll = s[id_cols].drop_duplicates(subset=['student_id', 'course_id']).copy()

print(f"  Total valid enrollments : {len(enroll):,}")

# Merge quiz attempt counts
enroll = enroll.merge(quizzes_per_student_course, on=['student_id', 'course_id'], how='left')
enroll['quizzes_attempted'] = enroll['quizzes_attempted'].fillna(0).astype(int)

# Merge max quizzes per course
enroll = enroll.merge(max_quizzes_per_course, on='course_id', how='left')
enroll['max_quizzes_in_course'] = enroll['max_quizzes_in_course'].fillna(1)

# Merge avg quiz score
enroll = enroll.merge(avg_quiz_scores, on=['student_id', 'course_id'], how='left')
enroll['avg_quiz_score_pct'] = enroll['avg_quiz_score_pct'].fillna(0.0)

zero_quiz_n = (enroll['quizzes_attempted'] == 0).sum()
print(f"  Students with zero quiz attempts : {zero_quiz_n:,} "
      f"({zero_quiz_n/len(enroll)*100:.1f}%) → engagement_score = 0 (Low)")

# ─────────────────────────────────────────────────────────────────────────────
# STEP 5 — COMPUTE COMPOSITE ENGAGEMENT SCORE
# ─────────────────────────────────────────────────────────────────────────────
print("\n[STEP 5] COMPUTING COMPOSITE ENGAGEMENT SCORE")
print("-" * 80)
print("  Formula: engagement_score = 0.6 × participation_rate + 0.4 × avg_quiz_score_pct")
print("  Weights : Participation = 60%  |  Quiz Performance = 40%")
print("  Rationale: Behavioural engagement (showing up) drives the score;")
print("             performance is captured separately in trajectory analysis (RQ2).")

enroll['participation_rate'] = (
    (enroll['quizzes_attempted'] / enroll['max_quizzes_in_course']) * 100
).clip(0, 100).round(4)

enroll['engagement_score'] = (
    0.6 * enroll['participation_rate'] +
    0.4 * enroll['avg_quiz_score_pct']
).round(4)

print(f"\n  Engagement score stats:")
print(f"    Mean   : {enroll['engagement_score'].mean():.2f}")
print(f"    Median : {enroll['engagement_score'].median():.2f}")
print(f"    Std    : {enroll['engagement_score'].std():.2f}")
print(f"    Min    : {enroll['engagement_score'].min():.2f}")
print(f"    Max    : {enroll['engagement_score'].max():.2f}")

# ─────────────────────────────────────────────────────────────────────────────
# STEP 6 — CLASSIFY ENGAGEMENT PROFILES
# ─────────────────────────────────────────────────────────────────────────────
print("\n[STEP 6] CLASSIFYING ENGAGEMENT PROFILES")
print("-" * 80)
print("  Thresholds:")
print("    Low    : 0.00  – 39.99  (Disengaged)")
print("    Medium : 40.00 – 59.99  (Moderately Engaged)")
print("    High   : 60.00 – 100.00 (Actively Engaged)")

def classify_profile(score):
    if score < 40.0:
        return 'Low'
    elif score < 60.0:
        return 'Medium'
    else:
        return 'High'

enroll['profile_label'] = enroll['engagement_score'].apply(classify_profile)

# Ordered category for consistent sorting
profile_order = ['Low', 'Medium', 'High']
enroll['profile_label'] = pd.Categorical(
    enroll['profile_label'],
    categories=profile_order,
    ordered=True
)

# ─────────────────────────────────────────────────────────────────────────────
# STEP 7 — PROFILE DISTRIBUTION (answers RQ1)
# ─────────────────────────────────────────────────────────────────────────────
print("\n[STEP 7] PROFILE DISTRIBUTION — RQ1 ANSWER")
print("-" * 80)

profile_dist = (
    enroll.groupby('profile_label', observed=True)
          .agg(
              n                   = ('student_id', 'count'),
              mean_engagement     = ('engagement_score', 'mean'),
              median_engagement   = ('engagement_score', 'median'),
              std_engagement      = ('engagement_score', 'std'),
              mean_participation  = ('participation_rate', 'mean'),
              mean_quiz_score_pct = ('avg_quiz_score_pct', 'mean'),
              mean_ese_pct        = ('ese_percentage', 'mean'),
          )
          .reset_index()
)

total = len(enroll)
profile_dist['pct'] = (profile_dist['n'] / total * 100).round(2)

print(f"\n  {'Profile':<10} {'n':>6} {'%':>7}  {'Mean Eng':>10}  "
      f"{'Mean Part':>10}  {'Mean Quiz%':>11}  {'Mean ESE%':>10}")
print(f"  {'-'*72}")
for _, row in profile_dist.iterrows():
    print(f"  {row['profile_label']:<10} {int(row['n']):>6} {row['pct']:>6.1f}%  "
          f"{row['mean_engagement']:>10.2f}  {row['mean_participation']:>10.2f}  "
          f"{row['mean_quiz_score_pct']:>11.2f}  {row['mean_ese_pct']:>10.2f}")

# ─────────────────────────────────────────────────────────────────────────────
# STEP 8 — SAVE OUTPUTS
# ─────────────────────────────────────────────────────────────────────────────
print("\n[STEP 8] SAVING OUTPUTS")
print("-" * 80)

# Main engagement profiles file (feeds into RQ3 and merged master for RQ3/RQ4)
out_cols = [
    'student_id', 'course_id', 'programme_level', 'Group',
    'course_name', 'course_code',
    'quizzes_attempted', 'max_quizzes_in_course',
    'participation_rate', 'avg_quiz_score_pct',
    'engagement_score', 'profile_label',
    'ese_percentage'
]
out_cols = [c for c in out_cols if c in enroll.columns]

enroll_out = enroll[out_cols].copy()
enroll_out.to_csv(P2_PROCESSED / 'engagement_profiles.csv', index=False)
print(f"  engagement_profiles.csv   : {len(enroll_out):,} rows")

# Profile distribution summary
profile_dist.to_csv(P2_RESULTS / 'rq1_profile_distribution.csv', index=False)
print(f"  rq1_profile_distribution.csv saved")

# ─────────────────────────────────────────────────────────────────────────────
# STEP 9 — FIGURES
# ─────────────────────────────────────────────────────────────────────────────
print("\n[STEP 9] GENERATING FIGURES")
print("-" * 80)

PROFILE_COLORS = {
    'Low'    : '#E05C5C',   # coral-red
    'Medium' : '#F5A623',   # amber
    'High'   : '#4CAF7D',   # green
}

plt.rcParams.update({
    'font.family'     : 'sans-serif',
    'font.size'       : 11,
    'axes.titlesize'  : 13,
    'axes.labelsize'  : 11,
    'savefig.dpi'     : 300,
    'savefig.bbox'    : 'tight',
})

# ── Figure 1: Engagement score histogram with profile bands ──────────────────
fig, ax = plt.subplots(figsize=(10, 5))

ax.hist(enroll['engagement_score'], bins=50, color='steelblue',
        edgecolor='white', alpha=0.80, zorder=2, label='Engagement Score')

ax.axvspan(0,  40,  alpha=0.12, color='#E05C5C', zorder=1)
ax.axvspan(40, 60,  alpha=0.12, color='#F5A623', zorder=1)
ax.axvspan(60, 100, alpha=0.12, color='#4CAF7D', zorder=1)

ax.axvline(40, color='#E05C5C', lw=1.5, ls='--', zorder=3, label='Low / Medium (40)')
ax.axvline(60, color='#4CAF7D', lw=1.5, ls='--', zorder=3, label='Medium / High (60)')
ax.axvline(enroll['engagement_score'].mean(), color='navy',
           lw=2, ls=':', zorder=3,
           label=f"Mean = {enroll['engagement_score'].mean():.1f}")

ymax = ax.get_ylim()[1]
ax.text(20,  ymax * 0.90, f"Low\n{profile_dist[profile_dist['profile_label']=='Low']['pct'].values[0]:.1f}%",
        ha='center', fontsize=10, color='#C0392B', fontweight='bold')
ax.text(50,  ymax * 0.90, f"Medium\n{profile_dist[profile_dist['profile_label']=='Medium']['pct'].values[0]:.1f}%",
        ha='center', fontsize=10, color='#B7770D', fontweight='bold')
ax.text(80,  ymax * 0.90, f"High\n{profile_dist[profile_dist['profile_label']=='High']['pct'].values[0]:.1f}%",
        ha='center', fontsize=10, color='#27AE60', fontweight='bold')

ax.set_title('Engagement Score Distribution with Profile Bands  [RQ1]',
             fontweight='bold', pad=12)
ax.set_xlabel('Composite Engagement Score (0–100)')
ax.set_ylabel('Number of Student-Course Enrollments')
ax.legend(fontsize=9)
plt.tight_layout()
plt.savefig(P2_FIGURES / 'rq1_engagement_histogram.png')
plt.close()
print(f"  rq1_engagement_histogram.png saved")

# ── Figure 2: Profile distribution bar chart ─────────────────────────────────
fig, axes = plt.subplots(1, 2, figsize=(12, 5))
fig.suptitle('Engagement Profile Distribution  [RQ1]',
             fontsize=14, fontweight='bold', y=1.01)

# Bar chart — counts with % labels
colors = [PROFILE_COLORS[p] for p in profile_dist['profile_label']]
bars = axes[0].bar(profile_dist['profile_label'].astype(str),
                   profile_dist['n'],
                   color=colors, edgecolor='white', linewidth=1.2, alpha=0.90)
for bar, (_, row) in zip(bars, profile_dist.iterrows()):
    axes[0].text(bar.get_x() + bar.get_width() / 2,
                 bar.get_height() + total * 0.005,
                 f"n={int(row['n'])}\n({row['pct']:.1f}%)",
                 ha='center', va='bottom', fontsize=10, fontweight='bold')
axes[0].set_title('Profile Counts')
axes[0].set_xlabel('Engagement Profile')
axes[0].set_ylabel('Number of Enrollments')
axes[0].set_ylim(0, profile_dist['n'].max() * 1.18)

# Box plot — ESE % by profile
profile_order_str = ['Low', 'Medium', 'High']
data_by_profile = [
    enroll[enroll['profile_label'] == p]['ese_percentage'].dropna().values
    for p in profile_order_str
]

bp = axes[1].boxplot(data_by_profile,
                     labels=profile_order_str,
                     patch_artist=True,
                     medianprops={'color': 'black', 'linewidth': 2})
for patch, p in zip(bp['boxes'], profile_order_str):
    patch.set_facecolor(PROFILE_COLORS[p])
    patch.set_alpha(0.75)
axes[1].set_title('ESE % by Engagement Profile\n(Preliminary — full analysis in RQ3)')
axes[1].set_xlabel('Engagement Profile')
axes[1].set_ylabel('ESE Percentage (%)')

plt.tight_layout()
plt.savefig(P2_FIGURES / 'rq1_profile_distribution.png')
plt.close()
print(f"  rq1_profile_distribution.png saved")

# ── Figure 3: Heatmap — profile breakdown by course (top 20 courses) ─────────
course_profile = (
    enroll.groupby(['course_code', 'profile_label'], observed=True)
          .size()
          .unstack(fill_value=0)
          .assign(total=lambda x: x.sum(axis=1))
          .sort_values('total', ascending=False)
          .head(20)
          .drop(columns='total')
)

if len(course_profile) > 0:
    course_profile_pct = course_profile.div(course_profile.sum(axis=1), axis=0) * 100

    fig, ax = plt.subplots(figsize=(10, 8))
    sns.heatmap(course_profile_pct,
                annot=True, fmt='.0f', cmap='RdYlGn',
                linewidths=0.5, linecolor='white',
                cbar_kws={'label': 'Percentage of Students (%)'},
                ax=ax)
    ax.set_title('Engagement Profile Distribution by Course (Top 20 Courses)  [RQ1]',
                 fontweight='bold', pad=12)
    ax.set_xlabel('Engagement Profile')
    ax.set_ylabel('Course Code')
    ax.tick_params(axis='x', rotation=0)
    ax.tick_params(axis='y', rotation=0, labelsize=9)
    plt.tight_layout()
    plt.savefig(P2_FIGURES / 'rq1_profile_by_course_heatmap.png')
    plt.close()
    print(f"  rq1_profile_by_course_heatmap.png saved")

# ─────────────────────────────────────────────────────────────────────────────
# FINAL SUMMARY
# ─────────────────────────────────────────────────────────────────────────────
elapsed = (datetime.now() - START_TIME).seconds

print("\n" + "=" * 80)
print("SCRIPT P2_01 COMPLETE — RQ1 ANSWERED")
print("=" * 80)
print(f"\n  Total student-course enrollments : {total:,}")
print(f"  Unit of analysis                 : student-course pair")
print(f"\n  ENGAGEMENT PROFILE DISTRIBUTION:")
for _, row in profile_dist.iterrows():
    print(f"    {str(row['profile_label']):<10} : "
          f"n={int(row['n']):>5,}  ({row['pct']:.1f}%)  "
          f"mean_engagement={row['mean_engagement']:.1f}")
print(f"\n  COMPOSITE SCORE FORMULA:")
print(f"    engagement_score = 0.6 × participation_rate + 0.4 × avg_quiz_score_pct")
print(f"    max_quizzes_in_course = empirically derived per course")
print(f"\n  OUTPUTS SAVED:")
print(f"    data/processed/paper2/engagement_profiles.csv")
print(f"    results/paper2/rq1_profile_distribution.csv")
print(f"    results/paper2/figures/rq1_engagement_histogram.png")
print(f"    results/paper2/figures/rq1_profile_distribution.png")
print(f"    results/paper2/figures/rq1_profile_by_course_heatmap.png")
print(f"\n  Time elapsed : {elapsed}s")
print(f"\n  NEXT : python scripts/P2_02_learning_trajectories.py")
print("=" * 80)
