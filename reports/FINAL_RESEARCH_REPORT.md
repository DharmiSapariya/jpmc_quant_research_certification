# Final research report

Generated from actual local experiment executions. Independent extensions, not JPMorgan-endorsed.

## Experimental design

- Forecasting: expanding-window, one-step forecasts on the final 24 monthly observations. Seasonal models trained on past only.
- Storage: illustrative assumed prices; LP is retrospective perfect-foresight upper bound, **not** a live strategy.
- Credit: stratified 75/25 holdout, preprocessing fit inside training pipeline; 10% recovery is an assumption.
- FICO: train-only boundaries and out-of-sample Bernoulli log-likelihood.

## Measured results

### forecasting

```
          model  n_test     mae    rmse    mape   smape  directional_accuracy
   holt_winters      24 0.18445 0.21908 1.57145 1.57201               0.65217
         sarima      24 0.29686 0.35871 2.51331 2.53437               0.60870
 moving_average      24 0.42083 0.50949 3.58590 3.60254               0.60870
   linear_trend      24 0.48827 0.56266 4.12585 4.14867               0.39130
 seasonal_naive      24 0.56667 0.62183 4.81264 4.95559               0.69565
historical_mean      24 0.79514 0.93491 6.61087 6.91951               0.52174
```

### storage

```
              scenario    npv  injection_cost  withdrawal_revenue  storage_cost  utilization
       base_assumption 1231.0          2460.0              3715.0          24.0      0.50000
  low_price_assumption  976.0          1970.0              2970.0          24.0      0.50000
 high_price_assumption 1486.0          2950.0              4460.0          24.0      0.50000
    higher_storage_fee 1075.0          2460.0              3715.0         180.0      0.50000
      reduced_capacity  741.0          1180.0              1945.0          24.0      0.50000
higher_transaction_fee  951.0          2600.0              3575.0          24.0      0.50000
 restricted_withdrawal  687.0          1682.0              2393.0          24.0      0.29583
```

### credit_risk

```
                 model  roc_auc  pr_auc  precision  recall      f1   brier  log_loss  assumed_recovery_rate  expected_loss_total
   logistic_regression  1.00000 0.99999    1.00000 0.99136 0.99566 0.00280   0.01281                    0.1         1.862519e+06
hist_gradient_boosting  0.99993 0.99968    0.98922 0.99136 0.99029 0.00263   0.00880                    0.1         1.854646e+06
         random_forest  0.99979 0.99913    0.98913 0.98272 0.98592 0.00588   0.02152                    0.1         1.853722e+06
         decision_tree  0.99766 0.98629    0.97254 0.91793 0.94444 0.01353   0.06879                    0.1         1.837295e+06
```

### fico

```
             method  buckets  test_log_likelihood  min_train_bucket  monotonic_train
dynamic_programming       10          -1086.07072                96            False
        equal_width       10          -1090.65958                 1             True
    equal_frequency       10          -1098.81869               712             True
           quantile       10          -1098.81869               712             True
```

## Limitations

- Gas dataset contains only 48 monthly observations; no claim of robust long-horizon accuracy or statistical significance.
- Storage optimization assumes all future prices are known and omits discounting, market impact, bid-ask spreads and stochastic dynamics.
- Loan data does not establish real-world temporal generalization or observed recovery rates.
- FICO binning can overfit; minimum population and holdout scoring reduce but do not eliminate this risk.
- SHAP, full forecasting uncertainty and live forecast-based storage dispatch remain future work.

## Reproduce

`python -m pip install -r requirements.txt && python run_research.py && python -m pytest -q`
