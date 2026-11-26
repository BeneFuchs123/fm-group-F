"""Compare MSCI World/EM country groups with GDP and market-cap data."""

from __future__ import annotations

import xml.etree.ElementTree as ET
from pathlib import Path

import matplotlib.pyplot as plt
import pandas as pd


ROOT = Path(__file__).resolve().parent
WORLD_HOLDINGS_FILE = ROOT / "iShares-MSCI-World-ETF_fund.xls"
EM_HOLDINGS_FILE = ROOT / "iShares-MSCI-Emerging-Markets-ETF_fund.xls"
IMF_FILE = ROOT / "dataset_2026-11-26T17_02_03.892761112Z_DEFAULT_INTEGRATION_IMF.RES_WEO_9.0.0.csv"
WORLD_BANK_FILE = (
    ROOT
    / "API_CM.MKT.LCAP.CD_DS2_en_csv_v2_73139"
    / "API_CM.MKT.LCAP.CD_DS2_en_csv_v2_73139.csv"
)

WORLD_TARGET_WEIGHT = 0.70
EM_TARGET_WEIGHT = 0.30
COMPARISON_YEAR = 2025
TREND_START_YEAR = 2015
TREND_END_YEAR = 2025
TREND_YEARS = [str(year) for year in range(TREND_START_YEAR, TREND_END_YEAR + 1)]
EM_COUNTRY_ROSTER_EXCLUSIONS = {"Russian Federation"}
XML_NAMESPACE = "urn:schemas-microsoft-com:office:spreadsheet"
NS = {"ss": XML_NAMESPACE}

IMF_COUNTRY_ALIASES = {
    "China": "China, People's Republic of",
    "Egypt": "Egypt, Arab Republic of",
    "Hong Kong": "Hong Kong Special Administrative Region, People's Republic of China",
    "Korea (South)": "Korea, Republic of",
    "Netherlands": "Netherlands, The",
    "Poland": "Poland, Republic of",
    "Taiwan": "Taiwan Province of China",
    "Turkey": "Türkiye, Republic of",
}

WORLD_BANK_COUNTRY_ALIASES = {
    "Czech Republic": "Czechia",
    "Egypt": "Egypt, Arab Rep.",
    "Hong Kong": "Hong Kong SAR, China",
    "Korea (South)": "Korea, Rep.",
    "Taiwan": "Taiwan, China",
    "Turkey": "Turkiye",
}


def load_ishares_holdings(path: Path) -> tuple[pd.DataFrame, str]:
    text = path.read_text(encoding="utf-8-sig")
    start = text.index('<ss:Worksheet ss:Name="Holdings">')
    end = text.index("</ss:Worksheet>", start) + len("</ss:Worksheet>")
    worksheet = text[start:end]
    root = ET.fromstring(
        f'<root xmlns:ss="{XML_NAMESPACE}">{worksheet}</root>'
    )
    rows = root.findall(".//ss:Row", NS)
    values = [
        [
            cell.findtext("ss:Data", default="", namespaces=NS)
            for cell in row.findall("ss:Cell", NS)
        ]
        for row in rows
    ]

    header_index = next(
        (index for index, row in enumerate(values) if row and row[0] == "Ticker"),
        None,
    )
    if header_index is None:
        raise ValueError(f"No holdings table found in {path.name}.")

    headers = values[header_index]
    records = [
        (row + [""] * len(headers))[: len(headers)]
        for row in values[header_index + 1 :]
    ]
    holdings = pd.DataFrame(records, columns=headers)
    required_columns = {"Asset Class", "Location", "Weight (%)"}
    if not required_columns.issubset(holdings.columns):
        raise ValueError(f"{path.name} is missing required holdings columns.")

    holdings["Weight (%)"] = pd.to_numeric(
        holdings["Weight (%)"],
        errors="coerce",
    )
    total_weight = holdings["Weight (%)"].sum()
    if pd.isna(total_weight) or abs(total_weight - 100) > 0.1:
        raise ValueError(
            f"Holdings weights in {path.name} sum to {total_weight:.4f}%, "
            "not approximately 100%."
        )

    as_of_row = next(
        (
            row
            for row in values
            if row and row[0] == "Fund Holdings as of" and len(row) > 1
        ),
        None,
    )
    as_of = as_of_row[1] if as_of_row else "date not found"
    return holdings, as_of


