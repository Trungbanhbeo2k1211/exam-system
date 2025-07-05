from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

db = SQLAlchemy()

# --- Account ---
class Account(db.Model):
    __tablename__ = 'Account'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True, nullable=False)
    password = db.Column(db.String(255), nullable=False)
    role = db.Column(db.String(10), nullable=False)  # 'admin' or 'student'

    answers = db.relationship('StudentAnswer', backref='student', lazy=True, cascade="all, delete-orphan")
    results = db.relationship('ExamResult', backref='student', lazy=True, cascade="all, delete-orphan")


# --- Exam ---
class Exam(db.Model):
    __tablename__ = 'Exam'
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.Unicode(100), nullable=False)
    description = db.Column(db.UnicodeText)
    duration = db.Column(db.Integer, nullable=False)  # in minutes
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    questions = db.relationship('Question', backref='exam', lazy=True, cascade="all, delete-orphan")
    results = db.relationship('ExamResult', backref='exam', lazy=True, cascade="all, delete-orphan")


# --- Question ---
class Question(db.Model):
    __tablename__ = 'Question'
    id = db.Column(db.Integer, primary_key=True)
    exam_id = db.Column(db.Integer, db.ForeignKey('Exam.id'), nullable=False)
    question_text = db.Column(db.UnicodeText, nullable=False)
    question_type = db.Column(db.Unicode(20), nullable=False)  # 'multiple_choice', 'fill_blank', 'true_false_multi', 'matching'

    choices = db.relationship('Choice', backref='question', lazy=True, cascade="all, delete-orphan")
    match_pairs = db.relationship('MatchPair', backref='question', lazy=True, cascade="all, delete-orphan")
    answers = db.relationship('StudentAnswer', backref='question', lazy=True, cascade="all, delete-orphan")


# --- Choice ---
class Choice(db.Model):
    __tablename__ = 'Choice'
    id = db.Column(db.Integer, primary_key=True)
    question_id = db.Column(db.Integer, db.ForeignKey('Question.id'), nullable=False)
    choice_text = db.Column(db.Unicode(255), nullable=False)
    is_correct = db.Column(db.Boolean, default=False)


# --- MatchPair (for matching questions) ---
class MatchPair(db.Model):
    __tablename__ = 'MatchPair'
    id = db.Column(db.Integer, primary_key=True)
    question_id = db.Column(db.Integer, db.ForeignKey('Question.id'), nullable=False)
    left_text = db.Column(db.Unicode(255), nullable=False)
    right_text = db.Column(db.Unicode(255), nullable=False)
    correct_pair = db.Column(db.Unicode(10))


# --- ExamResult ---
class ExamResult(db.Model):
    __tablename__ = 'ExamResult'
    id = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(db.Integer, db.ForeignKey('Account.id'), nullable=False)
    exam_id = db.Column(db.Integer, db.ForeignKey('Exam.id'), nullable=False)
    score = db.Column(db.Float)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)


# --- StudentAnswer ---
class StudentAnswer(db.Model):
    __tablename__ = 'StudentAnswer'
    id = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(db.Integer, db.ForeignKey('Account.id'), nullable=False)
    question_id = db.Column(db.Integer, db.ForeignKey('Question.id'), nullable=False)
    answer_text = db.Column(db.UnicodeText)
    is_correct = db.Column(db.Boolean, default=False)
    submitted_at = db.Column(db.DateTime, default=datetime.utcnow)
