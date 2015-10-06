#boilerplate
WTF_CSRF_ENABLED = True
SECRET_KEY = 'itsm0rphintim3'
#UPLOAD_FOLDER = UPLOAD_FOLDER

#boilerplate
import os
basedir = os.path.abspath(os.path.dirname(__file__))

#boilerplate
SQLALCHEMY_DATABASE_URI = 'sqlite:///' + os.path.join(basedir, 'app.db')
SQLALCHEMY_MIGRATE_REPO = os.path.join(basedir, 'db_repository')