def country_equity_weights(holdings: pd.DataFrame) -> pd.Series:
    equities = holdings.loc[
        holdings["Asset Class"].eq("Equity")
        & holdings["Location"].notna()
        & holdings["Location"].ne("")
        & holdings["Location"].ne("--")
    ]
    return equities.groupby("Location")["Weight (%)"].sum()


def sector_equity_weights(holdings: pd.DataFrame) -> pd.Series:
    equities = holdings.loc[
        holdings["Asset Class"].eq("Equity")
        & holdings["Sector"].notna()
        & holdings["Sector"].ne("")
        & holdings["Sector"].ne("--")
    ]
    return equities.groupby("Sector")["Weight (%)"].sum()


def load_imf_history(code: str) -> pd.DataFrame:
    data = pd.read_csv(IMF_FILE, low_memory=False)
    year_columns = [str(year) for year in range(TREND_START_YEAR, TREND_END_YEAR + 1)]
    matching = data.loc[
        data["SERIES_CODE"].astype("string").str.endswith(f".{code}.A", na=False),
        ["COUNTRY", *year_columns],
    ].copy()
    if matching.empty:
        raise ValueError(f"IMF series {code} was not found in {IMF_FILE.name}.")
    if matching["COUNTRY"].duplicated().any():
        raise ValueError(f"IMF series {code} has duplicate country rows.")
    return matching.set_index("COUNTRY")[year_columns].apply(
        pd.to_numeric,
        errors="coerce",
    )


def load_world_bank_series() -> pd.Series:
    data = pd.read_csv(WORLD_BANK_FILE, skiprows=4)
    if "Country Name" not in data or str(COMPARISON_YEAR) not in data:
        raise ValueError(f"Expected country and {COMPARISON_YEAR} columns in World Bank data.")
    values = data.set_index("Country Name")[str(COMPARISON_YEAR)]
    return pd.to_numeric(values, errors="coerce")


def regional_share(
    developed_countries: list[str],
    emerging_countries: list[str],
    values: pd.Series,
    aliases: dict[str, str],
) -> dict[str, object]:
    matched: dict[str, list[tuple[str, float]]] = {"developed": [], "emerging": []}
    missing: dict[str, list[str]] = {"developed": [], "emerging": []}

    for region, countries in (
        ("developed", developed_countries),
        ("emerging", emerging_countries),
    ):
        for country in countries:
            data_name = aliases.get(country, country)
            value = values.get(data_name)
            if value is None or pd.isna(value):
                missing[region].append(country)
            else:
                matched[region].append((country, float(value)))

    developed_total = sum(value for _, value in matched["developed"])
    emerging_total = sum(value for _, value in matched["emerging"])
    denominator = developed_total + emerging_total
    if denominator <= 0 or emerging_total <= 0:
        raise ValueError("No usable regional data was found for the comparison.")

    return {
        "em_share_pct": emerging_total / denominator * 100,
        "developed_share_pct": developed_total / denominator * 100,
        "developed_count": len(matched["developed"]),
        "developed_total": len(developed_countries),
        "emerging_count": len(matched["emerging"]),
        "emerging_total": len(emerging_countries),
        "missing_developed": ", ".join(missing["developed"]),
        "missing_emerging": ", ".join(missing["emerging"]),
    }


