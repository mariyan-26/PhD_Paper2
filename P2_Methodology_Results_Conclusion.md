# Methodology, Results and Conclusion
# Paper 2: Uncovering the Learning Patterns and Behavioral Trajectories in
# Continuous Assessment Beyond Average Performance

================================================================================

# 3. Methodology

## 3.1 Research Design

This study adopts a quantitative, descriptive-analytical research design grounded in learning analytics. The analytical framework combines rule-based descriptive classification for engagement profiling, linear regression-based trajectory analysis for learning pattern identification, and non-parametric inferential statistics for group comparisons. This design is consistent with established approaches in learning analytics research that prioritise interpretability and actionability over algorithmic complexity, particularly in institutional contexts where findings are intended to inform pedagogical intervention (Bergdahl et al., 2024; Namoun & Alshanqiti, 2021).

The unit of analysis is the student-course enrollment pair, reflecting the fact that a single student may enroll in multiple courses and may exhibit different engagement profiles and learning trajectories across courses. This approach preserves the course-level granularity of formative assessment data and avoids the aggregation bias that would result from collapsing multi-course students into a single institutional-level record.

---

## 3.2 Institutional Context and Data Source

The study was conducted at Kristu Jayanti College (Autonomous), Bengaluru, India, an institution affiliated with Bangalore North University. The Moodle Learning Management System is used as the primary platform for continuous internal assessment (CIA), which constitutes 40% of the total course grade. The End Semester Examination (ESE), administered through a separate institutional ERP system, constitutes the remaining 60%. This structural separation of formative (LMS-based) and summative (ERP-based) assessment creates a natural research design opportunity to examine the relationship between LMS engagement patterns and summative examination performance.

Data were extracted from three institutional sources for the Fall 2024 academic semester:

- **student_course_master.csv** — student enrollment records including course metadata, programme information, and ESE marks
- **quiz_performance.csv** — quiz attempt-level data including scores, attempt timestamps, and completion status
- **final_grades.csv** — Moodle composite grade records used as reference only

Following data cleaning (detailed in Section 3.3), the final analytical dataset comprised 18,363 valid student-course enrollment records across 29 courses, drawn from undergraduate (UG) and postgraduate (PG) programmes spanning the Faculties of Science, Commerce, Management, and Arts.

---

## 3.3 Data Cleaning and Preparation

Data cleaning followed established decisions from prior institutional data work and applied the following rules consistently:

**Student records:**
- Retained only records categorised as 'Academic Course' (excluded Add-On and Refresher programmes, which carry no ESE component)
- Excluded faculty records (Group = 'FACULTIES')
- Excluded students with absent (AB) or null ESE marks, as these records have no summative outcome to analyse
- ESE percentage was computed as: ESE% = (ESE Obtained Marks / ESE Maximum Marks) × 100, clipped to the range 0–100

**Quiz records:**
- Retained only 'finished' quiz attempts
- Null percentage scores in finished attempts were treated as zero (consistent with an attempt made but not recorded)
- Where a student had multiple attempts at the same quiz, only the best attempt (highest score) was retained, consistent with the principle that best-attempt performance reflects demonstrated capability
- Time-on-task values outside the range 0–14,400 seconds were treated as invalid and excluded from time-related features

**Quiz score scale:** All quiz scores in the Moodle dataset are recorded as percentage scores (0–100), normalised against the maximum marks available per quiz. The maximum marks per quiz in this institution is 10, and Moodle records percentage_score directly. No additional normalisation was required.

Following cleaning, 18,363 student-course enrollment records were retained. Of these, 16,949 (92.3%) had at least one associated quiz attempt, and 15,079 (82.1%) had three or more attempts, making them eligible for trajectory analysis.

---

## 3.4 Engagement Profile Classification (RQ1)

### 3.4.1 Operationalisation of Engagement

