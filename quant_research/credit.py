import time
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from sklearn.model_selection import train_test_split
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import StandardScaler
from sklearn.impute import SimpleImputer
from sklearn.linear_model import LogisticRegression
from sklearn.tree import DecisionTreeClassifier
from sklearn.ensemble import RandomForestClassifier, HistGradientBoostingClassifier
from sklearn.metrics import roc_auc_score,average_precision_score,precision_score,recall_score,f1_score,brier_score_loss,log_loss,ConfusionMatrixDisplay,RocCurveDisplay,PrecisionRecallDisplay
from sklearn.calibration import CalibrationDisplay
from .core import ROOT,SEED,save_table,record
DATA=ROOT/'task3_loan_default_prediction/Task_3_and_4_Loan_Data.csv'
FEATURES=['credit_lines_outstanding','loan_amt_outstanding','total_debt_outstanding','income','years_employed','fico_score']
def load():
    df=pd.read_csv(DATA)
    if df[FEATURES+['default']].isna().any().any():raise ValueError('Missing values: investigate before modelling')
    if (df.income<=0).any():raise ValueError('Income must be positive')
    if not set(df.default.unique()).issubset({0,1}):raise ValueError('Invalid target')
    df['debt_to_income']=df.total_debt_outstanding/df.income
    df['loan_to_income']=df.loan_amt_outstanding/df.income
    return df

def run():
    df=load(); features=['credit_lines_outstanding','debt_to_income','loan_to_income','years_employed','fico_score']
    xtr,xt,yt,ytest=train_test_split(df[features],df.default,test_size=.25,stratify=df.default,random_state=SEED)
    models={'logistic_regression':LogisticRegression(max_iter=2000,random_state=SEED), 'decision_tree':DecisionTreeClassifier(max_depth=5,min_samples_leaf=50,random_state=SEED), 'random_forest':RandomForestClassifier(n_estimators=150,min_samples_leaf=10,n_jobs=-1,random_state=SEED), 'hist_gradient_boosting':HistGradientBoostingClassifier(max_iter=100,random_state=SEED)}
    rows=[];reg=[];d=ROOT/'results/figures';d.mkdir(parents=True,exist_ok=True)
    for name,est in models.items():
        t=time.perf_counter();pipe=make_pipeline(SimpleImputer(strategy='median'),StandardScaler(),est);pipe.fit(xtr,yt)
        probs=pipe.predict_proba(xt)[:,1];pred=(probs>=.5).astype(int)
        met=dict(roc_auc=roc_auc_score(ytest,probs),pr_auc=average_precision_score(ytest,probs),precision=precision_score(ytest,pred,zero_division=0),recall=recall_score(ytest,pred),f1=f1_score(ytest,pred),brier=brier_score_loss(ytest,probs),log_loss=log_loss(ytest,probs))
        rows.append(dict(model=name,**met,assumed_recovery_rate=.1,expected_loss_total=float(np.sum(probs*.9*df.loc[xt.index,'loan_amt_outstanding']))))
        reg.append(record('credit_risk',name,DATA,met,'stratified random 75/25 split; held-out test, seed 42',time.perf_counter()-t))
        if name=='logistic_regression':
            for func,fn in [(RocCurveDisplay.from_predictions,'credit_roc.png'),(PrecisionRecallDisplay.from_predictions,'credit_precision_recall.png'),(CalibrationDisplay.from_predictions,'credit_calibration.png')]:
                func(ytest,probs);plt.tight_layout();plt.savefig(d/fn,dpi=170);plt.close()
            ConfusionMatrixDisplay.from_predictions(ytest,pred);plt.tight_layout();plt.savefig(d/'credit_confusion.png',dpi=170);plt.close()
            plt.figure(figsize=(8,4));plt.barh(features,pipe[-1].coef_[0]);plt.title('Standardized logistic coefficients');plt.tight_layout();plt.savefig(d/'credit_coefficients.png',dpi=170);plt.close()
    out=pd.DataFrame(rows).sort_values('roc_auc',ascending=False);save_table(out,'results/credit_risk/model_comparison.csv');return reg,out
