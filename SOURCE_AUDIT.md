# Source audit and numerical methods

This audit maps the figures and statistical reconstruction to specific source statements. It distinguishes **published** figures, **inferred** counts, **alternative denominator scenarios**, and **external published counts**. The original individual responses and author analysis scripts were unavailable. These analyses are not a reproduction of the original investigators' unknown data-cleaning decisions.

## 1. Source provenance

### A. Primary article: Alexander & Caitlin (2023; revised 2024)

[“Is sexual contact with a sleeping partner assault?” — Date Psychology](https://datepsychology.com/is-sexual-contact-with-a-sleeping-partner-assault/).

- `Methodology`: N = 1,343; 24.9% female; nonprobability social-media convenience sample; respondent current/past relationship status; sexual waking wording and follow-up evaluation and assault-label items.
- `Current Relationship`: 32.5% men and 28.1% women not currently partnered; among partnered respondents, 66.5% of men and 64.2% of women awakened for sex. Reported χ² = 0.33887, p = .5605. Assault labels: 3 men, 5 women; reported 99.6% of men and 96.9% of women answering no; χ² ≈ 0, p = 1. Flirting 66.2% men and 56.8% women, χ² = 6.3675, p = .01162. Current positivity, satisfaction and their Wilcoxon statistics are transcribed in `published_tests.csv` and `published_evaluation_percentages.csv`.
- `Past Relationships`: 16.8% men and 13.5% women reported never having been in a past relationship; 61.4% versus 76% of previously partnered respondents reported sexual waking; χ² = 3.7084, p = .05414. Assault labels: 14 men, 46 women; 98.3% and 83.6% said no; χ² = 86.126, p < 2.2e-16. Evaluation and Wilcoxon summary also transcribed.
- The article reports *no exact item-by-item denominator tables, unweighted data, weighting disclosures, codebook, original analysis scripts or 1–7 response counts*. Numerical reconstructions below therefore require assumptions.

The inputs used for these facts are `published_study_totals.csv`, `published_sample_percentages.csv`, `published_event_counts.csv`, `published_tests.csv`, and `published_evaluation_percentages.csv`. The 3/5 and 14/46 assault-label counts are transcribed as separate observed aggregates, not independently recovered individual records.

### B. VictimFocus report (2021)

[Taylor & Shrive, *I thought it was just a part of life*](https://static1.squarespace.com/static/68766fb86da746151279e1f4/t/68921578d204ff54b6628de2/1754404218620/I%2Bthought%2Bit%2Bwas%2Bjust%2Ba%2Bpart%2Bof%2Blife%2B-%2B%C2%A9VictinFocus.pdf) contains the 51% and 27% statements. These are **published survey results**, not quantities estimated from Date Psychology's sample. Their verbatim survey-item wording, precise sexual acts, consent circumstances and national representativeness cannot be established from this accessible material. `victimfocus_published_comparison.csv` stores these statements for the conceptual chart.

### C. Drouin & Cornelius (2026)

[“Sexual Touching While Sleeping: Occurrence, Context, Responses, and Perceptions of Sexual Assault Among Undergraduates,” *Sexes* 7(2), 26](https://doi.org/10.3390/sexes7020026) — **Table 3, “Contexts and Responses to Sexual Touch While Sleeping Incident.”**

The subset consisted of **172** respondents reporting on an incident, including **143** involving a spouse, committed partner or ongoing casual sex partner and **29** involving a one-time partner, one-night stand or stranger. The sample was not population-representative and the nonpartner group was small. Respondents could select more than one reaction; individual outcome percentages must not be added to 100%. All numerical outcomes from that table (14 lines) are transcribed as integer counts in `drouin_2026_table3.csv` and the four charted examples are selected by the script.

## 2. Sample-size inference from rounded percentages

For a published percent `p` rounded to `d` decimal places, code tests the integers `k` satisfying:

```text
p - 0.5 × 10^(-d) <= 100k/n < p + 0.5 × 10^(-d)
```

This assumes conventional round-to-nearest, ordinary whole-person counts, and no weighting. Values exactly on a rounding boundary are of no practical relevance for the central results.

The printed **24.9% female** allows more than one integer split of N = 1,343. Requiring simultaneous compatibility with the *current* relationship status and waking percentages yields one reconstruction:

| Subgroup | Men | Women |
|---|---:|---:|
| All | 1,009 | 334 |
| Currently partnered | 681 | 240 |
| Awakened for sex by current partner | 453 | 154 |
| Previously partnered | 839 | 289 |
| Awakened for sex by past partner | 515 | **219, 220 or 221** |

The last row is conditional on assuming complete response within previously partnered respondents. The article prints **76%**, not **76.0%**, for women: all three counts round to 76% out of 289. **The central charts use 220/289 as an explicitly illustrative choice**, not an exact recovery. `past_waking_rounding_sensitivity.csv` records all three cases.

## 3. Reconstructing the chi-squared and Fisher tests

For each 2×2 table the script calls SciPy `chi2_contingency(..., correction=True)` for Yates-corrected Pearson χ², also calculates uncorrected Pearson χ², and calls `fisher_exact` for a standard two-sided exact test.

| Comparison | Published χ² | Reconstructed χ² (Yates) | Conclusion |
|---|---:|---:|---|
| Current waking, 453/681 vs 154/240 | 0.33887 | 0.338866 | Essentially exact match. |
| Current assault label, 3/453 vs 5/154 | ≈ 0 (p = 1) | 4.082685 (p = .0433); Fisher p ≈ .0282 | Mismatch **under exposed-group denominators**. Only eight affirmative responses. |
| Current flirting, 451/681 vs 134/236 | 6.3675 | 6.368518 | Near match with **inferred four missing female answers**, not an exact reproduction. |
| Past waking, 515/839 vs 220/289 | 3.7084 | 19.933601 (p ≈ .000008) | Strong contradiction **if status and waking denominators are as inferred**. |
| Past assault label, 14/830 vs 46/280 | 86.126 | 86.126137 | Nearly exact match using inferred valid-response denominators. |

**Current assault percentage discrepancy.** Three of 453 exposed men means 99.34% responding “not assault,” whereas the article prints **99.6%**; five of 154 exposed women yields 96.75% “not assault,” versus printed **96.9%**. This is consistent with mixed denominators, different missingness, incorrect transcriptions, or other unexplained routing. The Fisher result is **not** a definitive population-level sex difference.

**Past assault denominator reconciliation.** 14/830 men and 46/280 women reproduce 98.3% and 83.6% saying no (after rounding) and yield χ² = **86.126137**. The group Ns (830, 280) are *inferred*, not directly printed. They are 9 fewer than the reconstructed previously-partnered groups of 839 men and 289 women. This supports but does not prove item nonresponse or another hidden exclusion rule. Conditional estimates of 14/515 = 2.7% men and 46/220 = 20.9% women **do not share the same known denominator** as the article's chi-squared test.

**Past waking sensitivity.** Using 219, 220 or 221 women from 289 and 515 men from 839 gives corrected chi-square values ≈ 18.972, 19.934 and 20.921 and p-values below 0.00002. Recovering χ² ≈ 3.7084 from the printed sex percentages would require dramatically different and unreported effective group sizes or a different analysis.

The machine-readable outputs are `reconstructed_chi_square.csv` and `past_waking_rounding_sensitivity.csv`. They provide **scenarios** and their p-values, not the original authors' unseen observations.

## 4. Evaluation triplets and denominator compatibility

Date Psychology reports current women's evaluations as **62.1% positive, 27.1% neutral and 10.8% negative**. These numbers require a **common denominator**, assuming they are unweighted fractions of the same people.

The script exhaustively enumerates all integer triples summing to `n` for `n ≤ 154`, the number of women reconstructed as reporting waking in current relationships. **There is no matching denominator**. If we instead permit all 240 currently partnered women, 149 positive, 65 neutral, 26 negative yield 62.1%, 27.1%, 10.8% at the displayed precision.

This is a mathematical compatibility result, *not* proof that the authors erroneously included the unexposed. Other explanations include a transcription mistake, undisclosed sample differences or weighting. Past women's triple (63.4%, 24.7%, 11.9%) is compatible with 123, 48, 23 out of **194** respondents, showing that variable effective denominators can matter.

`evaluation_denominator_candidates.csv` documents all compatible denominators, not just a preferred example.

## 5. Wilcoxon / Mann–Whitney terminology and bounds

The word **W** is not standardized across software. R's `wilcox.test` reports a Mann–Whitney-type U statistic, which must lie between 0 and `n1*n2`. Other packages can report the raw rank sum for one group. For `N = n1+n2`, the raw rank sum for a group of size `n1` is bounded:

```text
min raw rank sum = n1(n1+1)/2
max raw rank sum = n1(2N-n1+1)/2
```

The script tests both groups under both conventions. Midranks due to ties still respect those bounds. It also calculates **untied normal-approximation p-values for sensitivity only**, where W has a valid interpretation; those p-values are not an exact attempt to reconstruct tied seven-category ordinal data.

| Reported statistic | Reconstructed group assumption | Mathematical finding |
|---|---|---|
| Current positivity W = 180,772, p = .6372 | 453 exposed men, 154 exposed women | W impossible as U or raw rank sum for either group. |
| Same W with all partnered respondents | 681 men, 240 women | W possible as **raw women's rank sum**, but its untied approximate p is ~3.6 × 10^-87, far from .6372; exact original test still not available. |
| Men's relationship satisfaction W = 77,360, p = .9101 | 453 exposed, 228 not exposed | W can be U or raw rank sum for one group, so not a numerical impossibility; paired p is not independently reproduced. |
| Women's relationship satisfaction W = 98,737, p = .7578 | 154 exposed, 86 not exposed | W impossible for these 240 women under both conventions. Even the total sample of 334 women would have a total rank sum of only 55,945. |
| Past positivity W = 297,638, p = .7062 | 515 exposed men, 220 exposed women | W impossible as U or either raw rank sum. Also incompatible with all 839/289 previously partnered men/women under those conventions. |

Without the original item response frequencies, coding conventions, and test-call arguments, none of the Wilcoxon p-values can be *fully* recomputed. It is misleading to call them all formally incorrect without specifying assumptions; the incompatibilities above are explicitly conditional.

See `wilcoxon_statistic_bounds.csv` and [R's documentation](https://search.r-project.org/R/refmans/stats/html/wilcox.test.html).

## 6. Figure-by-figure provenance

| Figure | Exact input | Method | Important limitation |
|---|---|---|---|
| 1 — Measurement mismatch | Primary article methodology; VictimFocus report's 51%; Date Psychology 64.2% and 66.5% | Conceptual two-column diagram; “64–67%” represents a rounded span | Different questions, respondents, and operationalizations; **do not compare the percentages as estimates of the same behavior**. |
| 2 — Past waking by sex | 515/839 men and assumed 220/289 women; χ² values in primary article | Recalculated Wilson 95% intervals and Yates χ²; different test results explicitly labeled | Ordinary binomial intervals under reconstructed counts; *do not adjust for sample selection bias or imply population representativeness*. |
| 3 — Assault-label denominators | 14 and 46 reported yes; 830/280 inferred valid response denominators; 515/220 reconstructed exposed | Two sets of bars: all-valid rates vs estimated conditional rates | The latter assumes exposed people supplied the positive labels, and response counts may differ by question. |
| 4 — Partner vs nonpartner reaction | Drouin & Cornelius Table 3: 94/143 vs 4/29; 26/143 vs 4/29; 9/143 vs 6/29; 66/143 vs 2/29 | Descriptive paired bars; denominators explicitly displayed | Not a randomized comparison; multiple choices allowed; n=29 nonpartners, so imprecise. |

- `article_figures/` preserves the **published Substack source PNGs** byte-for-byte.
- `reproduced_figures/` contains independent regenerated PNGs and machine-readable plotting data (`figure_02_plot_data.csv`, `figure_03_plot_data.csv`, `figure_04_plot_data.csv`). Identical pixels are not guaranteed across Matplotlib releases or fonts.

## 7. What is outside the scope of numerical reproduction

The article also discusses consent law and psychological evidence. This repository does not redo that literature synthesis or imply numerical reproduction of studies without their original data. Principal interpretive sources include:

- [Sexual Offences Act 2003, Part 1](https://www.legislation.gov.uk/ukpga/2003/42/part/1), especially §§3, 74–75.
- [Crown Prosecution Service, Rape and Sexual Offences Guidance](https://www.cps.gov.uk/prosecution-guidance/rape-and-sexual-offences-prosecution-guidance-full-page-version).
- [Kern et al. (2022 online; 2024 print)](https://doi.org/10.1080/00224499.2022.2130855), psychological symptom associations.
- [Théorêt et al. (2026)](https://doi.org/10.1177/15248380251401927), systematic review of rape acknowledgment and mental health.

Readers should consult the **companion Substack article and its bibliography** for narrative interpretation. These studies are cited, not reanalyzed.

## 8. Missing data, rounding, and corrections

The original survey's full questionnaire, individual event-level records, exact item counts, sample selection, post-processing, code and analysis conventions are unknown. The code assumes unweighted respondent proportions and standard two-sided tests. It is possible that unpublished exclusions, alternative calculations, data-entry mistakes or other features explain some discrepancies. **No claim of intentional manipulation is made.**

This project deliberately includes (a) successful reconstructions, (b) cases that depend on ambiguous denominators and (c) contradictions under the explicit reported-sample interpretation. If corrected source figures or the actual response data become available, update the source CSVs, annotate the changes in this audit, and rerun the script and tests.
