# Sexual Contact During Sleep — Reproducibility Materials

Independent published-aggregate statistical reconstruction, documented input tables, automated checks, and four figure reproductions accompanying the [methodological review](https://datepsych.substack.com/p/sexual-contact-during-sleep-what) **“Sexual Contact During Sleep: What Date Psychology’s Survey Can—and Cannot—Tell Us.”**

**Scope:** This is **not** an independent replication of Alexander and Caitlin's 2023 survey, nor a reanalysis of their original participants. The individual responses, full codebook, per-item denominators, and original analysis code were not available. Counts described as *reconstructed*, *inferred*, or *estimated* must not be mistaken for observed respondent-level data. No results in this package can establish consent, causation, national prevalence, or individual psychological harm.

The format includes source-traced CSV inputs, a numerical-audit script, a source audit, original article figures preserved separately from regenerated figures, reference output, and unit tests.

## Contents

| File or directory | What it contains |
|---|---|
| [`reproduce_sleep_figures.py`](reproduce_sleep_figures.py) | Self-contained aggregate reconstructions; re-creates 4 figures and exports calculated results as CSVs. |
| [`published_study_totals.csv`](published_study_totals.csv) | Published overall sample size (N = 1,343). |
| [`published_sample_percentages.csv`](published_sample_percentages.csv) | Original percentages for sex, current and past partnerships, waking, and flirting. Decimal precision is recorded. |
| [`published_event_counts.csv`](published_event_counts.csv) | Reported numbers applying the assault label in current and past relationships; no original denominators are supplied. |
| [`published_tests.csv`](published_tests.csv) | All **nine** reported inferential tests, including reported statistics, p-values, and incomplete disclosure notes. |
| [`published_evaluation_percentages.csv`](published_evaluation_percentages.csv) | Published positive/neutral/negative proportions for current and past partners. |
| [`victimfocus_published_comparison.csv`](victimfocus_published_comparison.csv) | The separate VictimFocus 51% and 27% statements, with source and non-comparability warning. |
| [`drouin_2026_table3.csv`](drouin_2026_table3.csv) | Counts transcribed from Drouin and Cornelius (2026), Table 3; independent partner/nonpartner denominators. |
| [`SOURCE_AUDIT.md`](SOURCE_AUDIT.md) | Source provenance, explicit assumptions, formulae, figure-by-figure checks, and limitations. |
| [`reconstruction_results.txt`](reconstruction_results.txt) | Checked, human-readable output from the reconstruction script. |
| [`article_figures/`](article_figures/) | The **exact four PNGs** from the checked Substack article, copied unchanged. |
| [`reproduced_figures/`](reproduced_figures/) | Four regenerated plots, eight derived numeric CSVs, and matching reconstruction output. |
| [`tests/test_reconstruction.py`](tests/test_reconstruction.py) | 12 automated unit tests of counts, tests, conventions, rounding, and figure inputs. |
| [`requirements.txt`](requirements.txt) | Python dependencies. |
| [`.gitignore`](.gitignore) | Local Python/temporary file exclusions. |

## Reproduce the statistics and charts

Requires **Python 3.10 or newer**. From the top-level repository folder:

```bash
python -m pip install -r requirements.txt
python reproduce_sleep_figures.py
python -m unittest discover -s tests -v
```

To write results to another folder:

```bash
python reproduce_sleep_figures.py --out my_output
```

The script writes a clear-text numerical audit, machine-readable CSV calculations, and four PNG figures. It **never overwrites `article_figures/`**. Fonts and minor spacing can vary by operating system, but values and annotations should match. `reconstruction_results.txt` is intentionally updated when the script runs.

## Key reproducibility findings

1. **Current-partner waking comparison:** Under ordinary integer reconstruction, 453/681 men and 154/240 women produce a Yates-corrected chi-square of **0.338866**, matching the reported **0.33887**.
2. **Past-partner waking comparison:** 515/839 men and a plausible 220/289 women produce a Yates-corrected chi-square of **19.9336** (*p* ≈ **0.0000080**), not the reported **3.7084** (*p* = **0.05414**). The whole-percent reporting of women's 76% also permits 219 or 221 cases; all three scenarios remain far from the reported test. These are **conditional on inferred full-group denominators**.
3. **Current assault-label comparison:** Three men and five women produce an estimated **Fisher two-sided p ≈ 0.0282** when divided by the reconstructed currently exposed groups (453 and 154); the article reports **p = 1**. Such a small number of events makes this a fragile inference, not proof of a population sex difference.
4. **Current flirting:** 451/681 men and 134/236 women yield χ² ≈ **6.3685**, very close to the article's 6.3675, suggesting possible item-level nonresponse by four women. The exact denominators are unknown.
5. **Past assault labeling:** Using **14/830 men and 46/280 women** gives a Yates chi-square of **86.126137**, reproducing the published **86.126**. The inference that these were the original valid-response denominators is strong but not independently verified.
6. **Current women's evaluation:** Published positive/neutral/negative percentages (62.1%, 27.1%, 10.8%) cannot share any unweighted whole-person denominator ≤154, the reconstructed number who reported waking. They fit **149/65/26 out of 240**, the entire currently partnered female group. This indicates unresolved routing/denominator reporting rather than proving how data were processed.
7. **Wilcoxon figures:** W = 180,772, W = 98,737, and W = 297,638 cannot be produced by the specified exposed groups under standard U or unadjusted rank-sum conventions. Alternative group definitions and omitted coding decisions cannot be conclusively ruled out. W = 77,360 for men's satisfaction is within some permitted bounds but cannot be inferentially reproduced from the published data.

The report includes numerical sensitivity checks rather than treating a rounded percentage as an exact observed count. See [`SOURCE_AUDIT.md`](SOURCE_AUDIT.md) for a source-level, figure-level audit.

## Figures

| Figure | What is shown | Input basis |
|---|---|---|
| `figure_01_measure_mismatch.png` | VictimFocus and Date Psychology ask about **different behaviors**. | Independent descriptions from each publication. Their percentages are *not* comparable population estimates. |
| `figure_02_past_relationship_waking.png` | Reconstructed past-partner sex comparison with Wilson intervals, printed vs recalculated χ². | Date Psychology percentages; inferred counts. |
| `figure_03_assault_label_denominators.png` | Published/inferred all-respondent vs estimated exposure-conditional assault-label percentages. | Date Psychology event counts; inferred denominators. |
| `figure_04_reactions_by_relationship.png` | Four selected descriptive outcomes by partner/nonpartner relationship. | **Actual counts**, Drouin & Cornelius (2026), Table 3. |

## Sources and companion article

- **Primary target:** [Alexander & Caitlin, *Is sexual contact with a sleeping partner assault?* (2023; modified 2024)](https://datepsychology.com/is-sexual-contact-with-a-sleeping-partner-assault/).
- **Original comparator:** [Taylor & Shrive (2021), VictimFocus report](https://static1.squarespace.com/static/68766fb86da746151279e1f4/t/68921578d204ff54b6628de2/1754404218620/I%2Bthought%2Bit%2Bwas%2Bjust%2Ba%2Bpart%2Bof%2Blife%2B-%2B%C2%A9VictinFocus.pdf).
- **External response chart:** [Drouin & Cornelius (2026), *Sexual Touching While Sleeping*](https://doi.org/10.3390/sexes7020026), particularly Table 3.
- **Statistical convention:** [R `wilcox.test` documentation](https://search.r-project.org/R/refmans/stats/html/wilcox.test.html).
- **Companion Substack article:** Add the published article URL here after publication; this repository deliberately does not invent a link.

The full interpretive review and academic sources (including Kern et al. 2022/2024) belong in the companion Substack article. This code package only reproduces claims that can be checked from published summary numbers. It does **not** redistribute copyrighted reports, third-party PDFs, original source HTML, or respondent records.

## Reproducibility and corrections

The reconstructions are deliberately conservative in their claims: some numbers are provably consistent, others are incompatible **under specified assumptions**, and many questions remain unknowable without respondent-level data. An inconsistent statistic is not evidence of fraud or intent. If the primary authors provide exact denominator tables or analysis code, the inputs and conclusions should be updated accordingly.
