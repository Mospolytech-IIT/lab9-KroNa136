"""This module contains functions related to database operations."""

from sqlalchemy import create_engine, Column, Integer, String, Text, ForeignKey
from sqlalchemy.orm import DeclarativeBase, sessionmaker, Mapped, mapped_column, relationship

# Создание модели данных

# Опишите модель данных, состоящую из двух таблиц: Users и Posts.
# Таблица Users должна содержать следующие поля:
# id (целое число, первичный ключ, автоинкремент)
# username (строка, уникальное значение)
# email (строка, уникальное значение)
# password (строка)
# Таблица Posts должна содержать следующие поля:
# id (целое число, первичный ключ, автоинкремент)
# title (строка)
# content (текст)
# user_id (целое число, внешний ключ, ссылающийся на поле id таблицы Users)

# Создание таблиц

# Напишите программу на Python, которая подключается к выбранной базе данных и создает таблицы
#     Users и Posts на основе описанной модели данных.

engine = create_engine("postgresql+psycopg2://postgres:root@localhost/backend_lab9")

class Base(DeclarativeBase):
    """Base class for SQLAlchemy table classes."""

class User(Base):
    """Represents the 'users' table."""
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, autoincrement=True)
    username = Column(String, unique=True)
    email = Column(String, unique=True)
    password = Column(String)
    posts = relationship("Post", back_populates="user")

class Post(Base):
    """Represents the 'posts' table."""
    __tablename__ = "posts"

    id = Column(Integer, primary_key=True, autoincrement=True)
    title = Column(String)
    content = Column(Text)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"))
    user = relationship("User", back_populates="posts")

Base.metadata.create_all(bind=engine)

session = sessionmaker(bind=engine, autoflush=False)
db = session()

def rollback():
    """Does a rollback of the session. Intended for use after catching an SQLAlchemyError."""
    db.rollback()

# Добавление данных

# Напишите программу, которая добавляет в таблицу Users несколько записей с разными значениями
#     полей username, email и password.
# Напишите программу, которая добавляет в таблицу Posts несколько записей, связанных с
#     пользователями из таблицы Users.

def add_data():
    """Adds entries to the database."""
    users = [
        User(username="User 1", email="user1@example.com", password="1111"),
        User(username="User 2", email="user2@example.com", password="2222"),
        User(username="User 3", email="user3@example.com", password="3333"),
        User(username="User 4", email="user4@example.com", password="4444"),
        User(username="User 5", email="user5@example.com", password="5555"),
    ]

    db.add_all(users)
    db.commit()

    posts = [
        Post(title="Post 1", content="Content 1", user_id=2),
        Post(title="Post 2", content="Content 2", user_id=5),
        Post(title="Post 3", content="Content 3", user_id=1),
        Post(title="Post 4", content="Content 4", user_id=2)
    ]

    db.add_all(posts)
    db.commit()

# Извлечение данных

# Напишите программу, которая извлекает все записи из таблицы Users.
# Напишите программу, которая извлекает все записи из таблицы Posts, включая информацию о
#     пользователях, которые их создали.
# Напишите программу, которая извлекает записи из таблицы Posts, созданные конкретным пользователем.

def select_data():
    """Selects entries from the database."""
    all_users = db.query(User).all()

    for user in all_users:
        print(f"{user.id} | {user.username} | {user.email} | {user.password}")

    all_posts_including_authors = db.query(Post).join(User).all()

    for post in all_posts_including_authors:
        print(f"Пост: {post.id} | {post.title} | {post.content}\n\
    Автор: {post.user.id} | {post.user.username} | {post.user.email} | {post.user.password}")

    posts_by_user_2 = db.query(Post).filter(Post.user_id == 2).all()

    for post in posts_by_user_2:
        print(f"{post.id} | {post.title} | {post.content}")

# Обновление данных

# Напишите программу, которая обновляет поле email у одного из пользователей.
# Напишите программу, которая обновляет поле content у одного из постов.

def update_data():
    """Updates entries in the database."""
    user_5 = db.get(User, 5)
    user_5.email = "user5_email_test@example.com"
    db.commit()

    first_post_by_user_2 = db.query(Post).filter(Post.user_id == 2).first()
    first_post_by_user_2.content = "Some other content"
    db.commit()

# Удаление данных

# Напишите программу, которая удаляет один из постов.
# Напишите программу, которая удаляет пользователя и все его посты.

def delete_data():
    """Deletes entries from the database."""
    post_3 = db.get(Post, 3)
    db.delete(post_3)
    db.commit()

    user_id = 2
    posts_of_user = db.query(Post).filter(Post.user_id == user_id).all()

    for post in posts_of_user:
        db.delete(post)
        db.commit()

    user = db.get(User, user_id)
    db.delete(user)
    db.commit()

#add_data()
#select_data()
#update_data()
#delete_data()

def get_users():
    """Returns all users"""
    return db.query(User).all()

def get_user(user_id: int):
    """Returns a user with a given id"""
    return db.get(User, user_id)

def add_user(username: str, email: str, password: str):
    """Adds a new user"""
    user = User(username=username, email=email, password=password)
    db.add(user)
    db.commit()

def edit_user(user_id: int, username: str, email: str, password: str):
    """Edits a user with a given id"""
    user = db.get(User, user_id)

    if user is None:
        raise ValueError(f"There is no user with id={user_id}")

    user.username = username
    user.email = email
    user.password = password
    db.commit()

def delete_user(user_id: int, delete_posts_first = True):
    """Deletes a user with a given id"""
    user = db.get(User, user_id)

    if user is None:
        raise ValueError(f"There is no user with id={user_id}")

    if delete_posts_first:
        posts = db.query(Post).filter(Post.user_id == user.id).all()
        for post in posts:
            delete_post(post.id)

    user = db.get(User, user_id)
    db.delete(user)
    db.commit()

def get_posts():
    """Returns all posts"""
    return db.query(Post).all()

def get_post(post_id: int):
    """Returns a post with a given id"""
    return db.get(Post, post_id)

def add_post(title: str, content: str, user_id: int):
    """Adds a new post"""
    if user_id == -1:
        raise ValueError("A user must be selected.")

    if db.get(User, user_id) is None:
        raise ValueError(f"There is no user with id={user_id}")

    post = Post(title=title, content=content, user_id=user_id)
    db.add(post)
    db.commit()

def edit_post(post_id: int, title: str, content: str, user_id: int):
    """Edits a post with a given id"""
    post = db.get(Post, post_id)

    if post is None:
        raise ValueError(f"There is no post with id={user_id}")

    if user_id == -1:
        raise ValueError("A user must be selected.")

    if db.get(User, user_id) is None:
        raise ValueError(f"There is no user with id={user_id}")

    post.title = title
    post.content = content
    post.user_id = user_id
    db.commit()

def delete_post(post_id: int):
    """Deletes a post with a given id"""
    post = db.get(Post, post_id)

    if post is None:
        raise ValueError(f"There is no post with id={post_id}")

    db.delete(post)
    db.commit()
