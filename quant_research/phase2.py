"""Additional evidence-backed analysis; never replaces the original solutions."""
import json
import numpy as np
import pandas as pd
from scipy.stats import beta
from sklearn.model_selection import train_test_split, StratifiedKFold, cross_validate
from sklearn.pipeline import make_pipeline
from sklearn.impute import SimpleImputer
from sklearn.preprocessing import StandardScaler
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import roc_auc_score, average_precision_score, brier_score_loss
from sklearn.inspection import permutation_importance
from statsmodels.tsa.seasonal import seasonal_decompose
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from .core import ROOT, SEED, save_table
from . import forecasting, credit, fico, storage

PALETTE=['#1f487e','#219ebc','#f4a261','#8d5a97','#2a9d8f','#c44536']

def fig(module,name,title,xlabel='',ylabel=''):
    plt.title(title,loc='left',fontweight='bold',fontsize=12)
    plt.xlabel(xlabel);plt.ylabel(ylabel);plt.grid(alpha=.15);plt.tight_layout()
    dest=ROOT/'results/figures'/module;dest.mkdir(parents=True,exist_ok=True)
    plt.savefig(dest/(name+'.png'),dpi=220,bbox_inches='tight');plt.close()

def forecasting_analysis():
    d=forecasting.load();pred=pd.read_csv(ROOT/'results/forecasting/predictions.csv',parse_dates=['date'])
    out=ROOT/'results/forecasting';out.mkdir(exist_ok=True,parents=True)
    pred.to_csv(out/'forecast_predictions.csv',index=False)
    pred.assign(abs_error=lambda x:abs(x.residual),squared_error=lambda x:x.residual**2).to_csv(out/'forecast_errors.csv',index=False)
    plt.figure(figsize=(10,4));plt.plot(d.Dates,d.Prices,color=PALETTE[0]);fig('forecasting','01_history','Observed monthly natural-gas prices','Date','Dataset price units')
    dec=seasonal_decompose(d.Prices.to_numpy(),model='additive',period=12,extrapolate_trend='freq')
    plt.figure(figsize=(10,4));plt.plot(d.Dates,dec.trend,label='Trend');plt.plot(d.Dates,dec.seasonal,label='Seasonal component');plt.legend();fig('forecasting','02_decomposition','Additive decomposition (descriptive)','Date','Price units')
    best=pd.read_csv(out/'model_comparison.csv').iloc[0]['model'];sel=pred[pred.model==best].sort_values('date')
    plt.figure(figsize=(10,4));plt.plot(sel.date,sel.actual,label='Observed');plt.plot(sel.date,sel.predicted,label=best);plt.legend();fig('forecasting','03_best_model','Walk-forward forecasts','Date','Price units')
    plt.figure(figsize=(10,4))
    for name,group in pred.groupby('model'):plt.plot(group.date,group.predicted,label=name,alpha=.7)
    plt.legend(ncol=3,fontsize=8);fig('forecasting','04_all_models','Out-of-sample model forecasts','Date','Price units')
    plt.figure(figsize=(8,4));plt.hist(sel.residual,bins=12,color=PALETTE[0]);fig('forecasting','05_residual_hist','Best-model forecast residuals','Actual minus predicted','Count')
    from statsmodels.graphics.tsaplots import plot_acf
    plot_acf(sel.residual,lags=10,zero=False);fig('forecasting','06_residual_acf','Residual autocorrelation','Lag (months)','Correlation')
    plt.figure(figsize=(9,4));plt.plot(sel.date,sel.residual.abs().rolling(6,min_periods=1).mean());fig('forecasting','07_rolling_mae','Six-origin rolling absolute error','Date','MAE')
    comparison=pd.read_csv(out/'model_comparison.csv');plt.figure(figsize=(9,4));plt.barh(comparison.model,comparison.mae,color=PALETTE[0]);fig('forecasting','08_mae_comparison','One-step walk-forward MAE','MAE','Model')
    # Descriptive empirical interval from past one-step errors; not a calibrated multi-step prediction interval.
    err=sel.residual.to_numpy();q=np.quantile(np.abs(err),.9)
    plt.figure(figsize=(10,4));plt.plot(sel.date,sel.actual,label='Actual');plt.plot(sel.date,sel.predicted,label='Prediction');plt.fill_between(sel.date,sel.predicted-q,sel.predicted+q,alpha=.2,label='In-sample empirical 90th-percentile absolute-error band');plt.legend(fontsize=8);fig('forecasting','09_empirical_band','Descriptive residual band (not prospective coverage)','Date','Price units')
    (out/'forecast_summary.json').write_text(json.dumps({'best_model_by_mae':best,'n_months':len(d),'n_one_step_origins':len(sel),'empirical_abs_error_90pct':float(q),'warning':'Band estimated using same holdout errors; NOT calibrated out-of-sample coverage. Multi-step horizons not evaluated.'},indent=2))

