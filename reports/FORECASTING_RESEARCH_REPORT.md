# Forecasting — independent research extension

## Research question
Which available approach performs best on the supplied data according to mae?

## Methodology
Historical mean, seasonal naive, trailing moving average, linear trend, Holt-Winters and SARIMA. Each prediction uses only earlier observations. MAE = mean(|actual - prediction|).

## Measured results

| model           |   n_test |     mae |    rmse |    mape |   smape |   directional_accuracy |
|:----------------|---------:|--------:|--------:|--------:|--------:|-----------------------:|
| holt_winters    |       24 | 0.18445 | 0.21908 | 1.57145 | 1.57201 |                0.65217 |
| sarima          |       24 | 0.29686 | 0.35871 | 2.51331 | 2.53437 |                0.6087  |
| moving_average  |       24 | 0.42083 | 0.50949 | 3.5859  | 3.60254 |                0.6087  |
| linear_trend    |       24 | 0.48827 | 0.56266 | 4.12585 | 4.14867 |                0.3913  |
| seasonal_naive  |       24 | 0.56667 | 0.62183 | 4.81264 | 4.95559 |                0.69565 |
| historical_mean |       24 | 0.79514 | 0.93491 | 6.61087 | 6.91951 |                0.52174 |

## Interpretation
The top row by mae is **holt_winters**, with mae = **0.184447**. This is a descriptive ranking, not a claim of statistical significance.

## Limitations
48 monthly observations; one-step expanding-window test only. Empirical error band uses the same test errors and is not a calibrated prospective interval.

## Figures
- `results/figures/forecasting/01_history.png`
- `results/figures/forecasting/02_decomposition.png`
- `results/figures/forecasting/03_best_model.png`
- `results/figures/forecasting/04_all_models.png`
- `results/figures/forecasting/05_residual_hist.png`
- `results/figures/forecasting/06_residual_acf.png`
- `results/figures/forecasting/07_rolling_mae.png`
- `results/figures/forecasting/08_mae_comparison.png`
- `results/figures/forecasting/09_empirical_band.png`

## Reproduce
`python -m scripts.run_all_experiments && python -m scripts.generate_all_figures`
