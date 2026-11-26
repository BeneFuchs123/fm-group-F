# %% [markdown]
# 70/30 MSCI World / Emerging Markets backtest
#
# Strategy: invest 70% in URTH and 30% in EEM at the start, then hold without
# rebalancing so the weights drift with performance. ACWI is the broad global
# equity-market benchmark. All three are US-listed ETFs quoted in USD.
#
# The date range matches the previous report (2015 through October 2025).
# A 70/30 benchmark built from these same ETFs with the same no-rebalancing
# rule would duplicate the strategy, so ACWI is used for the meaningful
# comparison. Sector and geographic breakdowns require holdings data, which
# is not provided by this price-only download.

# %%
import numpy as np
import pandas as pd
import yfinance as yf
import matplotlib.pyplot as plt

plt.rcParams["figure.figsize"] = (10, 6)
plt.rcParams["axes.grid"] = True

# %%
START_DATE = "2015-01-01"
# yfinance treats `end` as exclusive; this includes data through 2025-10-31.
END_DATE = "2025-11-01"

WORLD_TICKER = "URTH"
EM_TICKER = "EEM"
BENCHMARK_TICKER = "ACWI"

STRATEGY_TICKERS = [WORLD_TICKER, EM_TICKER]
ALL_TICKERS = STRATEGY_TICKERS + [BENCHMARK_TICKER]
INITIAL_WEIGHTS = pd.Series(
    {WORLD_TICKER: 0.70, EM_TICKER: 0.30},
    dtype=float,
)

# %%
raw = yf.download(
    ALL_TICKERS,
    start=START_DATE,
    end=END_DATE,
    auto_adjust=True,
    progress=False,
)

if raw.empty:
    raise RuntimeError("Yahoo Finance returned no price data for the selected tickers and dates.")

if isinstance(raw.columns, pd.MultiIndex):
    close_level = next(
        (level for level in range(raw.columns.nlevels)
         if "Close" in raw.columns.get_level_values(level)),
        None,
    )
    if close_level is None:
        raise KeyError("The downloaded data has no Close price column.")
    prices = raw.xs("Close", axis=1, level=close_level)
else:
    if "Close" not in raw.columns:
        raise KeyError("The downloaded data has no Close price column.")
    prices = raw[["Close"]].rename(columns={"Close": ALL_TICKERS[0]})

missing_tickers = sorted(set(ALL_TICKERS) - set(prices.columns))
if missing_tickers:
    raise KeyError(f"Price data is missing ticker(s): {', '.join(missing_tickers)}")

# Keep only dates with prices for every ETF so all comparisons use the same dates.
prices = prices.reindex(columns=ALL_TICKERS).dropna(how="any")
if prices.empty:
    raise RuntimeError("No dates have complete price data for all selected ETFs.")

print(f"Using {prices.index[0].date()} to {prices.index[-1].date()} ({len(prices)} trading days).")
print(prices.head())

# %%
# Total-return-like growth using auto-adjusted prices. This models the initial
# 70/30 purchase and lets the actual weights drift; it does not rebalance.
asset_growth = prices[STRATEGY_TICKERS].div(prices[STRATEGY_TICKERS].iloc[0])
component_values = asset_growth.mul(INITIAL_WEIGHTS, axis="columns")
strategy_value = component_values.sum(axis="columns").rename("70/30 Buy-and-Hold")

benchmark_value = (
    prices[BENCHMARK_TICKER] / prices[BENCHMARK_TICKER].iloc[0]
).rename("MSCI ACWI (ACWI)")

equity_curves = pd.concat([strategy_value, benchmark_value], axis="columns")
daily_returns = prices.pct_change().dropna()
strategy_returns = strategy_value.pct_change().dropna()
benchmark_returns = benchmark_value.pct_change().dropna()

# The changing weights are the market values of each holding divided by
# the total portfolio value.
actual_weights = component_values.div(strategy_value, axis="index")

# %%
def performance_metrics(equity_curve: pd.Series) -> pd.Series:
    returns = equity_curve.pct_change().dropna()
    years = (equity_curve.index[-1] - equity_curve.index[0]).days / 365.25
    daily_volatility = returns.std(ddof=1)

    if years <= 0:
        raise ValueError("The backtest needs prices covering more than one calendar day.")

    cagr = (equity_curve.iloc[-1] / equity_curve.iloc[0]) ** (1 / years) - 1
    annualized_volatility = daily_volatility * np.sqrt(252)
    sharpe_ratio = (
        returns.mean() / daily_volatility * np.sqrt(252)
        if daily_volatility > 0
        else np.nan
    )
    max_drawdown = (equity_curve / equity_curve.cummax() - 1).min()

    return pd.Series(
        {
            "Cumulative return": equity_curve.iloc[-1] / equity_curve.iloc[0] - 1,
            "CAGR": cagr,
            "Annualized volatility": annualized_volatility,
            "Sharpe ratio (0% risk-free rate)": sharpe_ratio,
            "Maximum drawdown": max_drawdown,
        }
    )