def country_gdp_and_market_cap(
    developed_countries: list[str],
    emerging_countries: list[str],
    ppp: pd.Series,
    nominal: pd.Series,
    market_cap: pd.Series,
) -> pd.DataFrame:
    rows = []

    for region, countries in (
        ("Developed (MSCI World)", developed_countries),
        ("Emerging (MSCI EM)", emerging_countries),
    ):
        for country in countries:
            imf_name = IMF_COUNTRY_ALIASES.get(country, country)
            wb_name = WORLD_BANK_COUNTRY_ALIASES.get(country, country)
            rows.append(
                {
                    "MSCI region": region,
                    "Country": country,
                    f"IMF PPP GDP {COMPARISON_YEAR} (billion international $)": ppp.get(
                        imf_name
                    ),
                    f"IMF nominal GDP {COMPARISON_YEAR} (billion US$)": nominal.get(
                        imf_name
                    ),
                    f"World Bank/WFE market cap {COMPARISON_YEAR} (current US$)": market_cap.get(
                        wb_name
                    ),
                }
            )

    return pd.DataFrame(rows)


def gdp_share_history(
    developed_countries: list[str],
    emerging_countries: list[str],
    ppp_history: pd.DataFrame,
    nominal_history: pd.DataFrame,
) -> pd.DataFrame:
    rows = []
    for basis, values in (
        ("Nominal GDP (current US$)", nominal_history),
        ("GDP (PPP, international $)", ppp_history),
    ):
        country_names = {
            country: IMF_COUNTRY_ALIASES.get(country, country)
            for country in developed_countries + emerging_countries
        }
        missing = [
            country
            for country, data_name in country_names.items()
            if data_name not in values.index
            or values.loc[data_name, TREND_YEARS].isna().any()
        ]
        if missing:
            raise ValueError(
                f"{basis} is missing one or more observations for 2015–2025: "
                f"{', '.join(missing)}."
            )

        developed_total = values.loc[
            [country_names[country] for country in developed_countries],
            TREND_YEARS,
        ].sum(axis=0)
        emerging_total = values.loc[
            [country_names[country] for country in emerging_countries],
            TREND_YEARS,
        ].sum(axis=0)
        combined_total = developed_total + emerging_total
        for year in TREND_YEARS:
            em_share = emerging_total[year] / combined_total[year] * 100
            rows.append(
                {
                    "Year": int(year),
                    "GDP basis": basis,
                    "Developed GDP share (%)": 100 - em_share,
                    "Emerging GDP share (%)": em_share,
                }
            )

    return pd.DataFrame(rows)


def save_gdp_share_chart(trend: pd.DataFrame, holdings_date: str) -> None:
    fig, ax = plt.subplots(figsize=(10, 5.5))
    for basis, label, color in (
        ("Nominal GDP (current US$)", "Nominal GDP (current US$)", "#416B8C"),
        ("GDP (PPP, international $)", "GDP at PPP (international $)", "#9A6B32"),
    ):
        series = trend.loc[trend["GDP basis"].eq(basis)].sort_values("Year")
        ax.plot(
            series["Year"],
            series["Emerging GDP share (%)"],
            marker="o",
            linewidth=2,
            label=label,
            color=color,
        )
        final = series.iloc[-1]
        ax.annotate(
            f'{final["Emerging GDP share (%)"]:.1f}%',
            (final["Year"], final["Emerging GDP share (%)"]),
            xytext=(7, 0),
            textcoords="offset points",
            va="center",
            color=color,
            fontsize=9,
        )

    ax.axhline(
        EM_TARGET_WEIGHT * 100,
        color="#454545",
        linestyle="--",
        linewidth=1.2,
        label="Portfolio target: 30% EM",
    )
    ax.set_title("Emerging markets' share of GDP over time")
    ax.set_xlabel("Year")
    ax.set_ylabel("Emerging-market share of combined GDP (%)")
    ax.set_xticks(range(TREND_START_YEAR, TREND_END_YEAR + 1, 1))
    ax.set_ylim(25, 65)
    ax.legend(loc="upper left")
    ax.grid(axis="x", visible=False)
    fig.text(
        0.01,
        0.01,
        (
            f"Source: IMF WEO dataset (updated Oct 2026), {TREND_START_YEAR}–{TREND_END_YEAR}. "
            f"Current ETF country groups held constant; 47 markets; holdings dated {holdings_date}. "
            "Recent WEO observations may include estimates. 30% line is a portfolio target, "
            "not a GDP-derived value."
        ),
        fontsize=8,
    )
    fig.tight_layout(rect=(0, 0.08, 1, 1))
    fig.savefig(ROOT / "gdp_share_trend.png", dpi=180, bbox_inches="tight")
    plt.close(fig)


