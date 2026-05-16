# 🚀 دليل الرفع على PythonAnywhere
# Deployment Guide for PythonAnywhere

---

## الخطوة 1 — إنشاء حساب | Create Account
1. اذهب إلى: https://www.pythonanywhere.com
2. اضغط "Start running Python online in less than a minute"
3. اختر "Create a Beginner account" (مجاني)
4. سجّل باسم مستخدم — سيصبح رابط موقعك: `your_username.pythonanywhere.com`

---

## الخطوة 2 — رفع الملفات | Upload Files

### الطريقة الأسهل (Files):
1. من لوحة التحكم → اضغط **"Files"**
2. اضغط **"New directory"** → اسمها: `watania_web`
3. ادخل المجلد، ثم ارفع الملفات التالية:
   - `app.py`
   - `requirements.txt`
   - `wsgi.py`
4. أنشئ مجلد `templates` وارفع فيه كل ملفات `.html`

### أو عبر Bash Console:
```bash
mkdir ~/watania_web
mkdir ~/watania_web/templates
cd ~/watania_web
```

---

## الخطوة 3 — تثبيت Flask | Install Flask
1. من لوحة التحكم → **"Bash Console"**
2. اكتب:
```bash
pip3 install --user flask
```

---

## الخطوة 4 — إعداد تطبيق الويب | Setup Web App
1. من لوحة التحكم → **"Web"**
2. اضغط **"Add a new web app"**
3. اختر **"Manual configuration"**
4. اختر **Python 3.10**
5. في قسم **"WSGI configuration file"** → اضغط على رابط الملف
6. **احذف كل المحتوى** واستبدله بـ:

```python
import sys, os
project_path = '/home/YOUR_USERNAME/watania_web'
if project_path not in sys.path:
    sys.path.insert(0, project_path)
os.chdir(project_path)
from app import app, init_db
init_db()
application = app
```
⚠️ **غيّر `YOUR_USERNAME` لاسم مستخدمك الفعلي**

7. اضغط **Save**

---

## الخطوة 5 — إعداد Static Files
في صفحة **Web** → قسم **"Static files"**:
| URL       | Directory                              |
|-----------|----------------------------------------|
| /static/  | /home/YOUR_USERNAME/watania_web/static |

---

## الخطوة 6 — تشغيل | Launch!
1. اضغط **"Reload"** الأخضر في أعلى صفحة Web
2. زُر رابطك: `https://your_username.pythonanywhere.com` 🎉

---

## ✅ النتيجة المتوقعة | Expected Result
موقع ويب كامل بـ:
- لوحة تحكم بالإحصائيات
- تسجيل الطلاب
- البحث والتعديل والحذف
- تسجيل المواد الدراسية

---

## 🆘 مشاكل شائعة | Troubleshooting

| المشكلة | الحل |
|---|---|
| `ModuleNotFoundError: flask` | شغّل: `pip3 install --user flask` |
| صفحة 500 | تحقق من Error log في صفحة Web |
| مسار خاطئ | تأكد من اسم المستخدم في wsgi.py |
