import os

class Settings:
    DB_USER: str = os.getenv("POSTGRES_USER", "openrvm_admin")
    DB_PASS: str = os.getenv("POSTGRES_PASSWORD", "rvm_local_prod_pass_99")
    DB_NAME: str = os.getenv("POSTGRES_DB", "openrvm_db")
    DB_HOST: str = os.getenv("DB_HOST", "postgres-db")
    REDIS_HOST: str = os.getenv("REDIS_HOST", "redis-cache")
    SIMULATOR_URL: str = os.getenv("SIMULATOR_URL", "http://vendor-simulator:8081")
    MERCHANT_NO: str = os.getenv("VENDOR_MERCHANT_NO", "MY_RVM_MERCHANT_001")
    VENDOR_SECRET: str = os.getenv("VENDOR_SECRET", "super_secret_autogcm_key_2026")

    @property
    def DATABASE_URL(self) -> str:
        return f"postgresql+psycopg2://{self.DB_USER}:{self.DB_PASS}@{self.DB_HOST}:5432/{self.DB_NAME}"

settings = Settings()
