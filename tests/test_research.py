import numpy as np
import pytest
from quant_research.storage import Contract,value_schedule,optimize_hindsight
from quant_research.forecasting import forecast,load
from quant_research.fico import dp_edges,summarize

def test_storage_inventory_and_terminal():
    c=Contract(capacity=10,injection_limit=5,withdrawal_limit=5,storage_fee_per_period=0)
    result=value_schedule([2,5],[5,0],[0,5],c)
    assert result["npv"]==pytest.approx(15-0.1)
    assert np.allclose(result['inventory'],[5,0])

def test_storage_rejects_overdraw():
    with pytest.raises(ValueError):value_schedule([2],[0],[1])

def test_storage_same_period_not_silently_skipped():
    c=Contract(capacity=10,injection_limit=5,withdrawal_limit=5,storage_fee_per_period=0)
    v=value_schedule([3],[2],[2],c)
    assert v['npv']<0

def test_lp_zero_spread_not_profitable():
    v,_,_=optimize_hindsight([3,3,3],Contract(storage_fee_per_period=0))
    assert v['npv']<=1e-7

def test_forecast_uses_only_prefix():
    a=np.arange(1.,25.)
    assert forecast(a,'linear_trend')==pytest.approx(forecast(np.r_[a,999][:-1],'linear_trend'))

def test_data_chronological():
    assert load().Dates.is_monotonic_increasing

def test_fico_coverage_and_disjointness():
    x=np.repeat(np.arange(500,550),10);y=(x<525).astype(int)
    edges=dp_edges(x,y,4,20)
    out=summarize(x,y,edges)
    assert out['size'].sum()==len(x)
    assert len(edges)==5
