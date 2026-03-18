from backend.database import engine, Base
from backend.models import Patient, RefundRequest
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def reset_db():
    try:
        logger.info("Dropping database tables...")
        Base.metadata.drop_all(bind=engine)
        logger.info("Creating database tables...")
        Base.metadata.create_all(bind=engine)
        logger.info("Tables recreated successfully.")
    except Exception as e:
        logger.error(f"Error recreating tables: {e}")

if __name__ == "__main__":
    reset_db()
