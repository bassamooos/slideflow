#!/usr/bin/env python3
"""
Medical Laboratory Education Platform
منصة تعليم المختبرات الطبية

A comprehensive educational website for medical laboratory students
موقع تعليمي شامل لطلاب المختبرات الطبية
"""

from flask import Flask, render_template, request, jsonify, flash, redirect, url_for, session
import sqlite3
import os
import json
import hashlib
from datetime import datetime, timedelta
import logging

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)
app.secret_key = 'medical_lab_education_2024_secure_key'

# Configuration
app.config['DATABASE'] = os.path.join(os.path.dirname(__file__), 'medical_lab.db')
app.config['UPLOAD_FOLDER'] = os.path.join(os.path.dirname(__file__), 'uploads')

# Create necessary directories
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

def get_db():
    """Get database connection"""
    db = sqlite3.connect(app.config['DATABASE'])
    db.row_factory = sqlite3.Row
    return db

def init_database():
    """Initialize database with required tables"""
    db = get_db()
    
    # Users table
    db.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            email TEXT UNIQUE NOT NULL,
            password_hash TEXT NOT NULL,
            full_name TEXT NOT NULL,
            university TEXT,
            student_id TEXT,
            registration_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            last_login TIMESTAMP,
            is_active INTEGER DEFAULT 1,
            role TEXT DEFAULT 'student'
        )
    ''')
    
    # Courses table
    db.execute('''
        CREATE TABLE IF NOT EXISTS courses (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            title_ar TEXT NOT NULL,
            description TEXT NOT NULL,
            description_ar TEXT NOT NULL,
            category TEXT NOT NULL,
            difficulty_level TEXT DEFAULT 'beginner',
            duration_hours INTEGER DEFAULT 0,
            created_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            is_active INTEGER DEFAULT 1,
            thumbnail_url TEXT,
            instructor_id INTEGER,
            prerequisites TEXT,
            learning_objectives TEXT
        )
    ''')
    
    # Lessons table
    db.execute('''
        CREATE TABLE IF NOT EXISTS lessons (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            course_id INTEGER NOT NULL,
            title TEXT NOT NULL,
            title_ar TEXT NOT NULL,
            content TEXT NOT NULL,
            content_ar TEXT NOT NULL,
            lesson_order INTEGER NOT NULL,
            lesson_type TEXT DEFAULT 'theory',
            video_url TEXT,
            document_url TEXT,
            quiz_data TEXT,
            estimated_duration INTEGER DEFAULT 30,
            created_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            is_active INTEGER DEFAULT 1,
            FOREIGN KEY (course_id) REFERENCES courses (id)
        )
    ''')
    
    # User progress table
    db.execute('''
        CREATE TABLE IF NOT EXISTS user_progress (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            course_id INTEGER NOT NULL,
            lesson_id INTEGER,
            progress_percentage REAL DEFAULT 0,
            completion_date TIMESTAMP,
            last_accessed TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            quiz_score REAL DEFAULT 0,
            notes TEXT,
            FOREIGN KEY (user_id) REFERENCES users (id),
            FOREIGN KEY (course_id) REFERENCES courses (id),
            FOREIGN KEY (lesson_id) REFERENCES lessons (id)
        )
    ''')
    
    # Quiz results table
    db.execute('''
        CREATE TABLE IF NOT EXISTS quiz_results (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            lesson_id INTEGER NOT NULL,
            score REAL NOT NULL,
            total_questions INTEGER NOT NULL,
            correct_answers INTEGER NOT NULL,
            time_taken INTEGER,
            answers_json TEXT,
            completed_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users (id),
            FOREIGN KEY (lesson_id) REFERENCES lessons (id)
        )
    ''')
    
    # Discussions/Forums table
    db.execute('''
        CREATE TABLE IF NOT EXISTS discussions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            course_id INTEGER,
            lesson_id INTEGER,
            user_id INTEGER NOT NULL,
            title TEXT NOT NULL,
            content TEXT NOT NULL,
            parent_id INTEGER,
            created_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            likes_count INTEGER DEFAULT 0,
            is_resolved INTEGER DEFAULT 0,
            FOREIGN KEY (course_id) REFERENCES courses (id),
            FOREIGN KEY (lesson_id) REFERENCES lessons (id),
            FOREIGN KEY (user_id) REFERENCES users (id),
            FOREIGN KEY (parent_id) REFERENCES discussions (id)
        )
    ''')
    
    db.commit()
    
    # Insert sample data if tables are empty
    cursor = db.execute('SELECT COUNT(*) FROM courses')
    if cursor.fetchone()[0] == 0:
        insert_sample_data(db)
    
    db.close()

def insert_sample_data(db):
    """Insert sample educational data"""
    
    # Sample courses
    courses = [
        {
            'title': 'Clinical Chemistry Fundamentals',
            'title_ar': 'أساسيات الكيمياء الإكلينيكية',
            'description': 'Introduction to clinical chemistry principles and laboratory techniques',
            'description_ar': 'مقدمة في مبادئ الكيمياء الإكلينيكية وتقنيات المختبر',
            'category': 'chemistry',
            'difficulty_level': 'beginner',
            'duration_hours': 40,
            'prerequisites': '',
            'learning_objectives': 'Understanding basic chemistry principles, lab safety, analytical techniques'
        },
        {
            'title': 'Hematology and Blood Disorders',
            'title_ar': 'أمراض الدم والاضطرابات الدموية',
            'description': 'Comprehensive study of blood cells, disorders, and diagnostic techniques',
            'description_ar': 'دراسة شاملة لخلايا الدم والاضطرابات وتقنيات التشخيص',
            'category': 'hematology',
            'difficulty_level': 'intermediate',
            'duration_hours': 50,
            'prerequisites': 'Basic Biology, Anatomy',
            'learning_objectives': 'Blood cell identification, CBC interpretation, blood disorder diagnosis'
        },
        {
            'title': 'Microbiology and Infectious Diseases',
            'title_ar': 'علم الأحياء الدقيقة والأمراض المعدية',
            'description': 'Study of microorganisms and their role in human diseases',
            'description_ar': 'دراسة الكائنات الدقيقة ودورها في الأمراض البشرية',
            'category': 'microbiology',
            'difficulty_level': 'intermediate',
            'duration_hours': 60,
            'prerequisites': 'Basic Biology, Chemistry',
            'learning_objectives': 'Microorganism identification, culture techniques, antibiotic sensitivity'
        },
        {
            'title': 'Immunology and Serology',
            'title_ar': 'علم المناعة والأمصال',
            'description': 'Understanding immune system and serological testing methods',
            'description_ar': 'فهم جهاز المناعة وطرق الفحص المصلية',
            'category': 'immunology',
            'difficulty_level': 'advanced',
            'duration_hours': 45,
            'prerequisites': 'Microbiology, Basic Chemistry',
            'learning_objectives': 'Immune system function, antibody detection, serological tests'
        },
        {
            'title': 'Molecular Diagnostics',
            'title_ar': 'التشخيص الجزيئي',
            'description': 'Advanced molecular techniques for disease diagnosis',
            'description_ar': 'التقنيات الجزيئية المتقدمة لتشخيص الأمراض',
            'category': 'molecular',
            'difficulty_level': 'advanced',
            'duration_hours': 35,
            'prerequisites': 'Biochemistry, Genetics',
            'learning_objectives': 'PCR techniques, DNA sequencing, genetic testing'
        }
    ]
    
    for course in courses:
        db.execute('''
            INSERT INTO courses (title, title_ar, description, description_ar, 
                               category, difficulty_level, duration_hours, prerequisites, 
                               learning_objectives)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (course['title'], course['title_ar'], course['description'], 
              course['description_ar'], course['category'], course['difficulty_level'],
              course['duration_hours'], course['prerequisites'], course['learning_objectives']))
    
    # Sample lessons for the first course
    lessons = [
        {
            'course_id': 1,
            'title': 'Introduction to Clinical Chemistry',
            'title_ar': 'مقدمة في الكيمياء الإكلينيكية',
            'content': 'Clinical chemistry is the branch of laboratory medicine that deals with the analysis of bodily fluids...',
            'content_ar': 'الكيمياء الإكلينيكية هي فرع من طب المختبرات يتعامل مع تحليل سوائل الجسم...',
            'lesson_order': 1,
            'lesson_type': 'theory',
            'estimated_duration': 45
        },
        {
            'course_id': 1,
            'title': 'Laboratory Safety and Quality Control',
            'title_ar': 'سلامة المختبر ومراقبة الجودة',
            'content': 'Laboratory safety is paramount in clinical chemistry. This lesson covers safety protocols...',
            'content_ar': 'سلامة المختبر أمر بالغ الأهمية في الكيمياء الإكلينيكية. يغطي هذا الدرس بروتوكولات السلامة...',
            'lesson_order': 2,
            'lesson_type': 'practical',
            'estimated_duration': 60
        },
        {
            'course_id': 1,
            'title': 'Analytical Techniques and Instruments',
            'title_ar': 'التقنيات التحليلية والأجهزة',
            'content': 'Modern clinical laboratories use various analytical techniques and sophisticated instruments...',
            'content_ar': 'تستخدم المختبرات الإكلينيكية الحديثة تقنيات تحليلية مختلفة وأجهزة متطورة...',
            'lesson_order': 3,
            'lesson_type': 'theory',
            'estimated_duration': 50
        }
    ]
    
    for lesson in lessons:
        db.execute('''
            INSERT INTO lessons (course_id, title, title_ar, content, content_ar,
                               lesson_order, lesson_type, estimated_duration)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        ''', (lesson['course_id'], lesson['title'], lesson['title_ar'],
              lesson['content'], lesson['content_ar'], lesson['lesson_order'],
              lesson['lesson_type'], lesson['estimated_duration']))
    
    db.commit()

