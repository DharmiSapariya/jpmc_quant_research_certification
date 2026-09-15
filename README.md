# JPMorgan Chase & Co. — Quantitative Research Virtual Experience

[![Program](https://img.shields.io/badge/Forage-JPMorgan%20Chase%20QR-blue)](https://www.theforage.com)
[![Python](https://img.shields.io/badge/Python-3.10%2B-3776AB?logo=python&logoColor=white)](https://www.python.org/)
[![Status](https://img.shields.io/badge/Status-Completed-brightgreen)]()
[![License](https://img.shields.io/badge/License-MIT-lightgrey)]()

Repository: **https://github.com/DharmiSapariya/jpmc_quant_research_certification**

This repository contains my completed work from the **JPMorgan Chase & Co. Quantitative Research Job Simulation**, a self-paced virtual experience program run on [Forage](https://www.theforage.com). The simulation is built around two realistic business scenarios drawn from JPMorgan's Quantitative Research (QR) team: pricing natural gas storage contracts for a commodities trading desk, and building credit risk models for a retail banking arm.

> **Note on what this is:** This is an educational simulation, not paid employment, an internship, or official work product of JPMorgan Chase & Co. The task briefs and business scenarios were provided by JPMorgan for the Forage program; the code, models, analysis, and write-ups here are my own work completed in response to them.

---

## Table of Contents

- [Overview](#overview)
- [Repository Structure](#repository-structure)
- [Task 1 — Natural Gas Price Estimation](#task-1--natural-gas-price-estimation)
- [Task 2 — Natural Gas Storage Contract Pricing](#task-2--natural-gas-storage-contract-pricing)
- [Task 3 — Loan Default Prediction & Expected Loss](#task-3--loan-default-prediction--expected-loss)
- [Task 4 — FICO Score Bucketing (Quantization)](#task-4--fico-score-bucketing-quantization)
- [Tech Stack](#tech-stack)
- [How to Run](#how-to-run)
- [Extras](#extras)
- [Key Takeaways](#key-takeaways)

---

## Overview

The simulation is organized into two storylines and four tasks:

| # | Task | Storyline | Core Technique |
|---|---|---|---|
| 1 | Estimate natural gas prices for any date, past or future | Commodities trading desk | Linear regression + seasonal decomposition |
| 2 | Price a natural gas storage contract | Commodities trading desk | Cash-flow modeling |
| 3 | Predict probability of default & expected loss on loans | Retail banking risk | Logistic regression + random forest |
| 4 | Convert FICO scores into rating buckets | Retail banking risk | Dynamic programming / quantization |

Each task builds on the one before it — Task 1's price model feeds into Task 2's contract pricing, and Task 3's loan data is reused directly in Task 4's bucketing.

---

## Repository Structure

```
jpmc_quant_research_certification/
├── README.md                              <- you are here
├── .gitignore
├── task1_gas_price_estimation/
│   ├── gas_price_model.py
│   ├── Nat_Gas.csv
│   ├── gas_price_forecast.png
│   ├── seasonal_profile.png
│   └── README.md
├── task2_storage_contract_pricing/
│   ├── gas_contract_pricing.py
│   └── README.md
├── task3_loan_default_prediction/
│   ├── loan_default_model.py
│   ├── Task_3_and_4_Loan_Data.csv
│   └── README.md
├── task4_fico_bucketing/
│   ├── fico_bucketing.py
│   ├── Task_3_and_4_Loan_Data.csv
│   └── README.md
└── docs/
    ├── gas_and_credit_risk_guide.pdf
    └── JPMorgan_Chase_certificate.pdf
```

Every task folder is self-contained with its own code, data, and README — click into any of them for a full write-up of that specific problem.

---

## Task 1 — Natural Gas Price Estimation

**Problem:** A trading desk only has month-end price snapshots for natural gas (31 Oct 2020 – 30 Sep 2024). Clients need a price estimate for *any* date — including dates between snapshots and dates up to a year beyond the last one.

**Approach:** Prices are decomposed into `price(t) = trend(t) + seasonal(month)`:
- **Trend** — a linear regression capturing the slow multi-year price drift.
- **Seasonal** — the average detrended deviation per calendar month, capturing the summer-injection / winter-withdrawal storage cycle that drives natural gas seasonality.

Historical dates are answered by direct interpolation between real snapshots; dates up to a year in the future fall back to the trend + seasonal model.

📂 [`task1_gas_price_estimation/`](./task1_gas_price_estimation)

---

## Task 2 — Natural Gas Storage Contract Pricing

**Problem:** Turn a proposed storage deal — injection dates, withdrawal dates, prices, rates, capacity, and fees — into a single fair dollar value for the contract.

**Approach:** `price_contract(...)` merges every injection and withdrawal date into one chronological timeline, tracks the volume physically in storage at each step (enforcing capacity and availability limits), and sums every cash flow:

```
Value = (revenue from withdrawals) − (cost of injections)
        − (injection/withdrawal fees) − (storage rent)
```

Validated against a hand-calculated worked example from the task brief, plus a multi-date scenario and a deliberate capacity-violation test.

📂 [`task2_storage_contract_pricing/`](./task2_storage_contract_pricing)

---

## Task 3 — Loan Default Prediction & Expected Loss

**Problem:** Estimate, for any borrower, the **probability of default (PD)** and the resulting **expected loss**, to help the bank size capital reserves accurately.

**Approach:**
- ~10,000 historical loan records, with income, existing debt, credit lines, employment history, and FICO score as features.
- Raw dollar figures converted into `debt_to_income` and `payment_to_income` ratios so the model generalizes across income levels.
- **Logistic regression** (interpretable) trained alongside a **random forest** for comparison, both evaluated by AUC.
- Final `predict_expected_loss(...)` function: `Expected Loss = PD × (1 − Recovery Rate) × Loan Amount`, with a 10% recovery rate as given.

📂 [`task3_loan_default_prediction/`](./task3_loan_default_prediction)

---

## Task 4 — FICO Score Bucketing (Quantization)

**Problem:** Convert a continuous FICO score (300–850) into a fixed number of ordered rating buckets (lower rating = better credit) for use as categorical input to another model.

**Approach:** A **dynamic programming** solution that maximizes log-likelihood — a statistical measure of how internally consistent each bucket's default rate is — across every possible way of placing the bucket boundaries. Backtracking through the DP table recovers the actual boundary scores, and `fico_to_rating(score)` maps any raw score to its rating.

Result: default rate falls steadily from ~65% in the riskiest bucket to ~2% in the safest, confirming the buckets separate genuinely different risk levels rather than being arbitrary.

📂 [`task4_fico_bucketing/`](./task4_fico_bucketing)

---

## Tech Stack

- **Language:** Python 3
- **Libraries:** pandas, NumPy, scikit-learn, Matplotlib
- **Techniques:** linear regression, seasonal decomposition, cash-flow modeling, logistic regression, random forests, AUC/ROC evaluation, dynamic programming, quantization

---

## How to Run

```bash
git clone https://github.com/DharmiSapariya/jpmc_quant_research_certification.git
cd jpmc_quant_research_certification

pip install pandas numpy matplotlib scikit-learn

# run any task from inside its folder, e.g.:
cd task1_gas_price_estimation
python gas_price_model.py
```

Each script is self-contained — it loads its own CSV from the same folder and prints/saves its own results, so no extra setup is needed beyond the dependencies above.

---

## Extras

- 📘 [`docs/gas_and_credit_risk_guide.pdf`](./docs/gas_and_credit_risk_guide.pdf) — a from-scratch, beginner-friendly explanation of every concept and every line of code across all four tasks. Written as my own study notes to make sure I could explain this work confidently, not part of the original Forage assignment.
- 🎓 [`docs/JPMorgan_Chase_certificate.pdf`](./docs/JPMorgan_Chase_certificate.pdf) — program completion certificate.

---

## Key Takeaways

- Practiced translating an open-ended business problem (a trading desk needing price estimates, a bank needing loss estimates) into a concrete, testable modeling approach.
- Compared multiple modeling techniques (logistic regression vs. random forest) and made an explicit, explainable choice between them rather than picking one arbitrarily.
- Applied dynamic programming to a real optimization problem outside a typical algorithms-course setting.
- Practiced validating results against hand-calculated examples and known outcomes before trusting a model's output.

---

<p align="center"><i>Built as part of the JPMorgan Chase & Co. Quantitative Research Job Simulation on Forage.</i></p>
