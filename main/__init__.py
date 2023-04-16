from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from flask_migrate import Migrate
from flask_login import LoginManager


app = Flask(__name__)
app.config['SQLALCHEMY_TRACK_MODIFICATION'] = False
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://postgres:243313@localhost/evaluator'
app.config['SECRET_KEY'] ='38cfb4efdfaacb063d16d8ad'
db = SQLAlchemy(app)
migrate = Migrate(app, db)
bcrypt = Bcrypt(app)

login_manager = LoginManager(app)
login_manager.login_view = 'views.login'
login_manager.login_message_category = 'info'

# This is a place sensitive
# Because in views we import app and db so if we make an import from this page at the
# top of app, db this will raise a circular loop error
from .views import views
from .process_live import process
from .process_file import process_file

app.register_blueprint(views, url_prefix='/')
app.register_blueprint(process, url_prefix='/')
app.register_blueprint(process_file, url_prefix='/')