metrics = pd.DataFrame(
    {
        "70/30 Buy-and-Hold": performance_metrics(strategy_value),
        "MSCI ACWI (ACWI)": performance_metrics(benchmark_value),
    }
)

formatted_metrics = metrics.astype(object)
percentage_metrics = [
    "Cumulative return",
    "CAGR",
    "Annualized volatility",
    "Maximum drawdown",
]
for metric in percentage_metrics:
    formatted_metrics.loc[metric] = metrics.loc[metric].map(lambda value: f"{value:.2%}")
formatted_metrics.loc["Sharpe ratio (0% risk-free rate)"] = metrics.loc[
    "Sharpe ratio (0% risk-free rate)"
].map(lambda value: f"{value:.2f}")
print(formatted_metrics)

# %%
# Cumulative growth of $1 in each ETF and the broad-market benchmark.
growth_of_one = prices.div(prices.iloc[0])
growth_of_one.rename(
    columns={
        WORLD_TICKER: "MSCI World (URTH)",
        EM_TICKER: "Emerging Markets (EEM)",
        BENCHMARK_TICKER: "MSCI ACWI (ACWI)",
    }
).plot()
plt.title("Growth of $1: ETFs and Global Benchmark")
plt.ylabel("Value of $1")
plt.xlabel("Date")
plt.tight_layout()
plt.show()

# %%
# Portfolio versus benchmark: both series start at 1 on the first common date.
equity_curves.plot()
plt.title("70/30 Buy-and-Hold Portfolio vs. MSCI ACWI")
plt.ylabel("Growth of $1")
plt.xlabel("Date")
plt.tight_layout()
plt.show()

# %%
drawdowns = equity_curves.div(equity_curves.cummax()) - 1
drawdowns.plot()
plt.title("Drawdowns: Portfolio vs. MSCI ACWI")
plt.ylabel("Drawdown")
plt.xlabel("Date")
plt.tight_layout()
plt.show()

# %%
comparison_returns = pd.concat(
    {
        "70/30 Buy-and-Hold": strategy_returns,
        "MSCI ACWI (ACWI)": benchmark_returns,
    },
    axis="columns",
).dropna()
rolling_volatility = comparison_returns.rolling(252).std() * np.sqrt(252)
rolling_volatility.plot()
plt.title("Rolling 12-Month Annualized Volatility")
plt.ylabel("Annualized volatility")
plt.xlabel("Date")
plt.tight_layout()
plt.show()

# %%
asset_and_benchmark_returns = daily_returns[
    [WORLD_TICKER, EM_TICKER, BENCHMARK_TICKER]
].rename(
    columns={
        WORLD_TICKER: "MSCI World (URTH)",
        EM_TICKER: "Emerging Markets (EEM)",
        BENCHMARK_TICKER: "MSCI ACWI (ACWI)",
    }
)
correlations = asset_and_benchmark_returns.corr()

fig, ax = plt.subplots()
image = ax.imshow(correlations, cmap="coolwarm", vmin=-1, vmax=1)
ax.set_xticks(range(len(correlations.columns)), labels=correlations.columns, rotation=35, ha="right")
ax.set_yticks(range(len(correlations.index)), labels=correlations.index)
for row in range(len(correlations.index)):
    for column in range(len(correlations.columns)):
        ax.text(column, row, f"{correlations.iloc[row, column]:.2f}", ha="center", va="center")
fig.colorbar(image, ax=ax, label="Correlation")
ax.set_title("Daily Return Correlations")
fig.tight_layout()
plt.show()

# %%
rolling_correlations = pd.DataFrame(
    {
        "URTH vs. ACWI": daily_returns[WORLD_TICKER].rolling(252).corr(
            daily_returns[BENCHMARK_TICKER]
        ),
        "EEM vs. ACWI": daily_returns[EM_TICKER].rolling(252).corr(
            daily_returns[BENCHMARK_TICKER]
        ),
    }
)
rolling_correlations.plot()
plt.title("Rolling 12-Month Correlation with MSCI ACWI")
plt.ylabel("Correlation")
plt.xlabel("Date")
plt.ylim(-1, 1)
plt.tight_layout()
plt.show()

# %%
actual_weights.rename(
    columns={
        WORLD_TICKER: "MSCI World (URTH)",
        EM_TICKER: "Emerging Markets (EEM)",
    }
).plot()
plt.title("Portfolio Weights Over Time (No Rebalancing)")
plt.ylabel("Weight")
plt.xlabel("Date")
plt.tight_layout()
plt.show()
