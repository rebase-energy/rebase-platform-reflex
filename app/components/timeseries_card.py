import reflex as rx
from reflex_echarts import echarts
from typing import TypedDict, Literal
from datetime import datetime, timedelta


# Time series data point structure
class TimeSeriesDataPoint(TypedDict):
    time: str
    capacity: float
    actual: float
    forecast: float
    iceaware: float | None
    iceblind: float | None
    iceloss: float | None


# Time series card data structure
class TimeSeriesCardData(TypedDict):
    id: str
    name: str
    capacity_mw: float
    data: list[TimeSeriesDataPoint]
    view_tabs: list[str]  # ["Default view", "Iceloss", "Iceloss pct", "Iceloss weather"]


def _generate_dummy_data(capacity_mw: float) -> dict:
    """Generate dummy time series data for the chart."""
    import random
    from datetime import datetime, timedelta
    
    data_points = []
    now = datetime.now()
    start_time = now - timedelta(days=1)
    end_time = now + timedelta(days=4)
    current_time = start_time
    
    while current_time <= end_time:
        hour = current_time.hour
        base = capacity_mw * 0.6
        variation = capacity_mw * 0.3 * (0.5 + (hour % 12) / 12)
        actual = base + variation + (capacity_mw * 0.1 * random.uniform(-1, 1))
        forecast = actual * (1 + random.uniform(-0.1, 0.1))
        
        data_points.append({
            "time": current_time.strftime("%a %d/%m %H:%M"),
            "capacity": capacity_mw,
            "actual": max(0, min(capacity_mw, actual)),
            "forecast": max(0, min(capacity_mw, forecast)),
        })
        current_time += timedelta(hours=1)
    
    # Format times for x-axis: show date only, with time only for 00:00 and 12:00
    # Also store full times for tooltip
    times = []
    full_times = []  # Store full time strings for tooltip
    for point in data_points:
        time_str = point["time"]  # Full format: "Mon 01/01 03:12"
        full_times.append(time_str)
        
        parts = time_str.split(' ')
        if len(parts) >= 3:
            date_part = parts[0] + ' ' + parts[1]  # "Mon 01/01"
            time_part = parts[2]  # "03:12"
            hour, minute = map(int, time_part.split(':'))
            
            # Only show time for 00:00 and 12:00
            if (hour == 0 and minute == 0) or (hour == 12 and minute == 0):
                times.append(date_part + ' ' + time_part)
            else:
                times.append(date_part)
        else:
            times.append(time_str)
    
    actual_data = [point["actual"] for point in data_points]
    forecast_data = [point["forecast"] for point in data_points]
    
    # Reference line at 24 hours (1 day)
    reference_line_index = 24 if len(times) > 24 else len(times) - 1
    
    return {
        "times": times,
        "full_times": full_times,  # Full time strings for tooltip
        "actual": actual_data,
        "forecast": forecast_data,
        "reference_index": reference_line_index,
    }


def _build_chart_option(chart_data: dict) -> dict:
    """Build ECharts option with all series."""
    return {
        "backgroundColor": "rgb(23,23,25)",
        "grid": {
            "left": "0%",
            "right": "5%",
            "top": "50px",
            "bottom": "20px",
            "containLabel": False,
            "backgroundColor": "rgb(23,23,25)",
        },
        "xAxis": {
            "type": "category",
            "data": chart_data["times"],
            "axisLine": {"show": False},
            "axisTick": {"show": False},
            "axisLabel": {
                "color": "#9ca3af",
                "fontSize": 10,
                "margin": 8,
                "rotate": 0,
                "interval": "auto",  # Auto-hide overlapping labels
                "showMinLabel": True,
                "showMaxLabel": True,
            },
            "splitLine": {
                "show": True,
                "lineStyle": {
                    "color": "#374151",
                    "type": "solid",
                    "opacity": 0.3,  # Make vertical lines more subtle
                },
            },
            "boundaryGap": False,
        },
        "yAxis": {
            "type": "value",
            "axisLine": {"show": False},
            "axisTick": {"show": False},
            "axisLabel": {
                "color": "#9ca3af",
                "fontSize": 10,
                "margin": 8,
                "show": True,
            },
            "splitLine": {
                "show": True,
                "lineStyle": {
                    "color": "#374151",
                    "type": "solid",
                },
            },
            "show": True,  # Will be controlled by series visibility
        },
        "tooltip": {
            "trigger": "axis",
            "backgroundColor": "rgb(23,23,25)",
            "borderColor": "#374151",
            "borderWidth": 1,
            "textStyle": {
                "color": "#e5e7eb",
            },
            "axisPointer": {
                "type": "line",
            },
        },
        "legend": {
            "show": True,
            "top": "10px",
            "right": "20px",
            "orient": "horizontal",
            "itemGap": 16,
            "textStyle": {
                    "color": "#9ca3af",
                "fontSize": 10,
            },
            "selectedMode": True,  # Enable clicking to toggle series
            "data": [
                {
                    "name": "Actual",
                    "icon": "circle",
                    "itemStyle": {"color": "#f97316"},
                },
                {
                    "name": "Forecast",
                    "icon": "circle",
                    "itemStyle": {"color": "#22c55e"},
                },
            ],
            "itemWidth": 10,
            "itemHeight": 10,
            },
        "animation": False,
        "series": [
            {
                "name": "Actual",
                "type": "line",
                "data": chart_data["actual"],
                "lineStyle": {"color": "#f97316", "width": 2},
                "symbol": "none",
                "smooth": True,
            },
            {
                "name": "Forecast",
                "type": "line",
                "data": chart_data["forecast"],
                "lineStyle": {"color": "#22c55e", "width": 2},
                "symbol": "none",
                "smooth": True,
            },
            {
                # Hidden series for the red "now" line - always visible, not in legend
                "name": "_nowLine",
                "type": "line",
                "data": [],  # No data points
                "markLine": {
                    "silent": True,
                    "symbol": "none",
                    "label": {"show": False},
                    "animation": False,
                    "lineStyle": {"color": "#dc2626", "width": 1, "type": "dashed"},
                    "data": [{"xAxis": chart_data["reference_index"]}],
                },
                "legendHoverLink": False,
            },
        ],
    }


