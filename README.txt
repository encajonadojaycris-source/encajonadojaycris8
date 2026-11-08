LABORATORY ACTIVITY 8 – CRUD + CLASSMATE API

Project layout:
app.py
init_db.py
requirements.txt
students.db                 (created when init_db.py runs)
template/
    index.html

IMPORTANT:
- This project uses the existing singular folder name "template" from your earlier Flask project.
- If your folder is named "templates" instead, change:
      app = Flask(__name__, template_folder="template")
  to:
      app = Flask(__name__, template_folder="templates")

RUN IN CODESPACES:
1. python init_db.py
2. pip install -r requirements.txt
3. python app.py
4. Open the forwarded port shown by Codespaces.

API ENDPOINTS:
GET     /api/students       list all students
POST    /api/students       add a student
GET     /api/students/1     get one student by database ID
PUT     /api/students/1     update one student
DELETE  /api/students/1     delete one student

CLASSMATE:
- Enter the classmate's public URL ending in /api/students on the webpage.
- The browser first tries a direct request. If CORS blocks it, the app tries its
  read-only Flask proxy at /api/classmate?url=...
- Remote records can only be viewed. No remote update/delete features exist.

DEPLOYMENT:
- Keep using your existing GitHub repository and existing Render web service.
- Commit and push the updated files.
- Ensure requirements.txt includes Flask, gunicorn, and requests.
- On Render, use your existing start command, commonly: gunicorn app:app
- For persistent SQLite data on Render, note that the default filesystem may be
  temporary across redeploys/restarts unless a persistent disk is configured.
