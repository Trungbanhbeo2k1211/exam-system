from flask import Flask
from config import SQLALCHEMY_DATABASE_URI, SQLALCHEMY_TRACK_MODIFICATIONS
from models import db
from routes.auth_routes import auth_bp
from routes.admin_routes import admin_bp
from routes.exam_routes import exam_bp
from models import Account
from routes.student_routes import student_bp
from flask import Flask, render_template


app = Flask(__name__)
app.secret_key = 'secret-key-thi-online'
app.config['SQLALCHEMY_DATABASE_URI'] = SQLALCHEMY_DATABASE_URI
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = SQLALCHEMY_TRACK_MODIFICATIONS

db.init_app(app)

# Đăng ký blueprint
app.register_blueprint(auth_bp)
app.register_blueprint(admin_bp)
app.register_blueprint(exam_bp)
app.register_blueprint(student_bp)

# Tạo DB nếu chưa có
with app.app_context():
    db.create_all()

@app.route('/')
def home():
    return render_template('home.html')

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8000, debug=True)
