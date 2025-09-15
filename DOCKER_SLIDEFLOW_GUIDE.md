# دليل Docker لـ Slideflow
# Slideflow Docker Guide

## نظرة عامة | Overview

هذا الدليل يوضح كيفية تشغيل Slideflow باستخدام Docker، مما يوفر بيئة معزولة ومُكونة مسبقاً لتحليل علم الأمراض الرقمية.

This guide explains how to run Slideflow using Docker, providing an isolated and pre-configured environment for digital pathology analysis.

## المتطلبات الأساسية | Prerequisites

### ✅ متطلبات النظام | System Requirements
- نظام تشغيل: Linux, macOS, أو Windows مع WSL2
- ذاكرة: 8GB RAM كحد أدنى (16GB مُوصى به)  
- مساحة القرص: 10GB متاحة
- معالج رسوميات: NVIDIA GPU (اختياري لكن مُوصى به)

### 🐳 تثبيت Docker | Docker Installation

#### لنظام Ubuntu/Debian:
```bash
# تحديث الحزم
sudo apt update

# تثبيت Docker
sudo apt install docker.io docker-compose

# تشغيل Docker
sudo systemctl start docker
sudo systemctl enable docker

# إضافة المستخدم لمجموعة docker
sudo usermod -aG docker $USER
```

#### لنظام CentOS/RHEL:
```bash
# تثبيت Docker
sudo yum install -y docker

# تشغيل Docker  
sudo systemctl start docker
sudo systemctl enable docker

# إضافة المستخدم لمجموعة docker
sudo usermod -aG docker $USER
```

#### لنظام Windows:
1. تحميل Docker Desktop من: https://docs.docker.com/desktop/windows/install/
2. تثبيت وتشغيل Docker Desktop
3. تفعيل WSL2 integration

#### لنظام macOS:
1. تحميل Docker Desktop من: https://docs.docker.com/desktop/mac/install/
2. تثبيت وتشغيل Docker Desktop

### 🎮 دعم GPU | GPU Support

لاستخدام GPU مع Docker:

#### NVIDIA GPU Support:
```bash
# تثبيت NVIDIA Docker runtime
distribution=$(. /etc/os-release;echo $ID$VERSION_ID)
curl -s -L https://nvidia.github.io/nvidia-docker/gpgkey | sudo apt-key add -
curl -s -L https://nvidia.github.io/nvidia-docker/$distribution/nvidia-docker.list | sudo tee /etc/apt/sources.list.d/nvidia-docker.list

sudo apt update
sudo apt install -y nvidia-docker2
sudo systemctl restart docker
```

## الأوامر الأساسية | Basic Commands

### 🚀 الأوامر المطلوبة | Required Commands

#### 1. سحب صورة Slideflow | Pull Slideflow Image
```bash
# للإصدار مع TensorFlow
docker pull jamesdolezal/slideflow:latest-tf

# للإصدار مع PyTorch  
docker pull jamesdolezal/slideflow:latest-torch
```

#### 2. تشغيل الحاوية | Run Container

##### مع دعم GPU:
```bash
# TensorFlow version
docker run -it --gpus all jamesdolezal/slideflow:latest-tf

# PyTorch version  
docker run -it --shm-size=2g --gpus all jamesdolezal/slideflow:latest-torch
```

##### بدون GPU:
```bash
# TensorFlow version
docker run -it jamesdolezal/slideflow:latest-tf

# PyTorch version
docker run -it --shm-size=2g jamesdolezal/slideflow:latest-torch
```

### 🗂️ ربط المجلدات | Volume Mounting

لاستخدام بياناتك المحلية:

```bash
# ربط مجلد البيانات المحلي
docker run -it --gpus all \
  -v /path/to/your/data:/data \
  -v /path/to/your/projects:/projects \
  jamesdolezal/slideflow:latest-tf

# مثال عملي
docker run -it --gpus all \
  -v ~/slideflow_data:/data \
  -v ~/slideflow_projects:/projects \
  jamesdolezal/slideflow:latest-tf
```

### 🌐 تشغيل خدمات الويب | Web Services

