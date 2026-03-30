"""
=============================================================================
PhD Paper 2 — Script P2_03: Statistical Analysis (RQ3 & RQ4)
Uncovering Learning Patterns and Behavioral Trajectories in Continuous
Assessment Beyond Average Performance
Author  : Mariyan J Rooban
College : Kristu Jayanti College, Bengaluru
Date    : March 2026
=============================================================================

RESEARCH QUESTIONS:
  RQ3 — How do student engagement profiles relate to final examination outcomes?
  RQ4 — How do learning trajectories relate to final examination outcomes, and
         do students following different trajectories achieve comparable
         academic success?

STATISTICAL PIPELINE (same for RQ3 and RQ4):
  Step 1 — Normality check     : Shapiro-Wilk per group
                                  Levene's test for homogeneity of variance
  Step 2 — Primary test        : Kruskal-Wallis H-test (if non-normal)
                                  One-Way ANOVA (if normal + equal variance)
                                  Decision made automatically from Step 1
  Step 3 — Post-hoc test       : Dunn's test with Bonferroni correction
                                  (applied regardless — pairwise comparisons)
  Step 4 — Effect size         : Epsilon-squared (ε²) for Kruskal-Wallis
                                  Eta-squared (η²) for ANOVA
  Step 5 — Descriptive stats   : Mean, Median, SD, IQR, n per group

KEY COMPARISON FOR RQ4:
  Improvers vs Steady High Performers — tests the abstract's central claim
  that improving students achieve outcomes comparable to consistently high
  performers.

INPUTS:
  data/processed/paper2/student_profiles_master.csv  (from P2_02)

OUTPUTS:
  results/paper2/rq3_engagement_vs_ese_stats.csv
  results/paper2/rq3_posthoc_dunn.csv
  results/paper2/rq4_trajectory_vs_ese_stats.csv
  results/paper2/rq4_posthoc_dunn.csv
  results/paper2/rq3_rq4_normality_tests.csv
  results/paper2/figures/rq3_ese_by_profile_boxplot.png
  results/paper2/figures/rq3_ese_by_profile_violin.png
  results/paper2/figures/rq4_ese_by_trajectory_boxplot.png
  results/paper2/figures/rq4_ese_by_trajectory_violin.png
  results/paper2/figures/rq4_improver_vs_highperformer.png
=============================================================================
"""

import pandas as pd
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import seaborn as sns
from pathlib import Path
from datetime import datetime
from scipy import stats
from itertools import combinations
import warnings
warnings.filterwarnings('ignore')

pd.set_option('display.max_columns', None)
pd.set_option('display.float_format', '{:.4f}'.format)

# ── PATHS ─────────────────────────────────────────────────────────────────────
PROJECT_ROOT = Path(__file__).parent
P2_PROCESSED = PROJECT_ROOT / "data" / "processed" / "paper2"
P2_RESULTS   = PROJECT_ROOT / "results" / "paper2"
P2_FIGURES   = P2_RESULTS / "figures"


for d in [P2_RESULTS, P2_FIGURES]:
    d.mkdir(parents=True, exist_ok=True)

START_TIME = datetime.now()

print("=" * 80)
print("PAPER 2 — SCRIPT P2_03 : STATISTICAL ANALYSIS  (RQ3 & RQ4)")
print(f"Started : {START_TIME.strftime('%Y-%m-%d %H:%M:%S')}")
print("=" * 80)

# ─────────────────────────────────────────────────────────────────────────────
# HELPER FUNCTIONS
# ─────────────────────────────────────────────────────────────────────────────

def descriptive_stats(df, group_col, value_col):
    """Compute descriptive statistics per group."""
    result = []
    for group, grp in df.groupby(group_col, observed=True):
        vals = grp[value_col].dropna()
        result.append({
            'group'  : group,
            'n'      : len(vals),
            'mean'   : round(vals.mean(), 4),
            'median' : round(vals.median(), 4),
            'std'    : round(vals.std(), 4),
            'q1'     : round(vals.quantile(0.25), 4),
            'q3'     : round(vals.quantile(0.75), 4),
            'iqr'    : round(vals.quantile(0.75) - vals.quantile(0.25), 4),
            'min'    : round(vals.min(), 4),
            'max'    : round(vals.max(), 4),
        })
    return pd.DataFrame(result)


