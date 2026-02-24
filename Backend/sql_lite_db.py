# database.py
from sqlalchemy import create_engine, Column, Integer, String, Float, ForeignKey, Date
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

# Use a local file instead of a Postgres URL
DATABASE_URL = "sqlite:///./finance.db"

engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
Base = declarative_base()


# Models remain exactly the same as before
class Customer(Base):
    __tablename__ = "customers"
    id = Column(Integer, primary_key=True)
    name = Column(String)
    email = Column(String)


class Card(Base):
    __tablename__ = "cards"
    id = Column(Integer, primary_key=True)
    customer_id = Column(Integer, ForeignKey("customers.id"))
    card_number = Column(String)
    card_type = Column(String)


class Expense(Base):
    __tablename__ = "expenses"
    id = Column(Integer, primary_key=True)
    card_id = Column(Integer, ForeignKey("cards.id"))
    amount = Column(Float)
    category = Column(String)
    date = Column(Date)


Base.metadata.create_all(engine)
