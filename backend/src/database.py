from sqlmodel import SQLModel, create_engine
from prefect_sqlalchemy import SqlAlchemyConnector

from config import settings

DATABASE_URL = settings.DATABASE_URL

engine = create_engine(DATABASE_URL)


def create_db_and_tables():
    SQLModel.metadata.create_all(engine)


connector = SqlAlchemyConnector(connection_info=DATABASE_URL)

if __name__ == "__main__":
    connector.save("database-connector", overwrite=True)
