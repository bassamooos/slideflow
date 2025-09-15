#!/usr/bin/env python3
"""
Slideflow Web Application
تطبيق ويب لمكتبة Slideflow

A comprehensive web interface for the Slideflow digital pathology library.
واجهة ويب شاملة لمكتبة Slideflow لعلم الأمراض الرقمية.
"""

from flask import Flask, render_template, request, jsonify, flash, redirect, url_for, send_file
import os
import sys
import json
import tempfile
import traceback
from datetime import datetime
import logging

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Add slideflow to Python path if it exists
slideflow_path = os.path.join(os.path.dirname(__file__), 'slideflow')
if os.path.exists(slideflow_path):
    sys.path.insert(0, os.path.dirname(__file__))

app = Flask(__name__)
app.secret_key = 'slideflow_web_app_2024'

# Configuration
app.config['MAX_CONTENT_LENGTH'] = 100 * 1024 * 1024  # 100MB max file size
app.config['UPLOAD_FOLDER'] = os.path.join(os.path.dirname(__file__), 'uploads')

# Create necessary directories
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
os.makedirs(os.path.join(os.path.dirname(__file__), 'projects'), exist_ok=True)

# Try to import slideflow
try:
    import slideflow as sf
    SLIDEFLOW_AVAILABLE = True
    logger.info("Slideflow imported successfully")
except ImportError as e:
    SLIDEFLOW_AVAILABLE = False
    logger.warning(f"Slideflow not available: {e}")

@app.route('/')
def index():
    """Main dashboard - الصفحة الرئيسية"""
    slideflow_info = {}
    
    if SLIDEFLOW_AVAILABLE:
        try:
            slideflow_info = {
                'version': getattr(sf, '__version__', 'Unknown'),
                'available': True,
                'backend': os.environ.get('SF_BACKEND', 'auto'),
                'slide_backend': os.environ.get('SF_SLIDE_BACKEND', 'cucim'),
            }
        except Exception as e:
            slideflow_info = {'available': False, 'error': str(e)}
    else:
        slideflow_info = {'available': False, 'error': 'Slideflow not installed'}
    
    return render_template('index.html', slideflow_info=slideflow_info)

@app.route('/features')
def features():
    """Features page - صفحة الميزات"""
    features_list = [
        {
            'name': 'Slide Processing',
            'name_ar': 'معالجة الشرائح',
            'description': 'Advanced whole-slide image processing and tile extraction',
            'description_ar': 'معالجة متقدمة للصور الكاملة للشرائح واستخراج البلاط',
            'icon': 'bi-images'
        },
        {
            'name': 'Model Training',
            'name_ar': 'تدريب النماذج',
            'description': 'Train deep learning models for pathology analysis',
            'description_ar': 'تدريب نماذج التعلم العميق لتحليل علم الأمراض',
            'icon': 'bi-cpu'
        },
        {
            'name': 'Visualization',
            'name_ar': 'التصور',
            'description': 'Interactive heatmaps and visualization tools',
            'description_ar': 'خرائط حرارية تفاعلية وأدوات التصور',
            'icon': 'bi-graph-up'
        },
        {
            'name': 'Foundation Models',
            'name_ar': 'النماذج الأساسية',
            'description': 'Pre-trained foundation models for pathology',
            'description_ar': 'نماذج أساسية مُدربة مسبقاً لعلم الأمراض',
            'icon': 'bi-layers'
        }
    ]
    
    return render_template('features.html', features=features_list)

