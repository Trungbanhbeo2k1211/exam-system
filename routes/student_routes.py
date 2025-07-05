from flask import Blueprint, render_template, request, redirect, url_for, session
from models import db, Exam
from models import Exam, Question
from models import StudentAnswer
from models import ExamResult
from flask import jsonify, request
from models import Choice, MatchPair

student_bp = Blueprint('student', __name__, url_prefix='/student')

@student_bp.route('/exam/')
def exam_list():
    if 'role' not in session or session['role'] != 'student':
        return redirect(url_for('auth.login'))

    exams = Exam.query.all()
    return render_template('student/exam_list.html', exams=exams)



@student_bp.route('/exam/<int:exam_id>/take')
def take_exam(exam_id):
    if 'role' not in session or session['role'] != 'student':
        return redirect(url_for('auth.login'))

    exam = Exam.query.get_or_404(exam_id)
    questions = Question.query.filter_by(exam_id=exam_id).all()
    return render_template('student/take_exam.html', exam=exam, questions=questions)


@student_bp.route('/exam/<int:exam_id>/submit', methods=['POST'])
def submit_exam(exam_id):
    if 'role' not in session or session['role'] != 'student':
        return redirect(url_for('auth.login'))

    user_id = session['user_id']
    questions = Question.query.filter_by(exam_id=exam_id).all()
    total = len(questions)
    correct = 0

    for q in questions:
        key = f'q_{q.id}'
        user_input = ""
        is_correct = False

        if q.question_type in ['multiple_choice', 'true_false_multi']:
            selected = request.form.getlist(key)
            user_input = str(selected)
            correct_choices = [str(c.id) for c in q.choices if c.is_correct]
            if sorted(selected) == sorted(correct_choices):
                correct += 1
                is_correct = True

        elif q.question_type == 'fill_blank':
            answer = request.form.get(key, '').strip().lower()
            correct_answer = q.choices[0].choice_text.strip().lower()
            user_input = answer
            if answer == correct_answer:
                correct += 1
                is_correct = True

        elif q.question_type == 'matching':
            pairs = []
            all_correct = True
            for i, m in enumerate(q.match_pairs, start=1):
                ans = request.form.get(f'{key}_{i}', '').strip().lower()
                pairs.append(f'{m.left_text}-{ans}')
                if ans != m.right_text.strip().lower():
                    all_correct = False
            user_input = str(pairs)
            if all_correct:
                correct += 1
                is_correct = True

        # Lưu từng câu trả lời
        student_answer = StudentAnswer(
            student_id=user_id,
            question_id=q.id,
            answer_text=user_input,
            is_correct=is_correct
        )
        db.session.add(student_answer)

    score = round((correct / total) * 10, 2)

    # Lưu kết quả tổng
    result = ExamResult(
        student_id=user_id,
        exam_id=exam_id,
        score=score
    )
    db.session.add(result)
    db.session.commit()

    return render_template('student/exam_result.html', correct=correct, total=total, score=score)


@student_bp.route('/exam/history')
def exam_history():
    if 'role' not in session or session['role'] != 'student':
        return redirect(url_for('auth.login'))

    student_id = session['user_id']
    results = ExamResult.query.filter_by(student_id=student_id).order_by(ExamResult.timestamp.desc()).all()
    return render_template('student/exam_history.html', results=results)


# check kq
from flask import jsonify

# @student_bp.route('/check_answer', methods=['POST'])
# def check_answer():
#     data = request.get_json()
#     qid = data.get('question_id')
#     qtype = data.get('type')
#     question = Question.query.get(qid)

#     if not question:
#         return jsonify({"error": "Câu hỏi không tồn tại"}), 404

#     if qtype == 'multiple_choice':
#         choice_id = int(data.get('choice_id'))
#         choice = Choice.query.get(choice_id)
#         return jsonify({
#             "correct": choice.is_correct,
#             "correct_text": next((c.choice_text for c in question.choices if c.is_correct), "Không rõ")
#         })

#     elif qtype == 'fill_blank':
#         answer = data.get('answer', '').strip().lower()
#         correct_answer = question.choices[0].choice_text.strip().lower()
#         return jsonify({
#             "correct": answer == correct_answer,
#             "correct_text": question.choices[0].choice_text
#         })

#     elif qtype == 'matching':
#         left = data.get('left_text', '').strip().lower()
#         user_input = data.get('user_input', '').strip().lower()
#         pair = next((m for m in question.match_pairs if m.left_text.strip().lower() == left), None)

#         if not pair:
#             return jsonify({"correct": False, "correct_text": "Không tìm thấy cặp"})

#         return jsonify({
#             "correct": user_input == pair.right_text.strip().lower(),
#             "correct_text": pair.right_text
#         })

#     return jsonify({"error": "Loại câu hỏi không hỗ trợ"}), 400

@student_bp.route('/check_answer', methods=['POST'])
def check_answer():
    data = request.get_json()
    qid = data.get('question_id')
    qtype = data.get('type')
    question = Question.query.get(qid)

    if not question:
        return jsonify({"error": "Câu hỏi không tồn tại"}), 404

    # 🎯 1. Trắc nghiệm 1 đáp án đúng (radio)
    if qtype == 'multiple_choice':
        choice_id = int(data.get('choice_id'))
        choice = Choice.query.get(choice_id)
        return jsonify({
            "correct": choice.is_correct,
            "correct_text": next((c.choice_text for c in question.choices if c.is_correct), "Không rõ")
        })

    # 📝 2. Điền vào chỗ trống
    elif qtype == 'fill_blank':
        answer = data.get('answer', '').strip().lower()
        correct_answer = question.choices[0].choice_text.strip().lower()
        return jsonify({
            "correct": answer == correct_answer,
            "correct_text": question.choices[0].choice_text
        })

    # 🔁 3. Ghép nối
    elif qtype == 'matching':
        left = data.get('left_text', '').strip().lower()
        user_input = data.get('user_input', '').strip().lower()
        pair = next((m for m in question.match_pairs if m.left_text.strip().lower() == left), None)

        if not pair:
            return jsonify({"correct": False, "correct_text": "Không tìm thấy cặp"})

        return jsonify({
            "correct": user_input == pair.right_text.strip().lower(),
            "correct_text": pair.right_text
        })

    # ✅ 4. Đúng/Sai nhiều mục (checkbox): phải chọn đủ và không chọn nhầm
    elif qtype == 'true_false_multi':
        selected_ids = set(map(int, data.get('choice_ids', [])))
        correct_choices = {c.id for c in question.choices if c.is_correct}
        wrong_choices = {c.id for c in question.choices if not c.is_correct}

        if selected_ids == correct_choices:
            return jsonify({"correct": True})
        else:
            return jsonify({
                "correct": False,
                "correct_choices": [c.choice_text for c in question.choices if c.is_correct]
            })

    return jsonify({"error": "Loại câu hỏi không hỗ trợ"}), 400
