from flask import Flask, render_template, request, jsonify, redirect, url_for
from neo4j import GraphDatabase
from collections import defaultdict, Counter
import os
import uuid
from chromatic.greedy import greedy_coloring_welsh, greedy_coloring_random
from chromatic.dsatur import dsatur_coloring
from colouring.graph_builder import build_conflict_graph
from colouring.utils import update_course_slots
from db import run_query
import time

app = Flask(__name__)

# Konfigurasi Neo4j
NEO4J_URI = os.getenv("NEO4J_URI", "bolt://localhost:7687")
NEO4J_USER = os.getenv("NEO4J_USER", "neo4j")
NEO4J_PASSWORD = os.getenv("NEO4J_PASSWORD", "password")

driver = GraphDatabase.driver(NEO4J_URI, auth=(NEO4J_USER, NEO4J_PASSWORD))

def get_db():
    return driver

# ===== CRUD Operations =====
# Course Management
@app.route('/courses', methods=['GET', 'POST'])
def manage_courses():
    if request.method == 'POST':
        name = request.form['name']
        day = request.form.get('day', '')  # Get day from form
        time_slot = request.form.get('time_slot', '')  # Get time slot from form
        course_id = str(uuid.uuid4())
        
        # Combine day and time slot
        full_schedule = f"{day} {time_slot}" if day and time_slot else ""
        
        run_query("CREATE (c:Course {id: $id, name: $name, day: $day, time_slot: $time_slot, schedule: $schedule})", 
                 {'id': course_id, 'name': name, 'day': day, 'time_slot': time_slot, 'schedule': full_schedule})
        return redirect(url_for('manage_courses'))
    
    # Clean up any courses without proper IDs
    run_query("MATCH (c:Course) WHERE c.id IS NULL DETACH DELETE c")
    
    courses = run_query("MATCH (c:Course) RETURN c.id AS id, c.name AS name, c.day AS day, c.time_slot AS time_slot, c.schedule AS schedule")
    return render_template('courses.html', courses=courses)

@app.route('/course/delete/<id>', methods=['POST'])
def delete_course(id):
    if id:
        run_query("MATCH (c:Course {id: $id}) DETACH DELETE c", {'id': id})
    return redirect(url_for('manage_courses'))

@app.route('/course/update/<id>', methods=['POST'])
def update_course(id):
    if id:
        day = request.form.get('day', '')
        time_slot = request.form.get('time_slot', '')
        full_schedule = f"{day} {time_slot}" if day and time_slot else ""
        
        run_query("MATCH (c:Course {id: $id}) SET c.day = $day, c.time_slot = $time_slot, c.schedule = $schedule", 
                 {'id': id, 'day': day, 'time_slot': time_slot, 'schedule': full_schedule})
    return redirect(url_for('manage_courses'))

# Student Management
@app.route('/students', methods=['GET', 'POST'])
def manage_students():
    if request.method == 'POST':
        name = request.form['name']
        student_id = str(uuid.uuid4())
        run_query("CREATE (s:Student {id: $id, name: $name})", {'id': student_id, 'name': name})
        return redirect(url_for('manage_students'))
    
    # Clean up any students without proper IDs
    run_query("MATCH (s:Student) WHERE s.id IS NULL DETACH DELETE s")
    
    # Get students with course count
    students = run_query("""
        MATCH (s:Student)
        OPTIONAL MATCH (s)-[:ENROLLED_IN]->(c:Course)
        RETURN s.id AS id, s.name AS name, count(c) AS course_count
        ORDER BY s.name
    """)
    return render_template('students.html', students=students)

@app.route('/student/delete/<id>', methods=['POST'])
def delete_student(id):
    if id:
        run_query("MATCH (s:Student {id: $id}) DETACH DELETE s", {'id': id})
    return redirect(url_for('manage_students'))

