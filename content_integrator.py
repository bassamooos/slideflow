#!/usr/bin/env python3
"""
Content Integrator for Medical Lab Education Platform
مدمج المحتوى لمنصة تعليم المختبرات الطبية

Integrate extracted Slideflow content into the medical education database
دمج محتوى Slideflow المستخرج في قاعدة بيانات التعليم الطبي
"""

import json
import sqlite3
import os
from datetime import datetime
from pathlib import Path

class ContentIntegrator:
    """Integrate extracted content into the education platform"""
    
    def __init__(self, database_path="/home/user/webapp/medical_lab_education/medical_lab.db",
                 content_path="/home/user/webapp/slideflow_source"):
        self.database_path = database_path
        self.content_path = Path(content_path)
        
    def integrate_all_content(self):
        """Main integration method"""
        print("🔗 بدء تكامل المحتوى مع منصة التعليم...")
        print("🔗 Starting content integration with education platform...")
        
        # Load extraction metadata
        metadata_file = self.content_path / "extraction_metadata.json"
        if not metadata_file.exists():
            print("❌ ملف البيانات الوصفية غير موجود")
            return False
        
        with open(metadata_file, 'r', encoding='utf-8') as f:
            extracted_content = json.load(f)
        
        # Connect to database
        conn = sqlite3.connect(self.database_path)
        
        try:
            # Create Slideflow-specific course
            slideflow_course_id = self.create_slideflow_course(conn)
            
            # Integrate tutorials as lessons
            self.integrate_tutorials(conn, slideflow_course_id, extracted_content['tutorials'])
            
            # Create additional courses from documentation
            self.create_documentation_courses(conn, extracted_content['documentation'])
            
            # Add practical coding exercises
            self.add_code_examples(conn, extracted_content['code_examples'])
            
            conn.commit()
            print("✅ تم تكامل المحتوى بنجاح")
            print("✅ Content integration completed successfully")
            
            return True
            
        except Exception as e:
            print(f"❌ خطأ في التكامل: {e}")
            conn.rollback()
            return False
        finally:
            conn.close()
    
    def create_slideflow_course(self, conn):
        """Create main Slideflow course"""
        cursor = conn.cursor()
        
        # Check if Slideflow course already exists
        cursor.execute("SELECT id FROM courses WHERE title = ?", ("Slideflow Digital Pathology",))
        existing = cursor.fetchone()
        
        if existing:
            print("ℹ️ دورة Slideflow موجودة بالفعل")
            return existing[0]
        
        # Create new Slideflow course
        cursor.execute('''
            INSERT INTO courses (title, title_ar, description, description_ar, 
                               category, difficulty_level, duration_hours, 
                               prerequisites, learning_objectives)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            "Slideflow Digital Pathology",
            "Slideflow لعلم الأمراض الرقمية", 
            "Comprehensive course on digital pathology using Slideflow framework for AI-powered medical analysis",
            "دورة شاملة في علم الأمراض الرقمية باستخدام إطار عمل Slideflow للتحليل الطبي المدعوم بالذكاء الاصطناعي",
            "molecular",
            "advanced", 
            80,
            "Python programming, Basic machine learning, Medical terminology",
            "Master Slideflow framework, Develop AI models for pathology, Analyze medical images, Create diagnostic tools"
        ))
        
        course_id = cursor.lastrowid
        print(f"✓ تم إنشاء دورة Slideflow (ID: {course_id})")
        
        return course_id
    
    def integrate_tutorials(self, conn, course_id, tutorials):
        """Integrate tutorials as lessons"""
        cursor = conn.cursor()
        
        print("📚 إدراج الدروس التعليمية...")
        
        lesson_order = 1
        for tutorial_key, tutorial_data in tutorials.items():
            # Read tutorial content
            tutorial_file = self.content_path / "tutorials" / f"{tutorial_key}.rst"
            
            content = ""
            content_ar = ""
            
            if tutorial_file.exists():
                with open(tutorial_file, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                # Generate Arabic summary
                content_ar = self.generate_arabic_summary(tutorial_data['title'], content)
            
            # Insert lesson
            cursor.execute('''
                INSERT INTO lessons (course_id, title, title_ar, content, content_ar,
                                   lesson_order, lesson_type, estimated_duration, quiz_data)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                course_id,
                tutorial_data['title'],
                tutorial_data['title_ar'],
                content,
                content_ar,
                lesson_order,
                'practical' if 'code' in content.lower() else 'theory',
                self.estimate_duration(tutorial_data['word_count']),
                json.dumps(self.generate_quiz_questions(tutorial_data['title']))
            ))
            
            print(f"  ✓ {tutorial_data['title']}")
            lesson_order += 1
    
    def create_documentation_courses(self, conn, documentation):
        """Create courses from documentation"""
        cursor = conn.cursor()
        
        print("📖 إنشاء دورات من الوثائق...")
        
        # Group documentation by topic
        doc_groups = {
            'setup': ['installation', 'project_setup', 'overview'],
            'processing': ['slide_processing', 'dataset', 'features'],
            'modeling': ['model', 'training', 'evaluation']
        }
        
        for group_name, doc_keys in doc_groups.items():
            # Create course for this group
            group_info = self.get_group_info(group_name)
            
            cursor.execute('''
                INSERT INTO courses (title, title_ar, description, description_ar, 
                                   category, difficulty_level, duration_hours)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            ''', (
                group_info['title'],
                group_info['title_ar'],
                group_info['description'],
                group_info['description_ar'],
                'molecular',
                group_info['difficulty'],
                group_info['duration']
            ))
            
            course_id = cursor.lastrowid
            
            # Add documentation as lessons
            lesson_order = 1
            for doc_key in doc_keys:
                if doc_key in documentation:
                    doc_data = documentation[doc_key]
                    
                    # Read documentation content
                    doc_file = self.content_path / "documentation" / f"{doc_key}.rst"
                    
                    content = ""
                    if doc_file.exists():
                        with open(doc_file, 'r', encoding='utf-8') as f:
                            content = f.read()
                    
                    content_ar = self.generate_arabic_summary(doc_data['title'], content)
                    
                    cursor.execute('''
                        INSERT INTO lessons (course_id, title, title_ar, content, content_ar,
                                           lesson_order, lesson_type, estimated_duration)
                        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                    ''', (
                        course_id,
                        doc_data['title'],
                        doc_data['title_ar'],
                        content,
                        content_ar,
                        lesson_order,
                        'theory',
                        self.estimate_duration(doc_data['word_count'])
                    ))
                    
                    lesson_order += 1
            
            print(f"  ✓ {group_info['title']}")
    
    def add_code_examples(self, conn, code_examples):
        """Add code examples as practical lessons"""
        cursor = conn.cursor()
        
        print("💻 إضافة أمثلة الكود...")
        
        # Create a practical coding course
        cursor.execute('''
            INSERT INTO courses (title, title_ar, description, description_ar, 
                               category, difficulty_level, duration_hours)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', (
            "Slideflow Practical Coding",
            "البرمجة العملية لـ Slideflow",
            "Hands-on coding exercises and examples using Slideflow",
            "تمارين وأمثلة برمجية عملية باستخدام Slideflow",
            "molecular",
            "intermediate",
            30
        ))
        
        course_id = cursor.lastrowid
        
        # Add representative code examples as lessons
        example_count = 0
        lesson_order = 1
        
        for code_path, code_data in code_examples.items():
            if example_count < 10:  # Limit to 10 examples
                # Read code content
                full_path = self.content_path / "code_examples" / code_path
                
                content = ""
                if full_path.exists():
                    with open(full_path, 'r', encoding='utf-8') as f:
                        content = f.read()
                
                # Create lesson title from file path
                lesson_title = f"Code Example: {Path(code_path).stem.replace('_', ' ').title()}"
                lesson_title_ar = f"مثال برمجي: {Path(code_path).stem.replace('_', ' ')}"
                
                content_ar = f"""
مثال برمجي عملي من Slideflow
هذا المثال يوضح كيفية استخدام مكتبة Slideflow في التطبيقات العملية

الوصف: {code_data.get('docstring', 'مثال برمجي')}
عدد الدوال: {code_data.get('functions_count', 0)}
عدد الفئات: {code_data.get('classes_count', 0)}
عدد الأسطر: {code_data.get('lines_count', 0)}
"""
                
                cursor.execute('''
                    INSERT INTO lessons (course_id, title, title_ar, content, content_ar,
                                       lesson_order, lesson_type, estimated_duration)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                ''', (
                    course_id,
                    lesson_title,
                    lesson_title_ar,
                    content,
                    content_ar,
                    lesson_order,
                    'practical',
                    45
                ))
                
                lesson_order += 1
                example_count += 1
        
        print(f"  ✓ تم إضافة {example_count} مثال برمجي")
    
    def generate_arabic_summary(self, title, content):
        """Generate Arabic summary of English content"""
        # Simple content analysis and Arabic summary generation
        lines = content.split('\n')
        
        summary_lines = [
            "ملخص المحتوى:",
            "=" * 20,
            f"العنوان: {title}",
            f"تاريخ المعالجة: {datetime.now().strftime('%Y-%m-%d')}",
            "",
            "هذا المحتوى جزء من مكتبة Slideflow لعلم الأمراض الرقمية",
            "يتضمن شرحاً تفصيلياً للمفاهيم والتطبيقات العملية",
            "",
            "المحتوى الأصلي (باللغة الإنجليزية):",
            "-" * 40
        ]
        
        return '\n'.join(summary_lines) + '\n\n' + content
    
    def estimate_duration(self, word_count):
        """Estimate lesson duration based on word count"""
        # Assume 200 words per minute reading speed
        reading_minutes = word_count / 200
        
        # Add time for exercises and reflection
        total_minutes = reading_minutes * 1.5
        
        return max(15, min(120, int(total_minutes)))
    
    def generate_quiz_questions(self, title):
        """Generate simple quiz questions based on title"""
        questions = [
            {
                "question": f"What is the main topic of '{title}'?",
                "question_ar": f"ما هو الموضوع الرئيسي لـ '{title}'؟",
                "options": [
                    "Digital pathology",
                    "Basic programming", 
                    "Database design",
                    "Web development"
                ],
                "correct_answer": 0
            },
            {
                "question": "Which framework is being discussed?",
                "question_ar": "ما هو الإطار المناقش؟",
                "options": [
                    "TensorFlow",
                    "PyTorch", 
                    "Slideflow",
                    "Scikit-learn"
                ],
                "correct_answer": 2
            }
        ]
        
        return questions
    
    def get_group_info(self, group_name):
        """Get information for documentation groups"""
        groups = {
            'setup': {
                'title': 'Slideflow Setup and Configuration',
                'title_ar': 'إعداد وتكوين Slideflow',
                'description': 'Learn how to install and configure Slideflow for digital pathology',
                'description_ar': 'تعلم كيفية تثبيت وتكوين Slideflow لعلم الأمراض الرقمية',
                'difficulty': 'beginner',
                'duration': 20
            },
            'processing': {
                'title': 'Data Processing and Feature Extraction',
                'title_ar': 'معالجة البيانات واستخراج الميزات',
                'description': 'Master data processing techniques and feature extraction methods',
                'description_ar': 'إتقان تقنيات معالجة البيانات وطرق استخراج الميزات',
                'difficulty': 'intermediate',
                'duration': 35
            },
            'modeling': {
                'title': 'Model Development and Evaluation',
                'title_ar': 'تطوير النماذج والتقييم',
                'description': 'Build, train, and evaluate machine learning models for pathology',
                'description_ar': 'بناء وتدريب وتقييم نماذج التعلم الآلي لعلم الأمراض',
                'difficulty': 'advanced',
                'duration': 45
            }
        }
        
        return groups.get(group_name, groups['setup'])

def main():
    """Main execution function"""
    print("🔗 Content Integrator for Medical Lab Education")
    print("🔗 مدمج المحتوى لمنصة تعليم المختبرات الطبية")
    print("=" * 60)
    
    integrator = ContentIntegrator()
    success = integrator.integrate_all_content()
    
    if success:
        print("\n🎉 تم التكامل بنجاح!")
        print("🎉 Integration completed successfully!")
        print("\nيمكنك الآن الوصول إلى المحتوى من خلال منصة التعليم")
        print("You can now access the content through the education platform")
    else:
        print("\n❌ فشل التكامل")
        print("❌ Integration failed")

if __name__ == "__main__":
    main()