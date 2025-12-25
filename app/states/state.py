import reflex as rx
from typing import TypedDict, Literal
from .data import generate_time_series_data


class Site(TypedDict):
    name: str
    type: Literal["Wind", "Solar", "Load"]
    capacity: str
    status: str
    data: list[dict]
    tags: list[str]
    color: str


class DashboardState(rx.State):
    _sites: list[Site] = []
    search_query: str = ""
    show_add_site_modal: bool = False

    @rx.event
    def on_load(self):
        self._sites = [
            {
                "name": "Iceloss Wind",
                "type": "Wind",
                "capacity": "150000 kW",
                "status": "4/5",
                "data": generate_time_series_data("Wind", 150000),
                "tags": ["Iceloss"],
                "color": "#dbeafe",
            },
            {
                "name": "Demand Area",
                "type": "Load",
                "capacity": "",
                "status": "4/4",
                "data": generate_time_series_data("Load"),
                "tags": [],
                "color": "#dcfce7",
            },
            {
                "name": "Solar Site",
                "type": "Solar",
                "capacity": "1000 kW",
                "status": "6/6",
                "data": generate_time_series_data("Solar", 1000),
                "tags": [],
                "color": "#fef9c3",
            },
            {
                "name": "demand_se3",
                "type": "Load",
                "capacity": "",
                "status": "4/4",
                "data": generate_time_series_data("Load"),
                "tags": [],
                "color": "#dcfce7",
            },
        ]

    @rx.var
    def sites(self) -> list[Site]:
        if not self.search_query:
            return self._sites
        return [
            site
            for site in self._sites
            if self.search_query.lower() in site["name"].lower()
        ]

    @rx.event
    def toggle_add_site_modal(self):
        self.show_add_site_modal = not self.show_add_site_modal

    @rx.event
    def add_site(self, form_data: dict):
        site_type = form_data["site_type"]
        capacity = int(form_data.get("capacity") or 0)
        capacity_str = f"{capacity} kW" if capacity > 0 else ""
        new_site: Site = {
            "name": form_data["site_name"],
            "type": site_type,
            "capacity": capacity_str,
            "status": "0/0",
            "data": generate_time_series_data(
                site_type, capacity if capacity > 0 else None
            ),
            "tags": [],
            "color": "#e0e7ff",
        }
        self._sites.append(new_site)
        self.show_add_site_modal = False
        return rx.toast.success(f"Site '{new_site['name']}' created successfully!")

    @rx.event
    def download_all_sites_data(self) -> rx.event.EventSpec:
        import csv
        import io

        output = io.StringIO()
        writer = csv.writer(output)
        header = ["site_name", "time", "date", "capacity", "actual", "forecast"]
        writer.writerow(header)
        for site in self._sites:
            site_name = site["name"]
            for data_point in site["data"]:
                row = [
                    site_name,
                    data_point["time"],
                    data_point["date"],
                    data_point.get("capacity", ""),
                    data_point.get("actual", ""),
                    data_point.get("forecast", ""),
                ]
                writer.writerow(row)
        csv_data = output.getvalue()
        return rx.download(data=csv_data, filename="all_sites_data.csv")