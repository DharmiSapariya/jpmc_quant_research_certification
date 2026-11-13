# Credit risk — independent research extension

## Research question
Which available approach performs best on the supplied data according to roc_auc?

## Methodology
Stratified 75/25 split; preprocessing fit within training pipeline. ROC-AUC and PR-AUC are discrimination metrics; Brier and log loss measure probabilistic quality. Expected loss = PD x LGD x EAD.

## Measured results

| model                  |   roc_auc |   pr_auc |   precision |   recall |      f1 |   brier |   log_loss |   assumed_recovery_rate |   expected_loss_total |
|:-----------------------|----------:|---------:|------------:|---------:|--------:|--------:|-----------:|------------------------:|----------------------:|
| logistic_regression    |   1       |  0.99999 |     1       |  0.99136 | 0.99566 | 0.0028  |    0.01281 |                     0.1 |           1.86252e+06 |
| hist_gradient_boosting |   0.99993 |  0.99968 |     0.98922 |  0.99136 | 0.99029 | 0.00263 |    0.0088  |                     0.1 |           1.85465e+06 |
| random_forest          |   0.99979 |  0.99913 |     0.98913 |  0.98272 | 0.98592 | 0.00588 |    0.02152 |                     0.1 |           1.85372e+06 |
| decision_tree          |   0.99766 |  0.98629 |     0.97254 |  0.91793 | 0.94444 | 0.01353 |    0.06879 |                     0.1 |           1.8373e+06  |

## Interpretation
The top row by roc_auc is **logistic_regression**, with roc_auc = **0.999998**. This is a descriptive ranking, not a claim of statistical significance.

## Limitations
The data provenance is not verified. Near-perfect discrimination may reflect target construction; temporal and external validation are unavailable. LGD is assumed, not observed.

## Figures
- `results/figures/credit_risk/01_class_balance.png`
- `results/figures/credit_risk/02_fico_distribution.png`
- `results/figures/credit_risk/03_correlation.png`
- `results/figures/credit_risk/04_roc.png`
- `results/figures/credit_risk/05_pr.png`
- `results/figures/credit_risk/06_confusion.png`
- `results/figures/credit_risk/07_calibration.png`
- `results/figures/credit_risk/08_cv.png`
- `results/figures/credit_risk/09_permutation.png`
- `results/figures/credit_risk/10_expected_loss.png`
- `results/figures/credit_risk/11_thresholds.png`
- `results/figures/credit_risk/12_comparison.png`

## Reproduce
`python -m scripts.run_all_experiments && python -m scripts.generate_all_figures`
