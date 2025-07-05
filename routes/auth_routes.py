from flask import Blueprint, render_template, request, redirect, session, url_for
from models import db, Account

auth_bp = Blueprint('auth', __name__, url_prefix='/auth')

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username'].strip()
        password = request.form['password'].strip()

        user = Account.query.filter_by(username=username, password=password).first()

        if user:
            session['user_id'] = user.id
            session['username'] = user.username
            session['role'] = user.role

            if user.role == 'admin':
                return redirect('/admin/')
            else:
                return redirect('/exam/')
        else:
            return render_template('login.html', error="Sai tên đăng nhập hoặc mật khẩu!")

    return render_template('login.html')

@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username'].strip()
        password = request.form['password'].strip()
        confirm = request.form['confirm'].strip()

        # Kiểm tra mật khẩu khớp
        if password != confirm:
            return render_template('register.html', error="Mật khẩu không khớp")

        # Kiểm tra tên đăng nhập đã tồn tại chưa
        if Account.query.filter_by(username=username).first():
            return render_template('register.html', error="Tên đăng nhập đã tồn tại")

        # Tạo tài khoản mới
        new_user = Account(username=username, password=password, role='student')
        db.session.add(new_user)
        db.session.commit()

        return render_template('register.html', success="Đăng ký thành công! Hãy đăng nhập.")
    
    return render_template('register.html')