def save_portfolio_snapshot_charts(
    country_exposure: pd.DataFrame,
    sector_exposure: pd.DataFrame,
    holdings_date: str,
) -> None:
    country_column = "Portfolio country exposure (% of NAV)"
    country_weights = country_exposure[country_column].sort_values(ascending=False)
    top_countries = country_weights.head(10)
    country_plot = pd.concat(
        [
            top_countries,
            pd.Series({"Other countries": country_weights.iloc[10:].sum()}),
        ]
    ).sort_values()

    fig, ax = plt.subplots(figsize=(9, 6))
    bars = ax.barh(country_plot.index, country_plot.values, color="#416B8C")
    ax.bar_label(bars, fmt="%.1f%%", padding=3)
    ax.set_xlabel("Portfolio country exposure (% of NAV)")
    ax.set_title("Largest country exposures in the 70/30 portfolio")
    ax.text(
        0,
        -0.16,
        f"Source: iShares holdings, {holdings_date}; country weights combined using 70% World / 30% EM.",
        transform=ax.transAxes,
        fontsize=8,
        va="top",
    )
    ax.grid(axis="y", visible=False)
    fig.tight_layout()
    fig.savefig(ROOT / "portfolio_country_allocation.png", dpi=180, bbox_inches="tight")
    plt.close(fig)

    sector_column = "Portfolio sector exposure (% of NAV)"
    sector_plot = sector_exposure[sector_column].sort_values()
    fig, ax = plt.subplots(figsize=(9, 6))
    bars = ax.barh(sector_plot.index, sector_plot.values, color="#416B8C")
    ax.bar_label(bars, fmt="%.1f%%", padding=3)
    ax.set_xlabel("Portfolio sector exposure (% of NAV)")
    ax.set_title("Sector exposures in the 70/30 portfolio")
    ax.text(
        0,
        -0.16,
        f"Source: iShares holdings, {holdings_date}; equity-sector weights combined using 70% World / 30% EM.",
        transform=ax.transAxes,
        fontsize=8,
        va="top",
    )
    ax.grid(axis="y", visible=False)
    fig.tight_layout()
    fig.savefig(ROOT / "portfolio_sector_allocation.png", dpi=180, bbox_inches="tight")
    plt.close(fig)


