from flask import Flask, request, jsonify
from pymongo import MongoClient
from flask_cors import CORS
from flask_bcrypt import Bcrypt
from os import environ

app = Flask(__name__)

app.config.from_object(__name__)

CORS(app, resources={r"/*":{'origins':"*"}})

client = MongoClient(environ.get('DB_URI'), 27017)

db = client.user_database
users = db.users
cryptor = Bcrypt(app)

@app.route('/', methods=['GET'])
def index():
    all_users = users.find() 
    response_object = {'status':'success'}
    response_object['users'] = all_users
    return response_object

@app.route('/signup', methods=['POST'])
def signup():
    response_object = {'status':'success'}
    if request.method =="POST":
        new_user_data = request.get_json()
        user = users.find_one({'$or':[
                                    {'username': new_user_data.get('username')},
                                    {'email': new_user_data.get('email')},
                            ]})
        if user :
            response_object['message'] = 'Akun sudah terdaftar'
            response_object['status'] = 'error'
        else:
            hash_password = cryptor.generate_password_hash(new_user_data.get('password')).decode('utf-8')
            users.insert_one({
                'username': new_user_data.get('username'),
                'name': new_user_data.get('name'),
                'email': new_user_data.get('email'),
                'address': new_user_data.get('address'),
                'phone_number': new_user_data.get('phone_number'),
                'password' : hash_password
            })
            response_object['message'] = 'Akun telah terdaftar'
    return jsonify(response_object)

@app.route('/login', methods=['POST'])
def login():
    response_object = {'status':'success'}
    if request.method =="POST":
        user_data = request.get_json()
        user = users.find_one({'$or':[
                       {'username': user_data.get('username')},
                       {'email': user_data.get('username')},
                        ]
                    })
        if user:
            if cryptor.check_password_hash(user['password'], user_data.get('password')):
                response_object['message'] = 'Login Berhasil'
            else:
                response_object['status'] = 'error'
                response_object['message'] = 'Password salah'
        else:
            response_object['status'] = 'error'
            response_object['message'] = 'Username / Email belum terdaftar'
    return jsonify(response_object)

if __name__ == "__main__":
    app.run(debug=True)