def shapiro_per_group(df, group_col, value_col, max_n=5000):
    """
    Shapiro-Wilk normality test per group.
    For large groups (n > 5000), use Kolmogorov-Smirnov with normal params.
    """
    result = []
    for group, grp in df.groupby(group_col, observed=True):
        vals = grp[value_col].dropna().values
        n    = len(vals)
        if n < 3:
            result.append({'group': group, 'n': n, 'test': 'insufficient data',
                           'statistic': np.nan, 'p_value': np.nan, 'normal': False})
            continue
        if n > max_n:
            # KS test for very large groups
            mu, sigma = vals.mean(), vals.std()
            stat, p = stats.kstest(vals, 'norm', args=(mu, sigma))
            test_name = 'KS'
        else:
            stat, p = stats.shapiro(vals)
            test_name = 'Shapiro-Wilk'
        result.append({
            'group'    : group,
            'n'        : n,
            'test'     : test_name,
            'statistic': round(stat, 6),
            'p_value'  : round(p, 6),
            'normal'   : p > 0.05
        })
    return pd.DataFrame(result)


def levene_test(groups_data):
    """Levene's test for homogeneity of variance."""
    stat, p = stats.levene(*groups_data)
    return round(stat, 4), round(p, 6), p > 0.05


def kruskal_wallis_test(groups_data):
    """Kruskal-Wallis H test."""
    stat, p = stats.kruskal(*groups_data)
    return round(stat, 4), round(p, 6)


def one_way_anova(groups_data):
    """One-Way ANOVA F test."""
    stat, p = stats.f_oneway(*groups_data)
    return round(stat, 4), round(p, 6)


def epsilon_squared(h_stat, n_total, k_groups):
    """
    Epsilon-squared effect size for Kruskal-Wallis.
    ε² = (H - k + 1) / (n - k)
    Interpretation: small=0.01, medium=0.06, large=0.14
    """
    eps2 = (h_stat - k_groups + 1) / (n_total - k_groups)
    eps2 = max(0.0, round(eps2, 4))
    if   eps2 >= 0.14: interp = 'Large'
    elif eps2 >= 0.06: interp = 'Medium'
    elif eps2 >= 0.01: interp = 'Small'
    else:              interp = 'Negligible'
    return eps2, interp


def eta_squared(f_stat, df_between, df_within):
    """
    Eta-squared effect size for ANOVA.
    η² = SS_between / SS_total  (approximated from F)
    """
    ss_between = f_stat * df_between
    ss_total   = ss_between + df_within
    eta2 = round(ss_between / ss_total, 4)
    if   eta2 >= 0.14: interp = 'Large'
    elif eta2 >= 0.06: interp = 'Medium'
    elif eta2 >= 0.01: interp = 'Small'
    else:              interp = 'Negligible'
    return eta2, interp


def dunn_posthoc(df, group_col, value_col, alpha=0.05):
    """
    Dunn's test with Bonferroni correction for pairwise comparisons.
    Manual implementation using rank-based z-statistics.
    """
    groups = df[group_col].cat.categories.tolist() if hasattr(df[group_col], 'cat') \
             else df[group_col].unique().tolist()

    all_vals = df[[group_col, value_col]].dropna()
    all_vals = all_vals.copy()
    all_vals['rank'] = all_vals[value_col].rank(method='average')

    n_total  = len(all_vals)
    n_pairs  = len(list(combinations(groups, 2)))

    results = []
    for g1, g2 in combinations(groups, 2):
        r1 = all_vals[all_vals[group_col] == g1]['rank'].values
        r2 = all_vals[all_vals[group_col] == g2]['rank'].values
        n1, n2 = len(r1), len(r2)

        if n1 < 2 or n2 < 2:
            continue

        mean_r1 = r1.mean()
        mean_r2 = r2.mean()

        # Tie correction factor
        tie_correction = 1 - (
            sum((t**3 - t) for t in
                pd.Series(all_vals[value_col].dropna()).value_counts().values)
            / (n_total**3 - n_total)
        )

        se = np.sqrt(
            (n_total * (n_total + 1) / 12) *
            (1/n1 + 1/n2) *
            (tie_correction if tie_correction > 0 else 1.0)
        )

        if se == 0:
            continue

        z = (mean_r1 - mean_r2) / se
        p_raw = 2 * (1 - stats.norm.cdf(abs(z)))

        # Bonferroni correction
        p_adj = min(p_raw * n_pairs, 1.0)

        results.append({
            'group_1'     : str(g1),
            'group_2'     : str(g2),
            'mean_rank_1' : round(mean_r1, 4),
            'mean_rank_2' : round(mean_r2, 4),
            'mean_ese_1'  : round(all_vals[all_vals[group_col] == g1][value_col].mean(), 4),
            'mean_ese_2'  : round(all_vals[all_vals[group_col] == g2][value_col].mean(), 4),
            'z_statistic' : round(z, 4),
            'p_raw'       : round(p_raw, 6),
            'p_bonferroni': round(p_adj, 6),
            'significant' : p_adj < alpha,
            'n_1'         : n1,
            'n_2'         : n2,
        })

    return pd.DataFrame(results)


