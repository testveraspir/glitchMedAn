import datetime
import sqlalchemy
from sqlalchemy import orm
from flask_login import UserMixin
from data.db_session import SqlAlchemyBase
from werkzeug.security import generate_password_hash, check_password_hash


class User(SqlAlchemyBase, UserMixin):
    __tablename__ = 'users'
    id = sqlalchemy.Column(sqlalchemy.Integer,
                           primary_key=True,
                           autoincrement=True)
    name = sqlalchemy.Column(sqlalchemy.String,
                             nullable=True)
    lastname = sqlalchemy.Column(sqlalchemy.String,
                                 nullable=True)
    birthday = sqlalchemy.Column(sqlalchemy.String,
                                 nullable=True)
    gender = sqlalchemy.Column(sqlalchemy.String,
                               nullable=True)
    level = sqlalchemy.Column(sqlalchemy.Integer,
                              default=1)
    email = sqlalchemy.Column(sqlalchemy.String,
                              index=True,
                              unique=True,
                              nullable=True)
    hashed_password = sqlalchemy.Column(sqlalchemy.String,
                                        nullable=True)
    created_date = sqlalchemy.Column(sqlalchemy.DateTime,
                                     default=datetime.datetime.now)

    order = orm.relationship("Order", back_populates="user")

    def __repr__(self):
        return f'База {__class__.__name__} -> {self.name}'

    # уровень прав пользователя
    # 1 (по умолчанию) - пользователь
    # 2 админ - полные права
    def is_admin(self):
        return self.level > 1  # у обычного пользователя 1, если больше 1 вернёт true

    def set_password(self, password):
        self.hashed_password = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.hashed_password, password)
