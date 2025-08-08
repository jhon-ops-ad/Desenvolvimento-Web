from flask import Blueprint, request
from src.app import Role, db
from http import HTTPStatus


app = Blueprint('role', __name__, url_prefix='/roles')


@app.route('/', methods=['POST'])
def create_role():
    data = request.json
    role = Role(name=data['name'])
    db.session.add(role)
    db.session.commit()
    return {'message' : 'Role created!'}, HTTPStatus.CREATED


def __repr__(self) -> str:
    return f"Role(id={self.id!r}, name={self.name!r})"
