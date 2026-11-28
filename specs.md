# 70/30 MSCI World / Emerging Markets Strategy

## Purpose

This specs document describes the investment rationale, data, portfolio rules,
backtest methodology, results, and limitations of the 70% MSCI World / 30%
MSCI Emerging Markets strategy. It is intended to support a clear and
reproducible presentation of the analysis.

## Strategy rationale

We chose a fixed 70% allocation to developed-market equities through URTH
(iShares MSCI World ETF) and 30% to emerging-market equities through EEM
(iShares MSCI Emerging Markets ETF). The objective is to reduce US
concentration relative to the broad global benchmark while keeping most of
the portfolio invested in developed markets. Annual rebalancing restores
the intended regional weights.

**The benchmark.** The iShares MSCI ACWI ETF covers both developed and
emerging markets. On November 25, 2026, its holdings included 88.9% developed
market equities and 10.7% emerging market equities as shares of total fund
NAV. The rest was about 0.3% before rounding. MSCI World, tracked by URTH,
covers developed markets and has a 0% emerging-market allocation. Our 30%
target is about 19 percentage points above the observed ACWI weight.

**The economic context.** Across the fixed 47-country roster, emerging
markets accounted for 38.8% of 2025 GDP in current US dollars and 57.2% of
GDP at purchasing power parity (PPP). The PPP measure adjusts for differences
in price levels across countries. Both measures describe economic production
and help explain why we wanted meaningful emerging-market exposure. The 30%
weight is a deliberate allocation choice, and the GDP analysis provides
context for that choice.

**The market-cap cross-check.** The World Bank and World Federation of
Exchanges report the market capitalization of listed domestic companies.
For 2025, we sum the reported values for the countries in each group and
divide the emerging-market subtotal by the combined total. Approximately
USD 39.4 trillion divided by USD 136.6 trillion gives 28.9%. Coverage is
23 of 24 emerging markets and 11 of 23 developed markets. Taiwan, France,
and the United Kingdom are among the missing observations. The percentage
describes only the covered countries, whereas ACWI uses the free
float-adjusted capitalization of eligible securities. We use this figure
as a secondary comparison. Its proximity to 30% does not establish an
appropriate allocation.

**What changes in the portfolio.** At the November 25, 2026 snapshot, US
equities account for 50.9% of the 70/30 portfolio, 64.8% of ACWI, and 72.7%
of URTH. Taiwan has an 8.1% weight in the portfolio versus 2.9% in ACWI.
Information technology remains a large exposure across all three
(30.4%, 28.5%, and 27.4%, respectively). The main difference is geographic.
Similar moves are consistent with the strategy and benchmark both holding
broad equity exposure. The snapshot illustrates the target allocation after
the backtest sample.

## Target investors and investment horizon

The strategy is designed for individual investors seeking long-term capital
growth through the equity portion of a diversified portfolio. Its intended
investors have the financial capacity and willingness to absorb substantial
losses, have no planned near-term withdrawals from this allocation, and
deliberately want more emerging-market exposure than a broad market-weighted
portfolio such as ACWI. URTH spreads the majority allocation across developed
markets, while EEM provides exposure to emerging-market equities through a
single fund. Annual rebalancing maintains the intended regional allocation
over time.

The intended investment horizon is at least 10 years. This is a planning
assumption based on the strategy's all-equity exposure and the investor's
ability to stay invested through prolonged downturns. Losses remain possible
even over that horizon. The rebalanced portfolio fell 33.50% from peak to
trough and had a beta of 1.01 against ACWI in the sample, indicating broad
equity-market sensitivity
despite the different regional weights. Its historical CAGR of 9.84% also
trailed ACWI's 10.74%, so an investor should be willing to tolerate periods of
benchmark underperformance to maintain the chosen emerging-market exposure.

Emerging-market holdings bring additional political, regulatory, liquidity,
and currency risks. The analysis measures performance in USD, so investors
with spending needs in another currency also face exchange-rate effects on
their realized returns. The strategy assumes investors can cover near-term
spending from other assets.

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

