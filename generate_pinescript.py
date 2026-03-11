import pandas as pd

# Load signals exported from strategy
df = pd.read_csv("tv_signals.csv")

# Only keep rows where a trade happened
signals = df[(df["long_signal"] == True) | (df["short_signal"] == True)].copy()

signals.reset_index(inplace=True)

long_bars = signals[signals["long_signal"] == True]["index"].tolist()
short_bars = signals[signals["short_signal"] == True]["index"].tolist()

# Convert lists to PineScript array format
long_str = ",".join(str(x) for x in long_bars)
short_str = ",".join(str(x) for x in short_bars)

pine_code = f"""
//@version=5
indicator("Python Strategy Signals", overlay=true)

longBars = array.from({long_str})
shortBars = array.from({short_str})

isLong = array.includes(longBars, bar_index)
isShort = array.includes(shortBars, bar_index)

plotshape(isLong,
     title="Python Long",
     location=location.belowbar,
     color=color.green,
     style=shape.triangleup,
     size=size.large)

plotshape(isShort,
     title="Python Short",
     location=location.abovebar,
     color=color.red,
     style=shape.triangledown,
     size=size.large)
"""

with open("tv_strategy.pine", "w") as f:
    f.write(pine_code)

print("PineScript generated: tv_strategy.pine")