# Task 3 — Loan Default Prediction & Expected Loss

## Business problem

Retail banking wants a model that estimates, for any borrower, the **probability of default (PD)** and the resulting **expected loss**, to help set capital reserves.

## Approach

- Trained on ~10,000 historical borrower records (`credit_lines_outstanding`, loan amount, total debt, income, years employed, FICO score, and whether they defaulted).
- Raw dollar figures are converted into `debt_to_income` and `payment_to_income` ratios (feature engineering), which generalize better across income levels than raw amounts.
- **Logistic regression** is the primary model (interpretable coefficients); a **random forest** is trained alongside it for comparison.
- Both models evaluated with **AUC**.
- `predict_expected_loss(...)` combines the model's PD with a fixed 10% recovery rate:

  `Expected Loss = PD × (1 − Recovery Rate) × Loan Amount`

## Files

- `loan_default_model.py` — training, evaluation, and the `predict_expected_loss(...)` function.
- `Task_3_and_4_Loan_Data.csv` — the loan book sample (also used by Task 4).

## Run it

```bash
pip install pandas numpy scikit-learn
python loan_default_model.py
```

## Honest caveat

Both models scored very close to a perfect AUC (~0.99+) on this sample data — a sign the sample is unusually clean/separable rather than proof the model would perform this well on messier, real production data. Worth validating further before trusting it for actual capital decisions.
