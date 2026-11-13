# Architecture

```mermaid
flowchart TD
    A[Original certification datasets] --> B[Data validation]
    B --> C[Four independent research modules]
    C --> D[Forecasting and optimization experiments]
    D --> E[Evaluation and experiment registry]
    E --> F[Generated CSV JSON and figures]
    F --> G[Research reports and PDF]
    F --> H[Interactive Streamlit dashboard]
```

Original certification scripts are retained in `task1_*` through `task4_*` folders. The `quant_research` package provides independent implementations. `quant_research.phase2` generates additional diagnostics from real outputs.
