"""Read-only interactive explorer of actual experiment results."""
from pathlib import Path
import json
import pandas as pd
import streamlit as st
import plotly.express as px
ROOT=Path(__file__).resolve().parents[1]
st.set_page_config(page_title='Quantitative Research | Independent Extensions',layout='wide')
st.title('Quantitative Research / Independent Extensions')
st.caption('Original virtual-experience assignments preserved. Independent research; not affiliated with or endorsed by JPMorgan Chase. Illustrative storage prices are assumptions.')
sections={'Overview':None,'Forecasting':'forecasting','Storage valuation':'storage','Credit risk':'credit_risk','FICO segmentation':'fico','Experiment explorer':'registry'}
choice=st.sidebar.radio('Research modules',list(sections))
def csv(path):
    p=ROOT/path
    if not p.exists():st.warning(f'Result missing: {path}. Run experiments and figure generation first.');return None
    try:return pd.read_csv(p)
    except Exception as e:st.error(f'Cannot load {path}: {e}');return None
if choice=='Overview':
    reg=csv('results/experiment_registry.csv')
    if reg is not None:
        st.metric('Registered experiments',len(reg));st.dataframe(reg.groupby('task').size().rename('Experiments'),use_container_width=True)
    for label,path in [('Forecasting','results/forecasting/model_comparison.csv'),('Storage','results/storage/scenario_comparison.csv'),('Credit risk','results/credit_risk/model_comparison.csv'),('FICO','results/fico/segmentation_comparison.csv')]:
        st.subheader(label);data=csv(path)
        if data is not None:st.dataframe(data.head(8),use_container_width=True)
elif choice=='Experiment explorer':
    data=csv('results/experiment_registry.csv')
    if data is not None:
        selected=st.selectbox('Module',sorted(data.task.unique()));st.dataframe(data[data.task==selected],use_container_width=True)
else:
    module=sections[choice];paths={'forecasting':'results/forecasting/model_comparison.csv','storage':'results/storage/scenario_comparison.csv','credit_risk':'results/credit_risk/model_comparison.csv','fico':'results/fico/segmentation_comparison.csv'}
    data=csv(paths[module]);st.header(choice)
    if data is not None:st.dataframe(data,use_container_width=True)
    figdir=ROOT/'results/figures'/module
    if figdir.exists():
        files=sorted(figdir.glob('*.png'))
        if files:
            selected=st.selectbox('Research figure',[x.name for x in files]);st.image(str(figdir/selected),use_container_width=True)
        else:st.info('No generated figures yet. Run the figure generation command.')
    else:st.info('Figures have not been generated.')
    more={'forecasting':'results/forecasting/forecast_predictions.csv','storage':'results/storage/optimal_schedule.csv','credit_risk':'results/credit_risk/predictions.csv','fico':'results/fico/stability_results.csv'}
    extra=csv(more[module])
    if extra is not None:
        st.subheader('Underlying observations');st.dataframe(extra,use_container_width=True)
        numeric=extra.select_dtypes('number').columns.tolist()
        if len(numeric)>=2:
            x=st.selectbox('X axis',numeric,index=0);y=st.selectbox('Y axis',numeric,index=1)
            st.plotly_chart(px.scatter(extra,x=x,y=y,title='Interactive inspection of generated data'),use_container_width=True)