@app.route('/project/create', methods=['GET', 'POST'])
def create_project():
    """Create new project - إنشاء مشروع جديد"""
    if request.method == 'POST':
        try:
            project_name = request.form.get('project_name')
            project_path = os.path.join(os.path.dirname(__file__), 'projects', project_name)
            
            if SLIDEFLOW_AVAILABLE:
                # Create slideflow project
                annotations_csv = request.form.get('annotations_csv', '')
                slides_dir = request.form.get('slides_dir', '')
                tfrecords_dir = request.form.get('tfrecords_dir', '')
                
                project_config = {
                    'name': project_name,
                    'path': project_path,
                    'annotations': annotations_csv or None,
                    'slides': slides_dir or None,
                    'tfrecords': tfrecords_dir or None,
                    'created_at': datetime.now().isoformat()
                }
                
                # Save project configuration
                os.makedirs(project_path, exist_ok=True)
                with open(os.path.join(project_path, 'config.json'), 'w') as f:
                    json.dump(project_config, f, indent=2)
                
                flash(f'Project "{project_name}" created successfully!', 'success')
                return redirect(url_for('project_detail', project_name=project_name))
            else:
                flash('Slideflow is not available. Please install it first.', 'error')
                
        except Exception as e:
            flash(f'Error creating project: {str(e)}', 'error')
            logger.error(f"Error creating project: {e}")
    
    return render_template('create_project.html')

@app.route('/project/<project_name>')
def project_detail(project_name):
    """Project detail page - صفحة تفاصيل المشروع"""
    project_path = os.path.join(os.path.dirname(__file__), 'projects', project_name)
    config_path = os.path.join(project_path, 'config.json')
    
    if not os.path.exists(config_path):
        flash('Project not found', 'error')
        return redirect(url_for('projects_list'))
    
    try:
        with open(config_path, 'r') as f:
            project_config = json.load(f)
        
        # Get project statistics if slideflow is available
        stats = {}
        if SLIDEFLOW_AVAILABLE:
            # Add slide count, tile count, etc. if data is available
            pass
        
        return render_template('project_detail.html', 
                             project=project_config, 
                             stats=stats,
                             project_name=project_name)
    except Exception as e:
        flash(f'Error loading project: {str(e)}', 'error')
        return redirect(url_for('projects_list'))

@app.route('/projects')
def projects_list():
    """List all projects - قائمة جميع المشاريع"""
    projects_dir = os.path.join(os.path.dirname(__file__), 'projects')
    projects = []
    
    if os.path.exists(projects_dir):
        for project_name in os.listdir(projects_dir):
            project_path = os.path.join(projects_dir, project_name)
            config_path = os.path.join(project_path, 'config.json')
            
            if os.path.isdir(project_path) and os.path.exists(config_path):
                try:
                    with open(config_path, 'r') as f:
                        config = json.load(f)
                    projects.append(config)
                except Exception as e:
                    logger.error(f"Error reading project config for {project_name}: {e}")
    
    return render_template('projects_list.html', projects=projects)

@app.route('/models')
def models():
    """Available models page - صفحة النماذج المتاحة"""
    available_models = []
    
    if SLIDEFLOW_AVAILABLE:
        try:
            # Get available feature extractors
            extractors = [
                'resnet50', 'xception', 'vgg16', 'vgg19', 'inception_v3',
                'densenet121', 'densenet169', 'densenet201', 'nasnet_large',
                'efficientnet_b0', 'efficientnet_b1', 'efficientnet_b2'
            ]
            
            for extractor in extractors:
                available_models.append({
                    'name': extractor,
                    'type': 'Feature Extractor',
                    'description': f'Pre-trained {extractor} model for feature extraction'
                })
            
            # Add foundation models if available
            foundation_models = [
                'histossl', 'uni', 'ctranspath', 'retccl', 'plip', 'gigapath'
            ]
            
            for model in foundation_models:
                available_models.append({
                    'name': model,
                    'type': 'Foundation Model',
                    'description': f'Foundation model: {model.upper()}'
                })
                
        except Exception as e:
            logger.error(f"Error getting available models: {e}")
    
    return render_template('models.html', models=available_models)

@app.route('/api/system_info')
def api_system_info():
    """API endpoint for system information"""
    info = {
        'slideflow_available': SLIDEFLOW_AVAILABLE,
        'python_version': sys.version,
        'platform': sys.platform,
        'timestamp': datetime.now().isoformat()
    }
    
    if SLIDEFLOW_AVAILABLE:
        try:
            info['slideflow_version'] = getattr(sf, '__version__', 'Unknown')
            info['backend'] = os.environ.get('SF_BACKEND', 'auto')
            info['slide_backend'] = os.environ.get('SF_SLIDE_BACKEND', 'cucim')
        except Exception as e:
            info['slideflow_error'] = str(e)
    
    return jsonify(info)