def run_full_analysis(df, group_col, value_col, rq_label, alpha=0.05):
    """
    Full statistical pipeline for one RQ:
    Normality → Primary test → Post-hoc → Effect size
    Returns all results as a summary dict + DataFrames.
    """
    print(f"\n  {'─'*70}")
    print(f"  ANALYSIS: {rq_label}")
    print(f"  Group column : {group_col}")
    print(f"  Value column : {value_col} (ESE %)")
    print(f"  {'─'*70}")

    df_clean = df[[group_col, value_col]].dropna()
    groups   = df_clean[group_col].unique().tolist()
    if hasattr(df_clean[group_col], 'cat'):
        groups = [g for g in df_clean[group_col].cat.categories if g in groups]

    groups_data = [df_clean[df_clean[group_col] == g][value_col].values
                   for g in groups]
    n_total = len(df_clean)
    k       = len(groups)

    # ── DESCRIPTIVE STATS ────────────────────────────────────────────────────
    desc = descriptive_stats(df_clean, group_col, value_col)
    print(f"\n  Descriptive Statistics (ESE %):")
    print(f"  {'Group':<28} {'n':>5}  {'Mean':>7}  {'Median':>8}  "
          f"{'SD':>7}  {'IQR':>7}  {'Min':>6}  {'Max':>6}")
    print(f"  {'-'*78}")
    for _, row in desc.iterrows():
        print(f"  {str(row['group']):<28} {int(row['n']):>5}  {row['mean']:>7.2f}  "
              f"{row['median']:>8.2f}  {row['std']:>7.2f}  {row['iqr']:>7.2f}  "
              f"{row['min']:>6.1f}  {row['max']:>6.1f}")

    # ── NORMALITY TESTS ───────────────────────────────────────────────────────
    print(f"\n  Normality Tests:")
    norm_df = shapiro_per_group(df_clean, group_col, value_col)
    for _, row in norm_df.iterrows():
        flag = '✓ Normal' if row['normal'] else '✗ Non-normal'
        print(f"  {str(row['group']):<28} {row['test']:<14} "
              f"stat={row['statistic']:.4f}  p={row['p_value']:.4f}  {flag}")

    all_normal = norm_df['normal'].all()

    # ── LEVENE'S TEST ─────────────────────────────────────────────────────────
    lev_stat, lev_p, equal_var = levene_test(groups_data)
    print(f"\n  Levene's Test (homogeneity of variance):")
    print(f"  stat={lev_stat:.4f}  p={lev_p:.4f}  "
          f"{'Equal variances' if equal_var else 'Unequal variances'}")

    # ── PRIMARY TEST DECISION ─────────────────────────────────────────────────
    use_parametric = all_normal and equal_var

    if use_parametric:
        test_name = 'One-Way ANOVA'
        f_stat, p_val = one_way_anova(groups_data)
        df_between = k - 1
        df_within  = n_total - k
        eta2, eta2_interp = eta_squared(f_stat, df_between, df_within)
        effect_label = 'η²'
        effect_val   = eta2
        effect_interp = eta2_interp
        print(f"\n  → Decision: All groups normal + equal variance → {test_name}")
        print(f"  {test_name}: F({df_between}, {df_within}) = {f_stat:.4f},  p = {p_val:.6f}")
    else:
        test_name = 'Kruskal-Wallis H'
        h_stat, p_val = kruskal_wallis_test(groups_data)
        eps2, eps2_interp = epsilon_squared(h_stat, n_total, k)
        effect_label  = 'ε²'
        effect_val    = eps2
        effect_interp = eps2_interp
        reason = 'non-normal distributions' if not all_normal else 'unequal variances'
        print(f"\n  → Decision: {reason} detected → {test_name} (non-parametric)")
        print(f"  {test_name}: H = {h_stat:.4f},  df = {k-1},  p = {p_val:.6f}")

    sig = '*** (p < 0.001)' if p_val < 0.001 else \
          '** (p < 0.01)'   if p_val < 0.01  else \
          '* (p < 0.05)'    if p_val < 0.05  else \
          'ns (p ≥ 0.05)'
    print(f"  Significance : {sig}")
    print(f"  Effect size  : {effect_label} = {effect_val:.4f}  [{effect_interp}]")

    # ── POST-HOC DUNN'S TEST ──────────────────────────────────────────────────
    print(f"\n  Post-hoc: Dunn's Test with Bonferroni Correction (α = {alpha}):")
    posthoc_df = dunn_posthoc(df_clean, group_col, value_col, alpha=alpha)

    print(f"  {'Group 1':<26} {'Group 2':<26} "
          f"{'MeanESE1':>9} {'MeanESE2':>9} "
          f"{'z':>8} {'p_raw':>9} {'p_bonf':>9} {'Sig':>5}")
    print(f"  {'-'*100}")
    for _, row in posthoc_df.iterrows():
        sig_flag = '***' if row['p_bonferroni'] < 0.001 else \
                   '**'  if row['p_bonferroni'] < 0.01  else \
                   '*'   if row['p_bonferroni'] < 0.05  else 'ns'
        print(f"  {row['group_1']:<26} {row['group_2']:<26} "
              f"{row['mean_ese_1']:>9.2f} {row['mean_ese_2']:>9.2f} "
              f"{row['z_statistic']:>8.3f} {row['p_raw']:>9.4f} "
              f"{row['p_bonferroni']:>9.4f} {sig_flag:>5}")

    summary = {
        'rq'          : rq_label,
        'test'        : test_name,
        'statistic'   : f_stat if use_parametric else h_stat,
        'df_or_k'     : f'{df_between},{df_within}' if use_parametric else k - 1,
        'p_value'     : p_val,
        'significant' : p_val < alpha,
        'effect_label': effect_label,
        'effect_size' : effect_val,
        'effect_interp': effect_interp,
        'n_total'     : n_total,
        'k_groups'    : k,
    }

    return summary, desc, norm_df, posthoc_df


