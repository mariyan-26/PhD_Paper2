# Results

## 4.1 RQ1 — Student Engagement Profiles

A total of 18,363 student-course enrollment records were analysed to identify distinct engagement profiles. The composite engagement score — combining quiz participation rate (60%) and average quiz score percentage (40%) — ranged from 0 to 100 across the cohort, with a mean of 78.58 (SD = 29.45) and a median of 92.00, indicating a pronounced left-skewed distribution.

Applying the predefined thresholds (Low: 0–39.99; Medium: 40–59.99; High: 60–100), three distinct engagement profiles emerged (Table 1).

---

**Table 1. Engagement Profile Distribution (RQ1)**

| Profile | n | % | Mean Engagement Score | Mean Participation Rate | Mean Quiz Score (%) | Mean ESE (%) |
|---|---|---|---|---|---|---|
| Low | 2,154 | 11.7 | 4.97 | 2.72 | 8.34 | 66.19 |
| Medium | 879 | 4.8 | 50.69 | 34.88 | 74.40 | 70.22 |
| High | 15,330 | 83.5 | 90.52 | 96.23 | 81.94 | 73.18 |
| **Total** | **18,363** | **100** | | | | |

*Note. ESE = End Semester Examination. Engagement Score = 0.6 × Participation Rate + 0.4 × Avg Quiz Score %.*

---

The majority of students (83.5%, n = 15,330) were classified as High engagement, characterised by near-complete quiz participation (mean participation rate = 96.23%) and strong average quiz performance (mean = 81.94%). The Low engagement group accounted for 11.7% (n = 2,154) of enrollments, with a mean engagement score of 4.97, reflecting minimal participation (mean participation rate = 2.72%) and negligible quiz performance (mean = 8.34%). Of these, 1,794 students (9.8% of the total cohort) recorded zero quiz attempts and were assigned an engagement score of 0. The Medium engagement group was the smallest, comprising 4.8% (n = 879) of enrollments, with moderate participation (34.88%) and substantially higher quiz performance (74.40%) relative to their participation level.

The bimodal character of the engagement score distribution — with a dominant High cluster and a secondary Low cluster — suggests that most students adopted a consistent pattern of either full engagement or near-complete disengagement, with limited intermediate engagement behaviour. Preliminary inspection revealed a monotonically increasing association between engagement profile and mean ESE percentage (Low = 66.19%, Medium = 70.22%, High = 73.18%), which was examined statistically in RQ3.

---

## 4.2 RQ2 — Learning Trajectories

Trajectory analysis was restricted to student-course pairs with a minimum of three quiz attempts, yielding 15,079 eligible pairs (89.0% of the 16,949 pairs with any quiz data). The 1,870 ineligible pairs (11.0%) were retained in the engagement profile analysis (RQ1) but excluded from trajectory classification.

For each eligible pair, a linear regression was fitted to percentage quiz scores ordered chronologically. The resulting slope distribution had a mean of −0.70 (SD = 5.55), indicating a slight overall decline in quiz performance across the semester. Data-driven thresholds were established at mean ± 1 SD, yielding an Improver threshold of slope > +4.85 and a Decliner threshold of slope < −6.25, with all slopes within this range classified as Stable.

Five trajectory types were identified based on the combination of slope direction and average quiz score level (Table 2).

---

**Table 2. Learning Trajectory Distribution (RQ2)**

| Trajectory | n | % | Mean Avg Quiz Score (%) | Mean Slope | Mean ESE (%) |
|---|---|---|---|---|---|
| Steady High Performer | 11,625 | 77.1 | 85.42 | −0.72 | 73.91 |
| Improver | 1,431 | 9.5 | 75.96 | +9.54 | 68.06 |
| Decliner | 1,470 | 9.8 | 68.40 | −10.41 | 76.33 |
| Stable Average | 418 | 2.8 | 51.23 | −1.07 | 67.28 |
| Consistently Struggling | 135 | 0.9 | 28.64 | −0.93 | 65.02 |
| **Total eligible** | **15,079** | **100** | | | |

*Note. Slope = change in quiz score per quiz (0–100 scale). Thresholds: Improver > +4.85; Decliner < −6.25; Stable: within ±6.25 of mean. Slope takes priority over average score in classification.*

---

