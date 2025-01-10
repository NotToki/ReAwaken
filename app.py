import os
from flask import Flask, render_template, redirect, url_for, flash
from flask_migrate import Migrate
from flask_login import LoginManager, login_user, logout_user, login_required, current_user
from datetime import datetime as dt
from models import db, User, Feedback
from werkzeug.security import generate_password_hash, check_password_hash
from forms import SignupForm, LoginForm, ContactForm, FeedbackForm
from config import Config, DevelopmentConfig

app = Flask(__name__)
app.config.from_object(Config)
app.config.from_object(DevelopmentConfig)

os.makedirs(app.instance_path, exist_ok=True)

db.init_app(app)
migrate = Migrate(app, db)

login_manager = LoginManager()
login_manager.login_view = "login"
login_manager.init_app(app)

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

@app.context_processor
def inject_now():
    return {'now': dt.now()}

@app.route('/')
def root():
    return render_template('index.html')

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    form = SignupForm()
    if form.validate_on_submit():
        hashed_password = generate_password_hash(form.password.data, method="pbkdf2:sha256", salt_length=16)
        new_user = User(username=form.username.data, email=form.email.data, password=hashed_password)
        db.session.add(new_user)
        db.session.commit()
        flash("Signup successful! You can now log in.", "success")
        return redirect(url_for('login'))
    return render_template('signup.html', form=form)

@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user and check_password_hash(user.password, form.password.data):
            login_user(user)
            flash("Login successful!", "success")
            return redirect(url_for('root'))
        flash("Invalid username or password.", "error")
    return render_template('login.html', form=form)

@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash("You have logged out successfully.", "success")
    return redirect(url_for('root'))

@app.route('/programs')
def programs():
    example_programs = [
        {"name": "Strength Training", "description": "Build strength and muscle.", "price": "$50/month"},
        {"name": "Cardio Blast", "description": "Improve stamina and burn calories.", "price": "$40/month"},
    ]
    return render_template('programs.html', programs=example_programs)

@app.route('/admin', methods=['GET', 'POST'])
@login_required
def admin():
    if not current_user.is_admin:
        flash("Admin access only!", "error")
        return redirect(url_for('root'))

    users = User.query.all()
    feedback = Feedback.query.order_by(Feedback.created_at.desc()).all()

    return render_template('admin.html', users=users, feedback=feedback)

@app.route('/delete_user/<int:user_id>', methods=['POST'])
@login_required
def delete_user(user_id):
    if not current_user.is_admin:
        flash("Admin access only!", "error")
        return redirect(url_for('root'))

    user = User.query.get(user_id)
    if user:
        db.session.delete(user)
        db.session.commit()
        flash(f"User {user.username} deleted.", "success")
    else:
        flash("User not found.", "error")

    return redirect(url_for('admin'))

@app.errorhandler(500)
def internal_error(e):
    return render_template('500.html'), 500

@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html'), 404

@app.errorhandler(403)
def forbidden(e):
    return render_template('403.html'), 403

@app.errorhandler(401)
def unauthorized(e):
    return render_template('401.html'), 401

@app.errorhandler(400)
def bad_request(e):
    return render_template('400.html'), 400

@app.route('/purchase/<program_name>')
def purchase(program_name):
    return render_template('purchase.html', program_name=program_name)

from flask_mail import Mail, Message

mail = Mail(app)

@app.route('/contact', methods=['GET', 'POST'])
def contact():
    form = ContactForm()
    if form.validate_on_submit():
        sender_name = form.name.data
        sender_email = form.email.data
        message_body = form.message.data

        msg = Message(subject=f"Contact Form Submission from {sender_name}",
                      sender=sender_email,
                      recipients=[app.config['MAIL_USERNAME']])
        msg.body = f"From: {sender_name} <{sender_email}>\n\nMessage:\n{message_body}"

        try:
            mail.send(msg)
            flash("Your message has been sent successfully!", "success")
        except Exception as e:
            flash(f"An error occurred: {str(e)}", "danger")

        return redirect(url_for('contact'))

    return render_template('contact.html', form=form)

@app.route('/feedback', methods=['GET', 'POST'])
@login_required
def feedback():
    form = FeedbackForm()
    if form.validate_on_submit():
        new_feedback = Feedback(user_id=current_user.id, content=form.content.data)
        db.session.add(new_feedback)
        db.session.commit()
        flash("Your feedback has been submitted!", "success")
        return redirect(url_for('view_feedback'))
    return render_template('feedback.html', form=form)

@app.route('/view_feedback')
def view_feedback():
    all_feedback = Feedback.query.order_by(Feedback.created_at.desc()).all()
    return render_template('view_feedback.html', feedback=all_feedback)

@app.route('/my_feedback', methods=['GET', 'POST'])
@login_required
def my_feedback():
    user_feedback = Feedback.query.filter_by(user_id=current_user.id).order_by(Feedback.created_at.desc()).all()
    return render_template('my_feedback.html', feedback=user_feedback)

@app.route('/delete_feedback/<int:feedback_id>', methods=['POST'])
@login_required
def delete_feedback(feedback_id):
    feedback = Feedback.query.get(feedback_id)
    if feedback and feedback.user_id == current_user.id:
        db.session.delete(feedback)
        db.session.commit()
        flash("Your feedback has been deleted.", "success")
    else:
        flash("Feedback not found or not authorized to delete.", "danger")
    return redirect(url_for('my_feedback'))

if __name__ == '__main__':
    app.run(debug=False, host='0.0.0.0')