# ─────────────────────────────────────────────────────────────────────────────
# STEP 1 — LOAD DATA
# ─────────────────────────────────────────────────────────────────────────────
print("\n[STEP 1] LOADING DATA")
print("-" * 80)

master_path = P2_PROCESSED / 'student_profiles_master.csv'
if not master_path.exists():
    print(f"\n  ERROR: {master_path} not found.")
    print("  Please run P2_02_learning_trajectories.py first.")
    exit(1)

master = pd.read_csv(master_path, low_memory=False)

# Restore ordered categoricals
PROFILE_ORDER = ['Low', 'Medium', 'High']
TRAJ_ORDER    = ['Steady High Performer', 'Stable Average',
                 'Improver', 'Decliner', 'Consistently Struggling']

master['profile_label'] = pd.Categorical(
    master['profile_label'], categories=PROFILE_ORDER, ordered=True
)
master['trajectory_label'] = pd.Categorical(
    master['trajectory_label'], categories=TRAJ_ORDER, ordered=True
)

print(f"  student_profiles_master : {len(master):,} rows | {master.shape[1]} cols")
print(f"  ESE % available         : {master['ese_percentage'].notna().sum():,}")
print(f"  RQ1 (engagement)        : {master['profile_label'].notna().sum():,} rows")
print(f"  RQ2 (trajectory)        : {master['trajectory_label'].notna().sum():,} rows")

# ─────────────────────────────────────────────────────────────────────────────
# STEP 2 — RQ3: ENGAGEMENT PROFILES vs ESE
# ─────────────────────────────────────────────────────────────────────────────
print("\n" + "=" * 80)
print("[STEP 2] RQ3 — ENGAGEMENT PROFILES vs ESE OUTCOMES")
print("=" * 80)

rq3_df = master[['profile_label', 'ese_percentage']].dropna().copy()

rq3_summary, rq3_desc, rq3_norm, rq3_posthoc = run_full_analysis(
    df        = rq3_df,
    group_col = 'profile_label',
    value_col = 'ese_percentage',
    rq_label  = 'RQ3: Engagement Profile vs ESE %'
)

# Save RQ3 outputs
rq3_desc.to_csv(P2_RESULTS / 'rq3_engagement_vs_ese_stats.csv', index=False)
rq3_posthoc.to_csv(P2_RESULTS / 'rq3_posthoc_dunn.csv', index=False)
print(f"\n  rq3_engagement_vs_ese_stats.csv saved")
print(f"  rq3_posthoc_dunn.csv saved")

# ─────────────────────────────────────────────────────────────────────────────
# STEP 3 — RQ4: TRAJECTORIES vs ESE
# ─────────────────────────────────────────────────────────────────────────────
print("\n" + "=" * 80)
print("[STEP 3] RQ4 — LEARNING TRAJECTORIES vs ESE OUTCOMES")
print("=" * 80)

rq4_df = master[master['trajectory_eligible'] == True][
    ['trajectory_label', 'ese_percentage']
].dropna().copy()

rq4_summary, rq4_desc, rq4_norm, rq4_posthoc = run_full_analysis(
    df        = rq4_df,
    group_col = 'trajectory_label',
    value_col = 'ese_percentage',
    rq_label  = 'RQ4: Learning Trajectory vs ESE %'
)