Student engagement was operationalised as a composite score combining two dimensions: quiz participation and quiz performance. This two-dimensional operationalisation was adopted in preference to participation-only or performance-only approaches, on the grounds that meaningful engagement requires both the behavioural act of attempting assessments and the cognitive effort reflected in performance outcomes (Johar et al., 2023; Bergdahl et al., 2024).

The composite engagement score was defined as:

**Engagement Score = (0.6 × Participation Rate) + (0.4 × Average Quiz Score %)**

where:

- **Participation Rate** = (Quizzes Attempted / Max Quizzes in Course) × 100
- **Average Quiz Score %** = Mean of best-attempt percentage scores across all quizzes attempted by the student in a given course (already on a 0–100 scale)
- **Max Quizzes in Course** = Maximum number of distinct quizzes attempted by any student in that course, derived empirically from the data rather than hardcoded

The 60/40 weighting reflects the theoretical priority of behavioural participation over performance quality as the primary indicator of engagement. This weighting is consistent with findings from Johar et al. (2023), who identified participation-based metrics as more reliably predictive of academic outcomes than performance-based metrics alone. The performance component (40%) ensures that students who attempt quizzes but achieve near-zero scores are not classified identically to high-performing, high-participating students. The trajectory analysis (RQ2) independently captures the performance progression dimension, which avoids conceptual overlap between engagement profiling and learning trajectory classification.

Students who attempted zero quizzes in a course were assigned an engagement score of 0 and classified as Low engagement. This decision treats non-participation as the lowest form of engagement, consistent with the LMS engagement literature (Bergdahl et al., 2024).

### 3.4.2 Profile Classification Thresholds

Students were classified into three engagement profiles based on their composite engagement score:

| Profile | Composite Score Range | Interpretation |
|---|---|---|
| Low | 0 – 39.99 | Disengaged or minimally engaged |
| Medium | 40.00 – 59.99 | Moderately engaged |
| High | 60.00 – 100.00 | Actively engaged |

These thresholds were defined a priori based on theoretical and pedagogical grounds. The Low threshold (< 40) aligns with the standard fail threshold used in continuous assessment in the institutional context. The High threshold (≥ 60) corresponds to the minimum passing standard for the end semester examination, providing a consistent interpretive framework across assessment components.

---

## 3.5 Learning Trajectory Classification (RQ2)

### 3.5.1 Eligibility Criterion

Trajectory analysis requires a minimum temporal sequence of quiz attempts to compute a meaningful trend. Students with fewer than three quiz attempts in a course were excluded from trajectory analysis. This threshold was selected as the minimum number of data points required to fit a linear regression with any meaningful slope estimate, consistent with standard practice in time-series classification in educational data mining (Hung et al., 2021). Excluded students (n = 1,870; 11.0% of students with any quiz data) were retained in the engagement profile analysis (RQ1) but removed from trajectory analysis (RQ2).

### 3.5.2 Slope Computation

For each eligible student-course pair, a linear regression was fitted to the student's quiz percentage scores ordered chronologically by attempt timestamp (attempt_start). The slope of this regression line — representing the average rate of change in quiz score per quiz across the semester — served as the primary trajectory indicator.

Formally, for a student with quiz scores s₁, s₂, ..., sₙ at positions x = 1, 2, ..., n:

**Slope (β₁) = Σ[(xᵢ - x̄)(sᵢ - s̄)] / Σ[(xᵢ - x̄)²]**

A positive slope indicates improving quiz performance across the semester; a negative slope indicates declining performance; a slope near zero indicates stable performance. Scores were analysed on the 0–100 percentage scale.

### 3.5.3 Data-Driven Slope Thresholds

Rather than applying fixed arbitrary thresholds to define meaningful improvement or decline, a data-driven approach was adopted. The mean and standard deviation of all computed slopes across the eligible sample were calculated:

- Mean slope (μ) = −0.70
- Standard deviation of slopes (σ) = 5.55

Trajectory thresholds were set at one standard deviation above and below the mean:

- **Improver threshold**: slope > μ + σ = +4.85
- **Decliner threshold**: slope < μ − σ = −6.25
- **Stable range**: −6.25 ≤ slope ≤ +4.85

