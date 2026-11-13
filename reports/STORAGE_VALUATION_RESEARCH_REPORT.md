# Storage valuation — independent research extension

## Research question
Which available approach performs best on the supplied data according to npv?

## Methodology
Maximize sum(withdrawals * (price - transaction fee) - injections * (price + transaction fee) - storage fee), subject to inventory conservation, capacity, flow limits and terminal inventory.

## Measured results

| scenario               |   npv |   injection_cost |   withdrawal_revenue |   storage_cost |   utilization |
|:-----------------------|------:|-----------------:|---------------------:|---------------:|--------------:|
| base_assumption        |  1231 |             2460 |                 3715 |             24 |       0.5     |
| low_price_assumption   |   976 |             1970 |                 2970 |             24 |       0.5     |
| high_price_assumption  |  1486 |             2950 |                 4460 |             24 |       0.5     |
| higher_storage_fee     |  1075 |             2460 |                 3715 |            180 |       0.5     |
| reduced_capacity       |   741 |             1180 |                 1945 |             24 |       0.5     |
| higher_transaction_fee |   951 |             2600 |                 3575 |             24 |       0.5     |
| restricted_withdrawal  |   687 |             1682 |                 2393 |             24 |       0.29583 |

## Interpretation
The top row by npv is **high_price_assumption**, with npv = **1486**. This is a descriptive ranking, not a claim of statistical significance.

## Limitations
All prices are illustrative assumptions. LP uses perfect foresight and the displayed NPV is undiscounted (zero discount rate). No implementable real-time dispatch is established.

## Figures
- `results/figures/storage/01_inventory.png`
- `results/figures/storage/02_flows.png`
- `results/figures/storage/03_cashflows.png`
- `results/figures/storage/04_cumulative.png`
- `results/figures/storage/05_utilization.png`
- `results/figures/storage/06_strategy.png`
- `results/figures/storage/07_scenarios.png`
- `results/figures/storage/08_sensitivity.png`
- `results/figures/storage/09_storage_fee.png`

## Reproduce
`python -m scripts.run_all_experiments && python -m scripts.generate_all_figures`
