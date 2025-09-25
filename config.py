class Config:
    SECRET_KEY="MY_SECRET_KEY"
    SQLALCHEMY_DATABASE_URI="mysql+mysqldb://root:toto@localhost/mini_lms_db"
    SQLALCHEMY_TRACK_MODIFICATIONS=False