def main() -> None:
    world_holdings, world_as_of = load_ishares_holdings(WORLD_HOLDINGS_FILE)
    em_holdings, em_as_of = load_ishares_holdings(EM_HOLDINGS_FILE)
    world_country_weights = country_equity_weights(world_holdings)
    em_country_weights = country_equity_weights(em_holdings)

    country_exposure = pd.concat(
        [
            world_country_weights.rename("World ETF equity weight (%)"),
            em_country_weights.rename("Emerging Markets ETF equity weight (%)"),
        ],
        axis="columns",
    ).fillna(0)
    country_exposure["Portfolio country exposure (% of NAV)"] = (
        country_exposure["World ETF equity weight (%)"] * WORLD_TARGET_WEIGHT
        + country_exposure["Emerging Markets ETF equity weight (%)"] * EM_TARGET_WEIGHT
    )
    country_exposure.index.name = "Country"
    country_exposure = country_exposure.sort_values(
        "Portfolio country exposure (% of NAV)",
        ascending=False,
    )
    country_exposure.to_csv(ROOT / "portfolio_country_exposure.csv", float_format="%.6f")

    world_sector_weights = sector_equity_weights(world_holdings)
    em_sector_weights = sector_equity_weights(em_holdings)
    sector_exposure = pd.concat(
        [
            world_sector_weights.rename("World ETF equity weight (%)"),
            em_sector_weights.rename("Emerging Markets ETF equity weight (%)"),
        ],
        axis="columns",
    ).fillna(0)
    sector_exposure["Portfolio sector exposure (% of NAV)"] = (
        sector_exposure["World ETF equity weight (%)"] * WORLD_TARGET_WEIGHT
        + sector_exposure["Emerging Markets ETF equity weight (%)"] * EM_TARGET_WEIGHT
    )
    sector_exposure.index.name = "Sector"
    sector_exposure = sector_exposure.sort_values(
        "Portfolio sector exposure (% of NAV)",
        ascending=False,
    )
    sector_exposure.to_csv(ROOT / "portfolio_sector_exposure.csv", float_format="%.6f")
    save_portfolio_snapshot_charts(country_exposure, sector_exposure, em_as_of)

    developed_countries = sorted(world_country_weights.index.tolist())
    excluded_em_weight = em_country_weights.reindex(
        sorted(EM_COUNTRY_ROSTER_EXCLUSIONS)
    ).fillna(0).sum()
    if excluded_em_weight > 0.01:
        raise ValueError(
            "An excluded residual country has material EEM weight. "
            "Review the MSCI country roster before calculating regional shares."
        )
    emerging_countries = sorted(
        country
        for country in em_country_weights.index
        if country not in EM_COUNTRY_ROSTER_EXCLUSIONS
    )
    if len(developed_countries) != 23 or len(emerging_countries) != 24:
        raise ValueError(
            "The ETF country roster changed; review the MSCI classification "
            "before interpreting regional GDP or market-cap shares."
        )

    ppp_history = load_imf_history("PPPGDP")
    nominal_history = load_imf_history("NGDPD")
    market_cap_values = load_world_bank_series()
    ppp = regional_share(
        developed_countries,
        emerging_countries,
        ppp_history[str(COMPARISON_YEAR)],
        IMF_COUNTRY_ALIASES,
    )
    nominal = regional_share(
        developed_countries,
        emerging_countries,
        nominal_history[str(COMPARISON_YEAR)],
        IMF_COUNTRY_ALIASES,
    )
    market_cap = regional_share(
        developed_countries,
        emerging_countries,
        market_cap_values,
        WORLD_BANK_COUNTRY_ALIASES,
    )
    country_data = country_gdp_and_market_cap(
        developed_countries,
        emerging_countries,
        ppp_history[str(COMPARISON_YEAR)],
        nominal_history[str(COMPARISON_YEAR)],
        market_cap_values,
    )
    country_data.to_csv(ROOT / "regional_country_data.csv", index=False)
    trend = gdp_share_history(
        developed_countries,
        emerging_countries,
        ppp_history,
        nominal_history,
    )
    trend.to_csv(ROOT / "gdp_share_trend.csv", index=False, float_format="%.4f")
    save_gdp_share_chart(trend, em_as_of)
    roster_note = (
        "Country groups follow the current iShares MSCI World and MSCI EM "
        "equity-holding locations; the residual Russian Federation line in "
        "EEM is excluded from the EM index roster."
    )

    weighted_equity_exposure = (
        world_country_weights.sum() * WORLD_TARGET_WEIGHT
        + em_country_weights.sum() * EM_TARGET_WEIGHT
    )
    non_equity_exposure = 100 - weighted_equity_exposure

    summary = pd.DataFrame(
        [
            {
                "Measure": "Portfolio EEM sleeve",
                "Year or holdings date": f"{em_as_of} (World: {world_as_of})",
                "Developed-market share (%)": WORLD_TARGET_WEIGHT * 100,
                "Emerging-market share (%)": EM_TARGET_WEIGHT * 100,
                "Countries with data": "2 ETF holdings files",
                "Coverage note": "Target sleeve is set directly to 30%; not independently inferred.",
            },
            {
                "Measure": "IMF WEO GDP, PPP",
                "Year or holdings date": COMPARISON_YEAR,
                "Developed-market share (%)": ppp["developed_share_pct"],
                "Emerging-market share (%)": ppp["em_share_pct"],
                "Countries with data": (
                    f'Developed {ppp["developed_count"]}/{ppp["developed_total"]}; '
                    f'Emerging {ppp["emerging_count"]}/{ppp["emerging_total"]}'
                ),
                "Coverage note": roster_note,
            },
            {
                "Measure": "IMF WEO GDP, nominal USD",
                "Year or holdings date": COMPARISON_YEAR,
                "Developed-market share (%)": nominal["developed_share_pct"],
                "Emerging-market share (%)": nominal["em_share_pct"],
                "Countries with data": (
                    f'Developed {nominal["developed_count"]}/{nominal["developed_total"]}; '
                    f'Emerging {nominal["emerging_count"]}/{nominal["emerging_total"]}'
                ),
                "Coverage note": roster_note,
            },
            {
                "Measure": "World Bank/WFE market cap, available countries",
                "Year or holdings date": COMPARISON_YEAR,
                "Developed-market share (%)": market_cap["developed_share_pct"],
                "Emerging-market share (%)": market_cap["em_share_pct"],
                "Countries with data": (
                    f'Developed {market_cap["developed_count"]}/{market_cap["developed_total"]}; '
                    f'Emerging {market_cap["emerging_count"]}/{market_cap["emerging_total"]}'
                ),
                "Coverage note": (
                    f"{roster_note} Coverage-limited share among countries with reported values; "
                    f'missing developed: {market_cap["missing_developed"]}; '
                    f'missing emerging: {market_cap["missing_emerging"]}.'
                ),
            },
        ]
    )
    summary.to_csv(ROOT / "regional_weighting_summary.csv", index=False, float_format="%.4f")

    metrics = summary["Emerging-market share (%)"].astype(float)
    labels = [
        "ETF target\n(70/30)",
        "IMF GDP\n(PPP)",
        "IMF GDP\n(nominal USD)",
        "World Bank/WFE\nmarket cap*",
    ]
    fig, ax = plt.subplots(figsize=(9, 5.5))
    bars = ax.bar(
        labels,
        metrics,
        color=["#454545", "#416B8C", "#416B8C", "#9A6B32"],
    )
    ax.axhline(EM_TARGET_WEIGHT * 100, color="#454545", linestyle="--", linewidth=1.2)
    ax.bar_label(bars, fmt="%.1f%%", padding=4)
    ax.set_ylabel("Emerging-market share (%)")
    ax.set_ylim(0, max(65, float(metrics.max()) + 10))
    ax.set_title("Emerging-market share of GDP and reported market capitalization")
    ax.text(
        0,
        -0.24,
        (
            f"IMF WEO {COMPARISON_YEAR}; World Bank/WFE {COMPARISON_YEAR} available country rows "
            f"({market_cap['developed_count'] + market_cap['emerging_count']}/"
            f"{market_cap['developed_total'] + market_cap['emerging_total']} countries). "
            f"Dashed line: 30% strategy target. Holdings as of {em_as_of}; *coverage-limited."
        ),
        transform=ax.transAxes,
        fontsize=8,
        va="top",
    )
    ax.grid(axis="x", visible=False)
    fig.tight_layout()
    fig.savefig(ROOT / "regional_weighting_comparison.png", dpi=180, bbox_inches="tight")
    plt.close(fig)

    print(f"Holdings snapshots: World {world_as_of}; Emerging Markets {em_as_of}.")
    print(
        f"Regional GDP/cap shares use {len(developed_countries)} developed and "
        f"{len(emerging_countries)} emerging-market countries; "
        f"excluded EEM residual weight: {excluded_em_weight:.5f}%."
    )
    print(
        f"Weighted equity exposure: {weighted_equity_exposure:.3f}% of NAV; "
        f"cash/derivative residual: {non_equity_exposure:.3f}%."
    )
    print(summary.to_string(index=False))
    print("\n2025 market-cap data missing from the ETF country universe:")
    print(f"Developed: {market_cap['missing_developed']}")
    print(f"Emerging: {market_cap['missing_emerging']}")
    print("\nWrote regional_weighting_summary.csv, regional_country_data.csv,")
    print("portfolio_country_exposure.csv, portfolio_sector_exposure.csv,")
    print("portfolio_country_allocation.png, portfolio_sector_allocation.png,")
    print("regional_weighting_comparison.png, gdp_share_trend.csv, and gdp_share_trend.png.")


if __name__ == "__main__":
    main()
