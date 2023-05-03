import bcrypt
from flask import Flask, request
from flask_restful import Api, Resource, reqparse, abort, fields, marshal_with
from flask_restful_swagger import swagger
from flask_sqlalchemy import SQLAlchemy
from datetime import date

app = Flask(__name__)
api = swagger.docs(Api(app), apiVersion='0.1')
app.config['SQLALCHEMY_DATABASE-URI'] = 'sqlite:///database.db'
db = SQLAlchemy(app)


class User(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    email = db.Column(db.String(100), nullable=False, unique=True)
    current_balance = db.Column(db.Integer, default=0)
    pin_hash = db.Column(db.String(6))
    transactions = db.relationship('Transaction', backref='user', lazy=True)

    def set_pin(self, pin):
        self.pin_hash = bcrypt.hashpw(pin.encode('utf-8'), bcrypt.gensalt())

    def check_pin(self, pin):
        return bcrypt.checkpw(pin.encode('utf-8'), self.pin_hash)

    def __repr__(self):
        return f"User(email = {email}, current_balance = {current_balance}, pin_hash = {pin_hash})"


class Transaction(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    amount = db.Column(db.Integer, nullable=False)
    tx_type = db.Column(db.String, nullable=False)
    tx_date = db.Column(db.Date, default=date.today())
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)

    def __repr__(self):
        return f"User(amount = {amount}, tx_type = {tx_type}, tx_date = {tx_date}, user_id = {user_id})"


db.create_all()

user_get_args = reqparse.RequestParser()
user_get_args.add_argument(
    "user_id", type=int, help="User Id required", required=True)

user_post_args = reqparse.RequestParser()
user_post_args.add_argument(
    "email", type=str, help="Email required", required=True)
user_post_args.add_argument(
    "pin", type=str, help="Pin required", required=True)


user_cb_get_args = reqparse.RequestParser()
user_cb_get_args.add_argument(
    "email", type=str, help="Email required", required=True)
user_cb_get_args.add_argument(
    "pin", type=str, help="Pin required", required=True)

resource_fields = {
    'id': fields.Integer,
    'email': fields.String,
    'current_balance': fields.Integer,
    'pin_hash': fields.String
}


def abort_if_user_not_found(result):
    if not result:
        abort(404, message="User not found")


def abort_if_user_exists(result):
    if result:
        abort(409, message="User already exists")


def abort_not_enough_balance():
    abort(404, message="Not enough balance")


def abort_pin_incorrect():
    abort(404, message="Pin incorrect")


class Users(Resource):
    "Users"
    @marshal_with(resource_fields)
    @swagger.operation(
        summary='Get User by User Id',
        parameters=[
            {
                "name": "user_id",
                "description": "Id of User",
                "required": True,
                "dataType": "Integer",
                "paramType": "body"
            }
        ],
        responseMessages=[
            {
                "code": 200,
                "message": "OK"
            },
            {
                "code": 404,
                "message": "User not found"
            }
        ]
    )
    def get(self):
        args = user_get_args.parse_args()
        result = User.query.filter_by(id=args['user_id']).first()
        abort_if_user_not_found(result)
        return result, 200

    "Users"
    @marshal_with(resource_fields)
    @swagger.operation(
        summary='Create new User',
        parameters=[
            {
                "name": "email",
                "description": "Email of User",
                "required": True,
                "dataType": "String",
                "paramType": "body"
            },
            {
                "name": "pin",
                "description": "Pin to be set by User",
                "required": True,
                "dataType": "String",
                "paramType": "body"
            }
        ],
        responseMessages=[
            {
                "code": 201,
                "message": "Created"
            },
            {
                "code": 409,
                "message": "User already exists"
            }
        ]
    )
    def post(self):
        args = user_post_args.parse_args()
        result = User.query.filter_by(email=args['email']).first()
        abort_if_user_exists(result)
        user = User(email=args['email'])
        user.set_pin(args['pin'])
        db.session.add(user)
        db.session.commit()
        return user, 201


class UsersCurrentBalance(Resource):

    "Users"
    @swagger.operation(
        summary='Get current balance of User',
        parameters=[
            {
                "name": "email",
                "description": "Email of User",
                "required": True,
                "dataType": "String",
                "paramType": "body"
            },
            {
                "name": "pin",
                "description": "Pin of User",
                "required": True,
                "dataType": "String",
                "paramType": "body"
            }
        ],
        responseMessages=[
            {
                "code": 200,
                "message": "OK"
            },
            {
                "code": 404,
                "message": "User not found"
            },
            {
                "code": 404,
                "message": "Pin incorrect"
            }
        ]
    )
    def get(self):
        args = user_cb_get_args.parse_args()
        result = User.query.filter_by(email=args['email']).first()
        abort_if_user_not_found(result)
        if result.check_pin(args['pin']):
            return {"current_balance": result.current_balance}
        else:
            abort_pin_incorrect()


api.add_resource(Users, "/users")
api.add_resource(UsersCurrentBalance, "/users/current-balance")


transaction_post_args = reqparse.RequestParser()
transaction_post_args.add_argument(
    "amount", type=int, help="Amount required", required=True)
transaction_post_args.add_argument(
    "tx_type", type=str, help="Transaction type required", required=True)
transaction_post_args.add_argument(
    "email", type=str, help="Email required", required=True)
transaction_post_args.add_argument(
    "pin", type=str, help="Pin required", required=True)

tx_resource_fields = {
    'id': fields.Integer,
    'tx_type': fields.String,
    'amount': fields.Integer,
    'tx_date': fields.String,
    'user_id': fields.Integer
}


class Transactions(Resource):
    "Transactions"
    @swagger.operation(
        summary='Create new Deposit or Debit Transaction',
        parameters=[
            {
                "name": "email",
                "description": "Email of User",
                "required": True,
                "dataType": "String",
                "paramType": "body"
            },
            {
                "name": "pin",
                "description": "Pin of User",
                "required": True,
                "dataType": "String",
                "paramType": "body"
            },
            {
                "name": "amount",
                "description": "Amount of transaction",
                "required": True,
                "dataType": "Integer",
                "paramType": "body"
            },
            {
                "name": "tx_type",
                "description": "Kind of transaction to be done. (Debit or Deposit)",
                "required": True,
                "dataType": "Integer",
                "paramType": "body"
            },
        ],
        responseMessages=[
            {
                "code": 200,
                "message": "OK"
            },
            {
                "code": 404,
                "message": "Not enough balance"
            },
            {
                "code": 404,
                "message": "Pin incorrect"
            },
            {
                "code": 404,
                "message": "User not found"
            }
        ]
    )
    @marshal_with(tx_resource_fields)
    def post(self):
        args = transaction_post_args.parse_args()
        user = User.query.filter_by(email=args['email']).first()
        abort_if_user_not_found(user)
        transaction = Transaction(
            amount=args['amount'], tx_type=args['tx_type'], user_id=user.id)

        if user.check_pin(args['pin']):
            if transaction.tx_type == 'Deposit':
                user.current_balance = user.current_balance + transaction.amount
            if transaction.tx_type == 'Debit':
                if user.current_balance > transaction.amount:
                    user.current_balance = user.current_balance - transaction.amount
                else:
                    abort_not_enough_balance()
        else:
            abort_pin_incorrect()

        db.session.add(transaction)
        db.session.add(user)
        db.session.commit()
        return transaction, 201


api.add_resource(Transactions, "/transactions")

if __name__ == "__main__":
    app.run(debug=True)
