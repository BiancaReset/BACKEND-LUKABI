import os
import datetime
from flask import Flask, request, jsonify
from flask_migrate import Migrate
from flask_cors import CORS
from flask_jwt_extended import JWTManager, get_jwt_identity, create_access_token, jwt_required
from models import db, User, Foro, Comentarios
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
    
    correo = request.json.get("correo")
    password = request.json.get("password")
    nombre = request.json.get("nombre")
    apellido = request.json.get("apellido")
    direccion = request.json.get("direccion")
    pais = request.json.get("pais")
    region = request.json.get("region")
    fechanac = request.json.get("fechanac")
    
    # Validamos los datos ingresados
    if not correo:
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
        return jsonify({"fail": "fechanac es requerida"}), 422


    # Buscamos el usuario a ver si ya existe con ese username
    userFound = User.query.filter_by(correo=correo).first()
    
    if userFound:
        return jsonify({"fail": "correo electrónico ya está en uso!"}), 400
    
    # Aqui estamos creando al nuevo usuario
    user = User()
    user.correo = correo
    user.password = generate_password_hash(password) 
    user.nombre = nombre
    user.apellido = apellido
    user.pais = pais
    user.region = region
    user.fechanac = fechanac 
    user.save()
    
    return jsonify({ "success": "Registro exitoso, por favor inicie sesion!"}), 200

@app.route('/api/login', methods=['POST'])
def login():
    correo = request.json.get("correo")
    password = request.json.get("password")
    
    # Validamos los datos ingresados
    if not correo:
        return jsonify({"fail": "correo electronico es requerido!"}), 422
    
    if not password:
        return jsonify({"fail": "password es requerido!"}), 422
    
    # buscamos al usuario 
    user = User.query.filter_by(correo=correo).first()
    
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

@app.route('/api/id', methods=['GET'])
@jwt_required()
def profile():
    id = get_jwt_identity()
    user = User.query.get(id)
    
    return jsonify({ "message": "Ruta privada", "user": user.correo }), 200

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
    print(topics[0].user.serialize())
    result = list(map(lambda tema:tema.serialize(),topics))
    return jsonify(result)

@app.route('/api/post_comment', methods=['POST'])
def post_comment():
    data = request.json
    # Obtener el user_id y foro_id del cuerpo de la solicitud
    user_id = data.get('user_id')
    foro_id = data.get('foro_id')
    # Verificar si se proporcionó un user_id válido
    if user_id is None:
        return jsonify({'message': 'El campo user_id es requerido'}), 400
    # Verificar si el usuario existe en la base de datos
    user = User.query.get(user_id)
    if user is None:
        return jsonify({'message': 'El usuario no existe'}), 404
    # Verificar si se proporcionó un proyecto_id válido
    if foro_id is None:
        return jsonify({'message': 'El campo foro_id es requerido'}), 400
    # Verificar si el proyecto existe en la base de datos
    foro = Foro.query.get(foro_id)

   
     # Crea una instancia de la clase Foro con los datos proporcionados
    post = Comentarios(
        comentario=data["comentario"],
        user_id=user_id,  # Asigna el ID del usuario al tema
        foro_id=foro_id, # Asigna el ID del foro 
    )

    # Guarda el nuevo tema en la base de datos
    try:
        post.save()
        return jsonify({"message": "Publicado exitosamente"}), 201
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route('/api/post_comments/<int:foro_id>', methods=['GET'])
def get_comments(foro_id):
    # Busca los comentarios relacionados con el tema (post) por su ID en la base de datos
    comentarios = Comentarios.query.filter_by(foro_id=foro_id).all()

    # Serializa la lista de comentarios y devuelve como JSON
    serialized_comments = [comentario.serialize() for comentario in comentarios]

    return jsonify(serialized_comments), 200


@app.route('/api/delete_comment/<int:id>', methods=['DELETE'])
def delete_comment(id):
    user_id = request.json.get('user_id')  # Obtener user_id de la solicitud
    # Verificar si se proporcionó un user_id válido en la solicitud
    if user_id is None:
        return jsonify({'message': 'El campo user_id es requerido'}), 400
    # Buscar el comentario en la base de datos por su ID
    comentario = Comentarios.query.get(id)
    # Verificar si el comentario existe
    if comentario is None:
        return jsonify({'message': 'El comentario no existe'}), 404
    # Verificar si el user_id de la solicitud coincide con el user_id del comentario
    if user_id != comentario.user_id:
        return jsonify({'message': 'No tienes permiso para eliminar este comentario'}), 403
    # Eliminar el comentario de la base de datos
    try:
        comentario.delete()
        return jsonify({'message': 'Comentario eliminado exitosamente'}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

from flask import request, jsonify
@app.route('/api/update_comment/<int:id>', methods=['PUT'])
def update_comment(id):
    user_id = request.json.get('user_id')  # Obtener user_id de la solicitud
    # Verificar si se proporcionó un user_id válido en la solicitud
    if user_id is None:
        return jsonify({'message': 'El campo user_id es requerido'}), 400
    # Buscar el comentario en la base de datos por su ID
    comentario = Comentarios.query.get(id)
    # Verificar si el comentario existe
    if comentario is None:
        return jsonify({'message': 'El comentario no existe'}), 404
    # Verificar si el user_id de la solicitud coincide con el user_id del comentario
    if user_id != comentario.user_id:
        return jsonify({'message': 'No tienes permiso para actualizar este comentario'}), 403
    # Actualizar el contenido del comentario con los datos de la solicitud
    try:
        comentario.comentario = request.json.get('comentario', comentario.comentario)
        comentario.save()  # Guardar los cambios en la base de datos
        return jsonify({'message': 'Comentario actualizado exitosamente'}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500








if __name__ == '__main__':
    app.run()

