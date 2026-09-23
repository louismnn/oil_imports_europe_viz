# Europe Oil Imports Visualization

## Project Description

Europe Oil Imports is an interactive Dash application for exploring monthly oil imports into European countries. It combines a Leaflet map with a Plotly time-series chart.

Users can click a country on the map to identify it, display its boundary, draw partner-country import routes, and compare the main partner contributions over time.

## Features

- Interactive Leaflet map centered on Europe.
- Country selection through Nominatim reverse geocoding.
- Validation against the European country list in `assets/database.json`.
- Highlighting of the selected country's boundary.
- Curved directional import routes with arrowheads.
- Route thickness based on the latest import distribution.
- Interactive route tooltips.
- Stacked percentage time-series graph for the main partners and `OTHERS`.
- Automatic Eurostat refresh when local data is older than 120 days.
- Custom responsive styling from `assets/header.css`.

## Data Source

The application retrieves data from the Eurostat Dissemination API using the [`nrg_ti_oilm`](https://ec.europa.eu/eurostat/databrowser/view/NRG_TI_OILM/default/table?lang=en) dataflow.

The request uses monthly frequency (`M`), oil products (`O4000`), and thousand tonnes (`THS_T`). The downloaded data is normalized by `util.normalize_datas()` and saved as `assets/eurostat_data.csv`.

Country names and European-country validation data are stored in `assets/database.json`.

The application refreshes the dataset when the newest local observation is more than 120 days old. A network connection is required when the local data needs updating.

Moreover, geojson datas for countries shape are coming from the GitHub repository of [BenPortner](https://github.com/BenPortner/geojson-atlas/tree/main).

## Installation

Python 3.14 is recommended.

Create and activate a virtual environment from the project directory:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

Install the dependencies:

```powershell
python -m pip install -r requirements.txt
```

The main dependencies are Dash, Dash Leaflet, Plotly, pandas, NumPy, geopy, and countryinfo.

## Usage

1. Start the application from the project root.
2. Open the local URL shown by Dash in a browser.
3. Click inside a European country on the map.
4. Wait for reverse geocoding to identify the country.
5. Inspect the highlighted country, partner routes, tooltips, and time-series graph.

![Example for Germany](assets\fig_0.png)

The first click may take a few seconds because the application contacts the Nominatim reverse-geocoding service.

## How To Run

From the project root, with the virtual environment activated:

```powershell
python main.py
```

The application runs in debug mode on port `3000`:

```text
http://127.0.0.1:3000
```

Stop the server with `Ctrl+C` in the terminal running the application.

## Project Structure

```
|-- main.py                  Dash application and callbacks
|-- util.py                  Data processing, geocoding, and route helpers
|-- generate_time_series.py  Plotly graph construction
|-- requirements.txt         Python dependencies
|-- assets/
    |-- database.json         Country metadata
    |-- header.css            Application styling
    |-- favicon.ico
    |-- countries             Geojson datas
```

## Generated Data Files

`assets/eurostat_data.csv` is the normalized dataset used by the application. During a refresh, the raw download is temporarily written to `assets/eurostat_data_raw.csv` and then converted into the normalized CSV.

The raw file is removed after normalization by the current implementation.

## Troubleshooting

- If startup downloads data, wait for the Eurostat request and normalization to finish.
- If a map click does not update the graph, click on another country and wait few seconds to retry.
- Nominatim is an external service and may be slow or rate-limited.
- Start the application from the project root so relative `assets/` paths resolve correctly.
