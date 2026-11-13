"""Expanding-window one-step-ahead evaluation with no future-price features."""
import time
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from sklearn.metrics import mean_absolute_error, mean_squared_error
from statsmodels.tsa.holtwinters import ExponentialSmoothing
from statsmodels.tsa.statespace.sarimax import SARIMAX
from .core import ROOT, save_table, record

DATA = ROOT / 'task1_gas_price_estimation/Nat_Gas.csv'
def load():
    df = pd.read_csv(DATA)
    df['Dates'] = pd.to_datetime(df['Dates'],format='%m/%d/%y')
    df = df.sort_values('Dates')
    assert not df.Dates.duplicated().any()
    return df.reset_index(drop=True)

def forecast(y, name):
    n=len(y)
    if name=='historical_mean': return float(np.mean(y))
    if name=='seasonal_naive': return float(y[-12])
    if name=='moving_average': return float(np.mean(y[-3:]))
    if name=='linear_trend': return float(np.polyval(np.polyfit(np.arange(n),y,1),n))
    if name=='holt_winters':
        m=ExponentialSmoothing(y,trend='add',seasonal='add',seasonal_periods=12,initialization_method='estimated').fit(optimized=True)
        return float(m.forecast(1)[0])
    if name=='sarima':
        m=SARIMAX(y,order=(1,0,0),seasonal_order=(0,1,0,12),trend='n',enforce_stationarity=False,enforce_invertibility=False).fit(disp=False,maxiter=60)
        return float(m.forecast(1)[0])
    raise ValueError(name)

def metrics(y,p):
    y=np.asarray(y);p=np.asarray(p);err=y-p
    return dict(mae=mean_absolute_error(y,p),rmse=np.sqrt(mean_squared_error(y,p)),
        mape=np.mean(np.abs(err)/np.maximum(np.abs(y),1e-8))*100,
        smape=np.mean(2*np.abs(err)/np.maximum(np.abs(y)+np.abs(p),1e-8))*100,
        directional_accuracy=np.mean(np.sign(np.diff(y))==np.sign(np.diff(p))) if len(y)>1 else np.nan)

def run():
    df=load(); y=df.Prices.to_numpy(float)
    models=['historical_mean','seasonal_naive','moving_average','linear_trend','holt_winters','sarima']
    rows=[]; preds=[]; registry=[]
    for name in models:
        t=time.perf_counter(); yy=[];pp=[];dates=[]
        for i in range(24,len(y)):
            try: v=forecast(y[:i],name)
            except Exception as e: raise RuntimeError(f'{name} failed at origin {i}') from e
            yy.append(y[i]);pp.append(v);dates.append(df.Dates.iloc[i])
        met=metrics(yy,pp)
        rows.append(dict(model=name,n_test=len(yy),**met))
        registry.append(record('forecasting',name,DATA,met,'expanding window: first 24 observations minimum; 24 one-step holdouts',time.perf_counter()-t))
        preds.extend(dict(date=d,model=name,actual=a,predicted=b,residual=a-b) for d,a,b in zip(dates,yy,pp))
    comparison=pd.DataFrame(rows).sort_values('mae');save_table(comparison,'results/forecasting/model_comparison.csv')
    pd.DataFrame(preds).to_csv(ROOT/'results/forecasting/predictions.csv',index=False)
    figdir=ROOT/'results/figures';figdir.mkdir(parents=True,exist_ok=True)
    plt.figure(figsize=(10,5));plt.plot(df.Dates,df.Prices,label='Observed',color='#1d3557')
    for name in [comparison.iloc[0]['model'],'linear_trend']:
        sub=pd.DataFrame(preds).query('model == @name');plt.plot(sub.date,sub.predicted,label=f'{name} (walk-forward)',alpha=.85)
    plt.legend();plt.ylabel('Gas price (dataset units)');plt.title('Expanding-window out-of-sample forecasts');plt.tight_layout();plt.savefig(figdir/'forecast_actual_predicted.png',dpi=170);plt.close()
    plt.figure(figsize=(9,4));plt.bar(comparison.model,comparison.mae);plt.xticks(rotation=35,ha='right');plt.ylabel('MAE');plt.tight_layout();plt.savefig(figdir/'forecast_comparison.png',dpi=170);plt.close()
    best=comparison.iloc[0]['model']; sub=pd.DataFrame(preds).query('model == @best')
    plt.figure(figsize=(8,4));plt.hist(sub.residual,bins=12);plt.title(f'Residuals: {best}');plt.tight_layout();plt.savefig(figdir/'forecast_residuals.png',dpi=170);plt.close()
    return registry,comparison