@app.route('/')
def index():
    """Main page - الصفحة الرئيسية"""
    db = get_db()
    
    # Get featured courses
    courses = db.execute('''
        SELECT * FROM courses WHERE is_active = 1 ORDER BY created_date DESC LIMIT 6
    ''').fetchall()
    
    # Get statistics
    stats = {
        'total_courses': db.execute('SELECT COUNT(*) FROM courses WHERE is_active = 1').fetchone()[0],
        'total_lessons': db.execute('SELECT COUNT(*) FROM lessons WHERE is_active = 1').fetchone()[0],
        'registered_users': db.execute('SELECT COUNT(*) FROM users WHERE is_active = 1').fetchone()[0],
        'active_discussions': db.execute('SELECT COUNT(*) FROM discussions').fetchone()[0]
    }
    
    db.close()
    
    return render_template('index.html', courses=courses, stats=stats)

@app.route('/courses')
def courses():
    """Courses listing page"""
    db = get_db()
    
    # Get filter parameters
    category = request.args.get('category', '')
    level = request.args.get('level', '')
    search = request.args.get('search', '')
    
    # Build query
    query = 'SELECT * FROM courses WHERE is_active = 1'
    params = []
    
    if category:
        query += ' AND category = ?'
        params.append(category)
    
    if level:
        query += ' AND difficulty_level = ?'
        params.append(level)
    
    if search:
        query += ' AND (title LIKE ? OR title_ar LIKE ? OR description LIKE ? OR description_ar LIKE ?)'
        search_term = f'%{search}%'
        params.extend([search_term, search_term, search_term, search_term])
    
    query += ' ORDER BY created_date DESC'
    
    all_courses = db.execute(query, params).fetchall()
    
    # Get categories for filter
    categories = db.execute('SELECT DISTINCT category FROM courses WHERE is_active = 1').fetchall()
    
    db.close()
    
    return render_template('courses/index.html', 
                         courses=all_courses, 
                         categories=categories,
                         current_category=category,
                         current_level=level,
                         current_search=search)

