"""LLM provider configuration for DeepSeek API."""

from pydantic_ai.models.openai import OpenAIModel
from pydantic_ai.providers.openai import OpenAIProvider
from .settings import load_settings


def get_llm_model() -> OpenAIModel:
    """
    Get configured LLM model with DeepSeek API.

    Returns:
        OpenAIModel: Configured DeepSeek model compatible with Pydantic AI

    Raises:
        ValueError: If settings cannot be loaded
    """
    settings = load_settings()

    # Create OpenAI-compatible provider with DeepSeek base URL
    provider = OpenAIProvider(
        base_url=settings.deepseek_base_url,
        api_key=settings.deepseek_api_key
    )

    # Return OpenAI model with DeepSeek configuration
    return OpenAIModel(
        settings.deepseek_model,
        provider=provider
    )