#### تشغيل Jupyter Lab:
```bash
docker run -it --gpus all \
  -p 8888:8888 \
  -v ~/slideflow_data:/data \
  jamesdolezal/slideflow:latest-tf \
  jupyter lab --allow-root --ip=0.0.0.0 --port=8888
```

#### تشغيل Slideflow Studio:
```bash
docker run -it --gpus all \
  -p 5000:5000 \
  -v ~/slideflow_data:/data \
  jamesdolezal/slideflow:latest-tf \
  slideflow-studio --host=0.0.0.0 --port=5000
```

## أمثلة عملية | Practical Examples

### 📊 مثال 1: إنشاء مشروع جديد | Example 1: Creating a New Project

```bash
# تشغيل الحاوية التفاعلية
docker run -it --gpus all \
  -v ~/slideflow_projects:/projects \
  jamesdolezal/slideflow:latest-tf

# داخل الحاوية
python3 << EOF
import slideflow as sf

# إنشاء مشروع جديد
P = sf.create_project(
    '/projects/my_pathology_project',
    annotations='/data/annotations.csv',
    slides='/data/slides',
    tfrecords='/projects/tfrecords'
)

print("✅ تم إنشاء المشروع بنجاح!")
print("✅ Project created successfully!")
EOF
```

### 🔬 مثال 2: استخراج البلاط | Example 2: Tile Extraction

```bash
# تشغيل مع ربط البيانات
docker run -it --gpus all \
  -v ~/pathology_slides:/slides \
  -v ~/slideflow_projects:/projects \
  jamesdolezal/slideflow:latest-tf

# داخل الحاوية - استخراج البلاط
python3 << EOF
import slideflow as sf

# تحميل المشروع
P = sf.load_project('/projects/my_pathology_project')

# استخراج البلاط
P.extract_tiles(
    tile_px=299,        # حجم البلاط بالبكسل
    tile_um=302,        # حجم البلاط بالميكرون
    buffer='/tmp'       # مجلد مؤقت للتسريع
)

print("✅ تم استخراج البلاط بنجاح!")
EOF
```

### 🤖 مثال 3: تدريب نموذج | Example 3: Model Training

```bash
docker run -it --gpus all \
  -v ~/slideflow_projects:/projects \
  jamesdolezal/slideflow:latest-tf

python3 << EOF
import slideflow as sf

# تحميل المشروع
P = sf.load_project('/projects/my_pathology_project')

# إعداد معاملات النموذج
params = sf.ModelParams(
    tile_px=299,
    tile_um=302,
    batch_size=32,
    model='xception',
    learning_rate=0.0001
)

# تدريب النموذج
P.train(
    'diagnosis',          # المتغير المراد التنبؤ به
    params=params,
    save_predictions=True,
    multi_gpu=True
)

print("✅ تم التدريب بنجاح!")
EOF
```

## إدارة الحاويات | Container Management

### 📋 عرض الحاويات | List Containers
```bash
# الحاويات النشطة
docker ps

# جميع الحاويات  
docker ps -a
```

### 🛑 إيقاف الحاويات | Stop Containers
```bash
# إيقاف حاوية محددة
docker stop <container_id>

# إيقاف جميع الحاويات
docker stop $(docker ps -q)
```

### 🧹 تنظيف النظام | System Cleanup
```bash
# إزالة الحاويات المتوقفة
docker container prune

# إزالة الصور غير المستخدمة
docker image prune

# تنظيف شامل للنظام
docker system prune -a
```

## استكشاف الأخطاء | Troubleshooting

### ❌ المشاكل الشائعة | Common Issues

#### 1. خطأ في أذونات Docker | Docker Permission Error
```bash
# الحل: إضافة المستخدم لمجموعة docker
sudo usermod -aG docker $USER
# ثم إعادة تسجيل الدخول
```

#### 2. نفاد مساحة القرص | Disk Space Issues  
```bash
# تنظيف Docker
docker system prune -a
docker volume prune
```

#### 3. مشاكل GPU | GPU Issues
```bash
# التحقق من دعم NVIDIA
docker run --rm --gpus all nvidia/cuda:11.0-base nvidia-smi

# إذا فشل، تثبيت nvidia-docker2
sudo apt install nvidia-docker2
sudo systemctl restart docker
```