This approach ensures that Improver and Decliner classifications reflect statistically meaningful deviations from the population norm rather than arbitrary cutpoints, and adapts automatically to the empirical distribution of trends in the dataset.

### 3.5.4 Trajectory Classification Rules

Students were classified into one of five trajectory types based on the combination of slope direction and average quiz score level. Slope direction took priority over average score level in cases where both criteria applied simultaneously:

| Trajectory | Average Quiz Score | Slope | Priority |
|---|---|---|---|
| Steady High Performer | ≥ 60% | Stable | Score-based |
| Stable Average | 40% – 59.99% | Stable | Score-based |
| Consistently Struggling | < 40% | Stable | Score-based |
| Improver | Any | > +4.85 | Slope-based (overrides) |
| Decliner | Any | < −6.25 | Slope-based (overrides) |

The slope-priority rule means that a student with a high average score but a strongly negative slope is classified as a Decliner rather than a Steady High Performer. This reflects the theoretical priority of trajectory direction over current level when characterising learning dynamics.

---

## 3.6 Statistical Analysis (RQ3 and RQ4)

### 3.6.1 Normality and Variance Testing

Prior to selecting the primary inferential test, normality of ESE percentage distributions within each group was assessed using the Shapiro-Wilk test for groups with n ≤ 5,000, and the Kolmogorov-Smirnov test for larger groups. Levene's test was applied to assess homogeneity of variance across groups. These tests informed the choice between parametric (One-Way ANOVA) and non-parametric (Kruskal-Wallis H) group comparison methods.

### 3.6.2 Primary Inferential Test

Where normality and equal variance assumptions were met, One-Way ANOVA was applied. Where either assumption was violated — as anticipated given the large sample size and known negative skew of institutional ESE distributions — the Kruskal-Wallis H test was employed as the non-parametric equivalent of one-way ANOVA for comparing ESE outcomes across groups.

### 3.6.3 Effect Size

Effect size was quantified using epsilon-squared (ε²) for Kruskal-Wallis results, computed as:

**ε² = (H − k + 1) / (n − k)**

where H is the Kruskal-Wallis statistic, k is the number of groups, and n is the total sample size. Epsilon-squared values were interpreted using conventional benchmarks: small (ε² ≥ 0.01), medium (ε² ≥ 0.06), and large (ε² ≥ 0.14).

### 3.6.4 Post-hoc Comparisons

Following a significant Kruskal-Wallis result, pairwise group comparisons were conducted using Dunn's test with Bonferroni correction for multiple comparisons. This combination was selected in preference to alternatives (e.g., Conover's test, Steel-Dwass) due to its wider acceptance in educational research and its direct compatibility with the Kruskal-Wallis framework.

### 3.6.5 Key Pairwise Comparison

To test the central claim of the study — that Improvers achieve examination outcomes comparable to Steady High Performers — a dedicated Mann-Whitney U test was conducted comparing ESE scores between these two trajectory groups. This two-sided test was applied as a focused hypothesis test independent of the broader Kruskal-Wallis analysis.

A significance level of α = 0.05 was adopted throughout. All analyses were conducted in Python 3 using the SciPy, pandas, and NumPy libraries.

---

## 3.7 Analytical Pipeline Summary

The complete analytical pipeline proceeded as follows:

1. **P2_01_engagement_profiles.py** — Reads cleaned student and quiz data; computes participation rate, average quiz score, and composite engagement score; classifies students into Low/Medium/High profiles; outputs engagement_profiles.csv

2. **P2_02_learning_trajectories.py** — Filters eligible students (≥ 3 quizzes); computes OLS slope per student-course; derives data-driven thresholds; classifies five trajectory types; outputs learning_trajectories.csv and student_profiles_master.csv

3. **P2_03_statistical_analysis.py** — Loads student_profiles_master.csv; runs normality/variance tests; applies Kruskal-Wallis + Dunn's post-hoc for RQ3 and RQ4; computes effect sizes; outputs all statistical result tables and publication figures

