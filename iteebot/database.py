"""
ITEEBot database module. Currently the bot only uses one table for registering
courses. In the current implemenation the database is hardcoded for courses that
have names in two different languages.

SQLALchemy ORM is used to manage the database.
"""

from sqlalchemy import Column, Integer, String
from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base

Base = declarative_base()

class Course(Base):
    """
    Table for courses. Attributes:
    * code (str) - course code used in study guides etc.
    * name_fi (str) - course name in Finnish (optional)
    * name_en (str) - course name in English (optional)
    * message_id (int) - Discord message ID for the course's signup message
    * role_id (int) - ID for the Discord role that will be given to students    
    """

    __tablename__ = "course_table"
    
    id = Column(Integer, primary_key=True)
    code = Column(String, nullable=False)
    name_fi = Column(String, nullable=True)
    name_en = Column(String, nullable=True)
    message_id = Column(Integer, nullable=False)
    role_id = Column(Integer, nullable=False)

def get_engine(engine_str):
    """
    Utility function for getting the SQLALchemy engine.
    * engine_str (str) - SQLALchemy engine string
    """
    
    return create_engine(engine_str)
    
def init_db(engine_str):
    """
    Utility function for creating the database table(s).
    * engine_str (str) - SQLALchemy engine string
    """

    engine = get_engine(engine_str)
    Base.metadata.create_all(engine)
