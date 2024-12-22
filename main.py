"""A program for lab 9, demonstrating the usage of SQLAlchemy ORM."""

from typing import Annotated
from fastapi import FastAPI, Form, status
from fastapi.responses import HTMLResponse, RedirectResponse
from sqlalchemy.exc import SQLAlchemyError
import database

app = FastAPI()

@app.get("/")
def read_index():
    """Returns a page containing tables with info about users and posts."""
    html = """
<!DOCTYPE html>
<html>
    <head>
        <title>Main Page</title>
    </head>
    <body>
        <h2>Users</h2>
        <form method="get" action="/add-user"><button type="submit">Add</button></form>
        <table>
            <thead>
                <tr>
                    <th scope="col">ID</th>
                    <th scope="col">Username</th>
                    <th scope="col">Email</th>
                    <th scope="col">Password</th>
                    <th scope="col">Edit</th>
                    <th scope="col">Delete</th>
                </tr>
            </thead>
            <tbody>
                {0}
            </tbody>
        </table>
        <h2>Posts</h2>
        <form method="get" action="/add-post"><button type="submit">Add</button></form>
        <table>
            <thead>
                <tr>
                    <th scope="col">ID</th>
                    <th scope="col">Title</th>
                    <th scope="col">Content</th>
                    <th scope="col">User ID</th>
                    <th scope="col">Edit</th>
                    <th scope="col">Delete</th>
                </tr>
            </thead>
            <tbody>
                {1}
            </tbody>
        </table>
    </body>
</html>
"""

    user_item = """
<tr>
    <th scope="row">{0}</th>
    <td>{1}</td>
    <td>{2}</td>
    <td>{3}</td>
    <td><form method="get" action="/edit-user/{0}"><button type="submit">Edit</button></form></td>
    <td><form method="post" action="/delete-user/{0}"><button type="submit">Delete</button></form></td>
</tr>
"""

    post_item = """
<tr>
    <th scope="row">{0}</th>
    <td>{1}</td>
    <td>{2}</td>
    <td>{3}</td>
    <td><form method="get" action="/edit-post/{0}"><button type="submit">Edit</button></form></td>
    <td><form method="post" action="/delete-post/{0}"><button type="submit">Delete</button></form></td>
</tr>
"""

    try:
        users = database.get_users()
        posts = database.get_posts()

        user_items = ""
        for user in users:
            user_items += user_item.format(user.id, user.username, user.email, user.password) + "\n"

        post_items = ""
        for post in posts:
            post_items += post_item.format(post.id, post.title, post.content, post.user_id) + "\n"

        return HTMLResponse(content=html.format(user_items, post_items))
    except SQLAlchemyError as sqlalchemy_error:
        database.rollback()
        return RedirectResponse(f"/error?message={sqlalchemy_error}",
                                status_code=status.HTTP_302_FOUND)

@app.get("/add-user")
def read_add_user():
    """Returns a page for adding a new user."""
    html = """
<!DOCTYPE html>
<html>
    <head>
        <title>Add User Page</title>
    </head>
    <body>
        <h2>Add user</h2>
        <form method="post" action="/add-user">
            <div>
                <label for="username">Username:</label>
                <input name="username" id="username" type="text">
            </div>
            <div>
                <label for="email">Email:</label>
                <input name="email" id="email" type="email">
            <div>
                <label for="password">Password:</label>
                <input name="password" id="password" type="password">
            </div>
            <div>
                <button type="submit">Add</button>
            </div>
        </form>
    </body>
</html>
"""
    return HTMLResponse(content=html)

@app.post("/add-user")
def add_user(username: Annotated[str, Form()],
             email: Annotated[str, Form()],
             password: Annotated[str, Form()]):
    """Adds a new user."""
    try:
        database.add_user(username=username, email=email, password=password)
        return RedirectResponse("/", status_code=status.HTTP_302_FOUND)
    except SQLAlchemyError as sqlalchemy_error:
        database.rollback()
        return RedirectResponse(f"/error?message={sqlalchemy_error}",
                                status_code=status.HTTP_302_FOUND)

