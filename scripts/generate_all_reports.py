"""Generate module Markdown reports and a figure-embedded research PDF from measured CSV outputs."""
import json
from pathlib import Path
import pandas as pd
from reportlab.platypus import SimpleDocTemplate,Paragraph,Spacer,Image,Table,TableStyle,PageBreak,KeepTogether
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet,ParagraphStyle
from reportlab.lib.enums import TA_CENTER
from reportlab.lib.units import inch
from quant_research.core import ROOT

MODULES=[('Forecasting','forecasting','results/forecasting/model_comparison.csv','mae','lower'),('Storage valuation','storage','results/storage/scenario_comparison.csv','npv','higher'),('Credit risk','credit_risk','results/credit_risk/model_comparison.csv','roc_auc','higher'),('FICO segmentation','fico','results/fico/segmentation_comparison.csv','test_log_likelihood','higher')]
CAVEATS={'forecasting':'48 monthly observations; one-step expanding-window test only. Empirical error band uses the same test errors and is not a calibrated prospective interval.','storage':'All prices are illustrative assumptions. LP uses perfect foresight and the displayed NPV is undiscounted (zero discount rate). No implementable real-time dispatch is established.','credit_risk':'The data provenance is not verified. Near-perfect discrimination may reflect target construction; temporal and external validation are unavailable. LGD is assumed, not observed.','fico':'Train-fitted buckets are evaluated on held-out borrowers. Dynamic programming can overfit and the reported WoE/IV are train-only. Bootstrap stability remains untested.'}
METHOD={'forecasting':'Historical mean, seasonal naive, trailing moving average, linear trend, Holt-Winters and SARIMA. Each prediction uses only earlier observations. MAE = mean(|actual - prediction|).','storage':'Maximize sum(withdrawals * (price - transaction fee) - injections * (price + transaction fee) - storage fee), subject to inventory conservation, capacity, flow limits and terminal inventory.','credit_risk':'Stratified 75/25 split; preprocessing fit within training pipeline. ROC-AUC and PR-AUC are discrimination metrics; Brier and log loss measure probabilistic quality. Expected loss = PD x LGD x EAD.','fico':'Bucket boundaries are fit using training scores only. Held-out log-likelihood sums y log(p) + (1-y) log(1-p). WoE = log(nondefault share / default share), with 0.5 event smoothing.'}

def table_text(df):return df.round(5).to_markdown(index=False)

