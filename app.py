#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
نظام تسجيل الطلاب - جامعة الوطنية
Student Registration System - Al-Watania University
Flask Web Application
"""

from flask import Flask, render_template, request, redirect, url_for, flash, jsonify
import sqlite3
import os
from datetime import datetime

app = Flask(__name__)
app.secret_key = "watania_university_2025_secret"

DB_FILE = "university.db"

# ─── Database ─────────────────────────────────────────────
def get_conn():
    conn = sqlite3.connect(DB_FILE)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_conn()
    cur = conn.cursor()
    cur.executescript("""
    CREATE TABLE IF NOT EXISTS colleges (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name_ar TEXT NOT NULL,
        name_en TEXT NOT NULL
    );
    CREATE TABLE IF NOT EXISTS departments (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        college_id INTEGER NOT NULL REFERENCES colleges(id),
        name_ar TEXT NOT NULL,
        name_en TEXT NOT NULL
    );
    CREATE TABLE IF NOT EXISTS students (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        student_no TEXT UNIQUE NOT NULL,
        name_ar TEXT NOT NULL,
        name_en TEXT NOT NULL,
        gender TEXT CHECK(gender IN ('M','F')) NOT NULL,
        dob TEXT NOT NULL,
        national_id TEXT UNIQUE NOT NULL,
        phone TEXT,
        email TEXT,
        department_id INTEGER REFERENCES departments(id),
        level INTEGER DEFAULT 1,
        gpa REAL DEFAULT 0.0,
        status TEXT DEFAULT 'Active',
        registered_at TEXT DEFAULT (datetime('now'))
    );
    CREATE TABLE IF NOT EXISTS courses (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        course_code TEXT UNIQUE NOT NULL,
        name_ar TEXT NOT NULL,
        name_en TEXT NOT NULL,
        credit_hours INTEGER DEFAULT 3,
        department_id INTEGER REFERENCES departments(id)
    );
    CREATE TABLE IF NOT EXISTS enrollments (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        student_id INTEGER REFERENCES students(id),
        course_id INTEGER REFERENCES courses(id),
        semester TEXT NOT NULL,
        grade TEXT DEFAULT 'Enrolled',
        UNIQUE(student_id, course_id, semester)
    );
    """)

    if cur.execute("SELECT COUNT(*) FROM colleges").fetchone()[0] == 0:
        cur.executemany("INSERT INTO colleges(name_ar,name_en) VALUES(?,?)", [
            ("كلية الهندسة",       "Faculty of Engineering"),
            ("كلية العلوم",         "Faculty of Science"),
            ("كلية الطب والصحة",   "Faculty of Medicine"),
            ("كلية إدارة الأعمال", "Faculty of Business"),
            ("كلية القانون",        "Faculty of Law"),
        ])
        cur.executemany("INSERT INTO departments(college_id,name_ar,name_en) VALUES(?,?,?)", [
            (1,"هندسة الحاسوب","Computer Engineering"),
            (1,"الهندسة الكهربائية","Electrical Engineering"),
            (2,"علم الحاسوب","Computer Science"),
            (2,"الرياضيات","Mathematics"),
            (3,"الطب العام","General Medicine"),
            (4,"إدارة الأعمال","Business Administration"),
            (4,"المحاسبة","Accounting"),
            (5,"القانون العام","General Law"),
        ])
        cur.executemany("INSERT INTO courses(course_code,name_ar,name_en,credit_hours,department_id) VALUES(?,?,?,?,?)", [
            ("CS101","مقدمة البرمجة","Introduction to Programming",3,3),
            ("CS201","هياكل البيانات","Data Structures",3,3),
            ("CS301","قواعد البيانات","Database Systems",3,3),
            ("MATH101","حساب التفاضل","Calculus I",3,4),
            ("ENG101","الدوائر الكهربائية","Electric Circuits",3,2),
            ("BUS101","مبادئ الإدارة","Principles of Management",3,6),
            ("ACC101","مبادئ المحاسبة","Principles of Accounting",3,7),
        ])
    conn.commit()
    conn.close()

def gen_student_no():
    conn = get_conn()
    year = datetime.now().year
    count = conn.execute("SELECT COUNT(*) FROM students").fetchone()[0] + 1
    conn.close()
    return f"WU{year}{count:04d}"

# ─── Routes ───────────────────────────────────────────────

@app.route("/")
def index():
    conn = get_conn()
    total    = conn.execute("SELECT COUNT(*) FROM students").fetchone()[0]
    active   = conn.execute("SELECT COUNT(*) FROM students WHERE status='Active'").fetchone()[0]
    male     = conn.execute("SELECT COUNT(*) FROM students WHERE gender='M'").fetchone()[0]
    female   = conn.execute("SELECT COUNT(*) FROM students WHERE gender='F'").fetchone()[0]
    avg_gpa  = conn.execute("SELECT ROUND(AVG(gpa),2) FROM students").fetchone()[0] or 0
    enrolled = conn.execute("SELECT COUNT(*) FROM enrollments").fetchone()[0]
    depts    = conn.execute("""
        SELECT d.name_ar, d.name_en, COUNT(s.id) as cnt
        FROM departments d LEFT JOIN students s ON s.department_id=d.id
        GROUP BY d.id ORDER BY cnt DESC LIMIT 5
    """).fetchall()
    conn.close()
    return render_template("index.html",
        total=total, active=active, male=male, female=female,
        avg_gpa=avg_gpa, enrolled=enrolled, depts=depts)

@app.route("/students")
def students():
    search = request.args.get("q", "")
    conn = get_conn()
    if search:
        rows = conn.execute("""
            SELECT s.*, d.name_ar as dept_ar, d.name_en as dept_en
            FROM students s LEFT JOIN departments d ON s.department_id=d.id
            WHERE s.student_no LIKE ? OR s.name_ar LIKE ? OR s.name_en LIKE ?
            ORDER BY s.id DESC
        """, (f"%{search}%",f"%{search}%",f"%{search}%")).fetchall()
    else:
        rows = conn.execute("""
            SELECT s.*, d.name_ar as dept_ar, d.name_en as dept_en
            FROM students s LEFT JOIN departments d ON s.department_id=d.id
            ORDER BY s.id DESC
        """).fetchall()
    conn.close()
    return render_template("students.html", students=rows, search=search)

@app.route("/students/new", methods=["GET","POST"])
def new_student():
    conn = get_conn()
    depts = conn.execute("""
        SELECT d.id, d.name_ar, d.name_en, c.name_en as college
        FROM departments d JOIN colleges c ON d.college_id=c.id ORDER BY c.id,d.id
    """).fetchall()
    conn.close()

    if request.method == "POST":
        f = request.form
        student_no = gen_student_no()
        try:
            conn = get_conn()
            conn.execute("""
                INSERT INTO students(student_no,name_ar,name_en,gender,dob,national_id,phone,email,department_id,level)
                VALUES(?,?,?,?,?,?,?,?,?,?)
            """, (student_no, f["name_ar"], f["name_en"], f["gender"], f["dob"],
                  f["national_id"], f["phone"], f["email"], f["department_id"], f["level"]))
            conn.commit()
            conn.close()
            flash(f"✅ تم تسجيل الطالب بنجاح | رقمه: {student_no}", "success")
            return redirect(url_for("students"))
        except sqlite3.IntegrityError:
            flash("❌ الرقم الوطني أو البيانات مكررة / Duplicate national ID", "error")

    return render_template("new_student.html", depts=depts)

@app.route("/students/<int:sid>")
def view_student(sid):
    conn = get_conn()
    student = conn.execute("""
        SELECT s.*, d.name_ar as dept_ar, d.name_en as dept_en, c.name_ar as college_ar
        FROM students s
        LEFT JOIN departments d ON s.department_id=d.id
        LEFT JOIN colleges c ON d.college_id=c.id
        WHERE s.id=?
    """, (sid,)).fetchone()
    courses = conn.execute("""
        SELECT c.course_code, c.name_ar, c.name_en, c.credit_hours, e.semester, e.grade
        FROM enrollments e JOIN courses c ON e.course_id=c.id
        WHERE e.student_id=? ORDER BY e.semester
    """, (sid,)).fetchall()
    conn.close()
    if not student:
        flash("الطالب غير موجود", "error")
        return redirect(url_for("students"))
    return render_template("view_student.html", student=student, courses=courses)

@app.route("/students/<int:sid>/edit", methods=["GET","POST"])
def edit_student(sid):
    conn = get_conn()
    student = conn.execute("SELECT * FROM students WHERE id=?", (sid,)).fetchone()
    depts = conn.execute("""
        SELECT d.id, d.name_ar, d.name_en, c.name_en as college
        FROM departments d JOIN colleges c ON d.college_id=c.id ORDER BY c.id,d.id
    """).fetchall()
    conn.close()

    if not student:
        flash("الطالب غير موجود", "error")
        return redirect(url_for("students"))

    if request.method == "POST":
        f = request.form
        conn = get_conn()
        conn.execute("""
            UPDATE students SET name_ar=?,name_en=?,phone=?,email=?,
            department_id=?,level=?,gpa=?,status=? WHERE id=?
        """, (f["name_ar"], f["name_en"], f["phone"], f["email"],
              f["department_id"], f["level"], f["gpa"], f["status"], sid))
        conn.commit()
        conn.close()
        flash("✅ تم التحديث بنجاح / Updated successfully", "success")
        return redirect(url_for("view_student", sid=sid))

    return render_template("edit_student.html", student=student, depts=depts)

@app.route("/students/<int:sid>/delete", methods=["POST"])
def delete_student(sid):
    conn = get_conn()
    conn.execute("DELETE FROM enrollments WHERE student_id=?", (sid,))
    conn.execute("DELETE FROM students WHERE id=?", (sid,))
    conn.commit()
    conn.close()
    flash("🗑️ تم حذف الطالب / Student deleted", "info")
    return redirect(url_for("students"))

@app.route("/students/<int:sid>/enroll", methods=["GET","POST"])
def enroll(sid):
    conn = get_conn()
    student = conn.execute("SELECT * FROM students WHERE id=?", (sid,)).fetchone()
    courses = conn.execute("SELECT * FROM courses ORDER BY course_code").fetchall()
    conn.close()

    if request.method == "POST":
        f = request.form
        try:
            conn = get_conn()
            conn.execute("INSERT INTO enrollments(student_id,course_id,semester) VALUES(?,?,?)",
                        (sid, f["course_id"], f["semester"]))
            conn.commit()
            conn.close()
            flash("✅ تم تسجيل المادة / Course enrolled", "success")
        except sqlite3.IntegrityError:
            flash("⚠️ الطالب مسجل في هذه المادة مسبقاً / Already enrolled", "warning")
        return redirect(url_for("view_student", sid=sid))

    return render_template("enroll.html", student=student, courses=courses)

@app.route("/api/stats")
def api_stats():
    conn = get_conn()
    data = {
        "total": conn.execute("SELECT COUNT(*) FROM students").fetchone()[0],
        "active": conn.execute("SELECT COUNT(*) FROM students WHERE status='Active'").fetchone()[0],
        "male": conn.execute("SELECT COUNT(*) FROM students WHERE gender='M'").fetchone()[0],
        "female": conn.execute("SELECT COUNT(*) FROM students WHERE gender='F'").fetchone()[0],
    }
    conn.close()
    return jsonify(data)

if __name__ == "__main__":
    init_db()
    app.run(debug=True)
