from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

from datetime import datetime

db = SQLAlchemy()

class User(db.Model):
    __tablename__ = 'usuarios'
    id = db.Column(db.Integer, primary_key=True)
    correo = db.Column(db.String(120), nullable=False, unique=True)
    password = db.Column(db.String(120), nullable=False)
    activo = db.Column(db.Boolean(), default=True)
    nombre = db.Column(db.String(120), nullable=False)
    apellido = db.Column(db.String(120), nullable=False)
    direccion = db.Column(db.String(120))
    pais =db.Column(db.String(120), nullable=False)
    region = db.Column(db.String(120), nullable=False)
    fechanac = db.Column(db.String(120), nullable=False)
    
    def serialize(self):
        return {
            "id": self.id,
            "correo": self.correo,
            "activo": self.activo,
            "nombre": self.nombre,
            "apellido": self.apellido,
            "direccion": self.direccion, 
            "pais": self.pais,
            "region": self.region,
            "fechanac": self.fechanac
                }       
        
    def save(self):
        db.session.add(self)
        db.session.commit()
        
    def update(self):
        db.session.commit()
        
    def delete(self):
        db.session.delete(self)
        db.session.commit()
        
class Comercio(db.Model):
    __tablename__ = 'comercios'
    id = db.Column(db.Integer, primary_key=True)
    correo = db.Column(db.String(120), nullable=False, unique=True)
    password = db.Column(db.String(120), nullable=False)
    activo = db.Column(db.Boolean(), default=True)
    nombre = db.Column(db.String(120), nullable=False)
    direccion = db.Column(db.String(120))
    direccion2 = db.Column(db.String(120))
    pais =db.Column(db.String(120), nullable=False)
    region = db.Column(db.String(120), nullable=False)
    website = db.Column(db.String(120), nullable=False)
    descripcion = db.Column(db.String(250), nullable=False)

    def serialize(self):
        return {
            "id": self.id,
            "correo": self.correo,
            "nombre": self.nombre,
            "direccion": self.direccion, 
            "pais": self.pais,
            "region": self.region,
            "descripcion": self.descripcion,  
            "website": self.website,  
            }            
    def save(self):
        db.session.add(self)
        db.session.commit()
        
    def update(self):
        db.session.commit()
        
    def delete(self):
        db.session.delete(self)
        db.session.commit()

class Foro(db.Model):
    __tablename__ = 'foro'
    id = db.Column(db.Integer, primary_key=True)
    titulo = db.Column(db.String(120), nullable=False)
    fecha = db.Column(db.DateTime, default=datetime.today, nullable=False)
    activo = db.Column(db.Boolean(), default=True)
    comentario_rep = db.Column(db.String(240), nullable=False)
    contenido = db.Column(db.String(240), nullable=False)
    comentario = db.Column(db.String(120), default=True)
    user_id = db.Column(db.Integer, db.ForeignKey('usuarios.id'), nullable=False)
    user = db.relationship('User', backref=db.backref('foros', lazy=True))
    
    
    
    def serialize(self):
        return {
            "id": self.id,
            "titulo": self.titulo,
            "fecha": self.fecha.strftime("%Y-%m-%d %H:%M:%S"),
            "contenido": self.contenido,
            "comnetario": self.comentario,
            "user_id": self.user_id,
            "user": self.user.serialize(),
            "activo": self.activo.serialize(),
            "comentario_rep": self.comentario_rep.serialize(),
                        
                }       
        
    def save(self):
        db.session.add(self)
        db.session.commit()
        
    def update(self):
        db.session.commit()
        
    def delete(self):
        db.session.delete(self)
        db.session.commit()
        

class Comentarios(db.Model):
    __tablename__ = 'comentarios'
    id = db.Column(db.Integer, primary_key=True)
    fecha = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    comentario = db.Column(db.String(120), default=True)
    activo = db.Column(db.Boolean(), default=True)
    comentario_rep = db.Column(db.String(240), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('usuarios.id'), nullable=False)
    foro_id = db.Column(db.Integer, db.ForeignKey('foro.id'), nullable=False)
    user = db.relationship('User', backref=db.backref('comentarios', lazy=True))
    foro = db.relationship('Foro', backref=db.backref('comentarios', lazy=True))
    
    
    
    def serialize(self):
        return {
            "id": self.id,
            "fecha": self.fecha.strftime("%Y-%m-%d %H:%M:%S"),
            "comentario": self.comentario,
            "user_id": self.user_id,
            "foro_id": self.foro_id,
            "user": self.user.serialize(),
            "foro": self.foro.serialize(),
            "activo": self.activo.serialize(),
            "comentario_rep": self.comentario_rep.serialize(),
           
                        
                }       
        
    def save(self):
        db.session.add(self)
        db.session.commit()
        
    def update(self):
        db.session.commit()
        
    def delete(self):
        db.session.delete(self)
        db.session.commit()

class Informacion(db.Model):
    __tablename__ = 'informacion'
    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(120), nullable=False)
    fecha = db.Column(db.DateTime, default=datetime.today, nullable=False)
    direccion = db.Column(db.String(120), nullable=True)  # Puedes cambiar el nullable a False si es obligatorio
    descripcion = db.Column(db.String(240), nullable=True)  # Puedes cambiar el nullable a False si es obligatorio
    activo = db.Column(db.Boolean(), default=True)
    comentario_rep = db.Column(db.String(240), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('usuarios.id'), nullable=False)
    user = db.relationship('User', backref=db.backref('informacion', lazy=True))

    def serialize(self):
        return {
            "id": self.id,
            "nombre": self.nombre,
            "fecha": self.fecha.strftime("%Y-%m-%d %H:%M:%S"),
            "direccion": self.direccion,
            "descripcion": self.descripcion,
            "user_id": self.user_id,
            "user": self.user.serialize(),
            "activo": self.activo.serialize(),
            "comentario_rep": self.comentario_rep.serialize(),
        }

    def save(self):
        db.session.add(self)
        db.session.commit()


class ComentariosProducto(db.Model):
    __tablename__ = 'comentarios_productos'
    id = db.Column(db.Integer, primary_key=True)
    fecha = db.Column(db.DateTime,  default=datetime.today, nullable=False)
    comentario = db.Column(db.String(120), default=True)
    activo = db.Column(db.Boolean(), default=True)
    comentario_rep = db.Column(db.String(240), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('usuarios.id'), nullable=False)
    producto_id = db.Column(db.Integer, db.ForeignKey('informacion.id'), nullable=False)
    user = db.relationship('User', backref=db.backref('comentarios_productos', lazy=True))
    producto = db.relationship('Informacion', backref=db.backref('comentarios_productos', lazy=True))
    
    
    
    def serialize(self):
        return {
            "id": self.id,
            "fecha": self.fecha.strftime("%Y-%m-%d %H:%M:%S"),
            "comentario": self.comentario,
            "user_id": self.user_id,
            "producto_id": self.producto_id,
            "user": self.user.serialize(),
            "producto": self.producto.serialize(),
            "activo": self.activo.serialize(),
            "comentario_rep": self.comentario_rep.serialize(),
            
           
                        
                }       
        
    def save(self):
        db.session.add(self)
        db.session.commit()
        
    def update(self):
        db.session.commit()
        
    def delete(self):
        db.session.delete(self)
        db.session.commit()
        
            
