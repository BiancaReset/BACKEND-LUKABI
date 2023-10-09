import os
import datetime
from flask import Flask, request, jsonify


# Resto de tu código que utiliza 'cryptography'

from flask_migrate import Migrate
from flask_cors import CORS
from flask_jwt_extended import JWTManager, get_jwt_identity, create_access_token, jwt_required
from datetime import timedelta
from models import db, User, Foro, Informacion, Comentarios, Comercio, ComentariosProducto
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
    direccion2 = request.json.get("direccion2")
    pais = request.json.get("pais")
    region = request.json.get("region")
    fechanac = request.json.get("fechanac")
    role = request.json.get("role")
    
    # Validamos los datos ingresados
    if not correo:
        return jsonify({"fail": "correo electrónico es requerido!"}), 422
    
    if not password:
        return jsonify({"fail": "password es requerido!"}), 422

    if not nombre:
        return jsonify({"fail": "nombre es requerido"}), 422

    if not apellido:
        return jsonify({"fail": "apellido es requerido"}), 422

    if not pais:
        return jsonify({"fail": "pais es requerido"}), 422

    if not region:
        return jsonify({"fail": "region es requerida"}), 422

    if not fechanac:
        return jsonify({"fail": "fechanac es requerida"}), 422
    
    if not role:
        return jsonify({"fail": "role es requerida"}), 422


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
    user.role = role 
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
    access_token = create_access_token(identity=user.id, expires_delta=timedelta(days=365))
    
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

@app.route('/api/users', methods=['GET'])
@jwt_required()
def get_all_users():
    current_user_id = get_jwt_identity()
    # Asegúrate de que el usuario actual tiene permiso para acceder a esta ruta,
    # si es necesario.
    # Puedes verificar permisos o roles aquí antes de continuar.

    # Luego, obtén todos los usuarios de la base de datos.
    users = User.query.all()

    # Convierte los usuarios en una lista de diccionarios.
    user_list = [{"id": user.id, "correo": user.correo, "nombre": user.nombre, "apellido": user.apellido, "role": user.role} for user in users]

    return jsonify({"message": "Lista de usuarios", "users": user_list}), 200


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
    # print(topics[0].user.serialize())
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

