from sqlmodel import SQLModel, create_engine, Session
import utils

# Create DB Engine and Session
engine = create_engine(utils.get_database_url(), echo=False)
SessionLocal = Session(engine)


def create_db_and_tables():
    SQLModel.metadata.create_all(engine)


def main():
    create_db_and_tables()


# Dependency
def get_db_dependency():
    db = SessionLocal
    try:
        yield db
    finally:
        db.close()


# Dependency
def get_db():
    return SessionLocal


if __name__ == "__main__":
    main()
