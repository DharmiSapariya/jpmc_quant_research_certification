import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.dates as mdates

# Load the monthly snapshot data
df = pd.read_csv("Nat_Gas.csv")
df["Dates"] = pd.to_datetime(df["Dates"], format="%m/%d/%y")
df = df.sort_values("Dates").reset_index(drop=True)
df["Prices"] = df["Prices"].astype(float)

first_date = df["Dates"].iloc[0]
last_date = df["Dates"].iloc[-1]

# Number of days since the first data point, used as our time axis
df["days"] = (df["Dates"] - first_date).dt.days

# Fit a simple straight line trend through the data (price vs time)
slope, intercept = np.polyfit(df["days"], df["Prices"], 1)

def trend_price(days):
    return slope * days + intercept

# Natural gas has a seasonal pattern - cheaper in summer when it's
# injected into storage, more expensive in winter when it's withdrawn
# for heating demand. To capture this, look at how far each month's
# actual price sits from the trend line, then average that by month.
df["trend"] = trend_price(df["days"])
df["residual"] = df["Prices"] - df["trend"]
df["month"] = df["Dates"].dt.month

monthly_avg = df.groupby("month")["residual"].mean()
monthly_avg = monthly_avg - monthly_avg.mean()  # center around 0
seasonal_effect = monthly_avg.to_dict()

def get_seasonal(month):
    return seasonal_effect.get(month, 0)

def estimate_price(input_date):
    """
    Returns an estimated natural gas price for the given date.
    Works for any date between 2020-10-31 and one year past the
    last data point (2025-09-30).

    For dates we already have data around, it interpolates between
    the nearest real data points. For future dates beyond the data,
    it uses the trend line plus the seasonal adjustment for that month.
    """
    d = pd.to_datetime(input_date)

    cutoff = last_date + pd.DateOffset(years=1)
    if d < first_date or d > cutoff:
        raise ValueError(f"Date must be between {first_date.date()} and {cutoff.date()}")

    days = (d - first_date).days

    if d <= last_date:
        return float(np.interp(days, df["days"], df["Prices"]))
    else:
        return float(trend_price(days) + get_seasonal(d.month))


# quick check
for test_date in ["2021-06-15", "2023-12-25", "2024-09-30", "2025-01-15", "2025-09-30"]:
    print(test_date, "->", round(estimate_price(test_date), 2))

# build a daily series covering the data plus the extra forecast year, for plotting
all_dates = pd.date_range(first_date, last_date + pd.DateOffset(years=1), freq="D")
all_prices = [estimate_price(d) for d in all_dates]

plt.figure(figsize=(12, 6))
plt.scatter(df["Dates"], df["Prices"], color="navy", zorder=5, label="Actual monthly data")

hist_mask = all_dates <= last_date
plt.plot(all_dates[hist_mask], np.array(all_prices)[hist_mask], color="steelblue", label="Interpolated")
plt.plot(all_dates[~hist_mask], np.array(all_prices)[~hist_mask], color="firebrick", linestyle="--", label="Forecast (extrapolated)")

plt.axvline(last_date, color="gray", linestyle=":")
plt.title("Natural Gas Price - History and 1 Year Forecast")
plt.xlabel("Date")
plt.ylabel("Price")
plt.gca().xaxis.set_major_locator(mdates.YearLocator())
plt.gca().xaxis.set_major_formatter(mdates.DateFormatter("%Y"))
plt.legend()
plt.grid(alpha=0.3)
plt.tight_layout()
plt.savefig("gas_price_forecast.png", dpi=150)

# separate plot just to see the seasonal shape
plt.figure(figsize=(8, 4.5))
months = list(range(1, 13))
labels = ["Jan","Feb","Mar","Apr","May","Jun","Jul","Aug","Sep","Oct","Nov","Dec"]
values = [get_seasonal(m) for m in months]
plt.bar(labels, values, color=["firebrick" if v >= 0 else "steelblue" for v in values])
plt.axhline(0, color="black", linewidth=0.8)
plt.title("Seasonal Effect by Month")
plt.ylabel("$ vs trend")
plt.tight_layout()
plt.savefig("seasonal_profile.png", dpi=150)
