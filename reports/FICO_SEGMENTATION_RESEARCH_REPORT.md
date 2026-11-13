# FICO segmentation — independent research extension

## Research question
Which available approach performs best on the supplied data according to test_log_likelihood?

## Methodology
Bucket boundaries are fit using training scores only. Held-out log-likelihood sums y log(p) + (1-y) log(1-p). WoE = log(nondefault share / default share), with 0.5 event smoothing.

## Measured results

| method              |   buckets |   test_log_likelihood |   min_train_bucket | monotonic_train   |
|:--------------------|----------:|----------------------:|-------------------:|:------------------|
| dynamic_programming |        10 |              -1086.07 |                 96 | False             |
| equal_width         |        10 |              -1090.66 |                  1 | True              |
| equal_frequency     |        10 |              -1098.82 |                712 | True              |
| quantile            |        10 |              -1098.82 |                712 | True              |

## Interpretation
The top row by test_log_likelihood is **dynamic_programming**, with test_log_likelihood = **-1086.07**. This is a descriptive ranking, not a claim of statistical significance.

## Limitations
Train-fitted buckets are evaluated on held-out borrowers. Dynamic programming can overfit and the reported WoE/IV are train-only. Bootstrap stability remains untested.

## Figures
- `results/figures/fico/01_score_distribution.png`
- `results/figures/fico/02_population.png`
- `results/figures/fico/03_default_rate.png`
- `results/figures/fico/04_woe.png`
- `results/figures/fico/05_iv.png`
- `results/figures/fico/06_train_test.png`
- `results/figures/fico/07_method_comparison.png`
- `results/figures/fico/08_bucket_intervals.png`
- `results/figures/fico/09_stability.png`
- `results/figures/fico/10_population_vs_risk.png`

## Reproduce
`python -m scripts.run_all_experiments && python -m scripts.generate_all_figures`