# Save RQ4 outputs
rq4_desc.to_csv(P2_RESULTS / 'rq4_trajectory_vs_ese_stats.csv', index=False)
rq4_posthoc.to_csv(P2_RESULTS / 'rq4_posthoc_dunn.csv', index=False)
print(f"\n  rq4_trajectory_vs_ese_stats.csv saved")
print(f"  rq4_posthoc_dunn.csv saved")

# ─────────────────────────────────────────────────────────────────────────────
# STEP 4 — KEY COMPARISON: Improver vs Steady High Performer (RQ4 core claim)
# ─────────────────────────────────────────────────────────────────────────────
print("\n" + "=" * 80)
print("[STEP 4] KEY COMPARISON — Improver vs Steady High Performer  (RQ4 Core Claim)")
print("=" * 80)
print("  Testing abstract claim: 'improving students often achieve outcomes")
print("  comparable to consistently high performers'")

shp = master[master['trajectory_label'] == 'Steady High Performer']['ese_percentage'].dropna()
imp = master[master['trajectory_label'] == 'Improver']['ese_percentage'].dropna()

if len(shp) > 0 and len(imp) > 0:
    u_stat, u_p = stats.mannwhitneyu(shp, imp, alternative='two-sided')

    print(f"\n  Steady High Performer : n={len(shp):,}  mean={shp.mean():.2f}%  "
          f"median={shp.median():.2f}%")
    print(f"  Improver              : n={len(imp):,}  mean={imp.mean():.2f}%  "
          f"median={imp.median():.2f}%")
    print(f"\n  Mann-Whitney U test (two-sided):")
    print(f"  U = {u_stat:.2f},  p = {u_p:.6f}")

    if u_p >= 0.05:
        conclusion = "No significant difference — SUPPORTS abstract claim"
    else:
        mean_diff = shp.mean() - imp.mean()
        conclusion = (f"Significant difference detected (Δmean = {mean_diff:.2f}%) "
                      f"— abstract claim partially supported")
    print(f"  Conclusion: {conclusion}")
else:
    print("  WARNING: Insufficient data for one or both groups.")

# Save combined normality results
rq3_norm['rq'] = 'RQ3'
rq4_norm['rq'] = 'RQ4'
norm_combined = pd.concat([rq3_norm, rq4_norm], ignore_index=True)
norm_combined.to_csv(P2_RESULTS / 'rq3_rq4_normality_tests.csv', index=False)
print(f"\n  rq3_rq4_normality_tests.csv saved")

# ─────────────────────────────────────────────────────────────────────────────
# STEP 5 — FIGURES
# ─────────────────────────────────────────────────────────────────────────────
print("\n[STEP 5] GENERATING FIGURES")
print("-" * 80)

PROFILE_COLORS = {
    'Low'    : '#E05C5C',
    'Medium' : '#F5A623',
    'High'   : '#4CAF7D',
}
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


def add_significance_brackets(ax, pairs, posthoc_df, y_positions, data_max):
    """Draw significance brackets between pairs on a boxplot."""
    for i, (g1, g2) in enumerate(pairs):
        row = posthoc_df[
            ((posthoc_df['group_1'] == str(g1)) & (posthoc_df['group_2'] == str(g2))) |
            ((posthoc_df['group_1'] == str(g2)) & (posthoc_df['group_2'] == str(g1)))
        ]
        if len(row) == 0:
            continue
        p = row['p_bonferroni'].values[0]
        sig = '***' if p < 0.001 else '**' if p < 0.01 else '*' if p < 0.05 else 'ns'
        if sig == 'ns':
            continue
        x1, x2 = y_positions[i]
        y  = data_max + (i + 1) * 4
        ax.plot([x1, x1, x2, x2], [y, y + 1, y + 1, y], lw=1.2, color='black')
        ax.text((x1 + x2) / 2, y + 1.2, sig, ha='center', va='bottom',
                fontsize=10, fontweight='bold')


# ── Figure 1: RQ3 — Boxplot ESE % by Engagement Profile ─────────────────────
fig, axes = plt.subplots(1, 2, figsize=(13, 6))
fig.suptitle('RQ3: ESE Outcomes by Engagement Profile', fontsize=14,
             fontweight='bold', y=1.01)

# Boxplot
data_rq3    = [rq3_df[rq3_df['profile_label'] == p]['ese_percentage'].dropna().values
               for p in PROFILE_ORDER]
labels_rq3  = PROFILE_ORDER
colors_rq3  = [PROFILE_COLORS[p] for p in PROFILE_ORDER]