@app.get("/edit-user/{user_id}")
def read_edit_user(user_id: int):
    """Returns a page for editing a user with a given id."""
    user = database.get_user(user_id)
    if user is None:
        return RedirectResponse(f"/error?message={"User not found."}",
                                status_code=status.HTTP_302_FOUND)

    html = """
<!DOCTYPE html>
<html>
    <head>
        <title>Edit User Page</title>
    </head>
    <body>
        <h2>Edit user</h2>
        <form method="post" action="/edit-user/{0}">
            <div>
                <label for="username">Username:</label>
                <input name="username" id="username" type="text" value="{1}">
            </div>
            <div>
                <label for="email">Email:</label>
                <input name="email" id="email" type="email" value="{2}">
            <div>
                <label for="password">Password:</label>
                <input name="password" id="password" type="password" value="{3}">
            </div>
            <div>
                <button type="submit">Edit</button>
            </div>
        </form>
    </body>
</html>
"""
    return HTMLResponse(content=html.format(user.id, user.username, user.email, user.password))

@app.post("/edit-user/{user_id}")
def edit_user(user_id: int,
              username: Annotated[str, Form()],
              email: Annotated[str, Form()],
              password: Annotated[str, Form()]):
    """Edits a user with a given id."""
    try:
        database.edit_user(user_id=user_id, username=username, email=email, password=password)
        return RedirectResponse("/", status_code=status.HTTP_302_FOUND)
    except SQLAlchemyError as sqlalchemy_error:
        database.rollback()
        return RedirectResponse(f"/error?message={sqlalchemy_error}",
                                status_code=status.HTTP_302_FOUND)

@app.post("/delete-user/{user_id}")
def delete_user(user_id: int):
    """Deletes a user with a given id."""
    try:
        database.delete_user(user_id=user_id)
        return RedirectResponse("/", status_code=status.HTTP_302_FOUND)
    except SQLAlchemyError as sqlalchemy_error:
        database.rollback()
        return RedirectResponse(f"/error?message={sqlalchemy_error}",
                                status_code=status.HTTP_302_FOUND)
    except ValueError as value_error:
        return RedirectResponse(f"/error?message={value_error}",
                                status_code=status.HTTP_302_FOUND)

@app.get("/add-post")
def read_add_post():
    """Returns a page for adding a new post."""
    html = """
<!DOCTYPE html>
<html>
    <head>
        <title>Add Post Page</title>
    </head>
    <body>
        <h2>Add post</h2>
        <form method="post" action="/add-post">
            <div>
                <label for="title">Title:</label>
                <input name="title" id="title" type="text">
            </div>
            <div>
                <label for="content">Content:</label>
                <input name="content" id="content" type="text">
            <div>
                <label for="user_id">User:</label>
                <select name="user_id" id="user_id">
                    <option selected hidden value="-1">Choose a user...</option>
                    {0}
                </select>
            </div>
            <div>
                <button type="submit">Add</button>
            </div>
        </form>
    </body>
</html>
"""

    user_id_option_item = """<option value="{0}">{1}</option>"""

    try:
        users = database.get_users()

        user_id_option_items = ""
        for user in users:
            user_id_option_items += user_id_option_item.format(user.id, user.username) + "\n"

        return HTMLResponse(content=html.format(user_id_option_items))
    except SQLAlchemyError as sqlalchemy_error:
        database.rollback()
        return RedirectResponse(f"/error?message={sqlalchemy_error}",
                                status_code=status.HTTP_302_FOUND)

