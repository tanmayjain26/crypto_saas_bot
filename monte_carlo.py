import pandas as pd
import numpy as np

# load trade results
df = pd.read_csv("tv_signals.csv")

# collect returns
returns = df["close"].pct_change().dropna().values

SIMULATIONS = 1000
START_BALANCE = 1000

results = []

print("Running Monte Carlo simulation...")

for _ in range(SIMULATIONS):

    shuffled = np.random.choice(returns, size=len(returns), replace=True)

    balance = START_BALANCE

    for r in shuffled:
        balance *= (1 + r)

    results.append(balance)

print("\nMonte Carlo Results")
print("Worst case:", min(results))
print("Best case:", max(results))
print("Average:", sum(results) / len(results))