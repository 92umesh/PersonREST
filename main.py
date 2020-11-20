import json
import logging
from itertools import count

from flask import Flask, jsonify, request
from flask_marshmallow import Marshmallow, Schema
from flask_restful import Api
from flask_sqlalchemy import SQLAlchemy
from marshmallow import fields
from sqlalchemy import create_engine, Integer, String, MetaData, select, Table
from sqlalchemy.ext.declarative import DeclarativeMeta
from sqlalchemy.orm import sessionmaker

app = Flask(__name__)
api = Api(app)
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql+psycopg2://postgres:postgres@localhost:5432/postgres'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)
ma = Marshmallow(app)
logging.basicConfig(level=logging.INFO)


class Person(db.Model):
    """"
    This class represents database model for Person table
    """
    __tablename__ = "person"
    id = db.Column('id', Integer, primary_key=True)
    username = db.Column('username', String, unique=True)
    firstname = db.Column('firstname', String, unique=False)
    lastname = db.Column('lastname', String, unique=False)
    location = db.Column('location', String, nullable=True)
    mobile_number = db.Column('mobile_number', String, nullable=True)
    work_id = db.Column(db.Integer, db.ForeignKey('work.id'), nullable=True)
    work = db.relationship('Work', backref='parents')

    def __init__(self, id, username, firstname, lastname, mobile_number, work_id):
        self.id = id
        self.username = username
        self.firstname = firstname
        self.lastname = lastname
        self.mobile_number = mobile_number
        self.mobile_number = mobile_number
        self.work_id = work_id

    def __json__(self):
        return ['id', 'username', 'firstname', 'lastname', 'location', 'mobile_number', 'work_id']


class Work(db.Model):
    """"
        This class represents database model for Work table
    """
    __tablename__ = "work"
    id = db.Column('id', Integer, primary_key=True)
    org_id = db.Column('org_id', String, unique=False)
    org_name = db.Column('org_name', String, unique=False)
    org_location = db.Column('org_location', String, unique=False)

    def __init__(self, id, org_id, org_name, org_location, person_id):
        self.id = id
        self.org_id = org_id
        self.org_name = org_name
        self.org_location = org_location
        self.person_id = person_id


class WorkSchema(ma.Schema):
    """
    This class represents Marshmellow schema for Work table (WIP)
    """
    id = fields.String()
    org_id = fields.String()
    org_name = fields.String()
    org_location = fields.String()

    class Meta:
        fields = ('id', 'org_id', 'org_name', 'org_location', 'person_id')


class PersonSchema(ma.Schema):
    """
        This class represents Marshmellow schema for Person table (WIP)
        """
    id = fields.String()
    username = fields.String()
    firstname = fields.String()
    lastname = fields.String()
    location = fields.String()
    mobile_number = fields.String()
    work_id = fields.Integer()
    work = fields.Nested(WorkSchema)

    class Meta:
        fields = ('id', 'username', 'firstname', 'lastname', 'location', 'mobile_number', 'work_id')


class PersonWorkJoinSchema(ma.Schema):
    person = fields.Nested(PersonSchema)
    work = fields.Nested(WorkSchema)


person_schema = PersonSchema()
persons_schema = PersonSchema(many=True)


def get_connection():
    """
    generates connection for get_person and put_person resource
    :return:
    database connection and engine for postgresSQL
    """
    engine = create_engine("postgresql+psycopg2://postgres:postgres@localhost:5432/postgres")
    connection = engine.connect()
    return connection, engine


@app.route('/getallpersons/', methods=['GET'])
def get_person():
    """
    this REST resource fetches data for all people from person and work tables
    by performing join on both of the tables
    """
    connection, engine = get_connection()
    Session = sessionmaker(bind=engine)
    session = Session()

    res = session.query(Person, Work).join(Work).all()
    no_of_rows = len(res)
    logging.info('Number of rows in the result is ' + str(no_of_rows))
    json_object = json.dumps(res, cls=AlchemyEncoder)
    return json_object


def parse_sqlalchemy_object(o):
    """
    This function is used by AlchemyEncoder class for finding and transforming query rows into JSON fields
    :param o:
    :return:
    """
    data = {}
    fields = o.__json__() if hasattr(o, '__json__') else dir(o)
    for field in [f for f in fields if not f.startswith('_') and f not in ['metadata', 'query', 'query_class']]:
        value = o.__getattribute__(field)
        try:
            json.dumps(value)
            data[field] = value
        except TypeError:
            data[field] = None
    return data


class AlchemyEncoder(json.JSONEncoder):
    """
    This class is used for converting query results into JSON response
    """

    def default(self, o):
        if isinstance(o, tuple):
            data = {}
            for obj in o:
                data.update(parse_sqlalchemy_object(obj))
            return data
        if isinstance(o.__class__, DeclarativeMeta):
            return parse_sqlalchemy_object(o)
        return json.JSONEncoder.default(self, o)


@app.route('/putperson/<userid>', methods=['POST'])
def put_person(userid):
    """
    this method accepts JSON request for person and work. if valid writes the same into the database
    :param userid:
    :return:
    """
    request_json = request.json
    request_json = request_json["data"]

    for each_person in request_json:
        person_id = each_person.get("id")
        each_person_personal = each_person.get("personal")
        firstname = each_person_personal.get("firstname")
        lastname = each_person_personal.get("lastname")
        username = each_person_personal.get("username")
        mobile_number = each_person_personal.get("mobile_number")
        work_id = each_person_personal.get("work_id")
        new_person = Person(person_id, username, firstname, lastname, mobile_number, work_id)
        db.session.add(new_person)

        each_person_work = each_person.get("work")
        org_id = each_person_work.get("orgId")
        org_name = each_person_work.get("orgName")
        org_location = each_person_work.get("orgLocation")
        new_work = Work(person_id, org_id, org_name, org_location, person_id)
        db.session.add(new_work)

    db.session.commit()

    return 'POST successful'


if __name__ == "__main__":
    db.create_all()
    app.run(debug=True)
