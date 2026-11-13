# Initial repository audit

## Preserved baseline
Four certification task folders, their original scripts, explanations, CSVs, plots and certificate documents are retained unchanged.

## Findings from source inspection
- Task 1 fits its trend and seasonality on **all** 48 months; its plotted historical interpolation is not an out-of-sample accuracy test. No uncertainty or holdout evaluation.
- Task 2 uses `if`/`elif` for same-day flows (withdrawal ignored), `list.index` for repeated dates (only first matched), silently skips infeasible operations, and assumes `max(out_dates)` and `min(in_dates)` exist. Month billing is approximate.
- Task 3 trains and reports misclassification and ROC AUC on the **same** 10,000 records; ROC AUC uses hard class predictions rather than probabilities. No holdout, calibration, or validation. Recovery is assumed 10%.
- Task 4 DP initializes every zero-bucket prefix as feasible, and first-bucket likelihood is not tied correctly to each candidate cut; edge backtracking can return inconsistent boundaries. Printed bucket masks include both boundaries, double-counting observations at shared edges. Degenerate bins can score artificially well.
- The original dataset has 48 gas observations and 10,000 loan rows. Customer ID should be excluded from predictors. No missing cells in the supplied CSVs.

## Research extension scope
Independent implementations are in `quant_research/`; they do not overwrite the certification submission. All outputs are generated via `run_research.py`. The storage LP uses explicitly illustrative assumed prices and should never be presented as observed market results.

## Remaining methodological gaps
Full uncertainty quantification, multi-step forecasting, prospective storage optimization, hyperparameter selection via nested CV, SHAP, FICO WoE/IV, and inferential confidence intervals remain unimplemented. Do not infer statistical significance.