bp = axes[0].boxplot(data_rq3, labels=labels_rq3, patch_artist=True,
                     medianprops={'color': 'black', 'linewidth': 2.5},
                     whiskerprops={'linewidth': 1.5},
                     capprops={'linewidth': 1.5})
for patch, c in zip(bp['boxes'], colors_rq3):
    patch.set_facecolor(c); patch.set_alpha(0.78)

# Overlay individual means
for i, vals in enumerate(data_rq3, start=1):
    axes[0].scatter(i, np.mean(vals), marker='D', color='white',
                    edgecolor='black', s=55, zorder=5, label='Mean' if i == 1 else '')

# Annotate n
for i, (label, vals) in enumerate(zip(labels_rq3, data_rq3), start=1):
    axes[0].text(i, axes[0].get_ylim()[0] - 3, f'n={len(vals):,}',
                 ha='center', fontsize=9, color='dimgray')

p_text = '< 0.001' if rq3_summary['p_value'] < 0.001 else f"{rq3_summary['p_value']:.4f}"

test_line = (
    f"{rq3_summary['test']}: "
    f"H={rq3_summary['statistic']:.2f}, "
    f"p={p_text}, "
    f"{rq3_summary['effect_label']}={rq3_summary['effect_size']:.3f} "
    f"[{rq3_summary['effect_interp']}]"
)
axes[0].set_title(f'ESE % by Engagement Profile\n{test_line}', fontsize=10)
axes[0].set_xlabel('Engagement Profile')
axes[0].set_ylabel('ESE Percentage (%)')
axes[0].legend(fontsize=9)

# Violin plot
parts = axes[1].violinplot(data_rq3, positions=range(1, len(PROFILE_ORDER) + 1),
                            showmedians=True, showmeans=False)
for i, (pc, c) in enumerate(zip(parts['bodies'], colors_rq3)):
    pc.set_facecolor(c); pc.set_alpha(0.65)
axes[1].set_xticks(range(1, len(PROFILE_ORDER) + 1))
axes[1].set_xticklabels(PROFILE_ORDER)
axes[1].set_title('ESE % Distribution by Profile\n(Violin Plot)')
axes[1].set_xlabel('Engagement Profile')
axes[1].set_ylabel('ESE Percentage (%)')

plt.tight_layout()
plt.savefig(P2_FIGURES / 'rq3_ese_by_profile_boxplot.png')
plt.close()
print(f"  rq3_ese_by_profile_boxplot.png saved")

# ── Figure 2: RQ4 — Boxplot ESE % by Trajectory ──────────────────────────────
short_traj_labels = ['Steady\nHigh', 'Stable\nAverage',
                     'Improver', 'Decliner', 'Consistently\nStruggling']
data_rq4   = [rq4_df[rq4_df['trajectory_label'] == t]['ese_percentage'].dropna().values
              for t in TRAJ_ORDER]
colors_rq4 = [TRAJ_COLORS[t] for t in TRAJ_ORDER]

fig, axes = plt.subplots(1, 2, figsize=(14, 6))
fig.suptitle('RQ4: ESE Outcomes by Learning Trajectory', fontsize=14,
             fontweight='bold', y=1.01)

bp = axes[0].boxplot(data_rq4, labels=short_traj_labels, patch_artist=True,
                     medianprops={'color': 'black', 'linewidth': 2.5},
                     whiskerprops={'linewidth': 1.5},
                     capprops={'linewidth': 1.5})
for patch, c in zip(bp['boxes'], colors_rq4):
    patch.set_facecolor(c); patch.set_alpha(0.78)

for i, vals in enumerate(data_rq4, start=1):
    axes[0].scatter(i, np.mean(vals), marker='D', color='white',
                    edgecolor='black', s=55, zorder=5)
for i, (label, vals) in enumerate(zip(short_traj_labels, data_rq4), start=1):
    axes[0].text(i, axes[0].get_ylim()[0] - 3, f'n={len(vals):,}',
                 ha='center', fontsize=8, color='dimgray')

p_text = '< 0.001' if rq4_summary['p_value'] < 0.001 else f"{rq4_summary['p_value']:.4f}"

test_line4 = (
    f"{rq4_summary['test']}: "
    f"H={rq4_summary['statistic']:.2f}, "
    f"p={p_text}, "
    f"{rq4_summary['effect_label']}={rq4_summary['effect_size']:.3f} "
    f"[{rq4_summary['effect_interp']}]"
)

axes[0].set_title(f'ESE % by Learning Trajectory\n{test_line4}', fontsize=10)
axes[0].set_xlabel('Learning Trajectory')
axes[0].set_ylabel('ESE Percentage (%)')

