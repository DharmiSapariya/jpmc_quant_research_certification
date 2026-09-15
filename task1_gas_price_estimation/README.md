# Task 1 — Natural Gas Price Estimation

## Business problem

A trading desk only has monthly snapshot prices for natural gas (31 Oct 2020 – 30 Sep 2024). Clients need price estimates for *any* date — including dates between snapshots (interpolation) and dates up to a year beyond the last snapshot (extrapolation).

## Approach

Prices are decomposed into two parts: `price(t) = trend(t) + seasonal(month)`.

- **Trend** — a straight line fit (linear regression) capturing the slow multi-year drift in price.
- **Seasonal** — the average detrended deviation for each calendar month, capturing the summer-injection / winter-withdrawal storage cycle.

For historical dates, the function interpolates directly between real data points. For dates up to a year past the last snapshot, it falls back to trend + seasonal.

## Files

- `gas_price_model.py` — the model and `estimate_price(date)` function, plus a demo/plotting block.
- `Nat_Gas.csv` — the source data (month-end price snapshots).
- `gas_price_forecast.png` — historical prices, interpolation, and 1-year forecast.
- `seasonal_profile.png` — average seasonal price effect by month.

## Run it

```bash
pip install pandas numpy matplotlib
python gas_price_model.py
```

## Sample output

```
2021-06-15 -> $9.92
2023-12-25 -> $12.68
2024-09-30 -> $11.80
2025-01-15 -> $12.93
2025-09-30 -> $12.25
```