@app.post("/add-post")
def add_post(title: Annotated[str, Form()],
             content: Annotated[str, Form()],
             user_id: Annotated[int, Form()]):
    """Adds a new post."""
    try:
        database.add_post(title=title, content=content, user_id=user_id)
        return RedirectResponse("/", status_code=status.HTTP_302_FOUND)
    except SQLAlchemyError as sqlalchemy_error:
        database.rollback()
        return RedirectResponse(f"/error?message={sqlalchemy_error}",
                                status_code=status.HTTP_302_FOUND)
    except ValueError as value_error:
        return RedirectResponse(f"/error?message={value_error}",
                                status_code=status.HTTP_302_FOUND)

@app.get("/edit-post/{post_id}")
def read_edit_post(post_id: int):
    """Returns a page for editing a post with a given id."""
    post = database.get_post(post_id)
    if post is None:
        return RedirectResponse(f"/error?message={"Post not found."}",
                                status_code=status.HTTP_302_FOUND)

    html = """
<!DOCTYPE html>
<html>
    <head>
        <title>Edit Post Page</title>
    </head>
    <body>
        <h2>Edit post</h2>
        <form method="post" action="/edit-post/{0}">
            <div>
                <label for="title">Title:</label>
                <input name="title" id="title" type="text" value="{1}">
            </div>
            <div>
                <label for="content">Content:</label>
                <input name="content" id="content" type="text" value="{2}">
            <div>
                <label for="user_id">User:</label>
                <select name="user_id" id="user_id">
                    <option hidden value="-1">Choose a user...</option>
                    {3}
                </select>
            </div>
            <div>
                <button type="submit">Edit</button>
            </div>
        </form>
    </body>
</html>
"""

    user_id_option_item = """<option {0} value="{1}">{2}</option>"""

    try:
        users = database.get_users()

        user_id_option_items = ""
        for user in users:
            selected = "selected" if post.user_id == user.id else ""
            user_id_option_items += user_id_option_item.format(selected,
                                                               user.id,
                                                               user.username) + "\n"

        print(post.id, post.title, post.content, post.user_id)

        return HTMLResponse(content=html.format(post.id,
                                                post.title,
                                                post.content,
                                                user_id_option_items))
    except SQLAlchemyError as sqlalchemy_error:
        database.rollback()
        return RedirectResponse(f"/error?message={sqlalchemy_error}",
                                status_code=status.HTTP_302_FOUND)

@app.post("/edit-post/{post_id}")
def edit_post(post_id: int,
              title: Annotated[str, Form()],
              content: Annotated[str, Form()],
              user_id: Annotated[str, Form()]):
    """Edits a post with a given id."""
    try:
        database.edit_post(post_id=post_id, title=title, content=content, user_id=user_id)
        return RedirectResponse("/", status_code=status.HTTP_302_FOUND)
    except SQLAlchemyError as sqlalchemy_error:
        database.rollback()
        return RedirectResponse(f"/error?message={sqlalchemy_error}",
                                status_code=status.HTTP_302_FOUND)
    except ValueError as value_error:
        return RedirectResponse(f"/error?message={value_error}",
                                status_code=status.HTTP_302_FOUND)

@app.post("/delete-post/{post_id}")
def delete_post(post_id: int):
    """Deletes a post with a given id."""
    try:
        database.delete_post(post_id=post_id)
        return RedirectResponse("/", status_code=status.HTTP_302_FOUND)
    except SQLAlchemyError as sqlalchemy_error:
        database.rollback()
        return RedirectResponse(f"/error?message={sqlalchemy_error}",
                                status_code=status.HTTP_302_FOUND)
    except ValueError as value_error:
        return RedirectResponse(f"/error?message={value_error}",
                                status_code=status.HTTP_302_FOUND)

@app.get("/error")
def read_error(message: str):
    """Displays an error message."""
    html = """
<!DOCTYPE html>
<html>
    <head>
        <title>Error Page</title>
    </head>
    <body>
        <h2>Error</h2>
        <p>{0}</p>
        <form method="get" action="/"><button type="submit">To main page</button></form>
    </body>
</html>
"""
    return HTMLResponse(content=html.format(message))
