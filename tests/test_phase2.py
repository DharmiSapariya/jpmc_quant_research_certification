import json
import numpy as np
import pandas as pd
import pytest
from quant_research.core import ROOT
from quant_research.storage import Contract,value_schedule
from quant_research.fico import summarize

def test_no_action_pays_rental():
    x=value_schedule([2,3],[0,0],[0,0],Contract(storage_fee_per_period=2))
    assert x['npv']==-4

def test_inventory_conservation():
    x=value_schedule([2,3],[100,0],[0,100],Contract(storage_fee_per_period=0))
    assert np.allclose(x['inventory'],[100,0])

def test_invalid_flow_rejected():
    with pytest.raises(ValueError):value_schedule([2,3],[300,0],[0,300])

def test_fico_bucket_half_open():
    s=summarize(pd.Series([752,753,754]),pd.Series([0,1,0]),[-np.inf,753,np.inf])
    assert s['size'].tolist()==[1,2]

def test_phase2_outputs_present():
    for f in ['results/forecasting/forecast_predictions.csv','results/storage/optimal_schedule.csv','results/credit_risk/cross_validation_results.csv','results/fico/woe_iv_results.csv']:
        assert not pd.read_csv(ROOT/f).empty

def test_figure_catalogue_matches_files():
    assert len(list((ROOT/'results/figures').rglob('*.png')))>=40
