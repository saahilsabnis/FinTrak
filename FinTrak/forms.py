from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, BooleanField, DecimalField, SelectField
from wtforms.ext.sqlalchemy.fields import QuerySelectField
from wtforms.validators import DataRequired, Length, Email, EqualTo, ValidationError
from FinTrak.models import User, Categories
from flask_login import current_user
from wtforms.fields.html5 import DateField

class RegistrationForm(FlaskForm):
    username = StringField("Username", validators = [DataRequired(), Length(min = 2, max = 20)])
    email = StringField("Email", validators = [DataRequired(), Email()])
    password = PasswordField("Password", validators = [DataRequired()])
    confirm_password = PasswordField("Confirm Password", validators = [DataRequired(), EqualTo("password")])
    submit = SubmitField("Sign Up")

    def validate_username(self, username):
        user = User.query.filter_by(username = username.data).first()
        if user:
            raise ValidationError("Username already taken, please choose another one.")

    def validate_email(self, email):
        email = User.query.filter_by(email = email.data).first()
        if email:
            raise ValidationError("Email already taken, please choose another one.")



class LoginForm(FlaskForm):
    email = StringField("Email", validators = [DataRequired(), Email()])
    password = PasswordField("Password", validators = [DataRequired()])
    remember = BooleanField("Remember Me")
    submit = SubmitField("Log In")



class UpdateAccountForm(FlaskForm):
    username = StringField("Username", validators = [DataRequired(), Length(min = 2, max = 20)])
    email = StringField("Email", validators = [DataRequired(), Email()])
    submit = SubmitField("Update")

    def validate_username(self, username):
        if username.data != current_user.username:
            user = User.query.filter_by(username = username.data).first()
            if user:
                raise ValidationError("Username already taken, please choose another one.")

    def validate_email(self, email):
        if email.data != current_user.email:
            email = User.query.filter_by(email = email.data).first()
            if email:
                raise ValidationError("Email already taken, please choose another one.") 



class AddExpense(FlaskForm):
    description = StringField("Description", validators = [DataRequired()])
    category = QuerySelectField("Categories", query_factory = lambda: Categories.query.filter_by(user_id = current_user.id).all(),
                allow_blank = True, blank_text = "Select") # Generate select field from database entries of each user   
    amount = DecimalField("Amount", places = 2, validators = [DataRequired()])
    paidby = StringField("Paid By", default = "Self")
    date = DateField("Date", validators = [DataRequired()])


class CategoryAdd(FlaskForm):
    name = StringField("Description", validators = [DataRequired()])
    submit = SubmitField("Update")

    def validate_name(self, name):
        cats = Categories.query.filter_by(name = name.data, user_id = current_user.id).first()
        if cats:
            raise ValidationError("The category alredy exists!")

class CategoryRemove(FlaskForm):
    name = QuerySelectField("Categories", query_factory = lambda: Categories.query.filter_by(user_id = current_user.id).all(),
               allow_blank = True, blank_text = "Select")
    submit = SubmitField("Remove")

class BudgetForm(FlaskForm):
    weeklybudget = DecimalField("Weekly Budget", places = 2, validators = [DataRequired()])
    monthlybudget = DecimalField("Monthly Budget", places = 2, validators = [DataRequired()])
    yearlybudget = DecimalField("Yearly Budget", places = 2, validators = [DataRequired()])
    submit = SubmitField("Update")