================================================================================

# 4. Results

## 4.1 RQ1 — Student Engagement Profiles

A total of 18,363 student-course enrollment records were analysed to identify distinct engagement profiles across 29 courses in the Fall 2024 semester. The maximum number of distinct quizzes per course ranged from 1 to 18 (mean = 4.7), reflecting substantial variation in formative assessment intensity across the curriculum. Of the 18,363 students, 1,794 (9.8%) recorded zero quiz attempts and were assigned a composite engagement score of 0.

The composite engagement score ranged from 0 to 100 across the cohort, with a mean of 78.58 (SD = 29.45) and a median of 92.00. The pronounced gap between mean and median, together with the large standard deviation, indicates a heavily left-skewed distribution dominated by a high-engagement majority with a smaller low-engagement tail.

Applying the predefined thresholds, three engagement profiles were identified and their distributions are presented in Table 1.

---

**Table 1. Engagement Profile Distribution**

| Profile | n | % | Mean Engagement Score | Mean Participation Rate (%) | Mean Quiz Score (%) | Mean ESE (%) |
|---|---|---|---|---|---|---|
| Low | 2,154 | 11.7 | 4.97 | 2.72 | 8.34 | 66.19 |
| Medium | 879 | 4.8 | 50.69 | 34.88 | 74.40 | 70.22 |
| High | 15,330 | 83.5 | 90.52 | 96.23 | 81.94 | 73.18 |
| **Total** | **18,363** | **100** | | | | |

*Note. Engagement Score = 0.6 × Participation Rate + 0.4 × Avg Quiz Score %. ESE = End Semester Examination.*

---

The High engagement group accounted for the substantial majority of the cohort (83.5%, n = 15,330), characterised by near-complete quiz participation (mean = 96.23%) and strong performance (mean quiz score = 81.94%). The Low engagement group (11.7%, n = 2,154) exhibited near-zero participation (mean = 2.72%) and near-zero quiz performance (mean = 8.34%), with 1,794 of its members recording no quiz attempts at all. The Medium engagement group was notably small (4.8%, n = 879), suggesting that partial or moderate engagement is an uncommon sustained behavioural state in this cohort.

A preliminary monotonic relationship was observed between engagement profile and mean ESE percentage (Low = 66.19%, Medium = 70.22%, High = 73.18%), with the 6.99 percentage point gap between Low and High engagement groups warranting formal statistical examination in RQ3.

---

## 4.2 RQ2 — Learning Trajectories

Of the 16,949 student-course pairs with at least one quiz attempt, 15,079 (89.0%) met the minimum threshold of three quiz attempts and were included in trajectory analysis. The remaining 1,870 pairs (11.0%) were retained in engagement profile analysis but excluded from trajectory classification.

Linear regression slopes across all eligible pairs had a mean of −0.70 (SD = 5.55, min = −50.00, max = +50.00), indicating a slight overall downward trend in quiz performance across the semester cohort-wide. Data-driven thresholds were established at:

- Improver: slope > +4.85 (mean + 1 SD)
- Decliner: slope < −6.25 (mean − 1 SD)
- Stable range: −6.25 to +4.85

Five learning trajectories were identified and their distributions are presented in Table 2.

---

**Table 2. Learning Trajectory Distribution**

| Trajectory | n | % | Mean Quiz Score (%) | Mean Slope | Mean ESE (%) |
|---|---|---|---|---|---|
| Steady High Performer | 11,625 | 77.1 | 85.42 | −0.72 | 73.91 |
| Improver | 1,431 | 9.5 | 75.96 | +9.54 | 68.06 |
| Decliner | 1,470 | 9.8 | 68.40 | −10.41 | 76.33 |
| Stable Average | 418 | 2.8 | 51.23 | −1.07 | 67.28 |
| Consistently Struggling | 135 | 0.9 | 28.64 | −0.93 | 65.02 |
| **Total** | **15,079** | **100** | | | |

