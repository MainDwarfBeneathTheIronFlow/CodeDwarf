

class Settings:
    PROJECT_NAME: str = "Job Board"
    PROJECT_VERSION: str = "1.0.0"
    SECRET_KEY = "483235a3e50662ca32026396f418b332bd50278271f390a4ecd5473f1dcd9a55"
    ALGORITHM = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES = 30  # in mins


settings = Settings()