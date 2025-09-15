#!/usr/bin/env python3
"""
Slideflow Content Extractor and Organizer
مستخرج ومنظم محتوى Slideflow

Extract, organize, and store all Slideflow educational content for the medical lab platform
استخراج وتنظيم وحفظ جميع المحتوى التعليمي لـ Slideflow لمنصة المختبرات الطبية
"""

import os
import json
import shutil
from pathlib import Path
import re
from datetime import datetime

class SlideflowContentExtractor:
    """Extract and organize Slideflow educational content"""
    
    def __init__(self, source_dir="/home/user/webapp", output_dir="/home/user/webapp/slideflow_source"):
        self.source_dir = Path(source_dir)
        self.output_dir = Path(output_dir)
        self.extracted_content = {
            'tutorials': {},
            'documentation': {},
            'code_examples': {},
            'metadata': {
                'extraction_date': datetime.now().isoformat(),
                'total_files': 0,
                'categories': {}
            }
        }
    
    def extract_all_content(self):
        """Main extraction method"""
        print("🔬 بدء استخراج محتوى Slideflow...")
        print("🔬 Starting Slideflow content extraction...")
        
        # Create output directory
        self.output_dir.mkdir(exist_ok=True)
        
        # Extract different types of content
        self.extract_tutorials()
        self.extract_documentation()
        self.extract_code_examples()
        self.extract_configuration_files()
        
        # Save metadata
        self.save_extracted_content()
        
        print(f"✅ تم استخراج {self.extracted_content['metadata']['total_files']} ملف")
        print(f"✅ Extracted {self.extracted_content['metadata']['total_files']} files")
        
        return self.extracted_content
    
    def extract_tutorials(self):
        """Extract tutorial files"""
        print("📚 استخراج الدروس التعليمية...")
        
        tutorials_dir = self.output_dir / "tutorials"
        tutorials_dir.mkdir(exist_ok=True)
        
        # Find tutorial files
        docs_source = self.source_dir / "docs-source" / "source"
        
        if docs_source.exists():
            tutorial_files = list(docs_source.glob("tutorial*.rst"))
            tutorial_files.extend(list(docs_source.glob("quickstart.rst")))
            
            for tutorial_file in tutorial_files:
                if tutorial_file.exists():
                    # Copy and process tutorial
                    dest_file = tutorials_dir / tutorial_file.name
                    content = self.process_rst_content(tutorial_file)
                    
                    # Save processed content
                    with open(dest_file, 'w', encoding='utf-8') as f:
                        f.write(content)
                    
                    # Extract metadata
                    tutorial_info = self.extract_tutorial_metadata(tutorial_file, content)
                    self.extracted_content['tutorials'][tutorial_file.stem] = tutorial_info
                    
                    print(f"  ✓ {tutorial_file.name}")
        
        self.extracted_content['metadata']['categories']['tutorials'] = len(self.extracted_content['tutorials'])
    
    def extract_documentation(self):
        """Extract documentation files"""
        print("📖 استخراج الوثائق...")
        
        docs_dir = self.output_dir / "documentation"
        docs_dir.mkdir(exist_ok=True)
        
        docs_source = self.source_dir / "docs-source" / "source"
        
        if docs_source.exists():
            # Important documentation files
            doc_files = [
                "installation.rst", "overview.rst", "project_setup.rst",
                "slide_processing.rst", "training.rst", "evaluation.rst",
                "features.rst", "model.rst", "dataset.rst"
            ]
            
            for doc_file in doc_files:
                doc_path = docs_source / doc_file
                if doc_path.exists():
                    # Copy and process documentation
                    dest_file = docs_dir / doc_file
                    content = self.process_rst_content(doc_path)
                    
                    with open(dest_file, 'w', encoding='utf-8') as f:
                        f.write(content)
                    
                    # Extract metadata
                    doc_info = self.extract_doc_metadata(doc_path, content)
                    self.extracted_content['documentation'][doc_path.stem] = doc_info
                    
                    print(f"  ✓ {doc_file}")
        
        self.extracted_content['metadata']['categories']['documentation'] = len(self.extracted_content['documentation'])
    
    def extract_code_examples(self):
        """Extract code examples and scripts"""
        print("💻 استخراج أمثلة الكود...")
        
        code_dir = self.output_dir / "code_examples"
        code_dir.mkdir(exist_ok=True)
        
        # Extract Python examples from various directories
        example_dirs = [
            self.source_dir / "slideflow",
            self.source_dir / "scripts"
        ]
        
        for example_dir in example_dirs:
            if example_dir.exists():
                python_files = list(example_dir.rglob("*.py"))
                
                for py_file in python_files:
                    if self.is_educational_code(py_file):
                        # Create relative path structure
                        rel_path = py_file.relative_to(self.source_dir)
                        dest_file = code_dir / rel_path
                        dest_file.parent.mkdir(parents=True, exist_ok=True)
                        
                        # Copy file
                        shutil.copy2(py_file, dest_file)
                        
                        # Extract code metadata
                        code_info = self.extract_code_metadata(py_file)
                        self.extracted_content['code_examples'][str(rel_path)] = code_info
        
        self.extracted_content['metadata']['categories']['code_examples'] = len(self.extracted_content['code_examples'])
    
    def extract_configuration_files(self):
        """Extract configuration and setup files"""
        print("⚙️ استخراج ملفات التكوين...")
        
        config_dir = self.output_dir / "configuration"
        config_dir.mkdir(exist_ok=True)
        
        config_files = [
            "requirements.txt", "setup.py", "environment.yml",
            "tensorflow.Dockerfile", "torch.Dockerfile"
        ]
        
        for config_file in config_files:
            source_file = self.source_dir / config_file
            if source_file.exists():
                dest_file = config_dir / config_file
                shutil.copy2(source_file, dest_file)
                print(f"  ✓ {config_file}")
    
    def process_rst_content(self, file_path):
        """Process RST content and add Arabic annotations"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Add Arabic header
            arabic_header = f"""
