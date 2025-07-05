from flask import Blueprint, render_template, request, redirect, url_for, session
from models import db, Exam
from models import Exam, Question

admin_bp = Blueprint('admin', __name__, url_prefix='/admin')

@admin_bp.route('/')
def dashboard():
    exams = Exam.query.all()
    return render_template('admin/dashboard.html', exams=exams)

@admin_bp.route('/create-exam', methods=['GET', 'POST'])
def create_exam():
    # Kiểm tra quyền admin
    if 'role' not in session or session['role'] != 'admin':
        return redirect(url_for('auth.login'))

    if request.method == 'POST':
        title = request.form['title'].strip()
        description = request.form['description'].strip()
        duration = request.form['duration']

        if not title or not duration:
            return render_template('admin/create_exam.html', error="Vui lòng nhập đủ tiêu đề và thời gian")

        try:
            duration = int(duration)
        except ValueError:
            return render_template('admin/create_exam.html', error="Thời gian phải là số nguyên")

        # Lưu vào DB
        exam = Exam(title=title, description=description, duration=duration)
        db.session.add(exam)
        db.session.commit()

        return render_template('admin/create_exam.html', success="Tạo đề thi thành công!")

    return render_template('admin/create_exam.html')


# Add question
from models import Question, Choice, MatchPair

@admin_bp.route('/add-question/<int:exam_id>', methods=['GET', 'POST'])
def add_question(exam_id):
    if 'role' not in session or session['role'] != 'admin':
        return redirect(url_for('auth.login'))

    if request.method == 'POST':
        q_text = request.form['question_text'].strip()
        q_type = request.form['question_type']

        if not q_text or not q_type:
            return render_template('admin/add_question.html', exam_id=exam_id, error="Thiếu nội dung hoặc loại câu hỏi")

        question = Question(exam_id=exam_id, question_text=q_text, question_type=q_type)
        db.session.add(question)
        db.session.flush()  # Lấy question.id trước khi commit

        if q_type == 'multiple_choice':
            choices = {
                'a': request.form.get('choice_a'),
                'b': request.form.get('choice_b'),
                'c': request.form.get('choice_c'),
                'd': request.form.get('choice_d'),
            }
            correct = request.form.get('correct_choice')
            for key, text in choices.items():
                if text:
                    c = Choice(question_id=question.id, choice_text=text, is_correct=(key == correct))
                    db.session.add(c)

        elif q_type == 'true_false_multi':
            statements = request.form.get('statements', '').splitlines()
            for stmt in statements:
                parts = stmt.split("::")
                if len(parts) == 2:
                    text, tf = parts
                    is_correct = tf.strip().lower() == "true"
                    c = Choice(question_id=question.id, choice_text=text.strip(), is_correct=is_correct)
                    db.session.add(c)

        elif q_type == 'fill_blank':
            answer = request.form.get('fill_answer', '').strip()
            if answer:
                c = Choice(question_id=question.id, choice_text=answer, is_correct=True)
                db.session.add(c)

        elif q_type == 'matching':
            pairs = request.form.get('match_pairs', '').splitlines()
            for pair in pairs:
                parts = pair.split("::")
                if len(parts) == 2:
                    left, right = parts
                    m = MatchPair(question_id=question.id, left_text=left.strip(), right_text=right.strip())
                    db.session.add(m)

        db.session.commit()
        return render_template('admin/add_question.html', exam_id=exam_id, success="Thêm câu hỏi thành công")

    return render_template('admin/add_question.html', exam_id=exam_id)

# Xem danh sách câu hỏi
@admin_bp.route('/exam/<int:exam_id>/questions')
def view_questions(exam_id):
    if 'role' not in session or session['role'] != 'admin':
        return redirect(url_for('auth.login'))

    exam = Exam.query.get_or_404(exam_id)
    questions = Question.query.filter_by(exam_id=exam_id).all()

    return render_template('admin/view_questions.html', exam=exam, questions=questions)

# Sửa/xóa
@admin_bp.route('/edit-exam/<int:exam_id>', methods=['GET', 'POST'])
def edit_exam(exam_id):
    exam = Exam.query.get_or_404(exam_id)

    if request.method == 'POST':
        exam.title = request.form['title']
        exam.description = request.form['description']
        exam.duration = request.form['duration']
        db.session.commit()
        return redirect(url_for('admin.dashboard'))

    return render_template('admin/edit_exam.html', exam=exam)

@admin_bp.route('/delete-exam/<int:exam_id>')
def delete_exam(exam_id):
    exam = Exam.query.get_or_404(exam_id)
    db.session.delete(exam)
    db.session.commit()
    return redirect(url_for('admin.dashboard'))


# Sửa/ Xóa câu hỏi
@admin_bp.route('/edit-question/<int:question_id>', methods=['GET', 'POST'])
def edit_question(question_id):
    question = Question.query.get_or_404(question_id)

    if request.method == 'POST':
        question.question_text = request.form['question_text']
        db.session.commit()
        return redirect(url_for('admin.view_questions', exam_id=question.exam_id))

    return render_template('admin/edit_question.html', question=question)

@admin_bp.route('/delete-question/<int:question_id>/<int:exam_id>')
def delete_question(question_id, exam_id):
    question = Question.query.get_or_404(question_id)
    db.session.delete(question)
    db.session.commit()
    return redirect(url_for('admin.view_questions', exam_id=exam_id))
