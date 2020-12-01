from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, TextAreaField,  BooleanField, PasswordField
from wtforms.validators import DataRequired, Email

class ContactForm(FlaskForm):
    name = StringField("Name: ", validators=[DataRequired()])
    email = StringField("Email: ", validators=[Email()])
    message = TextAreaField("Message", validators=[DataRequired()])
    submit = SubmitField("Submit")

class LoginForm(FlaskForm):
    email = StringField("Email: ", validators=[DataRequired('Это поле обязательно для заполнения')])
    password = PasswordField("Password: ", validators=[DataRequired('Это поле обязательно для заполнения')])
    remember = BooleanField("Remember Me")
    submit = SubmitField()

class RegisterForm(FlaskForm):
    username = StringField("Username: ", validators=[DataRequired('Это поле обязательно для заполнения')])
    email = StringField("Email   : ", validators=[Email('Это поле обязательно для заполнения')])
    password = PasswordField("Password: ", validators=[DataRequired('Это поле обязательно для заполнения')])
    remember = BooleanField("Remember Me")
    submit = SubmitField('Sign Up')