*Note. Slope = change in quiz score per quiz (0–100 scale). Improver threshold: slope > +4.85; Decliner threshold: slope < −6.25.*

---

Steady High Performers dominated the cohort (77.1%, n = 11,625), characterised by consistently high quiz scores (85.42%) and a near-flat slope (−0.72). Improvers (9.5%, n = 1,431) and Decliners (9.8%, n = 1,470) formed comparably-sized groups with strongly positive (+9.54) and strongly negative (−10.41) slopes respectively. Stable Average students (2.8%, n = 418) maintained moderate quiz performance across the semester, while Consistently Struggling students (0.9%, n = 135) exhibited persistently low scores (28.64%) with negligible slope variation.

A notable preliminary observation was that Decliners recorded the highest mean ESE percentage (76.33%) across all five trajectory groups — higher even than Steady High Performers (73.91%). This counterintuitive pattern was formally examined in RQ4.

---

## 4.3 RQ3 — Engagement Profiles and ESE Outcomes

### 4.3.1 Assumption Testing

Shapiro-Wilk tests confirmed non-normality in the Low (W = 0.990, p < 0.001) and Medium (W = 0.978, p < 0.001) engagement groups, and the Kolmogorov-Smirnov test confirmed non-normality in the High engagement group (D = 0.067, p < 0.001). Levene's test indicated unequal variances across groups (F = 41.67, p < 0.001). Accordingly, the Kruskal-Wallis H test was applied.

### 4.3.2 Kruskal-Wallis Result

A statistically significant difference in ESE outcomes was found across engagement profiles (H(2) = 331.79, p < 0.001, ε² = 0.018). Descriptive statistics are presented in Table 3.

---

**Table 3. ESE Outcomes by Engagement Profile**

| Profile | n | Mean ESE (%) | Median ESE (%) | SD | IQR |
|---|---|---|---|---|---|
| Low | 2,154 | 66.19 | 67.50 | 15.28 | 19.71 |
| Medium | 879 | 70.22 | 72.00 | 13.50 | 16.66 |
| High | 15,330 | 73.18 | 72.50 | 15.65 | 24.00 |

*Note. Kruskal-Wallis H(2) = 331.79, p < 0.001, ε² = 0.018 [Small effect].*

---

### 4.3.3 Post-hoc Comparisons

Dunn's test with Bonferroni correction confirmed significant differences across all three pairwise comparisons (Table 4).

---

**Table 4. Post-hoc Comparisons — Engagement Profiles**

| Comparison | Mean ESE 1 (%) | Mean ESE 2 (%) | z | p (Bonferroni) | Sig. |
|---|---|---|---|---|---|
| Low vs Medium | 66.19 | 70.22 | −6.69 | < 0.001 | *** |
| Low vs High | 66.19 | 73.18 | −18.00 | < 0.001 | *** |
| Medium vs High | 70.22 | 73.18 | −4.23 | < 0.001 | *** |

*Note. *** p < 0.001.*

---

## 4.4 RQ4 — Learning Trajectories and ESE Outcomes

### 4.4.1 Assumption Testing

Normality tests were non-significant for all five trajectory groups (all p < 0.001), and Levene's test indicated unequal variances (F = 39.70, p < 0.001). The Kruskal-Wallis H test was applied.

### 4.4.2 Kruskal-Wallis Result

A statistically significant difference in ESE outcomes was found across trajectory groups (H(4) = 301.47, p < 0.001, ε² = 0.020). Descriptive statistics are presented in Table 5.

---

**Table 5. ESE Outcomes by Learning Trajectory**

| Trajectory | n | Mean ESE (%) | Median ESE (%) | SD | IQR |
|---|---|---|---|---|---|
| Steady High Performer | 11,518 | 73.91 | 73.33 | 15.66 | 23.34 |
| Decliner | 1,440 | 76.33 | 76.67 | 16.87 | 30.00 |
| Improver | 1,389 | 68.06 | 70.00 | 13.24 | 16.67 |
| Stable Average | 377 | 67.28 | 66.67 | 14.48 | 16.67 |
| Consistently Struggling | 133 | 65.02 | 62.86 | 17.80 | 24.67 |

