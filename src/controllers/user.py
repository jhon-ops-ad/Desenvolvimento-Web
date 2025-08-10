from flask import Blueprint, request
from src.app import User, db
from http import HTTPStatus
from flask_jwt_extended import jwt_required, get_jwt_identity

app = Blueprint('user', __name__, url_prefix='/users')

def _create_user():
    data = request.json
    user = User(
        username=data["username"],
        password=data["password"],
        role_id=data["role_id"],
    )
    db.session.add(user)
    db.session.commit()


def _list_users():
    query = db.select(User)
    users = db.session.execute(query).scalars()
    return [
        {   "id": user.id, 
            "username": user.username,
            "role_id": {
                "id": user.role.id,
                "name": user.role.name,
            },
        } for user in users]


@app.route('/', methods=['GET', 'POST'])
@jwt_required()
def list_or_create_user():
    user_id = (get_jwt_identity())
    user = db.get_or_404(User, user_id)

    if user.role.name != 'admin':
        return {"message": "User dont have access."}, HTTPStatus.FORBIDDEN
    
    if request.method == "POST":
        _create_user()
        return {"message": "User created!"}, HTTPStatus.CREATED
    else:
        return {"users": _list_users()}
    

@app.route('/<int:user_id>')
def get_user(user_id):
    user = db.get_or_404(User, user_id)
    return {
        'id': user.id,
        'username': user.username,
    }

@app.route('/<int:user_id>', methods=['PATCH'])
def update_user(user_id):
    user = db.get_or_404(User, user_id)
    data = request.json

    if 'username' in data:
        user.username = data['username']
        db.session.commit()

    return {
        'id': user.id,
        'username': user.username,
    }

@app.route('/<int:user_id>', methods=['DELETE'])
def delete_user(user_id):
    user = db.get_or_404(User, user_id)
    db.session.delete(user)
    db.session.commit()
    return '', HTTPStatus.NO_CONTENT
