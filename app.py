import os
import sqlite3
from urllib.parse import urlparse

import requests
from flask import Flask, jsonify, render_template, request

app = Flask(__name__, template_folder="template")
DATABASE = os.path.join(app.root_path, "students.db")


def get_db_connection():
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    return conn


def student_data_is_valid(data):
    required = ["student_id", "name", "program", "year", "section"]
    if not isinstance(data, dict):
        return False, "Send student information as JSON."
    missing = [field for field in required if data.get(field) in (None, "")]
    if missing:
        return False, "Missing required field(s): " + ", ".join(missing)
    try:
        year = int(data["year"])
    except (TypeError, ValueError):
        return False, "Year must be a number."
    if year < 1:
        return False, "Year must be at least 1."
    return True, ""


@app.route("/")
def home():
    return render_template("index.html")


# READ: Get all students
@app.route("/api/students", methods=["GET"])
def api_students():
    conn = get_db_connection()
    rows = conn.execute(
        "SELECT id, student_id, name, program, year, section FROM students ORDER BY id"
    ).fetchall()
    conn.close()
    return jsonify([dict(row) for row in rows])


# CREATE: Add a student
@app.route("/api/students", methods=["POST"])
def add_student():
    data = request.get_json(silent=True)
    valid, message = student_data_is_valid(data)
    if not valid:
        return jsonify({"error": message}), 400

    conn = get_db_connection()
    cursor = conn.execute(
        """INSERT INTO students (student_id, name, program, year, section)
           VALUES (?, ?, ?, ?, ?)""",
        (
            data["student_id"].strip(),
            data["name"].strip(),
            data["program"].strip(),
            int(data["year"]),
            data["section"].strip(),
        ),
    )
    conn.commit()
    new_id = cursor.lastrowid
    conn.close()
    return jsonify({"message": "Student added", "id": new_id}), 201


# READ: Get one student by database ID
@app.route("/api/students/<int:id>", methods=["GET"])
def api_get_student(id):
    conn = get_db_connection()
    student = conn.execute(
        "SELECT id, student_id, name, program, year, section FROM students WHERE id = ?",
        (id,),
    ).fetchone()
    conn.close()

    if student is None:
        return jsonify({"error": "Student not found"}), 404
    return jsonify(dict(student))


# UPDATE: Edit a student
@app.route("/api/students/<int:id>", methods=["PUT"])
def update_student(id):
    data = request.get_json(silent=True)
    valid, message = student_data_is_valid(data)
    if not valid:
        return jsonify({"error": message}), 400

    conn = get_db_connection()
    existing = conn.execute("SELECT id FROM students WHERE id = ?", (id,)).fetchone()
    if existing is None:
        conn.close()
        return jsonify({"error": "Student not found"}), 404

    conn.execute(
        """UPDATE students
           SET student_id = ?, name = ?, program = ?, year = ?, section = ?
           WHERE id = ?""",
        (
            data["student_id"].strip(),
            data["name"].strip(),
            data["program"].strip(),
            int(data["year"]),
            data["section"].strip(),
            id,
        ),
    )
    conn.commit()
    conn.close()
    return jsonify({"message": "Student updated", "id": id})


# DELETE: Remove a student
@app.route("/api/students/<int:id>", methods=["DELETE"])
def delete_student(id):
    conn = get_db_connection()
    cursor = conn.execute("DELETE FROM students WHERE id = ?", (id,))
    conn.commit()
    deleted = cursor.rowcount
    conn.close()

    if deleted == 0:
        return jsonify({"error": "Student not found"}), 404
    return jsonify({"message": "Student deleted", "id": id})


# Read-only server-side proxy for a classmate's public API.
# This is useful if the classmate's server does not allow browser CORS requests.
@app.route("/api/classmate", methods=["GET"])
def get_classmate_records():
    classmate_url = request.args.get("url", "").strip()
    parsed = urlparse(classmate_url)

    if parsed.scheme != "https" or not parsed.netloc:
        return jsonify({"error": "Enter a valid public HTTPS API URL."}), 400

    try:
        response = requests.get(classmate_url, timeout=20)
        response.raise_for_status()
        remote_data = response.json()
        if not isinstance(remote_data, list):
            return jsonify({"error": "The classmate API must return a JSON list."}), 502
        return jsonify(remote_data)
    except requests.RequestException as exc:
        return jsonify({"error": f"Could not retrieve classmate API: {exc}"}), 502
    except ValueError:
        return jsonify({"error": "The classmate API did not return valid JSON."}), 502


if __name__ == "__main__":
    app.run(debug=True)
