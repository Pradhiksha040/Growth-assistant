"""
Model and Provider configuration and inspection endpoints.
Enables switching between Ollama, Anthropic, OpenAI, and local offline engine without editing code.
"""
from fastapi import APIRouter, HTTPException, status

from backend.app.schemas.provider import ProvidersListResponse, ProviderConfigRequest
from backend.app.services.llm_provider import provider_manager

router = APIRouter(prefix="/providers", tags=["Providers"])

@router.get("", response_model=ProvidersListResponse)
async def list_providers():
    """Lists all available providers, connection statuses, active status, and models."""
    providers_info = await provider_manager.list_providers_status()
    active_key, active_p = await provider_manager.get_active_provider()
    
    active_model = getattr(active_p, "default_model", "lenny-grounded-engine-v1")
    
    return ProvidersListResponse(
        active_provider=active_key,
        active_model=active_model,
        providers=providers_info
    )

@router.post("/select")
async def select_provider(config: ProviderConfigRequest):
    """
    Selects the active LLM provider and optional target model.
    Verifies provider connectivity and returns actionable guidance if unavailable.
    """
    try:
        provider_manager.set_active_provider(config.provider, config.model)
        active_key, active_p = await provider_manager.get_active_provider()
        is_avail, msg, models = await active_p.check_availability()
        
        return {
            "status": "success",
            "active_provider": active_key,
            "active_model": getattr(active_p, "default_model", "default"),
            "is_available": is_avail,
            "message": msg,
            "available_models": models
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Failed to switch provider: {str(e)}"
        )
