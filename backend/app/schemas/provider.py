"""
Pydantic schemas for Provider configuration, inspection, and switching.
"""
from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field

class ProviderInfo(BaseModel):
    name: str = Field(..., description="Provider identifier ('ollama', 'anthropic', 'openai', 'offline')")
    display_name: str
    is_active: bool
    is_available: bool
    status_message: str
    active_model: str
    available_models: List[str] = []
    is_local: bool
    requires_key: bool
    has_key: bool

class ProviderConfigRequest(BaseModel):
    provider: str = Field(..., description="'ollama', 'anthropic', 'openai', or 'offline'")
    model: Optional[str] = None
    ollama_base_url: Optional[str] = None

class ProvidersListResponse(BaseModel):
    active_provider: str
    active_model: str
    providers: List[ProviderInfo]
