from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_name = db.Column(db.String(20), unique = True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(80), unique=False, nullable=False)
    favorites = db.relationship('Favorite', backref='user')

    def __repr__(self):
        return '<User %r,%r,%r,%r>' % (self.id,self.user_name,self.email,self.password)

    def serialize(self):
        return {
            "id": self.id,
            "user_name": self.user_name,
            "email": self.email,
            "favorites":[favorite.serialize() for favorite in self.favorites]
        }

class Favorite(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255), unique=False, nullable=False)
    entity_type = db.Column(db.String(255), unique=False, nullable=False)
    entity_id = db.Column(db.Integer, unique=False, nullable=False)
    user_name = db.Column(db.String(255), db.ForeignKey('user.user_name'))
    
    def __repr__(self):
        return '<Favorite %r,%r,%r,%r,%r>' % (self.id,self.name,self.entity_type,self.entity_id,self.user_name)

    def serialize(self):
        return {
            "id": self.id,
            "name": self.name,
            "entity_type": self.entity_type,
            "entity_id": self.entity_id,
            "user_name": self.user_name,
        }