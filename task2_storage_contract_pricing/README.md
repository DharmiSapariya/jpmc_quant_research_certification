# Task 2 — Natural Gas Storage Contract Pricing

## Business problem

Price a storage contract: a client buys gas on one or more injection dates, stores it, and sells it on one or more withdrawal dates. The contract's value must account for every cash flow — purchase/sale prices, injection/withdrawal fees, and storage rent — and generalize to any number of injection/withdrawal dates.

## Approach

`price_contract(...)` merges all injection and withdrawal dates into one chronological timeline, walks through it tracking the volume currently in storage, and tallies:

- Cost of gas bought (injections) + per-unit injection fees
- Revenue from gas sold (withdrawals) − per-unit withdrawal fees
- A flat monthly storage/rental fee for the full period the facility is in use

It also enforces physical limits: an injection can't exceed the facility's maximum capacity, and a withdrawal can't exceed what's currently in storage.

**Contract value = total cash in − total cash out.**

## Files

- `gas_contract_pricing.py` — the `price_contract(...)` function plus three test cases.

## Run it

```bash
python gas_contract_pricing.py
```

## Sample output

```
test 1: 580000.0     # matches the hand-calculated example exactly
test 2: 730000.0     # multi-date injection/withdrawal scenario
test 3 (expected error): can't inject on 2024-07-31, would go over max volume
```
