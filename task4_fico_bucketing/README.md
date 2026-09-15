# Task 4 — FICO Score Bucketing (Quantization)

## Business problem

A downstream model needs FICO scores (continuous, 300–850) converted into a fixed number of categorical **rating buckets**, where a **lower rating = better credit**, so it generalizes to future data.

## Approach

This is a **quantization** problem, solved by maximizing log-likelihood via **dynamic programming**:

- For any proposed bucket, log-likelihood measures how internally consistent it is — i.e., how well its observed default rate `p = k/n` explains the actual mix of defaults/non-defaults within it.
- A DP table `dp[b][j]` holds the best achievable total log-likelihood using `b` buckets to cover scores up to `j`, built up from smaller sub-problems.
- Backtracking through the recorded choices recovers the actual bucket boundaries.
- `fico_to_rating(score)` maps any FICO score to a rating (1 = best, N = worst).

## Files

- `fico_bucketing.py` — the DP bucketing logic and `fico_to_rating(...)`.
- `Task_3_and_4_Loan_Data.csv` — same loan data used for Task 3.

## Run it

```bash
pip install pandas numpy
python fico_bucketing.py
```

## Sample output

Default rate falls steadily from ~65% in the lowest bucket to ~2% in the highest — confirming the buckets separate genuinely different risk levels rather than being arbitrary cut points.