def storage_analysis():
    prices=np.array([2.7,2.6,2.4,2.3,2.5,2.9,3.2,3.7,4.,3.8,3.4,3.]);contract=storage.Contract()
    v,ins,outs=storage.optimize_hindsight(prices,contract)
    t=np.arange(1,len(prices)+1)
    df=pd.DataFrame({'period':t,'price_assumption':prices,'injection':ins,'withdrawal':outs,'inventory':v['inventory'],'cashflow':v['cashflows'],'cumulative_cashflow':np.cumsum(v['cashflows'])})
    out=ROOT/'results/storage';save_table(df,'results/storage/optimal_schedule.csv');save_table(df[['period','cashflow','cumulative_cashflow']],'results/storage/cash_flows.csv')
    strategies=[]
    for name,inj,wd in [('no_action',np.zeros(12),np.zeros(12)),('retrospective_lp',ins,outs)]:
        val=storage.value_schedule(prices,inj,wd,contract)
        strategies.append({'strategy':name,'npv_undiscounted':val['npv'],'perfect_foresight':name=='retrospective_lp'})
    save_table(pd.DataFrame(strategies),'results/storage/strategy_comparison.csv')
    scenarios=pd.read_csv(out/'scenario_comparison.csv');(out/'valuation_summary.json').write_text(json.dumps({'base_case_undiscounted_npv':v['npv'],'cashflow_sum':float(df.cashflow.sum()),'price_source':'Illustrative assumed 12-period price path; not market observations','discount_rate':0,'optimization':'Retrospective LP with perfect foresight','caveat':'Simultaneous injection and withdrawal are allowed in LP but positive transaction costs discourage them.'},indent=2))
    plt.figure(figsize=(9,4));plt.step(t,df.inventory,where='mid');fig('storage','01_inventory','Retrospective optimal inventory','Period','Volume units')
    plt.figure(figsize=(9,4));plt.bar(t-.15,ins,width=.3,label='Inject');plt.bar(t+.15,outs,width=.3,label='Withdraw');plt.legend();fig('storage','02_flows','Optimal flows under assumed prices','Period','Volume units')
    plt.figure(figsize=(9,4));plt.bar(t,df.cashflow,color=PALETTE[0]);fig('storage','03_cashflows','Period cash flows','Period','Assumed currency units')
    plt.figure(figsize=(9,4));plt.plot(t,df.cumulative_cashflow);fig('storage','04_cumulative','Cumulative undiscounted cash flow','Period','Assumed currency units')
    plt.figure(figsize=(9,4));plt.fill_between(t,df.inventory/contract.capacity,alpha=.4);plt.ylim(0,1);fig('storage','05_utilization','Storage utilization','Period','Capacity fraction')
    plt.figure(figsize=(9,4));plt.bar([x['strategy'] for x in strategies],[x['npv_undiscounted'] for x in strategies]);fig('storage','06_strategy','Retrospective upper bound vs inactivity','Strategy','Undiscounted net value')
    plt.figure(figsize=(10,4));plt.barh(scenarios.scenario,scenarios.npv);fig('storage','07_scenarios','Assumption-based scenario values','Undiscounted net value','Scenario')
    fees=np.linspace(0,25,12);scales=np.linspace(.7,1.3,12);grid=np.array([[storage.optimize_hindsight(prices*s,storage.Contract(storage_fee_per_period=float(f)))[0]['npv'] for s in scales] for f in fees]);plt.figure(figsize=(8,5));plt.imshow(grid,origin='lower',aspect='auto',extent=[scales[0],scales[-1],fees[0],fees[-1]]);plt.colorbar(label='Net value');fig('storage','08_sensitivity','Sensitivity to price scale and storage fee','Price multiplier','Storage fee per period')
    plt.figure(figsize=(9,4));plt.plot(fees,[storage.optimize_hindsight(prices,storage.Contract(storage_fee_per_period=float(f)))[0]['npv'] for f in fees]);fig('storage','09_storage_fee','Net value vs storage fee','Storage fee per period','Net value')