parts = axes[1].violinplot(data_rq4,
                            positions=range(1, len(TRAJ_ORDER) + 1),
                            showmedians=True)
for pc, c in zip(parts['bodies'], colors_rq4):
    pc.set_facecolor(c); pc.set_alpha(0.65)
axes[1].set_xticks(range(1, len(TRAJ_ORDER) + 1))
axes[1].set_xticklabels(short_traj_labels, fontsize=9)
axes[1].set_title('ESE % Distribution by Trajectory\n(Violin Plot)')
axes[1].set_xlabel('Learning Trajectory')
axes[1].set_ylabel('ESE Percentage (%)')

plt.tight_layout()
plt.savefig(P2_FIGURES / 'rq4_ese_by_trajectory_boxplot.png')
plt.close()
print(f"  rq4_ese_by_trajectory_boxplot.png saved")

# ── Figure 3: Post-hoc significance heatmaps ─────────────────────────────────
def plot_posthoc_heatmap(posthoc_df, groups, title, save_path, colors):
    n = len(groups)
    p_matrix = pd.DataFrame(np.ones((n, n)), index=groups, columns=groups)

    for _, row in posthoc_df.iterrows():
        g1, g2 = row['group_1'], row['group_2']
        if g1 in groups and g2 in groups:
            p_matrix.loc[g1, g2] = row['p_bonferroni']
            p_matrix.loc[g2, g1] = row['p_bonferroni']

    fig, ax = plt.subplots(figsize=(max(7, n * 1.5), max(6, n * 1.3)))

    # Color by significance level
    sig_matrix = p_matrix.applymap(
        lambda p: 3 if p < 0.001 else (2 if p < 0.01 else (1 if p < 0.05 else 0))
    )
    np.fill_diagonal(sig_matrix.values, -1)

    sns.heatmap(sig_matrix, annot=False, cmap='RdYlGn_r', vmin=-1, vmax=3,
                linewidths=1, linecolor='white', ax=ax, cbar=False)

    # Annotate with p-values and sig stars
    for i in range(n):
        for j in range(n):
            if i == j:
                ax.text(j + 0.5, i + 0.5, '—', ha='center', va='center',
                        fontsize=11, color='gray')
            else:
                p  = p_matrix.iloc[i, j]
                sig = '***' if p < 0.001 else '**' if p < 0.01 else '*' if p < 0.05 else 'ns'
                ax.text(j + 0.5, i + 0.5,
                        f'p={p:.3f}\n{sig}',
                        ha='center', va='center', fontsize=8.5,
                        color='white' if sig != 'ns' else 'dimgray',
                        fontweight='bold' if sig != 'ns' else 'normal')

    short = [g.replace(' ', '\n') for g in groups]
    ax.set_xticklabels(short, rotation=0, fontsize=9)
    ax.set_yticklabels(short, rotation=0, fontsize=9)

    legend_patches = [
        mpatches.Patch(color='#d73027', label='*** p < 0.001'),
        mpatches.Patch(color='#fc8d59', label='**  p < 0.01'),
        mpatches.Patch(color='#fee090', label='*   p < 0.05'),
        mpatches.Patch(color='#91cf60', label='ns  p ≥ 0.05'),
    ]
    ax.legend(handles=legend_patches, bbox_to_anchor=(1.02, 1),
              loc='upper left', fontsize=9, frameon=True)

    ax.set_title(title, fontweight='bold', pad=12)
    plt.tight_layout()
    plt.savefig(save_path)
    plt.close()


plot_posthoc_heatmap(
    rq3_posthoc, PROFILE_ORDER,
    'RQ3: Post-hoc Pairwise Comparisons (Dunn + Bonferroni)\nEngagement Profile vs ESE %',
    P2_FIGURES / 'rq3_posthoc_heatmap.png',
    PROFILE_COLORS
)
print(f"  rq3_posthoc_heatmap.png saved")

plot_posthoc_heatmap(
    rq4_posthoc, TRAJ_ORDER,
    'RQ4: Post-hoc Pairwise Comparisons (Dunn + Bonferroni)\nLearning Trajectory vs ESE %',
    P2_FIGURES / 'rq4_posthoc_heatmap.png',
    TRAJ_COLORS
)
print(f"  rq4_posthoc_heatmap.png saved")

