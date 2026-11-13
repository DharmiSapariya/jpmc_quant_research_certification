# Quantitative Research — Independent Extended Edition

**Natural gas forecasting · Storage valuation · Credit risk · FICO segmentation**

Independent research extensions to four preserved JPMorgan Chase quantitative research virtual-experience assignments. **Not JPMorgan-endorsed, affiliated, or employment experience.**

## Explore the work

- [Measured results](RESULTS.md) · [Research methodology](RESEARCH_METHODOLOGY.md)
- [Research PDF](reports/JPMORGAN_QUANTITATIVE_RESEARCH_FINAL_REPORT.pdf)
- [Figure catalogue](reports/FIGURE_CATALOGUE.md)
- [Architecture](docs/ARCHITECTURE.md)
- [Original assignment scripts](task1_gas_price_estimation/)

## Research modules

| Module | Evidence | Important caveat |
|---|---|---|
| Gas forecasting | Expanding-window comparisons for six models | 48 observations, one-step only |
| Storage | Linear-programming retrospective optimum, scenarios | Assumed prices, perfect foresight |
| Credit risk | Four held-out classifiers, calibration, CV and expected-loss sensitivity | Extremely high AUC; provenance unknown |
| FICO | Train-fitted dynamic programming and benchmark bins | Overfitting and boundary stability risks |

## Reproduce locally

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python -m scripts.run_all_experiments
python -m scripts.generate_all_figures
python -m scripts.generate_all_reports
python -m scripts.validate_all_results
python -m pytest -q
```

Optional interactive dashboard:

```bash
pip install -r requirements-dashboard.txt
streamlit run dashboard/app.py
```

The four original task folders remain untouched. Research code lives in `quant_research/`. Generated evidence lives in `results/` and `reports/`. All figures are based on real supplied records or **explicitly assumed** storage scenarios. See [limitations](docs/RESEARCH_LIMITATIONS.md).

## Validation status

Local: **13 tests passed**. The 26-page research PDF and 53 PNG figures were generated from supplied data and explicitly assumed storage prices. Streamlit browser execution and GitHub CI have not been verified. See [Phase 2 progress](reports/PHASE_2_PROGRESS.md) for incomplete research requirements.