# Enrollment Management
@app.route('/enroll', methods=['GET', 'POST'])
def manage_enrollments():
    if request.method == 'POST':
        student_id = request.form['student_id']
        course_id = request.form['course_id']
        run_query("""
            MATCH (s:Student {id: $student_id}), (c:Course {id: $course_id})
            MERGE (s)-[:ENROLLED_IN]->(c)
        """, {'student_id': student_id, 'course_id': course_id})
    
    students = run_query("MATCH (s:Student) RETURN s.id AS id, s.name AS name")
    courses = run_query("MATCH (c:Course) RETURN c.id AS id, c.name AS name")
    enrollments = run_query("""
        MATCH (s:Student)-[:ENROLLED_IN]->(c:Course)
        RETURN s.id AS student_id, s.name AS student_name, 
               c.id AS course_id, c.name AS course_name, c.schedule AS schedule
    """)

    # Deteksi konflik: mahasiswa mengambil dua mata kuliah di waktu yang sama
    student_schedules = defaultdict(list)
    for e in enrollments:
        if e['schedule']:
            student_schedules[e['student_id']].append(e['schedule'])
    # Hitung jadwal ganda
    student_conflicts = defaultdict(set)
    for sid, schedules in student_schedules.items():
        counter = Counter(schedules)
        for sched, count in counter.items():
            if count > 1:
                student_conflicts[sid].add(sched)
    # Tandai konflik pada enrollment
    for e in enrollments:
        e['has_conflict'] = False
        if e['schedule'] and e['student_id'] in student_conflicts:
            if e['schedule'] in student_conflicts[e['student_id']]:
                e['has_conflict'] = True

    return render_template('enrollments.html', 
                          students=students, 
                          courses=courses, 
                          enrollments=enrollments)

@app.route('/enroll/delete/<student_id>/<course_id>', methods=['POST'])
def delete_enrollment(student_id, course_id):
    if student_id and course_id:
        run_query("""
            MATCH (s:Student {id: $student_id})-[r:ENROLLED_IN]->(c:Course {id: $course_id})
            DELETE r
        """, {'student_id': student_id, 'course_id': course_id})
    return redirect(url_for('manage_enrollments'))

# ===== View Schedule =====
@app.route('/schedule')
def view_schedule():
    schedule = run_query("""
        MATCH (c:Course)
        OPTIONAL MATCH (s:Student)-[:ENROLLED_IN]->(c)
        RETURN c.id AS id, c.name AS name, c.day AS day, c.time_slot AS time_slot, c.schedule AS schedule, count(s) AS student_count
        ORDER BY c.day, c.time_slot
    """)
    # Kelompokkan berdasarkan hari
    schedule_dict = defaultdict(list)
    for course in schedule:
        if course['day'] and course['time_slot']:
            day = course['day']
            schedule_dict[day].append(course)
        else:
            schedule_dict['Belum dijadwalkan'].append(course)
    total_courses = len(schedule)
    # Hitung konflik pada jadwal: dua course dengan slot sama dan ada mahasiswa yang sama
    total_conflicts = run_query("""
        MATCH (s:Student)-[:ENROLLED_IN]->(c1:Course), (s)-[:ENROLLED_IN]->(c2:Course)
        WHERE c1.id < c2.id AND c1.day = c2.day AND c1.time_slot = c2.time_slot AND c1.day IS NOT NULL AND c1.time_slot IS NOT NULL
        RETURN count(DISTINCT [c1.id, c2.id]) AS conflict_count
    """)[0]['conflict_count']
    # Daftar konflik detail
    conflicts = run_query("""
        MATCH (s:Student)-[:ENROLLED_IN]->(c1:Course), (s)-[:ENROLLED_IN]->(c2:Course)
        WHERE c1.id < c2.id AND c1.day = c2.day AND c1.time_slot = c2.time_slot
              AND c1.day IS NOT NULL AND c1.time_slot IS NOT NULL
        RETURN c1.name AS course1, c2.name AS course2, c1.day AS day, c1.time_slot AS time_slot, collect(DISTINCT s.name) AS students
        ORDER BY day, time_slot, course1, course2
    """)
    return render_template('schedule.html', schedule=dict(schedule_dict), total_courses=total_courses, total_conflicts=total_conflicts, conflicts=conflicts)

