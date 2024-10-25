from models import ResponseModel
from typing import Any, Optional, Dict, List

def format_response(data: Any, links: Optional[List[Dict[str, str]]] = None) -> ResponseModel:
    return ResponseModel(data=data, links=links)