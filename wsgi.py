# WSGI configuration for PythonAnywhere
# ضع مسار مشروعك الصحيح / Replace with your actual username

import sys
import os

# ⚠️ غيّر "your_username" لاسم مستخدمك في PythonAnywhere
# ⚠️ Change "your_username" to your actual PythonAnywhere username
project_path = '/home/your_username/watania_web'

if project_path not in sys.path:
    sys.path.insert(0, project_path)

os.chdir(project_path)

from app import app, init_db
init_db()

application = app
