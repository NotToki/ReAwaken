from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, EmailField, SubmitField, TextAreaField
from wtforms.validators import DataRequired, Email, Length, EqualTo, ValidationError
from models import User

class SignupForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired(), Length(min=3, max=50)])
    email = EmailField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired(), Length(min=6)])
    confirm_password = PasswordField('Confirm Password', validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('Sign Up')

    def validate_username(self, username):
        if User.query.filter_by(username=username.data).first():
            raise ValidationError("Username already exists.")

    def validate_email(self, email):
        if User.query.filter_by(email=email.data).first():
            raise ValidationError("Email already exists.")

class LoginForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    submit = SubmitField('Log In')

class FeedbackForm(FlaskForm):
    content = StringField('Your Feedback', validators=[DataRequired(), Length(min=5, max=500)])
    submit = SubmitField('Submit Feedback')

class ContactForm(FlaskForm):
    name = StringField("Your Name", validators=[DataRequired(), Length(min=2, max=50)])
    email = EmailField("Your Email", validators=[DataRequired(), Email()])
    message = TextAreaField("Your Message", validators=[DataRequired(), Length(min=10, max=500)])
    submit = SubmitField("Send Message")