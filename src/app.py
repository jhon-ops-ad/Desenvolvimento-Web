import os

import click
from flask import Flask, current_app
from datetime import datetime

from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import DeclarativeBase, relationship

from sqlalchemy import Integer, String
import sqlalchemy as sa
from sqlalchemy.orm import Mapped, mapped_column
from flask_migrate import Migrate
from flask_jwt_extended import JWTManager

class Base(DeclarativeBase):
  pass

db = SQLAlchemy(model_class=Base)
migrate = Migrate()
jwt = JWTManager()


class Role(db.Model):
    id: Mapped[int] = mapped_column(sa.Integer, primary_key=True)
    name: Mapped[str] = mapped_column(sa.String, nullable=False)
    users: Mapped[list["User"]] = relationship(back_populates='role')

class User(db.Model):
    id: Mapped[int] = mapped_column(sa.Integer, primary_key=True)
    username: Mapped[str] = mapped_column(sa.String, unique=True, nullable=False)
    password: Mapped[str] = mapped_column(sa.String, nullable=False)
    #active: Mapped[bool] = mapped_column(sa.Boolean, default=True)
    role_id: Mapped[int] = mapped_column(sa.ForeignKey("role.id"))
    role: Mapped['Role'] = relationship(back_populates='users')

    def __repr__(self) -> str:
        return f"User(id={self.id!r}, username={self.username!r})"


'''
def__repr__ : quando pedir para consultar os dados no banco de dados via ORM,
quando fizer um print no dado retornável, será exibido nessa formatação
'''



class Post(db.Model):
    id: Mapped[int] = mapped_column(sa.Integer, primary_key=True)
    title: Mapped[str] = mapped_column(sa.String, nullable=False)
    body: Mapped[str] = mapped_column(sa.String, nullable=False)
    created: Mapped[datetime] = mapped_column(sa.DateTime, server_default=sa.func.now())
    author_id: Mapped[int] = mapped_column(sa.ForeignKey('user.id'))

    def __repr__(self) -> str:
        return f"Post(id={self.id!r}, title={self.title!r}, author_id={self.author_id!r})"
 
@click.command('init-db')
def init_db_command():
    """Clear the existing data and create new tables."""
    global db # acessa a variável global db
    with current_app.app_context():
        db.create_all()
    click.echo('Initialized the database.')

def create_app(test_config=None):
    # create and configure the app
    app = Flask(__name__, instance_relative_config=True)
    app.config.from_mapping(
        SECRET_KEY='dev',
        SQLALCHEMY_DATABASE_URI='sqlite:///dio_bank.sqlite',
        JWT_SECRET_KEY = "super-secret",
    )

    if test_config is None:
        # load the instance config, if it exists, when not testing
        app.config.from_pyfile('config.py', silent=True)
    else:
        # load the test config if passed in
        app.config.from_mapping(test_config)
    
    try:
        os.makedirs(app.instance_path)
    except OSError:
        pass

    # register cli command
    app.cli.add_command(init_db_command)

    # inicialize estensions
    db.init_app(app)
    migrate.init_app(app, db)
    jwt.init_app(app)

    # register blueprints
    from src.controllers import user, auth, role

    
    app.register_blueprint(user.app)
    app.register_blueprint(auth.app)
    app.register_blueprint(role.app)
    return app

    