The dominant trajectory was Steady High Performer (77.1%, n = 11,625), characterised by consistently high average quiz scores (85.42%) and a near-stable slope (−0.72). Improvers (9.5%, n = 1,431) and Decliners (9.8%, n = 1,470) formed comparable-sized groups, distinguished by markedly positive and negative slopes respectively (+9.54 and −10.41). Stable Average students comprised 2.8% (n = 418), maintaining moderate performance across the semester. Consistently Struggling students were the smallest group (0.9%, n = 135), characterised by persistently low quiz scores (mean = 28.64%) and minimal slope variation.

A noteworthy preliminary observation was that Decliners recorded the highest mean ESE percentage (76.33%) among all trajectory groups — higher than Steady High Performers (73.91%) — suggesting that students who begin the semester with high quiz performance and subsequently decline may still leverage their early knowledge gains to perform well in the end semester examination. This pattern was examined formally in RQ4.

---

## 4.3 RQ3 — Engagement Profiles and Final Examination Outcomes

To address RQ3, the relationship between engagement profiles and ESE percentage was examined. Shapiro-Wilk and Kolmogorov-Smirnov tests confirmed non-normality across all three profile groups (all p < 0.001), and Levene's test indicated unequal variances (F = 41.67, p < 0.001). Accordingly, the Kruskal-Wallis H test was employed as the primary inferential test, with Dunn's test and Bonferroni correction applied for pairwise post-hoc comparisons.

The Kruskal-Wallis test revealed a statistically significant difference in ESE outcomes across engagement profiles (H(2) = 331.79, p < 0.001), with a small effect size (ε² = 0.018). Descriptive statistics per profile are presented in Table 3.

---

**Table 3. ESE Outcomes by Engagement Profile (RQ3)**

| Profile | n | Mean ESE (%) | Median ESE (%) | SD | IQR |
|---|---|---|---|---|---|
| Low | 2,154 | 66.19 | 67.50 | 15.28 | 19.71 |
| Medium | 879 | 70.22 | 72.00 | 13.50 | 16.66 |
| High | 15,330 | 73.18 | 72.50 | 15.65 | 24.00 |

*Note. Kruskal-Wallis H(2) = 331.79, p < 0.001, ε² = 0.018 [Small effect].*

---

Post-hoc Dunn's tests with Bonferroni correction confirmed that all three pairwise profile comparisons were statistically significant (Table 4). The Low engagement group achieved significantly lower ESE scores than both Medium (z = −6.69, p < 0.001) and High (z = −18.00, p < 0.001) engagement groups. Medium and High engagement groups also differed significantly (z = −4.23, p < 0.001), with High engagement students outperforming Medium engagement students by a mean of 2.96 percentage points.

---

**Table 4. Post-hoc Pairwise Comparisons — Engagement Profiles (RQ3)**

| Comparison | Mean ESE Group 1 | Mean ESE Group 2 | z | p (Bonferroni) | Significance |
|---|---|---|---|---|---|
| Low vs Medium | 66.19 | 70.22 | −6.69 | < 0.001 | *** |
| Low vs High | 66.19 | 73.18 | −18.00 | < 0.001 | *** |
| Medium vs High | 70.22 | 73.18 | −4.23 | < 0.001 | *** |

*Note. *** p < 0.001. Bonferroni-corrected over 3 comparisons.*

---

These findings confirm that engagement profile is a statistically significant predictor of ESE outcomes, with higher engagement associated with progressively better examination performance. However, the small effect size (ε² = 0.018) indicates that while the relationship is reliable, engagement profile accounts for a modest proportion of variance in ESE outcomes, suggesting that other factors not captured by quiz participation and performance contribute substantially to final examination results.

---

## 4.4 RQ4 — Learning Trajectories and Final Examination Outcomes

To examine whether different learning trajectories were associated with differential ESE outcomes, the Kruskal-Wallis H test was applied across the five trajectory groups. Normality tests confirmed non-normality in all five groups (all p < 0.001), and Levene's test indicated unequal variances (F = 39.70, p < 0.001). Descriptive statistics are presented in Table 5.

---

**Table 5. ESE Outcomes by Learning Trajectory (RQ4)**

| Trajectory | n | Mean ESE (%) | Median ESE (%) | SD | IQR |
|---|---|---|---|---|---|
| Steady High Performer | 11,518 | 73.91 | 73.33 | 15.66 | 23.34 |
| Decliner | 1,440 | 76.33 | 76.67 | 16.87 | 30.00 |
| Improver | 1,389 | 68.06 | 70.00 | 13.24 | 16.67 |
| Stable Average | 377 | 67.28 | 66.67 | 14.48 | 16.67 |
| Consistently Struggling | 133 | 65.02 | 62.86 | 17.80 | 24.67 |