@app.route('/course/<int:course_id>')
def course_detail(course_id):
    """Course detail page"""
    db = get_db()
    
    # Get course details
    course = db.execute('SELECT * FROM courses WHERE id = ? AND is_active = 1', (course_id,)).fetchone()
    
    if not course:
        flash('الدورة غير موجودة', 'error')
        return redirect(url_for('courses'))
    
    # Get course lessons
    lessons = db.execute('''
        SELECT * FROM lessons 
        WHERE course_id = ? AND is_active = 1 
        ORDER BY lesson_order
    ''', (course_id,)).fetchall()
    
    # Get user progress if logged in
    user_progress = None
    if 'user_id' in session:
        user_progress = db.execute('''
            SELECT * FROM user_progress 
            WHERE user_id = ? AND course_id = ?
        ''', (session['user_id'], course_id)).fetchone()
    
    db.close()
    
    return render_template('courses/detail.html', 
                         course=course, 
                         lessons=lessons,
                         user_progress=user_progress)

@app.route('/lesson/<int:lesson_id>')
def lesson_detail(lesson_id):
    """Lesson detail page"""
    if 'user_id' not in session:
        flash('يرجى تسجيل الدخول أولاً', 'error')
        return redirect(url_for('login'))
    
    db = get_db()
    
    # Get lesson with course info
    lesson = db.execute('''
        SELECT l.*, c.title as course_title, c.title_ar as course_title_ar
        FROM lessons l
        JOIN courses c ON l.course_id = c.id
        WHERE l.id = ? AND l.is_active = 1
    ''', (lesson_id,)).fetchone()
    
    if not lesson:
        flash('الدرس غير موجود', 'error')
        return redirect(url_for('courses'))
    
    # Update user progress
    db.execute('''
        INSERT OR REPLACE INTO user_progress 
        (user_id, course_id, lesson_id, last_accessed)
        VALUES (?, ?, ?, ?)
    ''', (session['user_id'], lesson['course_id'], lesson_id, datetime.now()))
    
    db.commit()
    db.close()
    
    return render_template('lessons/detail.html', lesson=lesson)

