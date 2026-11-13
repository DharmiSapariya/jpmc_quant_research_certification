from pathlib import Path
import json
import pandas as pd
from quant_research.core import ROOT
required=['results/forecasting/model_comparison.csv','results/storage/scenario_comparison.csv','results/credit_risk/model_comparison.csv','results/fico/segmentation_comparison.csv','results/experiment_registry.csv']
for item in required:
    p=ROOT/item
    if not p.exists() or pd.read_csv(p).empty:raise RuntimeError(f'Missing/empty: {item}')
for p in (ROOT/'results').rglob('*.json'):json.loads(p.read_text())
print('Validated',len(required),'nonempty core result tables and JSON files')
