import logging

from flask import Flask, jsonify, request
from flask_marshmallow import Marshmallow
from flask_restful import Api, reqparse
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import create_engine, Integer, String, MetaData, select, Table

app = Flask(__name__)
api = Api(app)
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql+psycopg2://postgres:postgres@localhost:5432/postgres'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)
ma = Marshmallow(app)
logging.basicConfig(level=logging.INFO)


class Person(db.Model):
    __tablename__ = "person"
    id = db.Column('id', Integer, primary_key=True)
    username = db.Column('username', String, unique=True)
    firstname = db.Column('firstname', String, unique=False)
    lastname = db.Column('lastname', String, unique=False)
    location = db.Column('location', String, nullable=True)
    mobile_number = db.Column('mobile_number', String, nullable=True)

    def __init__(self, id, username, firstname, lastname, mobile_number):
        self.id = id
        self.username = username
        self.firstname = firstname
        self.lastname = lastname
        self.mobile_number = mobile_number


class Work(db.Model):
    __tablename__ = "work"
    id = db.Column('id', Integer, primary_key=True)


class PersonSchema(ma.Schema):
    class Meta:
        fields = ('id', 'username', 'firstname', 'lastname', 'location', 'mobile_number')


person_schema = PersonSchema()
persons_schema = PersonSchema(many=True)


def get_connection():
    """
    generates connection for ReturnJSON resource
    :return:
    database connection and engine for postgresSQL
    """
    engine = create_engine("postgresql+psycopg2://postgres:postgres@localhost:5432/postgres")
    connection = engine.connect()
    return connection, engine


@app.route('/getperson/<userid>', methods=['GET'])
def get_person(userid):
    """
        this resource accepts userId and returns corresponding username, firstname, lastname, location and mobile number
        should return 404 when no records found for given userId (WIP)
        """
    connection, engine = get_connection()
    metadata = MetaData(bind=None)
    table = Table('person', metadata, autoload=True, autoload_with=engine)
    stmt = select([table]).where(table.columns.id == userid)
    res = connection.execute(stmt)
    logging.info("Row count is %d", res.rowcount)
    if res.rowcount == 0:
        logging.info("No data found for id %s ", userid)
    result = persons_schema.dump(res)
    return jsonify(result)


put_person_args = reqparse.RequestParser()
put_person_args.add_argument("id", type=str, help="person id is required ", required=True)
put_person_args.add_argument("firstname", type=str, help="firstname is required ", required=True)
put_person_args.add_argument("lastname", type=str, help="lastname is required ", required=True)
put_person_args.add_argument("username", type=str, help="username is required ", required=True)


# class Person(Resource):
#     def put(self, userid):
#         args = put_person_args.parse_args()
#         return {userid: args}


@app.route('/putperson/<userid>', methods=['POST'])
def put_person(userid):
    request_json = request.json
    request_json = request_json["data"]

    for each_person in request_json:
        person_id = each_person.get("id")
        each_person_personal = each_person.get("personal")
        firstname = each_person_personal.get("firstname")
        lastname = each_person_personal.get("lastname")
        username = each_person_personal.get("username")
        mobile_number = each_person_personal.get("mobile_number")
        new_person = Person(person_id, username, firstname, lastname, mobile_number)
        db.session.add(new_person)
        print(person_id)
        print(firstname)
        print(lastname)
        print(username)
        print(mobile_number)

    print(new_person)

    # db.session.commit()

    return person_schema.jsonify("new_person")


if __name__ == "__main__":
    db.create_all()
    app.run(debug=True)
