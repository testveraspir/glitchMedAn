import sqlalchemy
from datetime import datetime
from sqlalchemy import orm
from flask_login import UserMixin
from data.db_session import SqlAlchemyBase


class Order(SqlAlchemyBase, UserMixin):
    __tablename__ = 'orders'
    id = sqlalchemy.Column(sqlalchemy.Integer,
                           primary_key=True,
                           autoincrement=True)
    num_order = sqlalchemy.Column(sqlalchemy.String)
    name = sqlalchemy.Column(sqlalchemy.String)
    price = sqlalchemy.Column(sqlalchemy.Integer)
    created_date = sqlalchemy.Column(sqlalchemy.DateTime,
                                     default=datetime.now)
    user_id = sqlalchemy.Column(sqlalchemy.Integer,
                                sqlalchemy.ForeignKey("users.id"),
                                nullable=False)
    user = orm.relationship("User")

    def __repr__(self):
        return f'База {__class__.__name__} -> {self.name}'
