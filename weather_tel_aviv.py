"""Show current weather for Tel Aviv using the Open-Meteo forecast API."""

from __future__ import annotations

import argparse
import json
import sys
import textwrap
import urllib.error
import urllib.parse
import urllib.request
from dataclasses import dataclass
from datetime import datetime


API_URL = "https://api.open-meteo.com/v1/forecast"
TEL_AVIV_LATITUDE = 32.0853
TEL_AVIV_LONGITUDE = 34.7818

WEATHER_CODES = {
    0: ("Clear sky", "sunny"),
    1: ("Mainly clear", "mostly sunny"),
    2: ("Partly cloudy", "partly cloudy"),
    3: ("Overcast", "cloudy"),
    45: ("Fog", "foggy"),
    48: ("Depositing rime fog", "foggy"),
    51: ("Light drizzle", "drizzly"),
    53: ("Moderate drizzle", "drizzly"),
    55: ("Dense drizzle", "very drizzly"),
    56: ("Light freezing drizzle", "icy drizzle"),
    57: ("Dense freezing drizzle", "icy drizzle"),
    61: ("Slight rain", "rainy"),
    63: ("Moderate rain", "rainy"),
    65: ("Heavy rain", "very rainy"),
    66: ("Light freezing rain", "icy rain"),
    67: ("Heavy freezing rain", "icy rain"),
    71: ("Slight snow", "snowy"),
    73: ("Moderate snow", "snowy"),
    75: ("Heavy snow", "very snowy"),
    77: ("Snow grains", "snowy"),
    80: ("Slight rain showers", "showery"),
    81: ("Moderate rain showers", "showery"),
    82: ("Violent rain showers", "stormy showers"),
    85: ("Slight snow showers", "snow showers"),
    86: ("Heavy snow showers", "snow showers"),
    95: ("Thunderstorm", "stormy"),
    96: ("Thunderstorm with slight hail", "stormy with hail"),
    99: ("Thunderstorm with heavy hail", "stormy with hail"),
}


@dataclass(frozen=True)
class WeatherReport:
    location: str
    observed_at: str
    temperature: float
    feels_like: float
    humidity: int
    precipitation: float
    wind_speed: float
    wind_gusts: float
    wind_direction: int
    cloud_cover: int
    weather_code: int

    @property
    def condition(self) -> str:
        return WEATHER_CODES.get(self.weather_code, ("Unknown conditions", "weather"))[0]

    @property
    def mood(self) -> str:
        return WEATHER_CODES.get(self.weather_code, ("Unknown conditions", "weather"))[1]


def fetch_weather() -> WeatherReport:
    params = {
        "latitude": TEL_AVIV_LATITUDE,
        "longitude": TEL_AVIV_LONGITUDE,
        "current": ",".join(
            [
                "temperature_2m",
                "relative_humidity_2m",
                "apparent_temperature",
                "precipitation",
                "weather_code",
                "cloud_cover",
                "wind_speed_10m",
                "wind_direction_10m",
                "wind_gusts_10m",
            ]
        ),
        "timezone": "Asia/Jerusalem",
        "forecast_days": 1,
    }
    url = f"{API_URL}?{urllib.parse.urlencode(params)}"

    try:
        with urllib.request.urlopen(url, timeout=12) as response:
            payload = json.loads(response.read().decode("utf-8"))
    except urllib.error.URLError as exc:
        raise RuntimeError(f"Could not reach Open-Meteo: {exc}") from exc
    except json.JSONDecodeError as exc:
        raise RuntimeError("Open-Meteo returned invalid JSON.") from exc

    current = payload.get("current")
    if not isinstance(current, dict):
        raise RuntimeError("Open-Meteo response did not include current weather data.")

    return WeatherReport(
        location="Tel Aviv, Israel",
        observed_at=str(current["time"]),
        temperature=float(current["temperature_2m"]),
        feels_like=float(current["apparent_temperature"]),
        humidity=int(current["relative_humidity_2m"]),
        precipitation=float(current["precipitation"]),
        wind_speed=float(current["wind_speed_10m"]),
        wind_gusts=float(current["wind_gusts_10m"]),
        wind_direction=int(current["wind_direction_10m"]),
        cloud_cover=int(current["cloud_cover"]),
        weather_code=int(current["weather_code"]),
    )


def format_observed_time(value: str) -> str:
    try:
        observed = datetime.fromisoformat(value)
    except ValueError:
        return value
    return observed.strftime("%A, %d %B %Y at %H:%M")


def color(text: str, code: str, enabled: bool) -> str:
    if not enabled:
        return text
    return f"\033[{code}m{text}\033[0m"


def render_report(report: WeatherReport, *, use_color: bool = True) -> str:
    title = f"Weather in {report.location}"
    subtitle = f"{report.condition} and {report.mood}"
    width = 56
    line = "-" * width

    rows = [
        ("Observed", format_observed_time(report.observed_at)),
        ("Temperature", f"{report.temperature:.1f} C"),
        ("Feels like", f"{report.feels_like:.1f} C"),
        ("Humidity", f"{report.humidity}%"),
        ("Cloud cover", f"{report.cloud_cover}%"),
        ("Precipitation", f"{report.precipitation:.1f} mm"),
        ("Wind", f"{report.wind_speed:.1f} km/h from {report.wind_direction} deg"),
        ("Gusts", f"{report.wind_gusts:.1f} km/h"),
    ]

    body = "\n".join(f"  {label:<14} {value}" for label, value in rows)
    banner = "\n".join(
        [
            color(f"+{line}+", "36", use_color),
            color(f"| {title:<54} |", "1;36", use_color),
            color(f"| {subtitle:<54} |", "36", use_color),
            color(f"+{line}+", "36", use_color),
            body,
            color(f"+{line}+", "36", use_color),
        ]
    )
    return banner


def parse_args(argv: list[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Display current weather for Tel Aviv in the terminal."
    )
    parser.add_argument(
        "--no-color",
        action="store_true",
        help="Disable ANSI color in the output.",
    )
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = parse_args(sys.argv[1:] if argv is None else argv)
    try:
        report = fetch_weather()
    except RuntimeError as exc:
        print(
            textwrap.fill(
                f"Weather lookup failed: {exc}",
                width=88,
            ),
            file=sys.stderr,
        )
        return 1

    print(render_report(report, use_color=not args.no_color))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
