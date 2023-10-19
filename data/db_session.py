# создание БД и сессии по работе с ней
import sqlalchemy as sa
import sqlalchemy.orm as orm
from sqlalchemy.orm import Session

# объект, который будет декларировать работу c ORM моделями
SqlAlchemyBase = orm.declarative_base()

# создана ли сессия
created = None


# глобальная инициализация базы данных, которая будет следить за db_file
def global_init(db_file):
    global created
    # если сессия была создана, то выходим
    if created:
        return

    # проверяем есть ли подключение к базе данных
    if not db_file or not db_file.strip():
        raise Exception('Забыли подключить файл базы данных')

    # подключаем базу данных
    conn_str = f'sqlite:///{db_file.strip()}?check_same_thread=False'
    print(f'Мы подключились к {conn_str} успешно.')

    # создаем движок, который подключился к базе данных и готов с ней работать
    engine = sa.create_engine(conn_str, echo=False)
    # created отвечает за то, что привязали к нашему движку сессию

    created = orm.sessionmaker(bind=engine)

    # теперь можем импортировать все модели
    from . import all_models

    SqlAlchemyBase.metadata.create_all(engine)


def create_session() -> Session:
    global created
    return created()  # возвращаем как конструктор будущего объекта
    # T.е. создаётся объект, который будет управлять сессией с нашей базой данных
