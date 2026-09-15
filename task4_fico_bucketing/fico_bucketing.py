import pandas as pd
import numpy as np

df = pd.read_csv("Task_3_and_4_Loan_Data.csv")

defaults = df["default"].to_list()
fico = df["fico_score"].to_list()
n = len(defaults)

# FICO scores officially run 300-850, so use that full range rather than
# just whatever happens to show up in this particular sample - that way
# the bucket map still makes sense if Charlie runs it on a different batch
# of loans later
MIN_SCORE = 300
MAX_SCORE = 850
span = MAX_SCORE - MIN_SCORE  # 550

default_count = [0] * (span + 1)
total_count = [0] * (span + 1)

for i in range(n):
    score = int(fico[i])
    idx = score - MIN_SCORE
    default_count[idx] += defaults[i]
    total_count[idx] += 1

# turn these into running totals, so total_count[j] is "everyone with a
# score <= j+300", not just people at exactly that score
for i in range(1, span + 1):
    default_count[i] += default_count[i - 1]
    total_count[i] += total_count[i - 1]


def log_likelihood(n_in_bucket, k_defaults):
    if n_in_bucket == 0:
        return 0
    p = k_defaults / n_in_bucket
    if p == 0 or p == 1:
        return 0
    return k_defaults * np.log(p) + (n_in_bucket - k_defaults) * np.log(1 - p)


def get_fico_buckets(num_buckets):
    """
    dp[b][j] holds [best log-likelihood, index of the previous cut]
    for splitting scores 0..j (i.e. 300..j+300) into b buckets.
    """
    dp = [[[-1e18, 0] for _ in range(span + 1)] for _ in range(num_buckets + 1)]

    for b in range(num_buckets + 1):
        for j in range(span + 1):
            if b == 0:
                dp[b][j][0] = 0
            else:
                for cut in range(j):
                    # skip cuts that don't actually separate any data
                    if total_count[j] == total_count[cut]:
                        continue
                    if b == 1:
                        dp[b][j][0] = log_likelihood(total_count[j], default_count[j])
                    else:
                        candidate = dp[b - 1][cut][0] + log_likelihood(
                            total_count[j] - total_count[cut],
                            default_count[j] - default_count[cut],
                        )
                        if candidate > dp[b][j][0]:
                            dp[b][j][0] = candidate
                            dp[b][j][1] = cut

    print("best log-likelihood:", round(dp[num_buckets][span][0], 4))

    # walk backwards through the dp table to pull out where the cuts landed
    boundaries = []
    j = span
    b = num_buckets
    while b >= 0:
        boundaries.append(j + MIN_SCORE)
        j = dp[b][j][1]
        b -= 1

    return sorted(set(boundaries))


edges = get_fico_buckets(10)
print("bucket edges:", edges)


def fico_to_rating(score, edges=edges):
    """Lower rating = better score, so the top bucket gets rating 1."""
    num_buckets = len(edges) - 1
    for bucket_idx in range(num_buckets):
        lower, upper = edges[bucket_idx], edges[bucket_idx + 1]
        is_last = bucket_idx == num_buckets - 1
        if (lower <= score < upper) or (is_last and lower <= score <= upper):
            return num_buckets - bucket_idx
    raise ValueError(f"fico score {score} is outside 300-850")


if __name__ == "__main__":
    print("\nbucket ranges and default rates:")
    for i in range(len(edges) - 1):
        lo, hi = edges[i], edges[i + 1]
        mask = (df["fico_score"] >= lo) & (df["fico_score"] <= hi)
        bucket_n = mask.sum()
        if bucket_n > 0:
            rate = df.loc[mask, "default"].mean()
            print(f"  [{lo}-{hi}]  n={bucket_n}  default_rate={rate:.3f}  rating={fico_to_rating((lo+hi)//2)}")

    print("\nsome example lookups:")
    for test_score in [320, 550, 600, 650, 700, 750, 820]:
        print(f"  fico {test_score} -> rating {fico_to_rating(test_score)}")
