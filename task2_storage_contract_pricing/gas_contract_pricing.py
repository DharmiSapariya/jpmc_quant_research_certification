from datetime import date
import math

# prices a gas storage contract - net value from buying, storing and selling gas
def price_contract(in_dates, in_prices, out_dates, out_prices, rate,
                    storage_cost_rate, total_vol, injection_withdrawal_cost_rate):

    volume = 0
    buy_cost = 0
    cash_in = 0

    # go through all dates in order so we process injections/withdrawals as they happen
    all_dates = sorted(set(in_dates + out_dates))

    for current_date in all_dates:
        if current_date in in_dates:
            # injecting gas - only if there's room left in storage
            if volume <= total_vol - rate:
                volume += rate
                buy_cost += rate * in_prices[in_dates.index(current_date)]
                injection_cost = rate * injection_withdrawal_cost_rate
                buy_cost += injection_cost
                print(f"Injected gas on {current_date} at a price of {in_prices[in_dates.index(current_date)]}")
            else:
                print(f"Injection is not possible on {current_date}, not enough space left in storage")

        elif current_date in out_dates:
            # withdrawing gas - only if there's enough currently stored
            if volume >= rate:
                volume -= rate
                cash_in += rate * out_prices[out_dates.index(current_date)]
                withdrawal_cost = rate * injection_withdrawal_cost_rate
                cash_in -= withdrawal_cost
                print(f"Extracted gas on {current_date} at a price of {out_prices[out_dates.index(current_date)]}")
            else:
                print(f"Extraction is not possible on {current_date}, not enough gas stored")

    # flat storage fee for the number of months the facility was in use
    store_cost = math.ceil((max(out_dates) - min(in_dates)).days / 30) * storage_cost_rate

    return cash_in - store_cost - buy_cost


# --- test it with a few sample dates, same shape as the course example ---
in_dates = [date(2022, 1, 1), date(2022, 2, 1), date(2022, 2, 21), date(2022, 4, 1)]
in_prices = [20, 21, 20.5, 22]
out_dates = [date(2022, 1, 27), date(2022, 2, 15), date(2022, 3, 20), date(2022, 6, 1)]
out_prices = [23, 19, 21, 25]

rate = 100_000                       # cubic feet per day, injection or withdrawal
storage_cost_rate = 10_000           # flat $ per month to store gas
injection_withdrawal_cost_rate = 0.0005   # $ per cubic foot moved
max_storage_volume = 500_000         # cubic feet capacity

result = price_contract(in_dates, in_prices, out_dates, out_prices, rate,
                         storage_cost_rate, max_storage_volume, injection_withdrawal_cost_rate)

print()
print(f"The value of the contract is: ${result}")


# --- a second test, using my own dates/rates instead of the example ones ---
in_dates2 = [date(2024, 6, 30), date(2024, 7, 31)]
in_prices2 = [2.1, 2.3]
out_dates2 = [date(2024, 12, 31), date(2025, 1, 31)]
out_prices2 = [3.5, 3.8]

result2 = price_contract(in_dates2, in_prices2, out_dates2, out_prices2,
                          rate=500_000, storage_cost_rate=100_000,
                          total_vol=1_000_000, injection_withdrawal_cost_rate=0.01)
print()
print(f"Second test contract value: ${result2}")
