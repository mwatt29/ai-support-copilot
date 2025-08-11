# In apps/api/scripts/create_tables.py
import logging
from apps.api.db import Base, engine

# --- ADD THIS LINE ---
# This line imports your models and registers them with SQLAlchemy's Base
from apps.api import models

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def main():
    logger.info("Creating database tables...")
    try:
        Base.metadata.create_all(bind=engine)
        logger.info("Database tables created successfully! ✅")
    except Exception as e:
        logger.error(f"An error occurred while creating tables: {e}")

if __name__ == "__main__":
    main()