@app.route('/register', methods=['GET', 'POST'])
def register():
    """User registration"""
    if request.method == 'POST':
        username = request.form.get('username')
        email = request.form.get('email')
        password = request.form.get('password')
        full_name = request.form.get('full_name')
        university = request.form.get('university', '')
        student_id = request.form.get('student_id', '')
        
        if not all([username, email, password, full_name]):
            flash('جميع الحقول مطلوبة', 'error')
            return render_template('auth/register.html')
        
        # Hash password
        password_hash = hashlib.sha256(password.encode()).hexdigest()
        
        db = get_db()
        
        try:
            db.execute('''
                INSERT INTO users (username, email, password_hash, full_name, 
                                 university, student_id)
                VALUES (?, ?, ?, ?, ?, ?)
            ''', (username, email, password_hash, full_name, university, student_id))
            db.commit()
            
            flash('تم التسجيل بنجاح! يمكنك الآن تسجيل الدخول', 'success')
            return redirect(url_for('login'))
            
        except sqlite3.IntegrityError:
            flash('اسم المستخدم أو البريد الإلكتروني مستخدم بالفعل', 'error')
        finally:
            db.close()
    
    return render_template('auth/register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    """User login"""
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        
        if not username or not password:
            flash('يرجى إدخال اسم المستخدم وكلمة المرور', 'error')
            return render_template('auth/login.html')
        
        password_hash = hashlib.sha256(password.encode()).hexdigest()
        
        db = get_db()
        user = db.execute('''
            SELECT * FROM users 
            WHERE username = ? AND password_hash = ? AND is_active = 1
        ''', (username, password_hash)).fetchone()
        
        if user:
            session['user_id'] = user['id']
            session['username'] = user['username']
            session['full_name'] = user['full_name']
            
            # Update last login
            db.execute('UPDATE users SET last_login = ? WHERE id = ?', 
                      (datetime.now(), user['id']))
            db.commit()
            
            flash(f'مرحباً بك {user["full_name"]}!', 'success')
            return redirect(url_for('dashboard'))
        else:
            flash('اسم المستخدم أو كلمة المرور غير صحيحة', 'error')
        
        db.close()
    
    return render_template('auth/login.html')

@app.route('/logout')
def logout():
    """User logout"""
    session.clear()
    flash('تم تسجيل الخروج بنجاح', 'success')
    return redirect(url_for('index'))

@app.route('/dashboard')
def dashboard():
    """User dashboard"""
    if 'user_id' not in session:
        flash('يرجى تسجيل الدخول أولاً', 'error')
        return redirect(url_for('login'))
    
    db = get_db()
    
    # Get user's enrolled courses
    enrolled_courses = db.execute('''
        SELECT DISTINCT c.*, 
               AVG(up.progress_percentage) as avg_progress,
               COUNT(l.id) as total_lessons,
               COUNT(CASE WHEN up.completion_date IS NOT NULL THEN 1 END) as completed_lessons
        FROM courses c
        JOIN user_progress up ON c.id = up.course_id
        LEFT JOIN lessons l ON c.id = l.course_id AND l.is_active = 1
        WHERE up.user_id = ?
        GROUP BY c.id
        ORDER BY up.last_accessed DESC
    ''', (session['user_id'],)).fetchall()
    
    # Get recent activity
    recent_activity = db.execute('''
        SELECT l.title, l.title_ar, c.title as course_title, 
               c.title_ar as course_title_ar, up.last_accessed
        FROM user_progress up
        JOIN lessons l ON up.lesson_id = l.id
        JOIN courses c ON l.course_id = c.id
        WHERE up.user_id = ? AND up.lesson_id IS NOT NULL
        ORDER BY up.last_accessed DESC
        LIMIT 5
    ''', (session['user_id'],)).fetchall()
    
    db.close()
    
    return render_template('dashboard.html', 
                         enrolled_courses=enrolled_courses,
                         recent_activity=recent_activity)

# API Routes
@app.route('/api/enroll', methods=['POST'])
def api_enroll():
    """Enroll in a course"""
    if 'user_id' not in session:
        return jsonify({'error': 'غير مسجل'}), 401
    
    course_id = request.json.get('course_id')
    
    if not course_id:
        return jsonify({'error': 'معرف الدورة مطلوب'}), 400
    
    db = get_db()
    
    # Check if already enrolled
    existing = db.execute('''
        SELECT id FROM user_progress 
        WHERE user_id = ? AND course_id = ?
    ''', (session['user_id'], course_id)).fetchone()
    
    if existing:
        return jsonify({'message': 'مسجل بالفعل في هذه الدورة'}), 200
    
    # Enroll user
    db.execute('''
        INSERT INTO user_progress (user_id, course_id, progress_percentage)
        VALUES (?, ?, 0)
    ''', (session['user_id'], course_id))
    
    db.commit()
    db.close()
    
    return jsonify({'message': 'تم التسجيل في الدورة بنجاح'})

# Initialize database on startup
init_database()

if __name__ == '__main__':
    print("🏥 Medical Laboratory Education Platform Starting...")
    print("🎓 منصة تعليم المختبرات الطبية تبدأ...")
    print(f"📁 Working directory: {os.getcwd()}")
    print(f"💾 Database: {app.config['DATABASE']}")
    
    app.run(host='0.0.0.0', port=3000, debug=True)