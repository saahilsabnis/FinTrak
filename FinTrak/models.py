from FinTrak import db, login_manager
from datetime import datetime
from flask_login import UserMixin


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key = True)
    username = db.Column(db.String(20), unique = True, nullable = False)
    email = db.Column(db.String(120), unique = True, nullable = False)
    image_file = db.Column(db.String(20), nullable = False, default = "default.jpg")
    password = db.Column(db.String(60),nullable = False)

    expenses = db.relationship("Expenses", backref = "user", lazy = True)  # referencing the Expenses class for relationship
    categories = db.relationship("Categories", backref = "user", lazy = True)  # Categories class
    budgets = db.relationship("Budgets", backref = "user", lazy = True)  # Budget class

    def __repr__(self):
        return f"User('{self.username}', '{self.email}', '{self.image_file}')"


class Expenses(db.Model):
    id = db.Column(db.Integer, primary_key = True)
    description = db.Column(db.String(40))
    category = db.Column(db.String(100), nullable = False)
    amount = db.Column(db.Float, nullable = False)
    date = db.Column(db.DateTime, nullable = False, default = datetime.utcnow)
    paidby = db.Column(db.String(20), nullable = False, default = "Self")
    user_id = db.Column (db.Integer, db.ForeignKey("user.id"), nullable = False)  # referencing the table and column name

    def __repr__(self):
        return f"Expenses('{self.description}', '{self.category}', '{self.amount}', '{self.date}', '{self.paidby}')"


class Categories(db.Model):
    id = db.Column(db.Integer, primary_key = True)
    name = db.Column(db.String(20), nullable = False)
    user_id = db.Column (db.Integer, db.ForeignKey("user.id"), nullable = False)  # referencing the table and column name

    def __repr__(self):
        return f"{self.name}"


class Budgets(db.Model):
    id = db.Column(db.Integer, primary_key = True)
    weeklybudget = db.Column(db.Float, nullable = False)
    monthlybudget = db.Column(db.Float, nullable = False)
    yearlybudget = db.Column(db.Float, nullable = False)
    user_id = db.Column (db.Integer, db.ForeignKey("user.id"), nullable = False)  # referencing the table and column name

    def __repr__(self):
        return f"Budgets('{self.weeklybudget}','{self.monthlybudget}','{self.yearlybudget}')"