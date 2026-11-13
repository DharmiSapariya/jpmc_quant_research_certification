PYTHON ?= python3
.PHONY: test experiments figures reports validate dashboard
experiments:
	$(PYTHON) -m scripts.run_all_experiments
figures:
	$(PYTHON) -m scripts.generate_all_figures
reports:
	$(PYTHON) -m scripts.generate_all_reports
validate:
	$(PYTHON) -m scripts.validate_all_results
test:
	$(PYTHON) -m pytest -q
dashboard:
	streamlit run dashboard/app.py
