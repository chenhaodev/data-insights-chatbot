"""Settings configuration for Data Insights Chatbot."""

from pydantic_settings import BaseSettings
from pydantic import Field, ConfigDict
from dotenv import load_dotenv
from typing import Optional

# Load environment variables from .env file
load_dotenv()


class Settings(BaseSettings):
    """Application settings with environment variable support."""

    model_config = ConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore"
    )

    # DeepSeek API Configuration
    deepseek_api_key: str = Field(
        ...,
        description="DeepSeek API key"
    )

    deepseek_model: str = Field(
        default="deepseek-chat",
        description="Model name (deepseek-chat or deepseek-reasoner)"
    )

    deepseek_base_url: str = Field(
        default="https://api.deepseek.com/v1",
        description="DeepSeek API base URL (OpenAI-compatible)"
    )

    # Application Settings
    max_dataframe_rows: int = Field(
        default=10000,
        description="Maximum rows for analysis and visualization"
    )

    default_chart_height: int = Field(
        default=6,
        description="Default chart height in inches"
    )

    default_chart_width: int = Field(
        default=8,
        description="Default chart width in inches"
    )


def load_settings() -> Settings:
    """
    Load settings with proper error handling.

    Returns:
        Settings: Configured application settings

    Raises:
        ValueError: If required settings are missing
    """
    try:
        return Settings()
    except Exception as e:
        error_msg = f"Failed to load settings: {e}"
        if "deepseek_api_key" in str(e).lower():
            error_msg += "\n\nMake sure to set DEEPSEEK_API_KEY in your .env file"
            error_msg += "\nCopy .env.example to .env and add your API key"
        raise ValueError(error_msg) from e