@app.route('/')
def index():
    # Get statistics
    course_count = run_query("MATCH (c:Course) RETURN count(c) AS count")[0]['count']
    student_count = run_query("MATCH (s:Student) RETURN count(s) AS count")[0]['count']
    enrollment_count = run_query("MATCH ()-[:ENROLLED_IN]->() RETURN count(*) AS count")[0]['count']
    scheduled_count = run_query("MATCH (c:Course) WHERE c.day IS NOT NULL AND c.time_slot IS NOT NULL RETURN count(c) AS count")[0]['count']
    
    return render_template('index.html', 
                          course_count=course_count,
                          student_count=student_count,
                          enrollment_count=enrollment_count,
                          scheduled_count=scheduled_count)

# ===== Algoritma Optimasi =====
# (fungsi-fungsi sudah dipindah ke modul terpisah)

@app.route('/optimasi', methods=['GET', 'POST'])
def optimasi():
    # Ambil semua course dan hitung jumlah konflik (jumlah tetangga di graph konflik)
    courses = run_query("""
        MATCH (c:Course)
        OPTIONAL MATCH (c)<-[:ENROLLED_IN]-(s:Student)-[:ENROLLED_IN]->(other:Course)
        WHERE c.id <> other.id
        WITH c, collect(DISTINCT other.id) AS neighbors
        RETURN c.id AS id, c.name AS name, size(neighbors) AS conflict_count, c.color AS color, c.day AS day, c.time_slot AS time_slot
        ORDER BY c.name
    """)
    # Jumlah simpul
    num_nodes = len(courses)
    # Jumlah konflik (edge pada graph konflik)
    num_edges = run_query("""
        MATCH (c1:Course)<-[:ENROLLED_IN]-(s:Student)-[:ENROLLED_IN]->(c2:Course)
        WHERE c1.id < c2.id
        RETURN count(DISTINCT [c1.id, c2.id]) AS edge_count
    """)[0]['edge_count']
    chromatic_number = None
    conflict_time = None
    coloring_time = None
    computation_time = None
    if request.method == 'POST':
        algorithm = request.form.get('algorithm')
        t0 = time.time()
        graph, id_to_name = build_conflict_graph()
        t1 = time.time()
        conflict_time = t1 - t0
        t2 = t1
        if algorithm == 'greedy':
            color_map = greedy_coloring_welsh(graph)
            t2 = time.time()
            update_course_slots(color_map)
        elif algorithm == 'greedy_random':
            color_map = greedy_coloring_random(graph)
            t2 = time.time()
            update_course_slots(color_map)
        elif algorithm == 'dsatur':
            color_map = dsatur_coloring(graph)
            t2 = time.time()
            update_course_slots(color_map)
        coloring_time = t2 - t1
        computation_time = t2 - t0
        # Chromatic number = jumlah warna unik
        chromatic_number = len(set(color_map.values())) if 'color_map' in locals() else None
        # Refresh data setelah optimasi
        courses = run_query("""
            MATCH (c:Course)
            OPTIONAL MATCH (c)<-[:ENROLLED_IN]-(s:Student)-[:ENROLLED_IN]->(other:Course)
            WHERE c.id <> other.id
            WITH c, collect(DISTINCT other.id) AS neighbors
            RETURN c.id AS id, c.name AS name, size(neighbors) AS conflict_count, c.color AS color, c.day AS day, c.time_slot AS time_slot
            ORDER BY c.name
        """)
    return render_template('optimasi.html', courses=courses, computation_time=computation_time, num_nodes=num_nodes, num_edges=num_edges, chromatic_number=chromatic_number, conflict_time=conflict_time, coloring_time=coloring_time)

if __name__ == '__main__':
    app.run(debug=True, port=5001)