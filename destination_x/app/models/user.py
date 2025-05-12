from  app import db
class User(db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(80))
    username = db.Column(db.String(80))
    def __init__(self, name, email):
        self.username = name
        self.email = email
       

    def _getEmail(self):
        return self.email
    
    def _getUsername(self):
        return self.username
    
    def _getId(self):
        return self.id
    
    