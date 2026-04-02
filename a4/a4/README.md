# CP321 Assignment 4 - COVID-19 Interactive Dashboard

Interactive Flask + Plotly web app visualizing monthly COVID-19 data for five countries (Canada, United States, United Kingdom, India, Japan) from January 2020 to December 2024.

## Setup

Requires Python 3.9+.

```bash
pip install flask plotly pandas
```

## Run

```bash
cd a4
python app.py
```

Then open http://127.0.0.1:5000 in a browser.

## Project Structure

```
a4/
├── app.py                              # Flask app (cleaning + routes)
├── COVID_Country_Sample.csv            # Raw dataset
├── COVID_Country_Sample_Cleaned.csv    # Cleaned dataset (generated on startup)
├── templates/
│   └── index.html                      # Dashboard template (Plotly + controls)
├── static/
│   └── style.css                       # Stylesheet
└── README.md
```

## Features

- Country dropdown and metric toggle update the Plotly chart via fetch() without page reload
- JSON API at /data?country=Canada&metric=new_cases
- Okabe-Ito colourblind-friendly palette with fixed colour-country mapping
- Responsive layout (laptop and mobile)
- Insights section with trend analysis and design choice justification

## Author

Nick Kunde-Lenny - Wilfrid Laurier University