.. Arabic Translation / الترجمة العربية
.. تمت معالجة هذا المحتوى لمنصة تعليم المختبرات الطبية
.. This content has been processed for the Medical Laboratory Education Platform
.. المصدر الأصلي: {file_path.name}
.. تاريخ الاستخراج: {datetime.now().strftime('%Y-%m-%d %H:%M')}

"""
            
            return arabic_header + content
            
        except Exception as e:
            print(f"Error processing {file_path}: {e}")
            return ""
    
    def extract_tutorial_metadata(self, file_path, content):
        """Extract metadata from tutorial files"""
        lines = content.split('\n')
        
        # Extract title
        title = ""
        for line in lines:
            if line.strip() and not line.startswith('..'):
                title = line.strip()
                break
        
        # Extract sections
        sections = []
        for line in lines:
            if re.match(r'^[=-]+$', line.strip()) and len(line.strip()) > 3:
                prev_line_idx = lines.index(line) - 1
                if prev_line_idx >= 0:
                    sections.append(lines[prev_line_idx].strip())
        
        return {
            'title': title,
            'title_ar': self.translate_title_to_arabic(title),
            'file_path': str(file_path),
            'sections': sections,
            'word_count': len(content.split()),
            'difficulty': self.assess_difficulty(content),
            'category': 'tutorial',
            'language': 'en'
        }
    
    def extract_doc_metadata(self, file_path, content):
        """Extract metadata from documentation files"""
        lines = content.split('\n')
        
        # Extract title
        title = ""
        for line in lines:
            if line.strip() and not line.startswith('..'):
                title = line.strip()
                break
        
        return {
            'title': title,
            'title_ar': self.translate_title_to_arabic(title),
            'file_path': str(file_path),
            'word_count': len(content.split()),
            'category': 'documentation',
            'language': 'en'
        }
    
    def extract_code_metadata(self, file_path):
        """Extract metadata from code files"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Extract docstring
            docstring = ""
            if '"""' in content:
                start = content.find('"""')
                if start != -1:
                    end = content.find('"""', start + 3)
                    if end != -1:
                        docstring = content[start+3:end].strip()
            
            # Count functions and classes
            functions = len(re.findall(r'^def\s+\w+', content, re.MULTILINE))
            classes = len(re.findall(r'^class\s+\w+', content, re.MULTILINE))
            
            return {
                'file_path': str(file_path),
                'docstring': docstring,
                'functions_count': functions,
                'classes_count': classes,
                'lines_count': len(content.split('\n')),
                'category': 'code',
                'language': 'python'
            }
        except Exception:
            return {}
    
    def is_educational_code(self, file_path):
        """Check if code file is educational"""
        educational_patterns = [
            'example', 'tutorial', 'demo', 'sample', 'test', 'quickstart'
        ]
        
        file_str = str(file_path).lower()
        return any(pattern in file_str for pattern in educational_patterns)
    
    def translate_title_to_arabic(self, title):
        """Simple title translation to Arabic"""
        translations = {
            'Quick Start': 'البدء السريع',
            'Installation': 'التثبيت',
            'Tutorial': 'درس تعليمي',
            'Overview': 'نظرة عامة',
            'Training': 'التدريب',
            'Evaluation': 'التقييم',
            'Features': 'الميزات',
            'Model': 'النموذج',
            'Dataset': 'مجموعة البيانات',
            'Slide Processing': 'معالجة الشرائح',
            'Project Setup': 'إعداد المشروع'
        }
        
        for en, ar in translations.items():
            if en.lower() in title.lower():
                return title.replace(en, f"{en} ({ar})")
        
        return title + " (محتوى تعليمي)"
    
    def assess_difficulty(self, content):
        """Assess content difficulty level"""
        advanced_keywords = ['advanced', 'complex', 'optimization', 'custom', 'api']
        beginner_keywords = ['introduction', 'basic', 'simple', 'getting started', 'first']
        
        content_lower = content.lower()
        
        advanced_count = sum(1 for keyword in advanced_keywords if keyword in content_lower)
        beginner_count = sum(1 for keyword in beginner_keywords if keyword in content_lower)
        
        if advanced_count > beginner_count:
            return 'advanced'
        elif beginner_count > 0:
            return 'beginner'
        else:
            return 'intermediate'
    
    def save_extracted_content(self):
        """Save extraction metadata"""
        self.extracted_content['metadata']['total_files'] = sum(
            len(category) for category in [
                self.extracted_content['tutorials'],
                self.extracted_content['documentation'],
                self.extracted_content['code_examples']
            ]
        )
        
        # Save main metadata file
        metadata_file = self.output_dir / "extraction_metadata.json"
        with open(metadata_file, 'w', encoding='utf-8') as f:
            json.dump(self.extracted_content, f, indent=2, ensure_ascii=False)
        
        # Save educational index
        self.create_educational_index()
        
        print(f"💾 حُفظت البيانات الوصفية في: {metadata_file}")
    
    def create_educational_index(self):
        """Create an educational index for the medical lab platform"""
        index_content = {
            'course_materials': {
                'digital_pathology_basics': {
                    'title': 'أساسيات علم الأمراض الرقمية',
                    'title_en': 'Digital Pathology Basics',
                    'description': 'مقدمة شاملة في علم الأمراض الرقمية باستخدام Slideflow',
                    'materials': list(self.extracted_content['tutorials'].keys())
                },
                'advanced_techniques': {
                    'title': 'التقنيات المتقدمة',
                    'title_en': 'Advanced Techniques',
                    'description': 'تقنيات متقدمة في التحليل والتصنيف',
                    'materials': [k for k, v in self.extracted_content['documentation'].items() 
                                if v.get('difficulty') == 'advanced']
                }
            },
            'practical_exercises': {
                'code_examples': list(self.extracted_content['code_examples'].keys())
            }
        }
        
        index_file = self.output_dir / "educational_index.json"
        with open(index_file, 'w', encoding='utf-8') as f:
            json.dump(index_content, f, indent=2, ensure_ascii=False)

def main():
    """Main execution function"""
    print("🔬 Slideflow Content Extractor")
    print("🔬 مستخرج محتوى Slideflow")
    print("=" * 50)
    
    extractor = SlideflowContentExtractor()
    result = extractor.extract_all_content()
    
    print("\n📊 ملخص الاستخراج / Extraction Summary:")
    print(f"📚 الدروس التعليمية: {len(result['tutorials'])}")
    print(f"📖 الوثائق: {len(result['documentation'])}")
    print(f"💻 أمثلة الكود: {len(result['code_examples'])}")
    print(f"📁 إجمالي الملفات: {result['metadata']['total_files']}")
    
    print(f"\n✅ تم حفظ جميع الملفات في: /home/user/webapp/slideflow_source")
    print("✅ All files saved to: /home/user/webapp/slideflow_source")

if __name__ == "__main__":
    main()