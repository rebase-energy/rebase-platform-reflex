"""
TimeDB API client for interacting with the TimeDB REST API.
API Documentation: https://rebase-energy--timedb-api-fastapi-app-dev.modal.run/docs
"""
import httpx
from typing import Optional, Dict, Any, List


class TimeDBAPI:
    """Client for TimeDB API."""
    
    BASE_URL = "https://rebase-energy--timedb-api-fastapi-app-dev.modal.run"
    
    def __init__(self, api_key: Optional[str] = None):
        """
        Initialize TimeDB API client.
        
        Args:
            api_key: Optional API key for authentication (X-API-Key header)
        """
        self.api_key = api_key
        self.headers = {}
        if api_key:
            self.headers["X-API-Key"] = api_key
    
    def create_series(
        self,
        series_key: str,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """
        Create a new time series.
        
        Args:
            series_key: Unique identifier for the time series (also used as 'name' in API)
            metadata: Optional metadata dictionary
            
        Returns:
            Response from the API
        """
        url = f"{self.BASE_URL}/series"
        payload = {
            "series_key": series_key,
            "name": series_key,  # API requires 'name' field, which is the same as series_key
        }
        if metadata:
            payload["metadata"] = metadata
        
        # Ensure Content-Type is set correctly
        headers = {**self.headers}
        if "Content-Type" not in headers:
            headers["Content-Type"] = "application/json"
        
        with httpx.Client() as client:
            response = client.post(url, json=payload, headers=headers, timeout=30.0)
            try:
                response.raise_for_status()
            except httpx.HTTPStatusError as e:
                # Include response body in error message for debugging
                error_detail = ""
                try:
                    error_json = response.json()
                    if isinstance(error_json, dict):
                        # FastAPI typically returns {"detail": [...]} for validation errors
                        detail = error_json.get("detail", error_json)
                        if isinstance(detail, list):
                            # Format list of validation errors
                            detail_str = "; ".join([
                                f"{err.get('loc', [])}: {err.get('msg', str(err))}" 
                                if isinstance(err, dict) else str(err)
                                for err in detail
                            ])
                            error_detail = detail_str
                        else:
                            error_detail = str(detail)
                    else:
                        error_detail = str(error_json)
                except:
                    error_detail = response.text or str(e)
                
                # Create a more informative error
                error_msg = f"{e.response.status_code} {e.response.reason_phrase}"
                if error_detail:
                    error_msg += f": {error_detail}"
                raise httpx.HTTPStatusError(
                    error_msg,
                    request=e.request,
                    response=e.response
                )
            return response.json()
    
    def list_timeseries(self) -> Dict[str, str]:
        """
        List all time series (series_id -> series_key mapping).
        
        Returns:
            Dictionary mapping series_id to series_key
        """
        url = f"{self.BASE_URL}/list_timeseries"
        
        with httpx.Client() as client:
            response = client.get(url, headers=self.headers, timeout=30.0)
            response.raise_for_status()
            return response.json()
    
    def read_values(
        self,
        series_id: Optional[str] = None,
        series_key: Optional[str] = None,
        start_time: Optional[str] = None,
        end_time: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Read time series values.
        
        Args:
            series_id: Time series ID
            series_key: Time series key (alternative to series_id)
            start_time: Start time filter (ISO format)
            end_time: End time filter (ISO format)
            
        Returns:
            Time series values
        """
        url = f"{self.BASE_URL}/values"
        params = {}
        if series_id:
            params["series_id"] = series_id
        if series_key:
            params["series_key"] = series_key
        if start_time:
            params["start_time"] = start_time
        if end_time:
            params["end_time"] = end_time
        
        with httpx.Client() as client:
            response = client.get(url, params=params, headers=self.headers, timeout=30.0)
            response.raise_for_status()
            return response.json()
    
    def upload_timeseries(
        self,
        series_id: Optional[str] = None,
        series_key: Optional[str] = None,
        values: Optional[List[Dict[str, Any]]] = None,
    ) -> Dict[str, Any]:
        """
        Upload time series data (create a new run with values).
        
        Args:
            series_id: Time series ID
            series_key: Time series key (alternative to series_id)
            values: List of value dictionaries with 'timestamp' and 'value' keys
            
        Returns:
            Response from the API
        """
        url = f"{self.BASE_URL}/upload"
        payload = {}
        if series_id:
            payload["series_id"] = series_id
        if series_key:
            payload["series_key"] = series_key
        if values:
            payload["values"] = values
        
        with httpx.Client() as client:
            response = client.post(url, json=payload, headers=self.headers, timeout=30.0)
            response.raise_for_status()
            return response.json()
    
    def update_records(
        self,
        series_id: Optional[str] = None,
        series_key: Optional[str] = None,
        values: Optional[List[Dict[str, Any]]] = None,
    ) -> Dict[str, Any]:
        """
        Update existing time series records.
        
        Args:
            series_id: Time series ID
            series_key: Time series key (alternative to series_id)
            values: List of value dictionaries with 'timestamp' and 'value' keys
            
        Returns:
            Response from the API
        """
        url = f"{self.BASE_URL}/values"
        payload = {}
        if series_id:
            payload["series_id"] = series_id
        if series_key:
            payload["series_key"] = series_key
        if values:
            payload["values"] = values
        
        with httpx.Client() as client:
            response = client.put(url, json=payload, headers=self.headers, timeout=30.0)
            response.raise_for_status()
            return response.json()

