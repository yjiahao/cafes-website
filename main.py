from flask import Flask, render_template, redirect, url_for, request, jsonify, flash
from flask_login import current_user, login_user, LoginManager, UserMixin, logout_user
from flask_sqlalchemy import SQLAlchemy
from flask_bootstrap import Bootstrap
from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField, IntegerField, BooleanField, PasswordField
from wtforms.validators import DataRequired
from wtforms.validators import InputRequired, Length
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)
bootstrap = Bootstrap(app)
db = SQLAlchemy()
login = LoginManager(app)

app.config['SECRET_KEY'] = 'your secret key'
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///cafes.db"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db.init_app(app)

    # def __init__(self, id, name, map_url, img_url, location, seats, has_toilet, has_wifi, has_sockets, can_take_calls, coffee_price):
    #     self.id = id
    #     self.name = name
    #     self.map_url = map_url
    #     self.img_url = img_url
    #     self.location = location
    #     self.seats = seats
    #     self.has_toilet = has_toilet
    #     self.has_wifi = has_wifi
    #     self.has_sockets = has_sockets
    #     self.can_take_calls = can_take_calls
    #     self.coffee_price = coffee_price


# starbucks = Cafes(
#     name="Starbucks @ Changi Airport",
#     map_url="www.sb.com",
#     img_url="www.sbsb.com",
#     location="Singapore,Changi Airport",
#     seats="90",
#     has_toilet=True,
#     has_wifi=True,
#     has_sockets=True,
#     can_take_calls=True
# )
#
# starbucks_2 = Cafes(
#     name="Starbucks @ NEX",
#     map_url="www.sb.com",
#     img_url="www.sbsb.com",
#     location="Singapore,Serangoon",
#     seats="90",
#     has_toilet=True,
#     has_wifi=True,
#     has_sockets=True,
#     can_take_calls=True
# )
#
# coffee_bean = Cafes(
#     name="Coffee Bean @ NEX",
#     map_url="www.coffeebean.com",
#     img_url="www.coffeebean.com",
#     location="Singapore,Serangoon",
#     seats="90",
#     has_toilet=True,
#     has_wifi=True,
#     has_sockets=True,
#     can_take_calls=True
# )
#
# with app.app_context():
#     db.session.add_all([coffee_bean,starbucks,starbucks_2])
#     db.session.commit()

class Cafes(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(250), unique=True, nullable=False)
    map_url = db.Column(db.String(500), nullable=False)
    img_url = db.Column(db.String(500), nullable=False)
    location = db.Column(db.String(250), nullable=False)
    seats = db.Column(db.String(250), nullable=False)
    has_toilet = db.Column(db.Boolean, nullable=False)
    has_wifi = db.Column(db.Boolean, nullable=False)
    has_sockets = db.Column(db.Boolean, nullable=False)
    can_take_calls = db.Column(db.Boolean, nullable=False)
    coffee_price = db.Column(db.String(250), nullable=True)

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(250), unique=True, nullable=False)
    password = db.Column(db.String(250), nullable=False)

with app.app_context():
    db.create_all()

class MyForm(FlaskForm):
    name = StringField('Name', validators=[DataRequired(), Length(min=0, max=250)])
    map_url = StringField('Map URL', validators=[DataRequired(), Length(min=0, max=250)])
    img_url = StringField('Image URL', validators=[DataRequired(), Length(min=0, max=250)])
    location = StringField('Location', validators=[DataRequired(), Length(min=0, max=250)])
    seats = StringField('No. of Seats', validators=[DataRequired(), Length(min=0, max=250)])
    has_toilet = BooleanField('Are there toilets?', validators=[DataRequired()], default='checked')
    has_wifi = BooleanField('Is there Wifi?', validators=[DataRequired()], default='checked')
    has_sockets = BooleanField('Are there power plugs?', validators=[DataRequired()], default='checked')
    can_take_calls = BooleanField('Able to take calls?', validators=[DataRequired()], default='checked')
    coffee_price = StringField('Price of coffee, in dollars', validators=[DataRequired(), Length(min=0, max=250)])

class RegisterForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Length(min=0, max=250)])
    password = PasswordField('Password', validators=[DataRequired(), Length(min=8, max=250)])


@login.user_loader
def load_user(id):
    return User.query.get(int(id))


@app.route("/")
def home():
    return render_template("index.html")


@app.route("/cafes")
def cafes():
    cafes = Cafes.query.all()
    return render_template("cafes.html", cafes=cafes)


@app.route('/cafes/delete/<int:id>')
def delete_cafe(id):
    cafe_to_delete = Cafes.query.get_or_404(id)
    try:
        db.session.delete(cafe_to_delete)
        db.session.commit()
        flash('Cafe is deleted!')
        cafes = Cafes.query.all()
        return render_template("cafes.html", cafes=cafes)
    except:
        flash("There was an error while deleting your cafe!")
        cafes = Cafes.query.all()
        return render_template("cafes.html", cafes=cafes)

@app.route("/cafes/<int:id>")
def cafe_info(id):
    cafe = Cafes.query.get_or_404(id)
    return render_template("cafe-info.html", cafe=cafe)

@app.route("/new-cafe", methods=['GET', 'POST'])
def submit():
    form = MyForm()
    if request.method == 'POST' and form.validate_on_submit() and current_user.is_authenticated:
        cafe = Cafes(name=form.name.data,
                     map_url=form.map_url.data,
                     img_url=form.img_url.data,
                     location=form.location.data,
                     seats=form.seats.data,
                     has_toilet=form.has_toilet.data,
                     has_wifi=form.has_wifi.data,
                     has_sockets=form.has_sockets.data,
                     can_take_calls=form.can_take_calls.data,
                     coffee_price=form.coffee_price.data
                     )
        db.session.add(cafe)
        db.session.commit()
        return redirect(url_for("home"))
    else:
        flash('You are not logged in. Only authenticated users can add to our database!')
    return render_template("form.html", form=form)


@app.route("/register", methods=['GET', 'POST'])
def register():
    register_form = RegisterForm()
    if request.method == 'POST' and register_form.validate_on_submit():
        email = register_form.email.data
        password = register_form.password.data
        user = User.query.filter_by(email=email).first()
        if user:
            flash('That email already exists!')
            return redirect(url_for('register'))
        else:
            user = User(
                email=register_form.email.data,
                password=generate_password_hash(register_form.password.data)
            )
            db.session.add(user)
            db.session.commit()
            login_user(user)
        return redirect(url_for("home"))
    return render_template("register-form.html", form=register_form)


@app.route("/login", methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    login_form = RegisterForm()
    if request.method == 'POST' and login_form.validate_on_submit():
        user = User.query.filter_by(email=login_form.email.data).first()
        if user and check_password_hash(user.password, login_form.password.data):
            login_user(user)
            flash('You are now logged in!')
            return render_template('index.html')
        else:
            flash('Email or password is incorrect. Try again!')
    return render_template('login.html', form=login_form)


@app.route("/logout")
def logout():
    logout_user()
    flash('You are now logged out!')
    return render_template('index.html')


if __name__ == '__main__':
    app.run(debug=True)

# Beautify buttons in cafes.html