# ── Figure 4: RQ4 Core Claim — Improver vs Steady High Performer ─────────────
if len(shp) > 0 and len(imp) > 0:
    fig, ax = plt.subplots(figsize=(8, 6))

    data_pair   = [shp.values, imp.values]
    labels_pair = ['Steady High\nPerformer', 'Improver']
    colors_pair = [TRAJ_COLORS['Steady High Performer'], TRAJ_COLORS['Improver']]

    bp = ax.boxplot(data_pair, labels=labels_pair, patch_artist=True,
                    medianprops={'color': 'black', 'linewidth': 2.5},
                    widths=0.45)
    for patch, c in zip(bp['boxes'], colors_pair):
        patch.set_facecolor(c); patch.set_alpha(0.78)

    for i, vals in enumerate(data_pair, start=1):
        ax.scatter(i, np.mean(vals), marker='D', color='white',
                   edgecolor='black', s=65, zorder=5)

    sig_label = ('ns — no significant difference' if u_p >= 0.05
                 else f'p = {u_p:.4f}')
    ymax = max(shp.max(), imp.max())
    ax.plot([1, 1, 2, 2], [ymax + 3, ymax + 5, ymax + 5, ymax + 3],
            lw=1.5, color='black')
    ax.text(1.5, ymax + 6, sig_label, ha='center', va='bottom',
            fontsize=11, fontweight='bold',
            color='green' if u_p >= 0.05 else 'red')

    ax.set_title('RQ4 Core Claim: Improver vs Steady High Performer\n'
                 f'Mann-Whitney U = {u_stat:.0f},  p = {u_p:.4f}',
                 fontweight='bold', pad=12)
    ax.set_ylabel('ESE Percentage (%)')
    ax.text(1, ax.get_ylim()[0] - 3, f'n={len(shp):,}',
            ha='center', fontsize=10, color='dimgray')
    ax.text(2, ax.get_ylim()[0] - 3, f'n={len(imp):,}',
            ha='center', fontsize=10, color='dimgray')

    plt.tight_layout()
    plt.savefig(P2_FIGURES / 'rq4_improver_vs_highperformer.png')
    plt.close()
    print(f"  rq4_improver_vs_highperformer.png saved")

# ─────────────────────────────────────────────────────────────────────────────
# FINAL SUMMARY
# ─────────────────────────────────────────────────────────────────────────────
elapsed = (datetime.now() - START_TIME).seconds

print("\n" + "=" * 80)
print("SCRIPT P2_03 COMPLETE — RQ3 & RQ4 ANSWERED")
print("=" * 80)

print(f"\n  RQ3 SUMMARY — Engagement Profile vs ESE %:")
print(f"    Test       : {rq3_summary['test']}")
print(f"    Statistic  : {rq3_summary['statistic']:.4f}")
print(f"    p-value    : {rq3_summary['p_value']:.6f}  "
      f"{'[SIGNIFICANT]' if rq3_summary['significant'] else '[NOT SIGNIFICANT]'}")
print(f"    Effect     : {rq3_summary['effect_label']} = {rq3_summary['effect_size']:.4f} "
      f"[{rq3_summary['effect_interp']}]")

print(f"\n  RQ4 SUMMARY — Learning Trajectory vs ESE %:")
print(f"    Test       : {rq4_summary['test']}")
print(f"    Statistic  : {rq4_summary['statistic']:.4f}")
print(f"    p-value    : {rq4_summary['p_value']:.6f}  "
      f"{'[SIGNIFICANT]' if rq4_summary['significant'] else '[NOT SIGNIFICANT]'}")
print(f"    Effect     : {rq4_summary['effect_label']} = {rq4_summary['effect_size']:.4f} "
      f"[{rq4_summary['effect_interp']}]")

print(f"\n  OUTPUTS SAVED:")
print(f"    results/paper2/rq3_engagement_vs_ese_stats.csv")
print(f"    results/paper2/rq3_posthoc_dunn.csv")
print(f"    results/paper2/rq4_trajectory_vs_ese_stats.csv")
print(f"    results/paper2/rq4_posthoc_dunn.csv")
print(f"    results/paper2/rq3_rq4_normality_tests.csv")
print(f"    results/paper2/figures/rq3_ese_by_profile_boxplot.png")
print(f"    results/paper2/figures/rq3_posthoc_heatmap.png")
print(f"    results/paper2/figures/rq4_ese_by_trajectory_boxplot.png")
print(f"    results/paper2/figures/rq4_posthoc_heatmap.png")
print(f"    results/paper2/figures/rq4_improver_vs_highperformer.png")
print(f"\n  Time elapsed : {elapsed}s")
print(f"\n  NEXT : Write results section using outputs from")
print(f"         rq3_engagement_vs_ese_stats.csv")
print(f"         rq3_posthoc_dunn.csv")
print(f"         rq4_trajectory_vs_ese_stats.csv")
print(f"         rq4_posthoc_dunn.csv")
print("=" * 80)
