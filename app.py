from flask import Flask, request
from flask_restful import Resource, Api, marshal_with, fields
from flask_sqlalchemy import SQLAlchemy
import os 
from datetime import datetime
import requests



app = Flask(__name__)
api = Api(app)

basedir = os.path.abspath(os.path.dirname(__file__)) 
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(basedir, 'sqllite.db') 
db = SQLAlchemy(app)

class HealthCheck(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String,nullable=False)
    url = db.Column(db.String,nullable=False)
    status = db.Column(db.String,nullable=False)
    description = db.Column(db.String,nullable=False)
    notes = db.Column(db.String,nullable=False)
    create_time = db.Column(db.DateTime,nullable=False)
    update_time = db.Column(db.DateTime,nullable=False)

    def __repr__(self):
        return self.name
    
class HealthCheckHistory(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    hc_id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String,nullable=False)
    url = db.Column(db.String,nullable=False)
    status = db.Column(db.String,nullable=False)
    description = db.Column(db.String,nullable=False)
    notes = db.Column(db.String,nullable=False)
    create_time = db.Column(db.DateTime,nullable=False)
    update_time = db.Column(db.DateTime,nullable=False)

    def __repr__(self):
        return self.name
    
healthCheckFields = {
    'id': fields.Integer,
    'name': fields.String,
    'url': fields.String,
    'status': fields.String,
    'description': fields.String,
    'notes': fields.String,
    'create_time': fields.String,
    'update_time': fields.String
}

healthCheckHistoryFields = {
    'id': fields.Integer,
    'hc_id': fields.Integer,
    'name': fields.String,
    'url': fields.String,
    'status': fields.String,
    'description': fields.String,
    'notes': fields.String,
    'create_time': fields.String,
    'update_time': fields.String
}

def save(x):
    data = x
    try:
        db.session.add(x)
        db.session.flush()
        hst = HealthCheckHistory(hc_id=x.id,name=data.name, url=data.url, status=data.status, description=data.description,notes=data.notes,create_time=datetime.now())

        db.session.add(hst)
        
    except:
        db.session.rollback()
        raise
    else:
        db.session.commit()
    
    
    db.session.commit()

class Items(Resource):
    @marshal_with(healthCheckFields)
    def get(self):
        list = HealthCheck.query.all()
        for x in list:
            resp = requests.get(x.url, timeout=5)
            if resp.status_code == 200:
                x.status = "OK"
            else: 
                x.status = "NOK"
            x.update_time = datetime.now()
            x.notes = "resp_code: {}, resp_time : {}" .format(resp.status_code,  resp.elapsed.total_seconds()*1000)
            save(x)
        return list
    
   
    @marshal_with(healthCheckFields)
    def post(self):
        data = request.json
        item = HealthCheck(name=data['name'], url=data['url'], status=data['status'], description=data['description'],create_time=datetime.now())
        resp = requests.get(data['url'],timeout=5)
        if resp.status_code == 200:
            item.status = "OK"
        else: 
            item.status = "NOK"
        item.notes = "resp_code: {}, resp_time : {}" .format(resp.status_code,  resp.elapsed.total_seconds()*1000)
        save(item)
        
        list = HealthCheck.query.all()
        return list
    

class Item(Resource):
    @marshal_with(healthCheckFields)
    def get(self,pk):
        task = HealthCheck.query.filter_by(id=pk).first()
    
        resp = requests.get(task.url,timeout=5)
        if resp.status_code == 200:
            task.status = "OK"
        else: 
            task.status = "NOK"
        task.notes = "resp_code: {}, resp_time : {}" .format(resp.status_code,  resp.elapsed.total_seconds()*1000)
        task.update_time = datetime.now()
        save(task)
        return task
    
    @marshal_with(healthCheckFields)
    def put(self,pk):
        data = request.json
        task = HealthCheck.query.filter_by(id=pk).first()
        task.name = data['name']
        task.url=data['url']
        task.status=data['status']
        task.description=data['description']
        task.notes=['notes']
        task.update_time = datetime.now()
        save(task)
        return task

api.add_resource(Items, '/')
api.add_resource(Item, '/<int:pk>')


if __name__ == '__main__':
    app.run(debug=True)