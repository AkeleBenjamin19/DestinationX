from app import db
class Visa_policies(db.Model):

    __tablename__ = 'visa_policies'
    id = db.Column(db.Integer, primary_key=True)
    visa_free =db.Column(db.Boolean)
    destination_id = db.Column(db.Integer, db.ForeignKey('countries.id'))
    e_visa = db.Column(db.Boolean)
    visa_required = db.Column(db.Boolean)

    def __init__(self, visa_free, destination_id, e_visa, visa_required):
        self.visa_free = visa_free
        self.destination_id = destination_id
        self.e_visa = e_visa
        self.visa_required = visa_required

    def _getVisaFree(self):
        return self.visa_free
    
    def _getDestinationId(self):
        return self.destination_id
    

    def _getEVisa(self):
        return self.e_visa
    

    def _getVisaRequired(self):
        return self.visa_required
    




