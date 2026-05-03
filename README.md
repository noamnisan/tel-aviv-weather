# Tel Aviv Weather

A tiny Python terminal app that fetches current weather for Tel Aviv and displays it in a readable box.

It uses the official [Open-Meteo forecast API](https://open-meteo.com/en/docs), which supports current weather variables by latitude and longitude and does not require an API key for basic usage.

## Run

```powershell
python .\weather_tel_aviv.py
```

Disable terminal colors:

```powershell
python .\weather_tel_aviv.py --no-color
```

## What It Shows

- Current condition
- Temperature and apparent temperature
- Humidity
- Cloud cover
- Precipitation
- Wind speed, gusts, and direction

## Notes

Tel Aviv coordinates are embedded in the script:

- Latitude: `32.0853`
- Longitude: `34.7818`