def timeseries_card(card_data: TimeSeriesCardData) -> rx.Component:
    """A time series card component matching the Rebase Platform design using ECharts."""
    # For now, use dummy data since we can't iterate over reactive Vars
    # In the future, this will be replaced with actual API data
    # We'll generate dummy data for each card based on a default capacity
    # The actual capacity from card_data will be displayed in the header
    chart_data = _generate_dummy_data(90.2)  # Default dummy data
    
    # Build chart option with ECharts built-in legend
    option = _build_chart_option(chart_data)
    
    # Prepare data for JavaScript tooltip formatting
    import json
    full_times_json = json.dumps(chart_data["full_times"])
    
    # Set up tooltip formatter using ECharts instance
    # We'll inject this via JavaScript after chart creation
    
    return rx.el.div(
        # Card header with title
            rx.el.div(
                rx.el.h3(
                    card_data["name"],
                    class_name="text-white font-bold text-lg",
            ),
            class_name="p-4 border-b border-gray-700",
        ),
        # Chart area with built-in legend
        rx.el.div(
            rx.el.div(
            echarts(
                option=option,
                style={"height": "250px", "width": "100%"},
                    id=f"chart-{card_data['id']}",
                ),
                rx.el.script(
                    f"""
                    (function() {{
                        const fullTimes = {full_times_json};
                        const chartId = 'chart-{card_data['id']}';
                        
                        function setupTooltipFormatter() {{
                            const chartContainer = document.getElementById(chartId);
                            if (!chartContainer) return false;
                            
                            // Get ECharts instance
                            if (typeof echarts === 'undefined') return false;
                            
                            const chartInstance = echarts.getInstanceByDom(chartContainer);
                            if (!chartInstance) return false;
                            
                            // Set tooltip formatter directly
                            chartInstance.setOption({{
                                tooltip: {{
                                    formatter: function(params) {{
                                        if (!params || params.length === 0) return '';
                                        const param = params[0];
                                        let result = '';
                                        
                                        // Get the data index
                                        const dataIndex = param.dataIndex;
                                        let dateStr = param.axisValue || '';
                                        
                                        // Add timestamp if available
                                        if (dataIndex >= 0 && fullTimes && fullTimes[dataIndex]) {{
                                            const fullTime = fullTimes[dataIndex];
                                            const timeParts = fullTime.split(' ');
                                            if (timeParts.length >= 3) {{
                                                const timestamp = timeParts[2];
                                                // Check if timestamp is already in dateStr
                                                if (dateStr.indexOf(timestamp) === -1) {{
                                                    dateStr = dateStr + ' ' + timestamp;
                                                }}
                                            }}
                                        }}
                                        
                                        result = dateStr + '<br/>';
                                        
                                        // Format each series value to exactly 2 decimal places
                                        params.forEach(function(item) {{
                                            if (item.seriesName !== 'now') {{
                                                const numValue = typeof item.value === 'number' ? item.value : parseFloat(item.value);
                                                const value = isNaN(numValue) ? item.value : numValue.toFixed(2);
                                                result += '<span style="display:inline-block;margin-right:5px;width:10px;height:10px;border-radius:50%;background-color:' + item.color + ';"></span>';
                                                result += item.seriesName + ': <span style="float:right;margin-left:20px;text-align:right;min-width:50px;">' + value + '</span><br/>';
                                            }}
                                        }});
                                        
                                        return result;
                                    }}
                                }}
                            }}, false);
                            
                            return true;
                        }}
                        
                        // Try multiple times to set up formatter
                        let attempts = 0;
                        const maxAttempts = 10;
                        const interval = setInterval(function() {{
                            if (setupTooltipFormatter() || attempts >= maxAttempts) {{
                                clearInterval(interval);
                            }}
                            attempts++;
                        }}, 100);
                        
                        // Also try immediately
                        setTimeout(setupTooltipFormatter, 50);
                    }})();
                    """
                ),
                class_name="mx-4 rounded-lg overflow-hidden",
                style={"backgroundColor": "rgb(23,23,25)"},
            ),
            class_name="pb-4 pt-2",
        ),
        class_name="rounded-lg border border-gray-700",
        style={"backgroundColor": "rgb(23,23,25)"},
    )

