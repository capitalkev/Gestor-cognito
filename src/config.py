from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    aws_region: str = "us-east-1"
    cognito_user_pool_id: str
    cognito_app_client_id: str

    allowed_email_domains: str = "@capitalexpress.cl,@capitalexpress.pe"

    api_keys: str = "default_api_key"

    model_config = SettingsConfigDict(
        env_file=".env", env_file_encoding="utf-8", extra="ignore"
    )

    @property
    def parsed_api_keys(self) -> list[str]:
        return [key.strip() for key in self.api_keys.split(",") if key.strip()]

    @property
    def parsed_domains(self) -> list[str]:
        return [
            domain.strip()
            for domain in self.allowed_email_domains.split(",")
            if domain.strip()
        ]


settings = Settings()