def credit_analysis():
    df=credit.load();out=ROOT/'results/credit_risk';out.mkdir(parents=True,exist_ok=True)
    features=['credit_lines_outstanding','debt_to_income','loan_to_income','years_employed','fico_score'];x=df[features];y=df.default
    tr,te=train_test_split(np.arange(len(df)),test_size=.25,stratify=y,random_state=SEED)
    estimator=make_pipeline(SimpleImputer(strategy='median'),StandardScaler(),LogisticRegression(max_iter=2000,random_state=SEED))
    estimator.fit(x.iloc[tr],y.iloc[tr]);prob=estimator.predict_proba(x.iloc[te])[:,1]
    pred=pd.DataFrame({'row_index':te,'actual':y.iloc[te].to_numpy(),'probability_default':prob,'predicted_at_0_5':(prob>=.5).astype(int),'exposure':df.iloc[te].loan_amt_outstanding.to_numpy()})
    save_table(pred,'results/credit_risk/predictions.csv')
    cv=StratifiedKFold(n_splits=5,shuffle=True,random_state=SEED)
    scores=cross_validate(estimator,x.iloc[tr],y.iloc[tr],cv=cv,scoring={'roc_auc':'roc_auc','average_precision':'average_precision','neg_brier':'neg_brier_score'},n_jobs=1)
    cvdf=pd.DataFrame({'fold':np.arange(1,6),'roc_auc':scores['test_roc_auc'],'pr_auc':scores['test_average_precision'],'brier':-scores['test_neg_brier']})
    save_table(cvdf,'results/credit_risk/cross_validation_results.csv')
    pi=permutation_importance(estimator,x.iloc[te],y.iloc[te],scoring='roc_auc',n_repeats=5,random_state=SEED)
    imp=pd.DataFrame({'feature':features,'importance_mean':pi.importances_mean,'importance_std':pi.importances_std}).sort_values('importance_mean',ascending=False)
    save_table(imp,'results/credit_risk/feature_importance.csv')
    bins=np.linspace(0,1,11);pred['prob_bin']=pd.cut(pred.probability_default,bins,include_lowest=True)
    cal=pred.groupby('prob_bin',observed=False).agg(n=('actual','size'),mean_pred=('probability_default','mean'),observed_default=('actual','mean')).reset_index();cal['prob_bin']=cal.prob_bin.astype(str)
    save_table(cal,'results/credit_risk/calibration_results.csv')
    scenarios=pd.DataFrame([{'lgd_assumption':lgd,'expected_loss':float((pred.probability_default*pred.exposure*lgd).sum()),'ead_source':'observed loan_amt_outstanding','lgd_source':'assumption'} for lgd in np.linspace(.1,.9,9)])
    save_table(scenarios,'results/credit_risk/expected_loss_scenarios.csv')
    plt.figure(figsize=(7,4));plt.bar(['nondefault','default'],y.value_counts().sort_index().to_numpy());fig('credit_risk','01_class_balance','Observed target distribution','Target','Count')
    plt.figure(figsize=(8,4));plt.hist(df.fico_score,bins=30,color=PALETTE[0]);fig('credit_risk','02_fico_distribution','FICO scores in supplied dataset','FICO','Count')
    plt.figure(figsize=(7,5));corr=df[features+['default']].corr();plt.imshow(corr,vmin=-1,vmax=1,cmap='coolwarm');plt.xticks(range(len(corr)),corr.columns,rotation=65,ha='right',fontsize=8);plt.yticks(range(len(corr)),corr.columns,fontsize=8);plt.colorbar();fig('credit_risk','03_correlation','Observed feature correlations')
    from sklearn.metrics import RocCurveDisplay,PrecisionRecallDisplay,ConfusionMatrixDisplay
    RocCurveDisplay.from_predictions(pred.actual,pred.probability_default);fig('credit_risk','04_roc','Held-out ROC curve','False positive rate','True positive rate')
    PrecisionRecallDisplay.from_predictions(pred.actual,pred.probability_default);fig('credit_risk','05_pr','Held-out precision-recall','Recall','Precision')
    ConfusionMatrixDisplay.from_predictions(pred.actual,pred.predicted_at_0_5);fig('credit_risk','06_confusion','Held-out confusion matrix')
    valid=cal[cal.n>0];plt.figure(figsize=(7,4));plt.plot([0,1],[0,1],'--',color='gray');plt.scatter(valid.mean_pred,valid.observed_default,s=valid.n/4);fig('credit_risk','07_calibration','Held-out reliability by probability decile','Predicted probability','Observed default rate')
    plt.figure(figsize=(7,4));plt.boxplot(cvdf.roc_auc);fig('credit_risk','08_cv','Training-only cross-validation ROC-AUC','', 'ROC-AUC')
    plt.figure(figsize=(9,4));plt.barh(imp.feature,imp.importance_mean);fig('credit_risk','09_permutation','Held-out permutation importance','ROC-AUC decrease','Feature')
    plt.figure(figsize=(8,4));plt.plot(scenarios.lgd_assumption,scenarios.expected_loss);fig('credit_risk','10_expected_loss','Expected loss sensitivity to assumed LGD','LGD','Expected loss (dataset units)')
    from sklearn.metrics import precision_score,recall_score,f1_score
    thresholds=np.linspace(.05,.95,19);td=pd.DataFrame([{'threshold':t,'precision':precision_score(pred.actual,prob>=t,zero_division=0),'recall':recall_score(pred.actual,prob>=t,zero_division=0),'f1':f1_score(pred.actual,prob>=t,zero_division=0)} for t in thresholds]);save_table(td,'results/credit_risk/threshold_sensitivity.csv')
    plt.figure(figsize=(9,4));[plt.plot(td.threshold,td[k],label=k) for k in ['precision','recall','f1']];plt.legend();fig('credit_risk','11_thresholds','Held-out threshold sensitivity (diagnostic only)','Threshold','Metric')
    comp=pd.read_csv(out/'model_comparison.csv');plt.figure(figsize=(9,4));plt.barh(comp.model,comp.roc_auc);plt.xlim(.95,1.001);fig('credit_risk','12_comparison','Model ROC-AUC (truncated axis)','ROC-AUC','Model')
    # Not evidence of leakage by itself; extremely strong predictive separation requires external validation.
    (out/'model_summary.json').write_text(json.dumps({'n_records':len(df),'n_default':int(y.sum()),'duplicate_rows':int(df.duplicated().sum()),'holdout_roc_auc':float(roc_auc_score(pred.actual,prob)),'holdout_pr_auc':float(average_precision_score(pred.actual,prob)),'cv_mean_roc_auc':float(cvdf.roc_auc.mean()),'synthetic_provenance':'Not established by provided data; do not claim real-world performance','warning':'Very high discrimination warrants target construction/provenance audit and external temporal validation; threshold curve uses test data for diagnostic illustration, not threshold selection.'},indent=2))

