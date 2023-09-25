from flask_sqlalchemy import SQLAlchemy
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


class Foro(db.Model):
    __tablename__ = 'foro'
    id = db.Column(db.Integer, primary_key=True)
    titulo = db.Column(db.String(120), nullable=False)
    fecha = db.Column(db.DateTime, default=datetime.today, nullable=False)
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
            
           
                        
                }       
        
    def save(self):
        db.session.add(self)
        db.session.commit()
        
    def update(self):
        db.session.commit()
        
    def delete(self):
        db.session.delete(self)
        db.session.commit()
        