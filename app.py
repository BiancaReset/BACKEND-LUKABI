import os
import datetime
from flask import Flask, request, jsonify
from flask_migrate import Migrate
from flask_cors import CORS
from flask_jwt_extended import JWTManager, get_jwt_identity, create_access_token, jwt_required
from models import db, User, Foro
from werkzeug.security import generate_password_hash, check_password_hash
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)
app.config['DEBUG'] = True
app.config['ENV'] = 'development'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URL')
app.config['JWT_SECRET_KEY'] = os.getenv('JWT_SECRET_KEY')

db.init_app(app)
Migrate(app, db) # flask db init, flask db migrate, flask db upgrade
jwt = JWTManager(app)
CORS(app)

@app.route('/')
def main():
    return jsonify({"message": "API REST con JWT"})


@app.route('/api/register', methods=['POST'])
def register():
    
    correoelectronico= request.json["correoelectronico"]
    password = request.json["password"]
    nombre = request.json["nombre"]
    apellido = request.json["apellido"]
    direccion = request.json["direccion"]
    pais = request.json["pais"]
    region = request.json["region"]
    fechanac = request.json["fechanac"]
    
    # Validamos los datos ingresados
    if not correoelectronico:
        return jsonify({"fail": "correo electrónico es requerido!"}), 422
    
    if not password:
        return jsonify({"fail": "password es requerido!"}), 422

    if not nombre:
        return jsonify({"fail": "nombre es requerido"}), 422

    if not apellido:
        return jsonify({"fail": "apellido es requerido"}), 422

    if not direccion:
        return jsonify({""}), 

    if not pais:
        return jsonify({"fail": "pais es requerido"}), 422

    if not region:
        return jsonify({"fail": "region es requerida"}), 422

    if not fechanac:
        return jsonify({"fail": "fechanac es requerids"}), 422


    # Buscamos el usuario a ver si ya existe con ese username
    userFound = User.query.filter_by(correoelectronico=correoelectronico).first()
    
    if userFound:
        return jsonify({"fail": "correo electrónico ya está en uso!"}), 400
    
    # Aqui estamos creando al nuevo usuario
    user = User()
    user.correoelectronico = correoelectronico
    user.nombre = nombre
    user.apellido = apellido
    user.direccion = direccion
    user.pais = pais
    user.region = region
    user.fechanac = fechanac
    user.password = generate_password_hash(password) 
    user.save()
    
    return jsonify({ "success": "Registro exitoso, por favor inicie sesion!"}), 200

@app.route('/api/login', methods=['POST'])
def login():
    correoelectronico = request.json.get("correoelectronico")
    password = request.json.get("password")
    
    # Validamos los datos ingresados
    if not correoelectronico:
        return jsonify({"fail": "correoelectronico es requerido!"}), 422
    
    if not password:
        return jsonify({"fail": "password es requerido!"}), 422
    
    # buscamos al usuario 
    user = User.query.filter_by(correoelectronico=correoelectronico).first()
    
    # si no exite el usuario 
    if not user:
        return jsonify({ "fail": "correo electrónico o password son incorrectos!"}), 401
    
    if not check_password_hash(user.password, password):
        return jsonify({ "fail": "correo electrónico o password son incorrectos!"}), 401
    
    # expires = datetime.timedelta(days=5)
    # access_token = create_access_token(identity=user.id, expires_delta=expires)
    access_token = create_access_token(identity=user.id)
    
    data = {
        "success": "Inicio de sesion exitoso!",
        "access_token": access_token,
        "type": "Bearer",
        "user": user.serialize()
    }
    
    return jsonify(data), 200

@app.route('/api/profile', methods=['GET'])
@jwt_required()
def profile():
    id = get_jwt_identity()
    user = User.query.get(id)
    
    return jsonify({ "message": "Ruta privada", "user": user.correoelectronico }), 200

@app.route('/api/post_topic', methods=['POST'])
def create_post():    
    
        

    # Obtiene los datos del nuevo tema del cuerpo de la solicitud JSON
    data = request.json
    user_id = data.get('user_id')
    # Crea una instancia de la clase Foro con los datos proporcionados
    nuevo_post = Foro(
        titulo=data["titulo"],
        
        contenido=data["contenido"],
        user_id=user_id  # Asigna el ID del usuario al tema
    )

    # Guarda el nuevo tema en la base de datos
    try:
        nuevo_post.save()
        return jsonify({"message": "Tema creado exitosamente"}), 201
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/post_topic_all', methods=['GET'])
def get_all_posts():
    topics = Foro.query.all()
    result = list(map(lambda tema:tema.serialize(),topics))
    return jsonify(result)

if __name__ == '__main__':
    app.run()