def fico_analysis():
    df=pd.read_csv(fico.DATA);train,test=train_test_split(df,test_size=.25,random_state=SEED,stratify=df.default)
    out=ROOT/'results/fico';out.mkdir(parents=True,exist_ok=True)
    edges=fico.dp_edges(train.fico_score.to_numpy(),train.default.to_numpy(),10,50)
    def table(sub,split):
        b=pd.cut(sub.fico_score,edges,right=False,labels=False)
        z=pd.DataFrame({'bucket':b,'default':sub.default}).groupby('bucket').default.agg(['sum','size']).reset_index()
        z['split']=split;z['default_rate']=z['sum']/z['size'];z['lower']=[edges[int(i)] for i in z.bucket];z['upper']=[edges[int(i)+1] for i in z.bucket]
        return z
    tr=table(train,'train');te=table(test,'test');allb=pd.concat([tr,te],ignore_index=True)
    save_table(allb,'results/fico/bucket_details_phase2.csv')
    # Convention: WoE = log(nondefault share/default share); Jeffreys smoothing prevents infinities.
    good=(tr['size']-tr['sum']+.5);bad=(tr['sum']+.5)
    woe=np.log((good/good.sum())/(bad/bad.sum()));iv=((good/good.sum())-(bad/bad.sum()))*woe
    w=pd.DataFrame({'bucket':tr.bucket,'woe':woe,'iv_contribution':iv,'train_count':tr['size'],'train_default_rate':tr.default_rate});save_table(w,'results/fico/woe_iv_results.csv')
    stability=tr[['bucket','default_rate','size']].merge(te[['bucket','default_rate','size']],on='bucket',suffixes=('_train','_test'));stability['absolute_default_rate_shift']=(stability.default_rate_train-stability.default_rate_test).abs();save_table(stability,'results/fico/stability_results.csv')
    plt.figure(figsize=(8,4));plt.hist(df.fico_score,bins=35);fig('fico','01_score_distribution','FICO score distribution','FICO score','Borrowers')
    plt.figure(figsize=(9,4));plt.bar(tr.bucket,tr['size']);fig('fico','02_population','DP training bucket populations','Bucket','Borrowers')
    plt.figure(figsize=(9,4));plt.bar(tr.bucket,tr.default_rate);fig('fico','03_default_rate','Training default rate by DP bucket','Bucket','Default fraction')
    plt.figure(figsize=(9,4));plt.bar(w.bucket,w.woe);fig('fico','04_woe','WoE: log(nondefault share / default share)','Bucket','WoE')
    plt.figure(figsize=(8,4));plt.bar(['DP total IV'],[iv.sum()]);fig('fico','05_iv','Train-only information value','Method','IV')
    plt.figure(figsize=(9,4));plt.plot(stability.bucket,stability.default_rate_train,'o-',label='Train');plt.plot(stability.bucket,stability.default_rate_test,'s-',label='Test');plt.legend();fig('fico','06_train_test','Bucket default rates across splits','Bucket','Default fraction')
    cmp=pd.read_csv(out/'segmentation_comparison.csv');plt.figure(figsize=(9,4));plt.barh(cmp.method,cmp.test_log_likelihood);fig('fico','07_method_comparison','Held-out Bernoulli log-likelihood','Log-likelihood (higher is better)','Method')
    ci_lo=beta.ppf(.025,tr['sum']+.5,tr['size']-tr['sum']+.5);ci_hi=beta.ppf(.975,tr['sum']+.5,tr['size']-tr['sum']+.5)
    plt.figure(figsize=(9,4));plt.errorbar(tr.bucket,tr.default_rate,yerr=[np.maximum(0,tr.default_rate-ci_lo),np.maximum(0,ci_hi-tr.default_rate)],fmt='o',capsize=3);fig('fico','08_bucket_intervals','Jeffreys 95% bucket rate intervals','Bucket','Default fraction')
    plt.figure(figsize=(9,4));plt.bar(stability.bucket,stability.absolute_default_rate_shift);fig('fico','09_stability','Absolute train-test default rate shift','Bucket','Absolute rate difference')
    plt.figure(figsize=(9,4));plt.scatter(tr['size'],tr.default_rate);fig('fico','10_population_vs_risk','Bucket population vs default rate','Train population','Train default fraction')
    (out/'segmentation_summary.json').write_text(json.dumps({'train_iv_dp':float(iv.sum()),'edges':edges.tolist(),'minimum_train_population':int(tr['size'].min()),'narrow_752_753_present':bool(any((tr.lower==752)&(tr.upper==753))),'warning':'The 752–753 anomaly requires direct original-assignment boundary analysis; these DP boundaries are separately fitted. No bootstrap analysis completed.'},indent=2))

def main():
    forecasting_analysis();storage_analysis();credit_analysis();fico_analysis()
    print('Phase 2 analysis figures:',len(list((ROOT/'results/figures').rglob('*.png'))))
if __name__=='__main__':main()