@app.route('/api/extract_tiles', methods=['POST'])
def api_extract_tiles():
    """API endpoint for tile extraction"""
    if not SLIDEFLOW_AVAILABLE:
        return jsonify({'error': 'Slideflow is not available'}), 400
    
    try:
        data = request.get_json()
        project_name = data.get('project_name')
        tile_px = int(data.get('tile_px', 299))
        tile_um = int(data.get('tile_um', 302))
        
        # This would be the actual tile extraction logic
        # For now, return a mock response
        result = {
            'status': 'success',
            'message': f'Tile extraction started for project {project_name}',
            'parameters': {
                'tile_px': tile_px,
                'tile_um': tile_um
            },
            'timestamp': datetime.now().isoformat()
        }
        
        return jsonify(result)
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/train_model', methods=['POST'])
def api_train_model():
    """API endpoint for model training"""
    if not SLIDEFLOW_AVAILABLE:
        return jsonify({'error': 'Slideflow is not available'}), 400
    
    try:
        data = request.get_json()
        project_name = data.get('project_name')
        model_type = data.get('model_type', 'xception')
        outcome = data.get('outcome')
        
        # This would be the actual training logic
        # For now, return a mock response
        result = {
            'status': 'success',
            'message': f'Model training started for project {project_name}',
            'parameters': {
                'model_type': model_type,
                'outcome': outcome
            },
            'timestamp': datetime.now().isoformat()
        }
        
        return jsonify(result)
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/documentation')
def documentation():
    """Documentation page - صفحة الوثائق"""
    return render_template('documentation.html')

@app.route('/tutorials')
def tutorials():
    """Tutorials page - صفحة الدروس"""
    tutorials_list = [
        {
            'title': 'Getting Started with Slideflow',
            'title_ar': 'البدء مع Slideflow',
            'description': 'Learn the basics of digital pathology with Slideflow',
            'description_ar': 'تعلم أساسيات علم الأمراض الرقمية باستخدام Slideflow',
            'level': 'Beginner',
            'duration': '30 minutes'
        },
        {
            'title': 'Project Setup and Configuration',
            'title_ar': 'إعداد المشروع والتكوين',
            'description': 'How to create and configure your first Slideflow project',
            'description_ar': 'كيفية إنشاء وتكوين مشروعك الأول في Slideflow',
            'level': 'Beginner',
            'duration': '45 minutes'
        },
        {
            'title': 'Tile Extraction and Processing',
            'title_ar': 'استخراج ومعالجة البلاط',
            'description': 'Advanced techniques for slide processing and tile extraction',
            'description_ar': 'تقنيات متقدمة لمعالجة الشرائح واستخراج البلاط',
            'level': 'Intermediate',
            'duration': '1 hour'
        },
        {
            'title': 'Model Training and Evaluation',
            'title_ar': 'تدريب النماذج وتقييمها',
            'description': 'Train and evaluate deep learning models for pathology',
            'description_ar': 'تدريب وتقييم نماذج التعلم العميق لعلم الأمراض',
            'level': 'Advanced',
            'duration': '2 hours'
        }
    ]
    
    return render_template('tutorials.html', tutorials=tutorials_list)

@app.errorhandler(404)
def page_not_found(e):
    """404 error handler"""
    return render_template('404.html'), 404

@app.errorhandler(500)
def internal_server_error(e):
    """500 error handler"""
    return render_template('500.html'), 500

if __name__ == '__main__':
    print("🔬 Slideflow Web Application Starting...")
    print("🌐 تطبيق Slideflow الويب يبدأ...")
    print(f"📁 Working directory: {os.getcwd()}")
    print(f"🐍 Python version: {sys.version}")
    
    if SLIDEFLOW_AVAILABLE:
        print("✅ Slideflow is available")
    else:
        print("❌ Slideflow is not available - some features will be limited")
    
    app.run(host='0.0.0.0', port=5000, debug=True)