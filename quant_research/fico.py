"""Train-fitted FICO bins evaluated on held-out borrowers; intervals [low, high)."""
import time
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from sklearn.model_selection import train_test_split
from .core import ROOT,SEED,save_table,record
DATA=ROOT/'task4_fico_bucketing/Task_3_and_4_Loan_Data.csv'

def dp_edges(scores,targets,buckets=10,min_population=50):
    """Exact DP on distinct observed score values, penalizing neither bin count nor nonmonotonicity."""
    grouped=pd.DataFrame({'score':scores,'target':targets}).groupby('score').target.agg(['sum','count']).sort_index()
    vals=grouped.index.to_numpy(); k=np.r_[0,grouped['sum'].cumsum().to_numpy()]; n=np.r_[0,grouped['count'].cumsum().to_numpy()];m=len(vals)
    if buckets<1 or buckets*min_population>n[-1]:raise ValueError('Infeasible number of buckets')
    def ll(i,j):
        nn=n[j]-n[i];kk=k[j]-k[i]
        if nn<min_population:return -np.inf
        q=np.clip(kk/nn,1e-12,1-1e-12)
        return kk*np.log(q)+(nn-kk)*np.log1p(-q)
    dp=np.full((buckets+1,m+1),-np.inf);back=np.full((buckets+1,m+1),-1,dtype=int);dp[0,0]=0
    for b in range(1,buckets+1):
        for j in range(b,m+1):
            for i in range(b-1,j):
                if np.isfinite(dp[b-1,i]):
                    score=dp[b-1,i]+ll(i,j)
                    if score>dp[b,j]:dp[b,j]=score;back[b,j]=i
    if not np.isfinite(dp[buckets,m]):raise ValueError('No feasible segmentation')
    cuts=[];j=m
    for b in range(buckets,0,-1):
        i=back[b,j]
        if i>0:cuts.append(int(vals[i]))
        j=i
    return np.array([-np.inf,*sorted(cuts),np.inf],float)

def summarize(scores,targets,edges):
    b=pd.cut(scores,bins=edges,right=False,labels=False,include_lowest=True)
    if pd.isna(b).any():raise ValueError('Uncovered FICO scores')
    out=pd.DataFrame({'bucket':b,'default':np.asarray(targets)}).groupby('bucket').default.agg(['size','sum','mean']).reset_index()
    return out

def run():
    df=pd.read_csv(DATA);train,test=train_test_split(df,test_size=.25,random_state=SEED,stratify=df.default)
    scores=train.fico_score.to_numpy();target=train.default.to_numpy();rows=[];reg=[];details=[]
    for name in ['equal_width','equal_frequency','quantile','dynamic_programming']:
        t=time.perf_counter()
        if name=='equal_width':edges=np.r_[-np.inf,np.linspace(300,850,11)[1:-1],np.inf]
        elif name=='dynamic_programming':edges=dp_edges(scores,target,10,50)
        else:
            # Quantile and equal-frequency coincide under empirical quantiles, except ties.
            edges=np.r_[-np.inf,np.unique(np.quantile(scores,np.arange(.1,1,.1))),np.inf]
        tr=summarize(train.fico_score,train.default,edges);te=summarize(test.fico_score,test.default,edges)
        rates=(tr.set_index('bucket')['sum']+.5)/(tr.set_index('bucket')['size']+1)
        ids=pd.cut(test.fico_score,edges,right=False,labels=False)
        prob=np.asarray([rates.get(int(i),float(train.default.mean())) for i in ids])
        yy=test.default.to_numpy();ll=float(np.sum(yy*np.log(prob)+(1-yy)*np.log1p(-prob)))
        monotonic=bool(np.all(np.diff(tr['mean'])>=0) or np.all(np.diff(tr['mean'])<=0))
        rows.append(dict(method=name,buckets=len(edges)-1,test_log_likelihood=ll,min_train_bucket=int(tr['size'].min()),monotonic_train=monotonic))
        reg.append(record('fico',name,DATA,{'test_log_likelihood':ll,'number_buckets':len(edges)-1},'stratified random 75/25; fit cuts on training only',time.perf_counter()-t))
        for _,r in te.iterrows():details.append(dict(method=name,bucket=int(r.bucket),test_count=int(r['size']),test_default_rate=float(r['mean'])))
    out=pd.DataFrame(rows).sort_values('test_log_likelihood',ascending=False);save_table(out,'results/fico/segmentation_comparison.csv');save_table(pd.DataFrame(details),'results/fico/bucket_details.csv')
    d=ROOT/'results/figures';d.mkdir(parents=True,exist_ok=True)
    for column,fn,ylabel in [('test_count','fico_population.png','Held-out population'),('test_default_rate','fico_default_rate.png','Held-out default rate')]:
        sub=pd.DataFrame(details).query('method == "dynamic_programming"');plt.figure(figsize=(8,4));plt.bar(sub.bucket,sub[column]);plt.xlabel('Bucket index (ascending score)');plt.ylabel(ylabel);plt.tight_layout();plt.savefig(d/fn,dpi=170);plt.close()
    return reg,out
