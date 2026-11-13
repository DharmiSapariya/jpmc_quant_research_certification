# Phase 2 measured research findings

Original certification scripts remain in their task folders. Independent analyses are in quant_research/.

## Forecasting
- Top by mae: holt_winters (0.184447)
- Important caveat: 48 monthly observations; one-step expanding-window test only. Empirical error band uses the same test errors and is not a calibrated prospective interval.

## Storage valuation
- Top by npv: high_price_assumption (1486)
- Important caveat: All prices are illustrative assumptions. LP uses perfect foresight and the displayed NPV is undiscounted (zero discount rate). No implementable real-time dispatch is established.

## Credit risk
- Top by roc_auc: logistic_regression (0.999998)
- Important caveat: The data provenance is not verified. Near-perfect discrimination may reflect target construction; temporal and external validation are unavailable. LGD is assumed, not observed.

## FICO segmentation
- Top by test_log_likelihood: dynamic_programming (-1086.07)
- Important caveat: Train-fitted buckets are evaluated on held-out borrowers. Dynamic programming can overfit and the reported WoE/IV are train-only. Bootstrap stability remains untested.
