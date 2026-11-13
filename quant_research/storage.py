"""Transparent deterministic cash flows and retrospective full-horizon LP."""
from dataclasses import dataclass
from datetime import date
import time
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from scipy.optimize import linprog
from .core import ROOT,save_table,record

@dataclass(frozen=True)
class Contract:
    capacity:float=1000
    injection_limit:float=250
    withdrawal_limit:float=250
    transaction_fee:float=0.01
    storage_fee_per_period:float=2
    initial_inventory:float=0
    terminal_inventory:float=0

def validate(contract, prices):
    p=np.asarray(prices,dtype=float)
    if p.ndim!=1 or not len(p) or not np.isfinite(p).all() or (p<0).any(): raise ValueError('Prices must be a nonempty finite nonnegative series')
    if contract.capacity<=0 or min(contract.injection_limit,contract.withdrawal_limit)<=0 or contract.transaction_fee<0 or contract.storage_fee_per_period<0: raise ValueError('Invalid contract limits or fees')
    if not (0<=contract.initial_inventory<=contract.capacity and 0<=contract.terminal_inventory<=contract.capacity): raise ValueError('Invalid inventory')
    return p

def value_schedule(prices,injections,withdrawals,contract=Contract()):
    p=validate(contract,prices);ins=np.asarray(injections,float);outs=np.asarray(withdrawals,float)
    if ins.shape!=p.shape or outs.shape!=p.shape or not np.isfinite(ins).all() or not np.isfinite(outs).all():raise ValueError('Invalid schedule dimensions')
    if (ins<0).any() or (outs<0).any() or (ins>contract.injection_limit+1e-8).any() or (outs>contract.withdrawal_limit+1e-8).any():raise ValueError('Invalid transaction volumes')
    inventory=contract.initial_inventory+np.cumsum(ins-outs)
    if (inventory < -1e-7).any() or (inventory > contract.capacity+1e-7).any() or abs(inventory[-1]-contract.terminal_inventory)>1e-7:raise ValueError('Inventory or terminal constraint violated')
    cash=outs*(p-contract.transaction_fee)-ins*(p+contract.transaction_fee)-contract.storage_fee_per_period
    return dict(npv=float(cash.sum()),cashflows=cash,inventory=inventory,injection_cost=float(np.sum(ins*(p+contract.transaction_fee))),withdrawal_revenue=float(np.sum(outs*(p-contract.transaction_fee))),storage_cost=float(len(p)*contract.storage_fee_per_period),utilization=float(np.mean(inventory/contract.capacity)))

def optimize_hindsight(prices,contract=Contract()):
    """LP with simultaneous flow allowed; positive fees prevent economically useful round trips."""
    p=validate(contract,prices);n=len(p)
    c=np.r_[p+contract.transaction_fee,-p+contract.transaction_fee]
    eq=np.zeros((n+1,2*n)); b=np.zeros(n+1)
    for t in range(n):
        eq[t,:t+1]=1;eq[t,n:n+t+1]=-1
        b[t]=contract.initial_inventory # replaced by inequality inventory bounds below
    # enforce final inventory only; inventory path via inequalities
    eq=np.zeros((1,2*n));eq[0,:n]=1;eq[0,n:]=-1
    beq=[contract.terminal_inventory-contract.initial_inventory]
    a=[];rhs=[]
    for t in range(n):
        row=np.zeros(2*n);row[:t+1]=1;row[n:n+t+1]=-1
        a.extend([row,-row]);rhs.extend([contract.capacity-contract.initial_inventory,contract.initial_inventory])
    bounds=[(0,contract.injection_limit)]*n+[(0,contract.withdrawal_limit)]*n
    res=linprog(c,A_ub=np.asarray(a),b_ub=np.asarray(rhs),A_eq=eq,b_eq=beq,bounds=bounds,method='highs')
    if not res.success:raise ValueError(f'Optimization infeasible: {res.message}')
    ins=np.maximum(res.x[:n],0);outs=np.maximum(res.x[n:],0)
    return value_schedule(p,ins,outs,contract),ins,outs

def run():
    # Illustrative deterministic scenario; NOT observed forward prices or an executable trading strategy.
    base=np.array([2.7,2.6,2.4,2.3,2.5,2.9,3.2,3.7,4.0,3.8,3.4,3.0])
    cases={'base_assumption':(base,Contract()),'low_price_assumption':(base*.8,Contract()),'high_price_assumption':(base*1.2,Contract()),'higher_storage_fee':(base,Contract(storage_fee_per_period=15)),'reduced_capacity':(base,Contract(capacity=500)),'higher_transaction_fee':(base,Contract(transaction_fee=.15)),'restricted_withdrawal':(base,Contract(withdrawal_limit=100))}
    rows=[];registry=[]
    for name,(prices,contract) in cases.items():
        t=time.perf_counter();v,ins,outs=optimize_hindsight(prices,contract)
        rows.append(dict(scenario=name,**{k:v[k] for k in ['npv','injection_cost','withdrawal_revenue','storage_cost','utilization']}))
        registry.append(record('storage',name,ROOT/'task1_gas_price_estimation/Nat_Gas.csv',{'npv':v['npv']},'illustrative assumed 12-period price path, retrospective perfect foresight',time.perf_counter()-t,contract.__dict__))
        if name=='base_assumption':
            d=ROOT/'results/figures';d.mkdir(parents=True,exist_ok=True)
            plt.figure(figsize=(9,4));plt.step(range(1,13),v['inventory'],where='mid');plt.xlabel('Assumed period');plt.ylabel('Inventory (volume units)');plt.title('Retrospective optimal inventory');plt.tight_layout();plt.savefig(d/'storage_inventory.png',dpi=170);plt.close()
            plt.figure(figsize=(9,4));plt.bar(range(1,13),v['cashflows']);plt.xlabel('Assumed period');plt.ylabel('Net cash flow (assumed units)');plt.tight_layout();plt.savefig(d/'storage_cashflows.png',dpi=170);plt.close()
    df=pd.DataFrame(rows);save_table(df,'results/storage/scenario_comparison.csv')
    plt.figure(figsize=(9,4));plt.bar(df.scenario,df.npv);plt.xticks(rotation=35,ha='right');plt.ylabel('NPV (assumed units)');plt.tight_layout();plt.savefig(ROOT/'results/figures/storage_scenarios.png',dpi=170);plt.close()
    return registry,df
