import sqlalchemy
from data.db_session import SqlAlchemyBase
from datetime import datetime
from sqlalchemy import orm


class Analysis(SqlAlchemyBase):
    __tablename__ = 'analyzes'
    id = sqlalchemy.Column(sqlalchemy.Integer,
                           primary_key=True,
                           autoincrement=True)
    name = sqlalchemy.Column(sqlalchemy.String)
    price = sqlalchemy.Column(sqlalchemy.Integer)
    created_date = sqlalchemy.Column(sqlalchemy.DateTime,
                                     default=datetime.now)

    order = orm.relationship("Order", back_populates="analiz")

    def __repr__(self):
        return f'База {__class__.__name__} -> {self.name}'