@app.route('/api/update_foro/<int:id>', methods=['PUT'])
def update_foro(id):
    user_id = request.json.get('user_id')  # Obtener user_id de la solicitud
    
    # Verificar si se proporcionó un user_id válido en la solicitud
    if user_id is None:
        return jsonify({'message': 'El campo user_id es requerido'}), 400
    # Buscar el comentario en la base de datos por su ID
    update = Foro.query.get(id)
    # Verificar si el comentario existe
    if update is None:
        return jsonify({'message': 'El producto no existe'}), 404
   
    try:
        update.activo = request.json.get('activo', update.activo)
        update.comentario_rep = request.json.get('comentario_rep', update.comentario_rep)
        update.save()  # Guardar los cambios en la base de datos
        return jsonify({'message': 'Articulo actualizado exitosamente'}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/post_comments/<int:foro_id>', methods=['GET'])
def get_comments(foro_id):
    # Busca los comentarios relacionados con el tema (post) por su ID en la base de datos
    comentarios = Comentarios.query.filter_by(foro_id=foro_id).all()

    # Serializa la lista de comentarios y devuelve como JSON
    serialized_comments = [comentario.serialize() for comentario in comentarios]

    return jsonify(serialized_comments), 200

@app.route('/informacion', methods=['GET'])
def obtener_informacion():
    informacion = Informacion.query.all()
    informacion_serializada = [item.serialize() for item in informacion]
    return jsonify(informacion_serializada), 200

@app.route('/api/informacion/user/<int:user_id>', methods=['GET'])
def obtener_informacion_por_user_id(user_id):
    # Buscar el registro en la base de datos por user_id
    informacion = Informacion.query.filter_by(user_id=user_id).first()

    # Verificar si el registro existe
    if not informacion:
        return jsonify({'error': 'Registro no encontrado para el user_id proporcionado'}), 404

    # Convertir el registro a un diccionario para la respuesta JSON
# Convertir el registro a un diccionario para la respuesta JSON
    informacion_dict = {
        'id': informacion.id,
        'user_id': informacion.user_id,
        'nombre': informacion.nombre,
        'direccion': informacion.direccion,
        'descripcion': informacion.descripcion
    }

    return jsonify(informacion_dict)

@app.route('/api/post_producto', methods=['POST'])
def post_producto():
    data = request.json
    # Obtener el user_id y foro_id del cuerpo de la solicitud
    user_id = data.get('user_id')
    nombre = data.get('nombre')
    direccion = data.get('direccion')
    descripcion = data.get('descripcion')
    # Verificar si se proporcionó un user_id válido
    if user_id is None:
        return jsonify({'message': 'El campo user_id es requerido'}), 400
    # Verificar si el usuario existe en la base de datos
    user = User.query.get(user_id)
    if user is None:
        return jsonify({'message': 'El usuario no existe'}), 404
    # Verificar si se proporcionó un proyecto_id válido
    
 

   
     # Crea una instancia de la clase Foro con los datos proporcionados
    post = Informacion(
        user_id=user_id,  # Asigna el ID del usuario al tema
        nombre=nombre, 
        direccion=direccion,
        descripcion=descripcion, # Asigna el ID del foro 
    )

    # Guarda el nuevo tema en la base de datos
    try:
        post.save()
        return jsonify({"message": "Publicado exitosamente"}), 201
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/update_producto/<int:id>', methods=['PUT'])
def update_producto(id):
    user_id = request.json.get('user_id')  # Obtener user_id de la solicitud
    nombre = request.json.get('nombre')  # Obtener user_id de la solicitud
    direccion = request.json.get('direccion')  # Obtener user_id de la solicitud
    descripcion = request.json.get('descripcion')  # Obtener user_id de la solicitud
    activo = request.json.get('activo')  # Obtener user_id de la solicitud
    comentario_rep = request.json.get('comentario_rep')  # Obtener user_id de la solicitud
    # Verificar si se proporcionó un user_id válido en la solicitud
    if user_id is None:
        return jsonify({'message': 'El campo user_id es requerido'}), 400
    # Buscar el comentario en la base de datos por su ID
    informacion = Informacion.query.get(id)
    # Verificar si el comentario existe
    if informacion is None:
        return jsonify({'message': 'El producto no existe'}), 404
    # Verificar si el user_id de la solicitud coincide con el user_id del comentario
  
    # Actualizar el contenido del comentario con los datos de la solicitud
    try:
        informacion.id = request.json.get('id', informacion.id)
        informacion.nombre = request.json.get('nombre', informacion.nombre)
        informacion.direccion = request.json.get('direccion', informacion.direccion)
        informacion.descripcion = request.json.get('descripcion', informacion.descripcion)
        informacion.activo = request.json.get('activo', informacion.activo)
        informacion.comentario_rep = request.json.get('comentario_rep', informacion.comentario_rep)
        informacion.save()  # Guardar los cambios en la base de datos
        return jsonify({'message': 'Articulo actualizado exitosamente'}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500
    
@app.route('/api/delete_producto/<int:id>', methods=['DELETE'])
def delete_producto(id):
    user_id = request.json.get('user_id')  # Obtener user_id de la solicitud
    # Verificar si se proporcionó un user_id válido en la solicitud
    if user_id is None:
        return jsonify({'message': 'El campo user_id es requerido'}), 400
    # Buscar el comentario en la base de datos por su ID
    informacion = Informacion.query.get(id)
    # Verificar si el comentario existe
    if informacion is None:
        return jsonify({'message': 'El informacion no existe'}), 404
    # Verificar si el user_id de la solicitud coincide con el user_id del informacion
    if user_id != informacion.user_id:
        return jsonify({'message': 'No tienes permiso para eliminar este informacion'}), 403
    # Eliminar el informacion de la base de datos
    try:
        db.session.delete(informacion)
        db.session.commit()

        return jsonify({'message': 'informacion eliminado exitosamente'}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500


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

    # Eliminar el comentario de la base de datos
    try:
        comentario.delete()
        return jsonify({'message': 'Comentario eliminado exitosamente'}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

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
    # Actualizar el contenido del comentario con los datos de la solicitud
    try:
        comentario.comentario = request.json.get('comentario', comentario.comentario)
        comentario.comentario_rep = request.json.get('comentario_rep', comentario.comentario_rep)
        comentario.activo = request.json.get('activo', comentario.activo)
        comentario.save()  # Guardar los cambios en la base de datos
        return jsonify({'message': 'Comentario actualizado exitosamente'}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/comercios', methods=['GET'])
def obtener_comercios():
    comercios = Comercio.query.all()

    lista_comercios = []
    for comercio in comercios:
        comercio_dict = {
            "nombre": comercio.nombre,
            "correo": comercio.correo,
            "direccion": comercio.direccion,
            "direccion2" : comercio.direccion2, 
            "pais": comercio.pais,
            "region": comercio.region,
            "website": comercio.website,
            "descripcion": comercio.descripcion
        }
        lista_comercios.append(comercio_dict)

    return jsonify(lista_comercios)


@app.route('/api/comercio', methods=['POST'])
def registrar_comercio():
    nombre = request.json.get("nombre")
    correo = request.json.get("correo")
    password = request.json.get("password")
    direccion = request.json.get("direccion")
    direccion2 = request.json.get("direccion2")
    pais = request.json.get("pais")
    region = request.json.get("region")
    website = request.json.get("website")
    descripcion = request.json.get("descripcion")
    
    # Validamos los datos ingresados
    if not correo:
        return jsonify({"fail": "correo electrónico es requerido!"}), 422
    
    if not password:
        return jsonify({"fail": "password es requerido!"}), 422

    if not nombre:
        return jsonify({"fail": "nombre es requerido"}), 422

    if not pais:
        return jsonify({"fail": "pais es requerido"}), 422

    if not region:
        return jsonify({"fail": "region es requerida"}), 422

    if not website:
        return jsonify({"fail": "website es requerida"}), 422


    # Buscamos el usuario a ver si ya existe con ese username
    userFound = User.query.filter_by(correo=correo).first()
    
    if userFound:
        return jsonify({"fail": "correo electrónico ya está en uso!"}), 400
    
    # Aqui estamos creando al nuevo usuario
    comercio = Comercio()
    comercio.correo = correo
    comercio.password = generate_password_hash(password) 
    comercio.nombre = nombre
    comercio.pais = pais
    comercio.region = region
    comercio.website = website
    comercio.descripcion = descripcion

    comercio.save()
    
    return jsonify({ "success": "Registro exitoso, por favor inicie sesion!"}), 200


@app.route('/api/post_product_comment', methods=['POST'])
def post_product_comment():
    data = request.json
    # Obtener el user_id y foro_id del cuerpo de la solicitud
    user_id = data.get('user_id')
    producto_id = data.get('producto_id')
    # Verificar si se proporcionó un user_id válido
    if user_id is None:
        return jsonify({'message': 'El campo user_id es requerido'}), 400
    # Verificar si el usuario existe en la base de datos
    user = User.query.get(user_id)
    if user is None:
        return jsonify({'message': 'El usuario no existe'}), 404
    # Verificar si se proporcionó un proyecto_id válido
    if producto_id is None:
        return jsonify({'message': 'El campo producto_id es requerido'}), 400
    # Verificar si el proyecto existe en la base de datos
    producto = Informacion.query.get(producto_id)

   
     # Crea una instancia de la clase Foro con los datos proporcionados
    post = ComentariosProducto(
        comentario=data["comentario"],
        user_id=user_id,  # Asigna el ID del usuario al tema
        producto_id=producto_id, # Asigna el ID del foro 
    )

    # Guarda el nuevo tema en la base de datos
    try:
        post.save()
        return jsonify({"message": "Publicado exitosamente"}), 201
    except Exception as e:
        return jsonify({"error": str(e)}), 500



@app.route('/api/product_comment/<int:producto_id>', methods=['GET'])
def get_product_comment(producto_id):
    # Busca los comentarios relacionados con el tema (post) por su ID en la base de datos
    comentarios = ComentariosProducto.query.filter_by(producto_id=producto_id).all()

    # Serializa la lista de comentarios y devuelve como JSON
    serialized_comments = [comentario.serialize() for comentario in comentarios]

    return jsonify(serialized_comments), 200

@app.route('/api/update_comment_product/<int:id>', methods=['PUT'])
def update_comment_product(id):
    user_id = request.json.get('user_id')  # Obtener user_id de la solicitud
    
    # Verificar si se proporcionó un user_id válido en la solicitud
    if user_id is None:
        return jsonify({'message': 'El campo user_id es requerido'}), 400
    # Buscar el comentario en la base de datos por su ID
    comentario = ComentariosProducto.query.get(id)
    # Verificar si el comentario existe
    if comentario is None:
        return jsonify({'message': 'El comentario no existe'}), 404
    # Actualizar el contenido del comentario con los datos de la solicitud
    try:
        comentario.comentario = request.json.get('comentario', comentario.comentario)
        comentario.activo = request.json.get('activo', comentario.activo)  # Obtener user_id de la solicitud
        comentario.comentario_rep = request.json.get('comentario_rep', comentario.comentario_rep)  # Obtener user_id de la solicitud
        comentario.save()  # Guardar los cambios en la base de datos
        return jsonify({'message': 'Comentario actualizado exitosamente'}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/delete_product_comment/<int:id>', methods=['DELETE'])
def delete_product_comment(id):
    user_id = request.json.get('user_id')  # Obtener user_id de la solicitud
    # Verificar si se proporcionó un user_id válido en la solicitud
    if user_id is None:
        return jsonify({'message': 'El campo user_id es requerido'}), 400
    # Buscar el comentario en la base de datos por su ID
    comentario = ComentariosProducto.query.get(id)
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

@app.route('/user/<int:user_id>', methods=['DELETE'])
def delete_user(user_id):
    user = User.query.get(user_id)

    if user is None:
        return jsonify({'message': 'El usuario no existe'}), 404

    db.session.delete(user)
    db.session.commit()

    return jsonify({'message': 'Usuario eliminado correctamente'}), 200



if __name__ == '__main__':
    app.run(debug=True)





    
    