*Note. Kruskal-Wallis H(4) = 301.47, p < 0.001, ε² = 0.020 [Small effect]. Ranked by Mean ESE descending.*

---

### 4.4.3 Post-hoc Comparisons

Dunn's test with Bonferroni correction identified 8 of 10 pairwise comparisons as statistically significant. Table 6 presents all pairwise results.

---

**Table 6. Post-hoc Comparisons — Learning Trajectories**

| Comparison | Mean ESE 1 (%) | Mean ESE 2 (%) | z | p (Bonferroni) | Sig. |
|---|---|---|---|---|---|
| Steady High Performer vs Decliner | 73.91 | 76.33 | −5.79 | < 0.001 | *** |
| Steady High Performer vs Stable Average | 73.91 | 67.28 | +8.00 | < 0.001 | *** |
| Steady High Performer vs Improver | 73.91 | 68.06 | +12.54 | < 0.001 | *** |
| Steady High Performer vs Consistently Struggling | 73.91 | 65.02 | +6.12 | < 0.001 | *** |
| Decliner vs Stable Average | 76.33 | 67.28 | +10.03 | < 0.001 | *** |
| Decliner vs Improver | 76.33 | 68.06 | +13.77 | < 0.001 | *** |
| Decliner vs Consistently Struggling | 76.33 | 65.02 | +7.67 | < 0.001 | *** |
| Stable Average vs Improver | 67.28 | 68.06 | −1.08 | 1.000 | ns |
| Stable Average vs Consistently Struggling | 67.28 | 65.02 | +1.14 | 1.000 | ns |
| Improver vs Consistently Struggling | 68.06 | 65.02 | +1.95 | 0.507 | ns |

*Note. *** p < 0.001; ns = not significant. Bonferroni-corrected over 10 comparisons.*

---

### 4.4.4 Key Comparison: Improver vs Steady High Performer

A dedicated Mann-Whitney U test directly compared ESE outcomes between Improvers and Steady High Performers to test the study's central proposition that improving students achieve outcomes comparable to consistently high performers. The test revealed a statistically significant difference (U = 9,652,709, p < 0.001), with Steady High Performers outperforming Improvers by a mean of 5.85 percentage points (73.91% vs 68.06%). The study's central proposition is therefore partially — but not fully — supported: Improvers outperform lower trajectory groups but do not match the ESE outcomes of students who maintained consistently high performance throughout the semester.

---

## 4.5 Interpretation of Findings

### 4.5.1 Engagement Polarisation

The distribution of engagement profiles reveals a strongly polarised cohort rather than a gradient of engagement levels. The scarcity of Medium engagement students (4.8%) and the dominance of High engagement students (83.5%) suggest that in this institutional context — where quiz performance contributes directly to the continuous internal assessment grade — most students either engage fully or disengage almost entirely. This polarisation is reinforced by the 9.8% of students recording zero quiz attempts. From a practical standpoint, this bimodal distribution implies that engagement interventions should be calibrated for two qualitatively distinct target groups: proactive outreach for non-participants and early-declining students, and enrichment or challenge for the large high-engagement majority.

### 4.5.2 The Decliner Paradox

The most striking finding of the study is the superior ESE performance of Decliners (mean ESE = 76.33%) relative to all other trajectory groups, including Steady High Performers (73.91%). Decliners are students whose quiz scores decline significantly across the semester (mean slope = −10.41) but who, on average, entered the quiz sequence with relatively strong performance (mean quiz score = 68.40%). Three interpretive mechanisms are plausible: (i) Decliners may have robust prior knowledge that supports strong ESE performance independently of continued formative engagement; (ii) declining quiz scores may reflect strategic effort reallocation toward ESE preparation rather than genuine knowledge deterioration; and (iii) the quiz instrument itself may be insensitive to the type of learning that is captured by the ESE. Regardless of mechanism, the practical implication is clear: declining quiz scores should not be treated as an unambiguous at-risk signal. EWS frameworks that flag all students with declining formative engagement as at-risk will generate false positives among a high-performing Decliner sub-group.

