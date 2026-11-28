# FM2270 Financial Modelling Group Project

The project backtests a portfolio invested 70% in URTH (iShares MSCI World ETF)
and 30% in EEM (iShares MSCI Emerging Markets ETF). ACWI is the broad global
equity benchmark.

## Run the notebook in Google Colab

1. Open [world_em_backtest.ipynb in Colab](https://colab.research.google.com/github/BeneFuchs123/fm-group-F/blob/main/world_em_backtest.ipynb).
   You can also upload `world_em_backtest.ipynb` from your computer.
2. Select **Runtime > Run all**. The setup cell installs `yfinance`.
3. Use the tables and figures from that run in the prospectus.

The notebook is self-contained and requires an internet connection. It fetches
ETF prices from Yahoo Finance, 3-month US Treasury yields from FRED, GDP from
IMF DataMapper, listed-company market capitalization from the World Bank, and
dated ETF holdings from iShares. The notebook is the only project file needed
in Colab.

## What the notebook produces

The backtest uses adjusted daily closing prices from January 2015 through
October 2026. It compares annual rebalancing and buy-and-hold with ACWI.
The 2026 calendar-year return covers the period through October 30.
The performance tables show annualized arithmetic return, CAGR, volatility,
Sharpe ratio, maximum drawdown, tracking error, information ratio, alpha,
and beta. The primary Sharpe ratio uses the FRED Treasury yield. Annualized
alpha is the daily excess-return regression intercept multiplied by 252.
Beta is the slope of the daily regression. The backtest excludes trading
costs, taxes, and ongoing contributions.

The regional analysis produces four figures:

- The emerging-market share of nominal and purchasing-power-adjusted GDP from
  2015 to 2025, with the 30% target as a reference.
- A comparison of emerging-market portfolio weights with 2025 GDP and
  World Bank/WFE listed-company market-cap shares.
- A comparison of the largest country equity exposures in the 70/30
  portfolio, ACWI, and MSCI World (URTH), with a full country table.
- A comparison of equity sector exposures for the same three portfolios,
  with a full sector table.

The country and sector comparisons use the November 25, 2026 holdings
snapshot. The GDP trend uses a fixed set of countries, and the World Bank
market-cap comparison reports which share of each country group has data.
[specs.md](./specs.md) explains the rationale, methodology, and limitations.

## Run the backtest as a Python script

Use Python 3.10 or newer to run the backtest calculations and performance
charts locally.

```bash
python -m pip install -r requirements.txt
python world_em_backtest.py
```

Use the notebook for the regional comparisons and the prospectus figures.
