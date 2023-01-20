import json
from typing import Any, Optional

import requests
from sqlalchemy import create_engine


_floor_map = {}

_repairtype_map = {}

def geocoder(address: str) -> Optional[int]:
    pass

def get_city_cent_meters(realty_id: int, date: str='max') -> int:
    pass

def get_price_sqm_model_diff_rate(features: dict[str, Any], date: str='max') -> int:
    pass
    