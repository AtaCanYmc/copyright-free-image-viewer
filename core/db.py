import os
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker, scoped_session, declarative_base
from utils.env_constants import project_name
from utils.log_utils import logger

# Create database directory if it doesn't exist
DB_FOLDER = f"assets/{project_name}/database"
os.makedirs(DB_FOLDER, exist_ok=True)

DB_PATH = os.path.join(DB_FOLDER, f"{project_name}.db")
DATABASE_URL = f"sqlite:///{DB_PATH}"

engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = scoped_session(sessionmaker(autocommit=False, autoflush=False, bind=engine))

Base = declarative_base()

def init_db():
    Base.metadata.create_all(bind=engine)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def delete_db():
    if os.path.exists(DB_PATH):
        os.remove(DB_PATH)
        logger.info(f"Database deleted: {DB_PATH}")


def drop_all_tables():
    Base.metadata.drop_all(bind=engine)
    logger.info("All tables dropped")


def get_table_as_json(table_name: str) -> list[dict]:
    db = next(get_db())
    try:
        query = text(f"SELECT * FROM {table_name}")
        result = db.execute(query).mappings().all()
        return [dict(row) for row in result]
    except Exception as e:
        logger.error(f"Database error while fetching {table_name}: {e}")
        return []
    finally:
        db.close()