*Note. Kruskal-Wallis H(4) = 301.47, p < 0.001, ε² = 0.020 [Small effect]. Ranked by Mean ESE descending.*

---

The Kruskal-Wallis test was significant (H(4) = 301.47, p < 0.001, ε² = 0.020), confirming that ESE outcomes differed significantly across trajectory groups. Post-hoc Dunn's tests with Bonferroni correction (10 pairwise comparisons) revealed several notable patterns (Table 6).

---

**Table 6. Post-hoc Pairwise Comparisons — Learning Trajectories (RQ4)**

| Comparison | Mean ESE 1 | Mean ESE 2 | z | p (Bonferroni) | Significance |
|---|---|---|---|---|---|
| Steady High Performer vs Stable Average | 73.91 | 67.28 | +8.00 | < 0.001 | *** |
| Steady High Performer vs Improver | 73.91 | 68.06 | +12.54 | < 0.001 | *** |
| Steady High Performer vs Decliner | 73.91 | 76.33 | −5.79 | < 0.001 | *** |
| Steady High Performer vs Consistently Struggling | 73.91 | 65.02 | +6.12 | < 0.001 | *** |
| Stable Average vs Improver | 67.28 | 68.06 | −1.08 | 1.000 | ns |
| Stable Average vs Decliner | 67.28 | 76.33 | −10.03 | < 0.001 | *** |
| Stable Average vs Consistently Struggling | 67.28 | 65.02 | +1.14 | 1.000 | ns |
| Improver vs Decliner | 68.06 | 76.33 | −13.77 | < 0.001 | *** |
| Improver vs Consistently Struggling | 68.06 | 65.02 | +1.95 | 0.507 | ns |
| Decliner vs Consistently Struggling | 76.33 | 65.02 | +7.67 | < 0.001 | *** |

*Note. *** p < 0.001; ns = not significant. Bonferroni-corrected over 10 comparisons.*

---

Three findings from RQ4 warrant particular attention.

**First**, Decliners achieved the highest mean ESE percentage of all trajectory groups (76.33%), significantly outperforming Steady High Performers (73.91%; z = −5.79, p < 0.001), Improvers (68.06%; z = −13.77, p < 0.001), Stable Average students (67.28%; z = −10.03, p < 0.001), and Consistently Struggling students (65.02%; z = +7.67, p < 0.001). This counterintuitive pattern suggests that students classified as Decliners — characterised by high early quiz performance followed by declining scores — may possess strong foundational subject knowledge, which is reflected in superior final examination outcomes despite reduced quiz engagement toward the semester end. This finding challenges the assumption that declining formative engagement necessarily predicts poorer summative outcomes.

**Second**, the comparison between Improvers and Steady High Performers — the central claim of this study regarding multiple pathways to success — revealed a statistically significant difference in ESE outcomes (Mann-Whitney U = 9,652,709, p < 0.001), with Steady High Performers outperforming Improvers by a mean of 5.85 percentage points (73.91% vs 68.06%). This finding partially supports the study's proposition: while Improvers demonstrate measurable performance gains across the semester, they do not fully close the gap with students who maintained consistently high performance throughout. The absence of a significant difference between Improvers and Consistently Struggling students (p = 0.507) and between Stable Average and Consistently Struggling students (p = 1.000) further suggests that trajectory type alone is insufficient to distinguish certain groups in terms of summative outcomes.

**Third**, Stable Average and Consistently Struggling students showed no significant difference in ESE outcomes (p = 1.000), indicating that moderate but stable engagement does not confer a meaningful examination advantage over persistently low-performing students in this cohort.

---

## 4.5 Summary of Key Findings

Taken together, the four research questions reveal a complex picture of student engagement and performance in online continuous assessment. Three engagement profiles were identified — with the large majority of students (83.5%) classified as High engagement — and all profiles were significantly associated with ESE outcomes, albeit with a small effect size. Five learning trajectories emerged from the data, with Steady High Performers representing the dominant pattern (77.1%). Contrary to expectation, Decliners achieved the highest summative outcomes, while Improvers — despite positive within-semester progress — did not match the examination performance of consistently high-performing peers. These findings collectively underscore the heterogeneity of student learning pathways and the complexity of the formative-to-summative performance relationship.
