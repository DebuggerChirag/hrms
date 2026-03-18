from backend.database import engine, Base
from backend.models import Patient, RefundRequest
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def init_db():
    try:
        logger.info("Creating database tables...")
        Base.metadata.create_all(bind=engine)
        logger.info("Tables created successfully.")
    except Exception as e:
        logger.error(f"Error creating tables: {e}")
        # Note: In development with missing Postgres, it might fail if the DB doesn't exist
        logger.warning("Please ensure PostgreSQL is running and the database 'hrms' exists.")

if __name__ == "__main__":
    init_db()