The analysis reports cumulative return, CAGR, annualized arithmetic average
return, annualized volatility, Sharpe ratio, maximum drawdown, annualized
active return, tracking error, information ratio, alpha, and beta. The
arithmetic average return is the mean daily return multiplied by 252 and is
reported separately from geometric CAGR.

Alpha and beta are estimated from aligned daily excess returns using an OLS
market model against ACWI: portfolio excess return is regressed on ACWI excess
return, with both excess returns measured over the date-matched FRED DGS3MO
rate. Alpha is the daily intercept multiplied by 252; beta is the regression
slope and is not annualized. Alpha and beta are not shown for ACWI itself,
which is the reference portfolio. These estimates are sample-dependent and
are not forecasts.

Visualizations include cumulative growth, drawdown, rolling volatility,
correlation, portfolio weights, calendar-year returns, and the daily excess
return regression for the rebalanced strategy.

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

The annualized arithmetic average returns were **10.92%** for the rebalanced
70/30 portfolio, **11.03%** for buy-and-hold, and **11.65%** for ACWI. The
market-model estimates against ACWI were an annualized alpha of **−0.86%** and
beta of **1.01** for the rebalanced portfolio, and an annualized alpha of
**−0.73%** and beta of **1.01** for buy-and-hold. Alpha is the annualized daily
regression intercept; beta is not annualized. ACWI is the reference and is
therefore not assigned alpha or beta against itself.

The arithmetic average returns are higher than the corresponding CAGRs because
the arithmetic measure annualizes the average daily return without accounting
for compounding and volatility drag. The rebalanced portfolio's beta of 1.01
indicates approximately one-for-one historical sensitivity to ACWI's daily
excess returns. Its negative alpha of −0.86% per year indicates that its
average return was below the one-factor market-model estimate after accounting
for that exposure. Buy-and-hold shows a similar beta and a negative alpha of
−0.73% per year.

The 70/30 strategy underperformed ACWI over this sample period on CAGR, Sharpe
ratio, and estimated alpha. These are sample-period observations, not
forecasts or proof that emerging markets alone caused the difference. A
formal performance attribution would be required to quantify the contribution
of each allocation and of rebalancing.

## Regional and sector exhibits

The notebook's regional-context analysis retrieves IMF DataMapper GDP series
(NGDPD and PPPGDP) and the World Bank WDI market-cap series
(CM.MKT.LCAP.CD) through public APIs. It uses a fixed 47-country roster
(23 MSCI World and 24 MSCI Emerging Markets countries) taken from the iShares
holdings snapshot dated November 25, 2026; those groups are held constant over
the 2015–2025 GDP trend. The API-based notebook analysis does not read local
CSV, Excel, or Python source files.

The notebook retrieves the November 25, 2026 holdings from the iShares API,
verifies the date for URTH, EEM, and ACWI and sums equity positions by country
of risk and sector. It compares the 70/30 target portfolio with ACWI and URTH
using percentages of total NAV. The comparison puts these allocations
alongside the IMF GDP and World Bank/WFE market capitalization shares. The
holdings cover a single date after the backtest period.

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
  calculations, performance charts, regional comparisons, and dated holdings
  exposures.
- [`world_em_backtest.py`](./world_em_backtest.py) contains the main
  backtest logic as a Python script.
- [`regional_weighting_analysis.py`](./regional_weighting_analysis.py)
  provides separate supplemental country and sector holdings snapshots; it
  requires the local source files described in the README.

Run the notebook from top to bottom in Google Colab or Jupyter. Its setup cell
installs `yfinance`. The notebook retrieves price, Treasury, GDP, market-cap,
and iShares holdings data online. To run the standalone backtest script
locally, install the requirements:

```bash
python -m pip install -r requirements.txt
python world_em_backtest.py
```

The optional local holdings-snapshot script can be run separately with:

```bash
python regional_weighting_analysis.py
```

All notebook API downloads require an internet connection.
