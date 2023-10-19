import sqlalchemy
from data.db_session import SqlAlchemyBase
from datetime import datetime


class Analysis(SqlAlchemyBase):
    __tablename__ = 'analyzes'
    id = sqlalchemy.Column(sqlalchemy.Integer,
                           primary_key=True,
                           autoincrement=True)
    name = sqlalchemy.Column(sqlalchemy.String)
    price = sqlalchemy.Column(sqlalchemy.Integer)
    created_date = sqlalchemy.Column(sqlalchemy.DateTime,
                                     default=datetime.now)

    def __repr__(self):
        return f'База {__class__.__name__} -> {self.name}'
