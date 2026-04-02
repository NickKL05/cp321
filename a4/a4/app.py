"""
Assignment 4 - Interactive Web Visualization with Flask & Plotly
CP321 Data Analytics, Wilfrid Laurier University
Author: Nick Kunde-Lenny

This module loads, inspects, and cleans the COVID_Country_Sample.csv dataset,
then serves an interactive Plotly dashboard via Flask.
"""

import os
import pandas as pd
import numpy as np
from flask import Flask, render_template, request, jsonify

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# ──────────────────────────────────────────────────────────────
# Part A - Load, Inspect, Clean
# ──────────────────────────────────────────────────────────────

raw = pd.read_csv(os.path.join(BASE_DIR, "COVID_Country_Sample.csv"), parse_dates=["date"])

# ---- inspection (printed once at startup for development) ----
print("=" * 60)
print("RAW DATA INSPECTION")
print("=" * 60)
print(f"\nShape: {raw.shape}")
print(f"\nColumns & dtypes:\n{raw.dtypes}")
print(f"\nHead:\n{raw.head()}")
print(f"\nDescribe:\n{raw.describe()}")
print(f"\nMissing values:\n{raw.isnull().sum()}")
print(f"\nCountries: {sorted(raw['country'].unique())}")
print(f"Date range: {raw['date'].min()} to {raw['date'].max()}")

# ---- cleaning ----
df = raw.copy()

# 1. Missing new_vaccinations (6 nulls).
#    These fall in early months (pre-rollout) where no country had begun
#    vaccinating yet.  Filling with 0 is the correct domain interpretation:
#    no vaccines were administered, not that the value is unknown.
print(f"\nnew_vaccinations nulls before fill: {df['new_vaccinations'].isnull().sum()}")
df["new_vaccinations"] = df["new_vaccinations"].fillna(0).astype(int)
print(f"new_vaccinations nulls after fill:  {df['new_vaccinations'].isnull().sum()}")

# 2. Spike / outlier detection.
#    The assignment notes the CSV "contains a few spikes for realism."
#    I flag per-country values beyond 3 IQRs above Q3 so I can annotate
#    them in the chart and discuss them in the insights section rather
#    than silently removing real data points.
spike_flags = []
for country in df["country"].unique():
    mask = df["country"] == country
    for col in ["new_cases", "new_deaths"]:
        series = df.loc[mask, col]
        q1, q3 = series.quantile(0.25), series.quantile(0.75)
        iqr = q3 - q1
        upper = q3 + 3 * iqr
        spikes = df.loc[mask & (df[col] > upper)]
        for _, row in spikes.iterrows():
            spike_flags.append(
                f"  {country} | {row['date'].strftime('%Y-%m')} | {col} = {row[col]}"
                f"  (upper fence = {upper:.0f})"
            )

if spike_flags:
    print(f"\nDetected {len(spike_flags)} spike(s) (kept, will annotate):")
    for s in spike_flags:
        print(s)
else:
    print("\nNo spikes detected beyond 3×IQR.")

# 3. Confirm no remaining issues.
assert df.isnull().sum().sum() == 0, "Unexpected nulls remain after cleaning"
print(f"\nCleaned shape: {df.shape}  |  Nulls remaining: {df.isnull().sum().sum()}")

# 4. Save cleaned CSV.
df.to_csv(os.path.join(BASE_DIR, "COVID_Country_Sample_Cleaned.csv"), index=False)
print("Saved cleaned CSV.\n")


# ──────────────────────────────────────────────────────────────
# Precompute summary for template
# ──────────────────────────────────────────────────────────────

countries = sorted(df["country"].unique().tolist())
date_min = df["date"].min().strftime("%B %Y")
date_max = df["date"].max().strftime("%B %Y")
metrics = [
    {"value": "new_cases",                "label": "New Cases"},
    {"value": "new_deaths",               "label": "New Deaths"},
    {"value": "new_vaccinations",         "label": "New Vaccinations"},
    {"value": "cases_per_million",        "label": "Cases per Million"},
    {"value": "vaccinations_per_hundred", "label": "Vaccinations per Hundred"},
]

# Okabe-Ito mapping - consistent across every chart, colourblind-friendly.
COUNTRY_COLORS = {
    "Canada":         "#0072B2",
    "India":          "#E69F00",
    "Japan":          "#009E73",
    "United Kingdom": "#CC79A7",
    "United States":  "#D55E00",
}


# ──────────────────────────────────────────────────────────────
# Part B - Flask App Skeleton
# ──────────────────────────────────────────────────────────────

app = Flask(__name__)


@app.route("/")
def index():
    """Root route - renders the dashboard with summary context."""
    return render_template(
        "index.html",
        countries=countries,
        metrics=metrics,
        date_min=date_min,
        date_max=date_max,
    )


# ──────────────────────────────────────────────────────────────
# Part D - JSON Data Endpoint
# ──────────────────────────────────────────────────────────────

@app.route("/data")
def data():
    """
    Returns JSON for a given country + metric.
    Usage: /data?country=Canada&metric=new_cases
    """
    country = request.args.get("country", "Canada")
    metric = request.args.get("metric", "new_cases")

    if country not in countries:
        return jsonify({"error": f"Unknown country: {country}"}), 400
    valid_metrics = [m["value"] for m in metrics]
    if metric not in valid_metrics:
        return jsonify({"error": f"Unknown metric: {metric}"}), 400

    subset = df[df["country"] == country][["date", metric]].copy()
    subset["date"] = subset["date"].dt.strftime("%Y-%m-%d")

    return jsonify({
        "country": country,
        "metric": metric,
        "color": COUNTRY_COLORS.get(country, "#333333"),
        "dates": subset["date"].tolist(),
        "values": subset[metric].tolist(),
    })


if __name__ == "__main__":
    app.run(debug=True)