### 4.5.3 Partial Support for Multiple Pathways

Improvers demonstrate that positive within-semester change in quiz performance is associated with meaningfully better ESE outcomes than stable underperformance or consistent struggle. However, the 5.85 percentage point gap between Improvers and Steady High Performers, confirmed as statistically significant, indicates that improvement during the semester does not fully compensate for the cumulative advantage of sustained high performance from the outset. The non-significant differences among Improvers, Stable Average, and Consistently Struggling students indicate that these three groups — despite different trajectory shapes — achieve broadly similar ESE outcomes. This convergence at the lower end of the outcome distribution suggests that the nature and quality of engagement, not merely its direction of change, is the critical determinant of summative performance.

### 4.5.4 Small Effect Sizes in Context

Both RQ3 (ε² = 0.018) and RQ4 (ε² = 0.020) yielded small effect sizes despite highly significant p-values. This pattern — common in large-sample educational data studies — reflects the fact that engagement and trajectory indicators, while reliably associated with ESE outcomes, account for only a modest proportion of variance in examination performance. Factors outside the LMS environment — including prior academic preparation, attendance, study habits, and socioeconomic conditions — contribute substantially to ESE performance and are not captured by quiz interaction data alone. The small effect sizes therefore argue for the integration of LMS-based engagement indicators with broader student data in comprehensive predictive and intervention frameworks, rather than their use as standalone risk signals.

================================================================================

# 5. Conclusion

## 5.1 Summary of Findings

This study set out to examine whether students exhibit distinct and meaningfully different patterns of engagement and learning behaviour in online continuous assessment, and whether these patterns are differentially associated with final examination outcomes. Analysing 18,363 student-course enrollment records from Fall 2024 across a large Indian higher education institution, the study addressed four research questions through engagement profiling, trajectory analysis, and non-parametric group comparison.

The principal findings are as follows:

**RQ1** — Three engagement profiles were identified: High (83.5%), Low (11.7%), and Medium (4.8%). The distribution was strongly polarised, with most students either fully engaged or substantially disengaged, and limited sustained middle ground.

**RQ2** — Five learning trajectories were identified: Steady High Performers (77.1%), Decliners (9.8%), Improvers (9.5%), Stable Average (2.8%), and Consistently Struggling (0.9%). The cohort exhibited a slight overall negative trend in quiz scores across the semester (mean slope = −0.70).

**RQ3** — Engagement profiles were significantly associated with ESE outcomes (H(2) = 331.79, p < 0.001), with all pairwise profile comparisons reaching significance after Bonferroni correction. Higher engagement was monotonically associated with higher ESE scores, though the effect size was small (ε² = 0.018).

**RQ4** — Learning trajectories were significantly associated with ESE outcomes (H(4) = 301.47, p < 0.001, ε² = 0.020). Counter to the study's initial proposition, Decliners achieved the highest mean ESE scores (76.33%), outperforming Steady High Performers (73.91%). Improvers did not achieve outcomes statistically equivalent to Steady High Performers (mean difference = 5.85%, p < 0.001), partially — but not fully — confirming the multiple-pathways proposition.

---

## 5.2 Theoretical Contributions

This study makes three principal theoretical contributions to the learning analytics and educational technology literatures.

**First**, it establishes the Decliner trajectory as a theoretically important and empirically consequential group that has received insufficient attention in the learning analytics literature. The finding that declining formative engagement is associated with superior — not inferior — summative outcomes represents a significant challenge to the prevailing assumption that sustained LMS engagement is a prerequisite for academic success, and has direct implications for the design and calibration of Early Warning Systems.

