import reflex as rx
import random
from datetime import datetime, timedelta


def generate_time_series_data(site_type: str, capacity_kw: float | None = None):
    data = []
    now = datetime.now()
    start_time = now - timedelta(days=1)
    end_time = now + timedelta(days=4)
    current_time = start_time
    while current_time <= end_time:
        time_str = current_time.strftime("%H:%M")
        date_str = current_time.strftime("%a %d/%m")
        point = {
            "time": time_str,
            "date": date_str,
            "capacity": None,
            "actual": None,
            "forecast": None,
        }
        if site_type == "Wind":
            if capacity_kw:
                point["capacity"] = capacity_kw
                actual_val = capacity_kw * (
                    0.6 + random.uniform(-0.2, 0.2) + current_time.hour % 12 / 24
                )
                forecast_val = actual_val * (1 + random.uniform(-0.1, 0.1))
                point["actual"] = max(0, actual_val)
                point["forecast"] = max(0, forecast_val)
        elif site_type == "Solar":
            if capacity_kw:
                point["capacity"] = capacity_kw
                if 6 <= current_time.hour <= 18:
                    solar_factor = (
                        1 - abs(current_time.hour - 12) / 6
                    ) * random.uniform(0.7, 1.0)
                    actual_val = capacity_kw * solar_factor
                    forecast_val = actual_val * (1 + random.uniform(-0.05, 0.05))
                    point["actual"] = max(0, actual_val)
                    point["forecast"] = max(0, forecast_val)
                else:
                    point["actual"] = 0
                    point["forecast"] = 0
        elif site_type == "Load":
            base_load = 2000
            peak_load = 2200
            load_factor = 1 + current_time.hour % 24 / 48 + random.uniform(-0.1, 0.1)
            if 8 <= current_time.hour <= 20:
                actual_val = peak_load * load_factor
            else:
                actual_val = base_load * load_factor
            forecast_val = actual_val * (1 + random.uniform(-0.05, 0.05))
            point["actual"] = max(1800, actual_val)
            point["forecast"] = max(1800, forecast_val)
        data.append(point)
        current_time += timedelta(hours=1)
    return data