"""Execute all independent experiments and generate evidence-backed reports."""
import json
import pandas as pd
from quant_research.core import ROOT,save_table
from quant_research import forecasting,storage,credit,fico

def main():
    registry=[];summary={}
    for name,module in [('forecasting',forecasting),('storage',storage),('credit_risk',credit),('fico',fico)]:
        print('Running',name,flush=True)
        reg,table=module.run();registry.extend(reg);summary[name]=table.to_dict(orient='records')
        print(table.to_string(index=False),flush=True)
    save_table(pd.DataFrame(registry),'results/experiment_registry.csv')
    (ROOT/'results/research_summary.json').write_text(json.dumps(summary,indent=2))
    lines=['# Final research report','','Generated from actual local experiment executions. Independent extensions, not JPMorgan-endorsed.','','## Experimental design','','- Forecasting: expanding-window, one-step forecasts on the final 24 monthly observations. Seasonal models trained on past only.','- Storage: illustrative assumed prices; LP is retrospective perfect-foresight upper bound, **not** a live strategy.','- Credit: stratified 75/25 holdout, preprocessing fit inside training pipeline; 10% recovery is an assumption.','- FICO: train-only boundaries and out-of-sample Bernoulli log-likelihood.','','## Measured results','']
    for name,table in summary.items():
        lines.extend(['### '+name,'','```',pd.DataFrame(table).round(5).to_string(index=False),'```',''])
    lines+=['## Limitations','','- Gas dataset contains only 48 monthly observations; no claim of robust long-horizon accuracy or statistical significance.','- Storage optimization assumes all future prices are known and omits discounting, market impact, bid-ask spreads and stochastic dynamics.','- Loan data does not establish real-world temporal generalization or observed recovery rates.','- FICO binning can overfit; minimum population and holdout scoring reduce but do not eliminate this risk.','- SHAP, full forecasting uncertainty and live forecast-based storage dispatch remain future work.','','## Reproduce','','`python -m pip install -r requirements.txt && python run_research.py && python -m pytest -q`']
    (ROOT/'reports/FINAL_RESEARCH_REPORT.md').write_text('\n'.join(lines)+'\n')
if __name__=='__main__':main()
