# FM2270 Financial Modelling Group Project

Backtest of a portfolio invested 70% in URTH (iShares MSCI World ETF) and 30%
in EEM (iShares MSCI Emerging Markets ETF), compared with ACWI as a broad
global equity-market benchmark.

## Files

- `world_em_backtest.ipynb` — interactive notebook with calculations and charts.
- `world_em_backtest.py` — Python script containing the main backtest logic, organized into VS Code/Jupyter cells. The notebook also includes the regional analysis section.
- `regional_weighting_analysis.py` — compares current iShares country holdings with IMF GDP and World Bank/WFE market-cap data.

## Run

Install the requirements, then run the backtest from the notebook or script:

```bash
python -m pip install -r requirements.txt
```

Use Python 3.10 or newer.

Open `world_em_backtest.ipynb` and run all cells, or run the backtest script:

```bash
python world_em_backtest.py
```

The notebook downloads adjusted closing prices from Yahoo Finance for
January 2015 through October 2026. It models annual rebalancing at calendar
year boundaries, and also shows a 70/30 buy-and-hold portfolio for comparison.
The primary Sharpe ratio uses a date-matched 3-month U.S. Treasury yield from
FRED; a zero-risk-free-rate Sharpe ratio is included as a sensitivity check.
Transaction costs, taxes, and ongoing contributions are not modelled. The final
2026 calendar-year return is partial, through October 31.

ACWI is used as the broad market benchmark. A separate 70/30 benchmark made
from the same ETFs and rebalanced on the same schedule would reproduce the
strategy rather than provide an independent comparison.

The code includes cumulative growth, portfolio-versus-benchmark performance,
drawdowns, rolling volatility, return correlations, rolling correlations,
portfolio weights, calendar-year returns, and performance metrics. Price
history alone cannot produce historical sector or country allocations. The
notebook's final section instead displays current holdings snapshots from the
provided iShares files, clearly distinguished from backtest-period results.

The supplied example notebook uses a different allocation: 50% SSAC.L and 50%
ACWD.L, with ACWU.L as its benchmark. These are all MSCI ACWI-tracking funds,
so that example mainly compares ETF implementations of the same broad index;
it is not the 70/30 World/Emerging Markets strategy. Its hard-coded allocation
charts do not come from its price backtest. The current notebook compares the
70/30 portfolio with ACWI and uses the supplied current iShares holdings for
its separate country and sector snapshots.

Historical results are illustrative and do not predict future performance.

## Regional weighting comparison

Run the regional analysis from the project directory:

```bash
python regional_weighting_analysis.py
```

It reads the supplied iShares World and Emerging Markets holdings exports, the
IMF WEO dataset, and the World Bank market-cap download. It writes the
country-level equity exposure for a 70/30 combination to
`portfolio_country_exposure.csv`, a source/coverage summary to
`regional_weighting_summary.csv`, country-level input data to
`regional_country_data.csv`, and a comparison chart to
`regional_weighting_comparison.png`. The IMF GDP share time series is saved to
`gdp_share_trend.csv` and visualized in `gdp_share_trend.png`. Current sector
exposures are saved as `portfolio_sector_exposure.csv`; country and sector
charts are saved as `portfolio_country_allocation.png` and
`portfolio_sector_allocation.png`. The notebook's final section runs this
analysis and displays these charts alongside the GDP visualizations.

The ETF holdings are dated November 25, 2026. Country weights in
`portfolio_country_exposure.csv` use the 70/30 target and iShares' reported
holding weights. Separately, GDP and market-cap shares are calculated by
summing country data across the MSCI World and MSCI Emerging Markets country
groups; the 70/30 target is not applied to these sums. Country groups follow
the current iShares index holdings, with an immaterial residual Russian
Federation position excluded from the EM roster.

[Finanzfluss describes 70/30](https://www.finanzfluss.de/etf/portfolio/70-30/)
as an approximate GDP-oriented allocation but does not specify a GDP basis or
publish a calculation. The IMF comparison therefore reports both PPP GDP and
nominal GDP in current U.S. dollars. The
trend chart shows both EM GDP shares from 2015 to 2025 against the fixed 30%
portfolio target. Current country groups are held constant across the series;
this is a descriptive comparison, not a historical reclassification or
portfolio backtest. The latest WEO observations may include estimates.

The country and sector charts adapt the holdings-based exhibits in the Group
AL report using the current 70/30 ETF holdings. They are a snapshot dated
November 25, 2026, not historical allocation charts. Performance, drawdown,
volatility, correlation, and portfolio-weight plots remain in the backtest
notebook; only exhibits that can be supported by this strategy's data are
included.
2025 World Bank/WFE market-cap comparison is coverage-limited because the
download has missing country observations. Its listed-domestic-company values
are not the same as MSCI's free-float-adjusted investable market capitalization.
Use these results as rationale and context, not as evidence that 30% is the
uniquely correct allocation.
