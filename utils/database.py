import os
from mongoengine import connect, get_connection
import logging

logger = logging.getLogger(__name__)


def initialize_database():
    """
    Initialize MongoDB connection.
    """
    try:
        # Check if connection already exists
        conn = get_connection()
        if conn:
            logger.debug("Database connection already initialized.")
            return
    except Exception:
        # No existing connection, proceed with new connection
        pass

    mongo_uri = os.getenv("MONGODB_URI")
    db_name = os.getenv("DATABASE_NAME")

    try:
        connect(
            db=db_name,
            host=mongo_uri,
            serverSelectionTimeoutMS=30000,
            retryWrites=True,
        )
        logger.info(f"Database connection established to {db_name}.")
    except Exception as e:
        logger.error(f"Failed to connect to database: {e}")
        raise
