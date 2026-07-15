"""Application handlers that keep Streamlit independent from services."""

from __future__ import annotations

from services.address_service import AddressService
from services.polish_service import PolishService
from services.roc_date_service import RocDateService

roc_date_service = RocDateService()
address_service = AddressService()
polish_service = PolishService()
