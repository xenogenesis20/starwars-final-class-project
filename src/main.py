"""
This module takes care of starting the API Server, Loading the DB and Adding the endpoints
"""
import os
from flask import Flask, request, jsonify, url_for
from flask_migrate import Migrate
from flask_swagger import swagger
from flask_cors import CORS
from utils import APIException, generate_sitemap
from admin import setup_admin
from models import db, User,Favorite
from flask_jwt_extended import create_access_token
from flask_jwt_extended import get_jwt_identity
from flask_jwt_extended import jwt_required
from flask_jwt_extended import JWTManager
import datetime
#from models import Person

app = Flask(__name__)
app.url_map.strict_slashes = False
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DB_CONNECTION_STRING')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
MIGRATE = Migrate(app, db)
db.init_app(app)
CORS(app)
setup_admin(app)
app.config["JWT_SECRET_KEY"] = "super-secret"  # Change this "super secret" with something else!
jwt = JWTManager(app)


# Handle/serialize errors like a JSON object
@app.errorhandler(APIException)
def handle_invalid_usage(error):
    return jsonify(error.to_dict()), error.status_code

# generate sitemap with all your endpoints
@app.route('/')
def sitemap():
    return generate_sitemap(app)

@app.route("/login", methods=["POST"])
def create_token():
    credentials = request.get_json()
    username = credentials.get("username", None)
    password = credentials.get("password", None)
    # Query your database for username and password
    user = User.query.filter_by(user_name=username, password=password).first()
    if user is None:
        # the user was not found on the database
        return jsonify({"msg": "Invalid username or password"}), 401
    
    # create a new token with the user id inside
    expires = datetime.timedelta(days=7)
    access_token = create_access_token(identity=user.user_name,expires_delta=expires)
    return jsonify({ "token": access_token, "user_id": user.user_name })    

@app.route('/user', methods=['GET'])
def handle_hello():
    all_users = User.query.all()
    all_users = list(map(lambda user: user.serialize(), all_users))
    response_body = {
        "users": all_users
    }

    return jsonify(response_body), 200

@app.route('/pizza', methods=['GET'])
# jwt_required on private endpoints
@jwt_required()
def jwt_test():
    current_user_id = get_jwt_identity()
    # user = User.query.get(current_user_id)
    
   
    return jsonify(user=current_user_id), 200

@app.route('/<user>/favorites', methods=['GET'])
def get_Favorites(user):
    single_user = User.query.filter_by(user_name=user).first()
    if single_user is None:
        raise APIException("User not found", status_code=404)
    favorites = Favorite.query.filter_by(user_name=user)
    all_favorites = list(map(lambda fav: fav.serialize(), favorites))
    response_body = {
        "all_favorites": all_favorites
    }

    return jsonify(response_body), 200

@app.route('/favorite/planet/<int:id>', methods=['POST','DELETE'])

def add_planet(id):
    request_body = request.get_json()
    if request_body is None or request_body =={}:
        raise APIException("Body cannot be empty", status_code=404)
    if request.method == 'POST':
        new_planet = Favorite(name=request_body["name"], entity_type="planet",entity_id=id,user_name=request_body["user_name"])
        db.session.add(new_planet)
        db.session.commit()
    if request.method == 'DELETE':
        deleted_planet = Favorite.query.filter_by(entity_type="planet",entity_id=id,user_name=request_body["user_name"]).first()
        if deleted_planet is None:
            raise APIException("Planet not found", status_code=404)
        db.session.delete(deleted_planet)
        db.session.commit()
    favorites = Favorite.query.filter_by(user_name=request_body["user_name"])
    all_favorites = list(map(lambda fav: fav.serialize(), favorites))
    response_body = {
        "all_favorites": all_favorites 
    }
    return jsonify(response_body), 200

@app.route('/favorite/person/<int:id>', methods=['POST','DELETE'])
def add_person(id):
    request_body = request.get_json()
    if request_body is None or request_body =={}:
        raise APIException("Body cannot be empty", status_code=404)
    if request.method == 'POST':
        person = Favorite.query.filter_by(user_name=request_body["user_name"],name = request_body["name"]).first()
        if person:
            raise APIException("Favorite already exists", status_code=418)
        new_person = Favorite(name=request_body["name"], entity_type="person",entity_id=id,user_name=request_body["user_name"])
        db.session.add(new_person)
        db.session.commit()
    if request.method == 'DELETE':
        deleted_person = Favorite.query.filter_by(entity_type="person",entity_id=id,user_name=request_body["user_name"]).first()
        if deleted_person is None:
            raise APIException("person not found", status_code=404)
        db.session.delete(deleted_person)
        db.session.commit()
    favorites = Favorite.query.filter_by(user_name=request_body["user_name"])
    all_favorites = list(map(lambda fav: fav.serialize(), favorites))
    response_body = {
        "all_favorites": all_favorites 
    }
    return jsonify(response_body), 200








# this only runs if `$ python src/main.py` is executed
if __name__ == '__main__':
    PORT = int(os.environ.get('PORT', 3000))
    app.run(host='0.0.0.0', port=PORT, debug=False)
