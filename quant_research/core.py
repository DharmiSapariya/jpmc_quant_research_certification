import hashlib
import json
import platform
from datetime import datetime, timezone
from pathlib import Path
import numpy as np
import pandas as pd
import sklearn

ROOT = Path(__file__).resolve().parents[1]
SEED = 42

def dataset_hash(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()

def save_table(df, path):
    path = ROOT / path
    path.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(path, index=False)

def record(task, model, dataset, metrics, split, seconds, params=None):
    return dict(experiment_id=f"{task}-{model}".replace(" ", "_"), task=task,
                model=model, dataset=str(dataset.relative_to(ROOT)), dataset_sha256=dataset_hash(dataset),
                random_seed=SEED, hyperparameters=json.dumps(params or {}), split=split,
                metrics=json.dumps({k:float(v) for k,v in metrics.items()}),
                runtime_seconds=round(seconds,4), python=platform.python_version(),
                numpy=np.__version__, pandas=pd.__version__, sklearn=sklearn.__version__,
                timestamp_utc=datetime.now(timezone.utc).isoformat())
