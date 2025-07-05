from flask import Blueprint, render_template, session, redirect, url_for
from models import Exam  # Giả sử bạn đã có model Exam

exam_bp = Blueprint('exam', __name__, url_prefix='/exam')

@exam_bp.route('/')
def exam_list():
    # ✅ Kiểm tra đăng nhập và vai trò
    if 'role' not in session or session['role'] != 'student':
        return redirect(url_for('auth.login'))

    # ✅ Lấy tất cả đề thi
    exams = Exam.query.all()

    # ✅ Render template hiển thị
    return render_template('student/exam_list.html', exams=exams)
