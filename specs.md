# 70/30 MSCI World / Emerging Markets Strategy

## Purpose

This specs document describes the investment rationale, data, portfolio rules,
backtest methodology, results, and limitations of the 70% MSCI World / 30%
MSCI Emerging Markets strategy. It is intended to support a clear and
reproducible presentation of the analysis.

## Strategy rationale

The strategy combines developed-market equities through URTH (iShares MSCI
World ETF) with emerging-market equities through EEM (iShares MSCI Emerging
Markets ETF). The 70/30 allocation is a fixed policy choice informed by the
common GDP-oriented 70/30 approach described by Finanzfluss. It is not
calculated dynamically from GDP or market capitalization, and the analysis
does not establish that 30% is an optimal allocation.

GDP is used as an economic reference because it measures the scale of
production, while equity-market capitalization reflects the value of listed
companies. These measures describe different things: GDP is not itself an
investable market portfolio, and an economy's GDP share does not determine its
stock-market return.

The IMF comparison uses the 47 countries represented in the current MSCI World
and MSCI Emerging Markets holdings universe. For 2025, emerging markets
represented 38.8% of nominal GDP and 57.2% of GDP at purchasing power parity
(PPP) within that country universe. These figures provide context for a
30% EM allocation, but they do not produce that allocation exactly. The
country groups are based on current ETF holdings and are held constant in the
2015–2025 trend; this is a descriptive comparison, not a historical
reclassification.

As an additional reference, the 2025 World Bank/World Federation of Exchanges
market-cap data gives a 28.9% EM share among countries with reported data.
Coverage is incomplete: values are available for 11 of 23 developed markets
and 23 of 24 emerging markets. This result is therefore not a robust estimate
of global investable market capitalization and is not used to set the
portfolio weights.

The current holdings snapshot dated November 25, 2026, shows approximately
50.9% US exposure in the combined 70/30 portfolio. This is calculated from
the current country weights of both ETFs and is not a historical exposure
series. MSCI World is not a US-only index, but its substantial US weight means
the portfolio remains considerably exposed to the United States. The EM
allocation broadens regional exposure; it does not create an equal regional
weighting or remove US concentration.

## Portfolio and benchmark rules

- **World allocation:** 70% URTH.
- **Emerging-markets allocation:** 30% EEM.
- **Rebalancing:** The primary strategy is reset to 70/30 annually at the
  calendar-year boundary. A 70/30 buy-and-hold portfolio is included to show
  the effect of not rebalancing.
- **Benchmark:** ACWI is used as a broad, global, market-cap-weighted equity
  benchmark. A separate benchmark made from the same 70/30 ETFs and rebalanced
  on the same schedule would reproduce the strategy rather than provide an
  independent comparison.
- **Currency:** ETF prices, returns, and the benchmark comparison are in USD.

## Data and methodology

The backtest downloads adjusted daily closing prices from Yahoo Finance for
URTH, EEM, and ACWI. Adjusted prices are used as a proxy for total returns.
The date range is January 2015 through October 2026; the latest price in the
validated run is October 30, 2026. The 2026 calendar-year return is therefore
partial.

Daily simple returns are calculated from the adjusted prices. Portfolio
returns are calculated using the weights in place at the start of each daily
interval. At each calendar-year boundary, the primary portfolio is restored
to its 70/30 target weights for the following year's returns.

The primary Sharpe ratio uses the date-matched 3-month US Treasury yield,
FRED series DGS3MO. The annualized yield is converted into an approximate
risk-free return over each price interval. The Sharpe ratio is calculated as
the mean daily portfolio excess return divided by the standard deviation of
portfolio daily returns, multiplied by the square root of 252. A zero
risk-free-rate Sharpe ratio is also reported as a sensitivity check. The
Treasury yield is a proxy for a risk-free return, not a directly invested
daily Treasury total-return series.

The analysis reports cumulative return, CAGR, annualized volatility, Sharpe
ratio, maximum drawdown, annualized active return, tracking error, and
information ratio. It also includes cumulative-growth, drawdown, rolling
volatility, correlation, portfolio-weight, and calendar-year-return
visualizations.

## Historical results

For the validated run from January 2, 2015, through October 30, 2026:

- The annually rebalanced 70/30 portfolio had a CAGR of **9.84%**, annualized
  volatility of **17.38%**, maximum drawdown of **−33.50%**, and
  3-month-Treasury Sharpe ratio of **0.51**.
- The 70/30 buy-and-hold portfolio had a CAGR of **9.98%**, annualized
  volatility of **17.28%**, maximum drawdown of **−33.49%**, and
  3-month-Treasury Sharpe ratio of **0.51**.
- ACWI had a CAGR of **10.74%**, annualized volatility of **16.87%**, maximum
  drawdown of **−33.53%**, and 3-month-Treasury Sharpe ratio of **0.56**.

The 70/30 strategy underperformed ACWI over this sample period on both CAGR
and Sharpe ratio. This is an observed historical result, not evidence that
emerging markets alone caused the difference. A formal performance
attribution would be required to quantify the contribution of each allocation
and of rebalancing.

## Regional and sector exhibits

The regional analysis combines the November 25, 2026 iShares holdings using
the 70/30 target to estimate current country and sector exposures. These are
holdings snapshots, not historical backtest allocations. Price history alone
cannot establish historical country or sector composition.

The IMF GDP comparison and the World Bank/WFE market-cap comparison are
calculated separately across the country groups; the 70/30 portfolio weights
are not applied to those GDP or market-cap totals. Recent IMF WEO observations
may include estimates. World Bank/WFE listed-company capitalization is not
equivalent to MSCI free-float-adjusted investable capitalization.

## Limitations

- Historical results do not predict future performance.
- Trading costs, taxes, and investor cash flows are not modeled.
- ETF expense ratios are not itemized separately in the backtest.
- The 2026 result covers only the period through October 30.
- The current country and sector holdings snapshots should not be interpreted
  as historical exposures.
- The World Bank/WFE market-cap comparison has material country-coverage gaps.
- The 70/30 allocation is a fixed, GDP-informed choice, not a uniquely derived
  or optimized weight.

## Project files and reproduction

- [`world_em_backtest.ipynb`](./world_em_backtest.ipynb) contains the
  calculations, performance charts, and regional exhibits.
- [`world_em_backtest.py`](./world_em_backtest.py) contains the main
  backtest logic as a Python script.
- [`regional_weighting_analysis.py`](./regional_weighting_analysis.py)
  calculates GDP comparisons and current country and sector exposures.

Install the requirements and run the backtest from the project directory:

```bash
python -m pip install -r requirements.txt
python world_em_backtest.py
```

Run the regional analysis separately with:

```bash
python regional_weighting_analysis.py
```

The price and risk-free-rate downloads require an internet connection.