**Second**, it provides fine-grained empirical evidence for the partial — rather than full — equivalence of improvement trajectories and sustained high performance trajectories. The Improver group demonstrates that within-semester recovery is positively associated with summative outcomes, but the persistent gap with Steady High Performers argues for the cumulative advantage of early and sustained engagement that cannot be fully replicated by late-semester correction.

**Third**, it contributes to the engagement polarisation literature by documenting that high-stakes LMS integration drives a bimodal distribution of engagement behaviour, with implications for how institutions design and monitor formative assessment systems. The near-absence of a stable Medium engagement group challenges classification frameworks that assume a meaningful middle tier of engagement, suggesting that binary (engaged / disengaged) monitoring may be more practically useful than a three-tiered profile approach in contexts where assessment is grade-contributing.

---

## 5.3 Practical Implications

The findings support a differentiated approach to student support and intervention in which strategy is calibrated to the engagement profile and trajectory type of the target student, rather than applied uniformly:

- **High engagement — Steady High Performers** require minimal academic intervention. Resources are better directed toward enrichment, peer leadership opportunities, and advanced academic development.

- **Decliners** should be monitored carefully but should not be automatically flagged as at-risk. EWS systems should incorporate ESE performance monitoring alongside declining LMS signals to distinguish genuine at-risk students from strategic disengagers with strong foundational knowledge.

- **Improvers** benefit most from early intervention — before their improvement begins — given that recovery trajectories do not fully close the gap with consistent performers. Early formative feedback, academic coaching, and timely notification of performance standing are likely to be more impactful than mid-semester remediation.

- **Stable Average and Consistently Struggling students** share broadly similar summative outcomes despite different trajectory shapes. For these students, qualitative engagement with course content — not merely participation — is the critical intervention target. Study skills support, subject-specific tutoring, and motivational coaching are appropriate strategies.

- **Non-participating students** (zero quiz attempts) represent the most urgent intervention priority, requiring direct personal outreach from academic advisors before the first assessment period closes.

---

## 5.4 Limitations and Future Directions

The study is subject to several limitations. The data are drawn from a single semester at one institution, restricting temporal and contextual generalisability. The composite engagement score, while theoretically grounded, applies fixed weights (60/40) that may not be optimal across different course types or student populations; future work should explore adaptive or data-driven weighting schemes. The linear trajectory model does not capture non-linear patterns of learning behaviour, such as U-shaped or inverted-U trajectories that may be theoretically meaningful. The small effect sizes in both RQ3 and RQ4 indicate that substantial unexplained variance in ESE outcomes remains — future studies should integrate engagement and trajectory data with prior academic performance, attendance records, and demographic variables to build more comprehensive predictive models.

Future research should also investigate the Decliner trajectory in greater depth. Qualitative or mixed-methods follow-up — including student interviews or think-aloud protocols — would clarify whether Decliner behaviour reflects deliberate strategic effort reallocation, knowledge consolidation, or disengagement from a weakly motivating assessment format. Additionally, the longitudinal extension of this analysis across multiple semesters would enable examination of whether engagement profiles and trajectories are stable individual characteristics or context-dependent responses to specific course structures.

---

## 5.5 Connection to the Broader Research Programme

This study constitutes Paper 2 of a two-paper dissertation strategy investigating the relationship between LMS-based formative assessment data and academic outcomes. While Paper 1 established quiz-based features as moderate predictors of ESE performance through regression and feature importance analysis, Paper 2 moves beyond aggregate prediction to characterise the diversity of pathways students follow through continuous assessment. Together, the two papers provide complementary evidence — predictive and descriptive — for the design of the hybrid Rule-Based System and Proximal Policy Optimisation (RBS-PPO) adaptive learning framework that is the primary contribution of the doctoral research. The engagement profiles and trajectory labels produced in this study are directly deployable as state variables in the RBS-PPO model: rule-based conditions can encode at-risk states (Low engagement, Consistent Struggle, early Decliner signals), while the reinforcement learning component can learn optimal, trajectory-sensitive intervention sequences from historical outcome data. This conceptual bridge from descriptive classification to adaptive intervention represents the ultimate applied contribution of the present work.