#### 4. مشاكل الذاكرة | Memory Issues
```bash
# زيادة shared memory للـ PyTorch
docker run -it --shm-size=8g jamesdolezal/slideflow:latest-torch
```

### 🔍 سجلات التشخيص | Diagnostic Logs
```bash
# عرض سجلات الحاوية
docker logs <container_id>

# متابعة السجلات المباشرة
docker logs -f <container_id>

# عرض معلومات النظام
docker system info
```

## الأمان | Security

### 🔒 أفضل الممارسات | Best Practices

1. **تجنب تشغيل الحاويات كـ root:**
```bash
# إنشاء مستخدم داخل الحاوية
docker run -it --user $(id -u):$(id -g) jamesdolezal/slideflow:latest-tf
```

2. **استخدام شبكات معزولة:**
```bash
# إنشاء شبكة مخصصة  
docker network create slideflow-net
docker run --network slideflow-net jamesdolezal/slideflow:latest-tf
```

3. **تحديد موارد الحاوية:**
```bash
# تحديد الذاكرة والمعالج
docker run --memory=8g --cpus=4 jamesdolezal/slideflow:latest-tf
```

## النشر في الإنتاج | Production Deployment

### 🚀 باستخدام Docker Compose

إنشاء ملف `docker-compose.yml`:

```yaml
version: '3.8'

services:
  slideflow:
    image: jamesdolezal/slideflow:latest-tf
    runtime: nvidia
    environment:
      - NVIDIA_VISIBLE_DEVICES=all
    volumes:
      - ./data:/data
      - ./projects:/projects
      - ./results:/results
    ports:
      - "8888:8888"
      - "5000:5000"
    command: jupyter lab --allow-root --ip=0.0.0.0
    
  slideflow-worker:
    image: jamesdolezal/slideflow:latest-tf
    runtime: nvidia
    environment:
      - NVIDIA_VISIBLE_DEVICES=all
    volumes:
      - ./data:/data
      - ./projects:/projects
    command: python worker.py
    depends_on:
      - slideflow
```

تشغيل الخدمات:
```bash
docker-compose up -d
```

### ⚖️ التحجيم التلقائي | Auto Scaling

باستخدام Docker Swarm:
```bash
# تهيئة swarm
docker swarm init

# نشر الخدمة
docker service create \
  --name slideflow-service \
  --replicas 3 \
  --mount type=bind,src=/data,dst=/data \
  jamesdolezal/slideflow:latest-tf

# تحديث عدد النسخ
docker service scale slideflow-service=5
```

## الموارد الإضافية | Additional Resources

### 📚 روابط مفيدة | Useful Links
- [Slideflow Documentation](https://slideflow.dev)
- [Docker Official Docs](https://docs.docker.com)
- [NVIDIA Docker Guide](https://github.com/NVIDIA/nvidia-docker)

### 💬 الدعم التقني | Support
- GitHub Issues: https://github.com/slideflow/slideflow/issues
- Docker Hub: https://hub.docker.com/r/jamesdolezal/slideflow
- Community Forum: https://slideflow.dev/community

### 🏷️ إصدارات الصور | Image Tags
```bash
# الأحدث مع TensorFlow
jamesdolezal/slideflow:latest-tf

# الأحدث مع PyTorch
jamesdolezal/slideflow:latest-torch

# إصدارات محددة
jamesdolezal/slideflow:2.1.0-tf
jamesdolezal/slideflow:2.1.0-torch
```

---

## خلاصة | Summary

هذا الدليل يوفر كل ما تحتاجه لتشغيل Slideflow باستخدام Docker بنجاح. تذكر دائماً:

This guide provides everything you need to successfully run Slideflow using Docker. Always remember:

- ✅ تأكد من توفر المتطلبات الأساسية
- ✅ استخدم المجلدات المربوطة لحفظ بياناتك  
- ✅ راقب استخدام الموارد
- ✅ نظف النظام بانتظام
- ✅ احتفظ بنسخ احتياطية من مشاريعك

**🎯 الهدف:** توفير بيئة موثوقة ومتسقة لتطوير تطبيقات علم الأمراض الرقمية

**🎯 Goal:** Provide a reliable and consistent environment for developing digital pathology applications