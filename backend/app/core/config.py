from pydantic import BaseModel, Field


class Settings(BaseModel):
    app_name: str = Field(default="ChatWeb Backend")
    default_stream_format: str = Field(default="json")
    token_delay_seconds: float = Field(default=0.05)


settings = Settings()
