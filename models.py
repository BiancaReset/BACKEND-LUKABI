from flask_sqlalchemy import SQLAlchemy
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
        