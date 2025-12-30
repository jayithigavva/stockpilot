"""
Application configuration settings.
"""

from pydantic_settings import BaseSettings
from typing import Optional, Union
import json


class Settings(BaseSettings):
    """Application settings."""
    
    # Database
    DATABASE_URL: str = "postgresql://user:password@localhost/stockpilot"
    
    # Security
    SECRET_KEY: str = "your-secret-key-change-in-production"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 7  # 7 days
    
    # CORS - can be string (comma-separated) or list
    CORS_ORIGINS: Optional[Union[str, list]] = None
    
    def get_cors_origins(self) -> list:
        """Parse CORS origins from environment variable or use defaults."""
        if self.CORS_ORIGINS:
            # Support comma-separated string or JSON array string
            if isinstance(self.CORS_ORIGINS, str):
                if self.CORS_ORIGINS.startswith('['):
                    try:
                        return json.loads(self.CORS_ORIGINS)
                    except json.JSONDecodeError:
                        pass
                return [origin.strip() for origin in self.CORS_ORIGINS.split(',')]
            elif isinstance(self.CORS_ORIGINS, list):
                return self.CORS_ORIGINS
        return ["http://localhost:3000", "http://localhost:3001"]
    
    # Application
    APP_NAME: str = "StockPilot"
    DEBUG: bool = True
    
    class Config:
        env_file = ".env"
        case_sensitive = True


settings = Settings()