def main():
    rep=ROOT/'reports';rep.mkdir(exist_ok=True)
    styles=getSampleStyleSheet();styles.add(ParagraphStyle(name='CoverTitle2',parent=styles['Title'],fontSize=22,leading=28,spaceAfter=24,textColor=colors.HexColor('#193b65')))
    styles.add(ParagraphStyle(name='Caption2',parent=styles['Normal'],fontSize=8,textColor=colors.HexColor('#4d647c'),spaceAfter=12))
    styles['BodyText'].leading=14
    story=[Spacer(1,1.5*inch),Paragraph('QUANTITATIVE RESEARCH',styles['CoverTitle2']),Paragraph('Independent Research Extensions to a JPMorgan Chase Virtual Experience',styles['Heading2']),Spacer(1,.5*inch),Paragraph('Reproducible forecasting, storage valuation, credit-risk modelling and FICO segmentation',styles['BodyText']),Spacer(1,.3*inch),Paragraph('Research portfolio edition | Generated from actual repository outputs',styles['Caption2']),Spacer(1,.4*inch),Paragraph('Disclaimer: The original virtual-experience assignments are separate from these independently developed research extensions. No JPMorgan Chase endorsement or employment is implied.',styles['BodyText']),PageBreak()]
    story += [Paragraph('Abstract',styles['Heading1']),Paragraph('This report examines four quantitative research tasks using the datasets and experiment outputs included in the accompanying repository. It prioritizes auditable evaluation, clear modelling assumptions and mathematical constraints over claims of production readiness.',styles['BodyText']),Spacer(1,12),Paragraph('Contents',styles['Heading1'])]
    for i,(title,*_) in enumerate(MODULES,1):story.append(Paragraph(f'{i}. {title}',styles['BodyText']))
    story.extend([Paragraph('5. Reproducibility and limitations',styles['BodyText']),PageBreak()])
    cat=['# Figure catalogue','', 'Every figure below is generated from a repository CSV or raw dataset.','']
    summary=['# Phase 2 measured research findings','','Original certification scripts remain in their task folders. Independent analyses are in quant_research/.','']
    for i,(title,key,path,metric,order) in enumerate(MODULES,1):
        df=pd.read_csv(ROOT/path);best=df.sort_values(metric,ascending=(order=='lower')).iloc[0];identity=best.get('model',best.get('method',best.get('scenario','')))
        md=[f'# {title} — independent research extension','', '## Research question',f'Which available approach performs best on the supplied data according to {metric}?','', '## Methodology',METHOD[key],'','## Measured results','',table_text(df),'','## Interpretation',f'The top row by {metric} is **{identity}**, with {metric} = **{best[metric]:.6g}**. This is a descriptive ranking, not a claim of statistical significance.','','## Limitations',CAVEATS[key],'','## Figures']
        figures=sorted((ROOT/'results/figures'/key).glob('*.png'))
        for f in figures:
            md.append(f'- `{f.relative_to(ROOT)}`')
            cat.extend([f'## {f.stem}',f'- Module: {key}',f'- Source: {path} and module-specific generated CSV / raw data',f'- Interpretation: {f.stem.replace("_"," ")} — inspect axes and limitations in module report','- Experiment ID: linked to module in `results/experiment_registry.csv`',''])
        md+=['','## Reproduce','`python -m scripts.run_all_experiments && python -m scripts.generate_all_figures`']
        filename={'forecasting':'FORECASTING_RESEARCH_REPORT.md','storage':'STORAGE_VALUATION_RESEARCH_REPORT.md','credit_risk':'CREDIT_RISK_RESEARCH_REPORT.md','fico':'FICO_SEGMENTATION_RESEARCH_REPORT.md'}[key]
        (rep/filename).write_text('\n'.join(md)+'\n')
        summary += [f'## {title}',f'- Top by {metric}: {identity} ({best[metric]:.6g})',f'- Important caveat: {CAVEATS[key]}','']
        story.extend([Paragraph(f'{i}. {title}',styles['Heading1']),Paragraph('Research methodology',styles['Heading2']),Paragraph(METHOD[key],styles['BodyText']),Spacer(1,10),Paragraph('Measured comparison',styles['Heading2'])])
        cols=list(df.columns)[:5];view=df[cols].head(8).copy()
        for c in view.columns:
            if pd.api.types.is_numeric_dtype(view[c]):view[c]=view[c].map(lambda v:f'{v:.4g}')
        cells=[cols]+view.astype(str).values.tolist();width=7.1*inch/len(cols)
        tab=Table(cells,colWidths=[width]*len(cols),repeatRows=1,hAlign='LEFT');tab.setStyle(TableStyle([('BACKGROUND',(0,0),(-1,0),colors.HexColor('#e8eef5')),('TEXTCOLOR',(0,0),(-1,0),colors.HexColor('#193b65')),('GRID',(0,0),(-1,-1),.25,colors.HexColor('#d2dae4')),('FONTSIZE',(0,0),(-1,-1),7),('BOTTOMPADDING',(0,0),(-1,-1),6)]));story.extend([tab,Spacer(1,12),Paragraph('Interpretation and limitations',styles['Heading2']),Paragraph(f'Top by {metric}: {identity}, {best[metric]:.6g}. {CAVEATS[key]}',styles['BodyText'])])
        for f in figures:
            from PIL import Image as PILImage
            with PILImage.open(f) as im:w,h=im.size
            scale=min(6.7*inch/w,3.25*inch/h)
            story.append(KeepTogether([Spacer(1,12),Paragraph(f.stem.replace('_',' ').title(),styles['Heading3']),Image(str(f),width=w*scale,height=h*scale),Paragraph(f'Research visualization: {f.stem.replace("_"," ")}.',styles['Caption2'])]))
        story.append(PageBreak())
    story.extend([Paragraph('5. Reproducibility and limitations',styles['Heading1']),Paragraph('Run pip install -r requirements.txt, then python -m scripts.run_all_experiments, python -m scripts.generate_all_figures, python -m scripts.generate_all_reports, and python -m pytest -q. Dashboard requires pip install -r requirements-dashboard.txt and streamlit run dashboard/app.py.',styles['BodyText']),Spacer(1,12),Paragraph('Limitations',styles['Heading2'])])
    for c in CAVEATS.values():story.append(Paragraph(c,styles['BodyText']))
    story.extend([Spacer(1,16),Paragraph('References and methods',styles['Heading2']),Paragraph('Hyndman and Athanasopoulos, Forecasting: Principles and Practice; scikit-learn model evaluation documentation; statsmodels time-series documentation; SciPy HiGHS linear programming documentation. This report does not claim peer review.',styles['BodyText'])])
    target=rep/'JPMORGAN_QUANTITATIVE_RESEARCH_FINAL_REPORT.pdf'
    doc=SimpleDocTemplate(str(target),pagesize=(8.27*inch,11.69*inch),leftMargin=.65*inch,rightMargin=.65*inch,topMargin=.7*inch,bottomMargin=.65*inch)
    def footer(canvas,doc):
        canvas.saveState();canvas.setFont('Helvetica',8);canvas.setFillColor(colors.HexColor('#52667b'));canvas.drawString(.65*inch,.38*inch,'Independent quantitative research | Not JPMorgan-endorsed');canvas.drawRightString(7.62*inch,.38*inch,f'Page {doc.page}');canvas.restoreState()
    doc.build(story,onFirstPage=footer,onLaterPages=footer)
    (rep/'FIGURE_CATALOGUE.md').write_text('\n'.join(cat))
    (ROOT/'RESULTS.md').write_text('\n'.join(summary))
    print('Generated PDF:',target)
if __name__=='__main__':main()
