"""
Simple Task Management Web App with SQLite-backed login and per-user task storage.
"""

from flask import Flask, render_template_string, request, jsonify, session
from datetime import datetime
import secrets
import sqlite3
from pathlib import Path

app = Flask(__name__)
app.secret_key = secrets.token_hex(16)

DATABASE_PATH = Path("task_manager.db")

# In-memory storage retained for compatibility with existing code/tests.
tasks = []
task_counter = 1
users = {"admin": "password123"}

# HTML Template
HTML_TEMPLATE = """
<!DOCTYPE html>
<html>
<head>
    <title>Task Manager</title>
    <style>
        :root {
            color-scheme: dark;
            --bg1: #0b0a08;
            --bg2: #17120a;
            --card: rgba(20, 16, 8, 0.78);
            --border: rgba(212, 175, 55, 0.2);
            --text: #f8e7b2;
            --muted: #c9b46a;
            --accent: #d4af37;
            --accent2: #f0c75e;
            --danger: #b45309;
            --success: #f59e0b;
            --shadow: 0 20px 45px rgba(0, 0, 0, 0.45);
        }

        * {
            box-sizing: border-box;
        }

        body {
            font-family: Inter, ui-sans-serif, system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
            margin: 0;
            min-height: 100vh;
            color: var(--text);
            background:
                radial-gradient(circle at top left, rgba(212, 175, 55, 0.22), transparent 30%),
                radial-gradient(circle at top right, rgba(240, 199, 94, 0.14), transparent 35%),
                linear-gradient(180deg, var(--bg1), var(--bg2));
            display: flex;
            justify-content: center;
            align-items: flex-start;
            padding: 32px 18px;
        }

        body::before {
            content: "";
            position: fixed;
            inset: 0;
            pointer-events: none;
            background: linear-gradient(120deg, rgba(255,255,255,0.03), transparent 35%, rgba(255,255,255,0.02));
            opacity: 0.65;
        }

        .app-shell {
            width: 100%;
            max-width: 900px;
            position: relative;
            z-index: 1;
        }

        h1, h2 {
            letter-spacing: -0.03em;
            margin: 0 0 16px;
        }

        h1 {
            font-size: 2.4rem;
            font-weight: 800;
            text-shadow: 0 10px 30px rgba(0, 0, 0, 0.25);
        }

        h2 {
            font-size: 1.1rem;
            font-weight: 700;
            color: var(--muted);
            margin-top: 24px;
        }

        .subtle {
            color: var(--muted);
            margin-top: 6px;
            margin-bottom: 24px;
        }

        .panel {
            background: var(--card);
            border: 1px solid var(--border);
            backdrop-filter: blur(14px);
            border-radius: 20px;
            box-shadow: var(--shadow);
            padding: 24px;
        }

        .toolbar,
        .pagination,
        form {
            display: flex;
            gap: 10px;
            flex-wrap: wrap;
            align-items: center;
        }

        input, button {
            font: inherit;
        }

        input[type="text"],
        input[type="number"] {
            background: rgba(20, 16, 8, 0.75);
            border: 1px solid rgba(212, 175, 55, 0.25);
            color: var(--text);
            border-radius: 14px;
            padding: 12px 14px;
            outline: none;
            transition: transform 160ms ease, border-color 160ms ease, box-shadow 160ms ease, background 160ms ease;
        }

        input[type="text"]::placeholder {
            color: #8c7b42;
        }

        input[type="text"]:focus,
        input[type="number"]:focus {
            border-color: rgba(212, 175, 55, 0.95);
            box-shadow: 0 0 0 4px rgba(212, 175, 55, 0.16);
            transform: translateY(-1px);
        }

        button {
            appearance: none;
            border: 0;
            color: #1a1407;
            background: linear-gradient(135deg, var(--accent), #f0c75e);
            border-radius: 14px;
            padding: 12px 16px;
            font-weight: 700;
            cursor: pointer;
            box-shadow: 0 10px 20px rgba(212, 175, 55, 0.2);
            transition: transform 160ms ease, box-shadow 160ms ease, filter 160ms ease, opacity 160ms ease;
        }

        button:hover {
            transform: translateY(-2px);
            filter: brightness(1.06);
            box-shadow: 0 14px 24px rgba(212, 175, 55, 0.26);
        }

        button:active {
            transform: translateY(1px) scale(0.99);
            box-shadow: 0 6px 14px rgba(212, 175, 55, 0.18);
        }

        .secondary {
            background: rgba(32, 24, 12, 0.92);
            color: var(--text);
            box-shadow: none;
            border: 1px solid rgba(212, 175, 55, 0.18);
        }

        .danger {
            background: linear-gradient(135deg, #b45309, #7c2d12);
            color: #fff7d6;
        }

        #tasks {
            display: grid;
            gap: 12px;
            margin-top: 12px;
        }

        .task {
            border: 1px solid rgba(212, 175, 55, 0.16);
            background: rgba(20, 16, 8, 0.78);
            padding: 14px 16px;
            border-radius: 16px;
            display: flex;
            justify-content: space-between;
            align-items: center;
            gap: 12px;
            transition: transform 180ms ease, border-color 180ms ease, background 180ms ease, box-shadow 180ms ease;
        }

        .task:hover {
            transform: translateY(-2px);
            border-color: rgba(212, 175, 55, 0.38);
            box-shadow: 0 12px 26px rgba(0, 0, 0, 0.24);
            background: rgba(28, 22, 11, 0.95);
        }

        .task strong {
            display: block;
            margin-bottom: 4px;
        }

        .task-meta {
            color: var(--muted);
            font-size: 0.92rem;
        }

        .completed {
            opacity: 0.7;
        }

        .completed strong {
            text-decoration: line-through;
        }

        .task-actions {
            display: flex;
            gap: 8px;
            flex-wrap: wrap;
        }

        .task-actions button {
            padding: 10px 14px;
            border-radius: 12px;
        }

        .task-actions .secondary {
            background: rgba(45, 34, 17, 0.92);
        }

        .task-actions .danger {
            background: linear-gradient(135deg, #b45309, #92400e);
        }

        .topbar {
            display: flex;
            justify-content: space-between;
            gap: 16px;
            align-items: flex-start;
            margin-bottom: 18px;
            flex-wrap: wrap;
        }

        .welcome {
            margin: 0;
        }

        .pagination {
            margin-top: 18px;
        }

        .pagination button {
            min-width: 112px;
        }

        @media (max-width: 640px) {
            body {
                padding: 18px 12px;
            }

            .panel {
                padding: 18px;
                border-radius: 18px;
            }

            h1 {
                font-size: 1.9rem;
            }

            .task {
                flex-direction: column;
                align-items: flex-start;
            }

            .task-actions {
                width: 100%;
            }

            .task-actions button,
            .pagination button,
            .toolbar button,
            form button {
                width: 100%;
            }

            .toolbar,
            .pagination,
            form {
                width: 100%;
            }

            input[type="text"],
            input[type="number"] {
                width: 100%;
            }
        }
    </style>
</head>
<body>
    <div class="app-shell">
        <div class="topbar">
            <div>
                <h1>Task Manager {{ user }}</h1>
                <p class="subtle">A cleaner way to keep track of what matters.</p>
            </div>
        </div>

        <div class="panel">
            <div class="toolbar">
                <input type="text" id="taskInput" placeholder="Enter task">
                <input type="number" id="priority" placeholder="Priority (1-5)" min="1" max="5">
                <button onclick="addTask()">Add Task</button>
                <button class="secondary" onclick="logout()">Logout</button>
            </div>
            
            <h2>Tasks (Page {{ page }})</h2>
            <div id="tasks"></div>
            
            <div class="pagination">
                <button class="secondary" onclick="prevPage()">Previous</button>
                <button class="secondary" onclick="nextPage()">Next</button>
            </div>
        </div>
    </div>

    <script>
        let currentPage = 1;
        
        async function loadTasks() {
            const res = await fetch('/api/tasks?page=' + currentPage);
            const data = await res.json();
            document.getElementById('tasks').innerHTML = '';
            data.tasks.forEach(t => {
                let div = document.createElement('div');
                div.className = 'task' + (t.completed ? ' completed' : '');
                div.innerHTML = `
                    <div>
                        <strong>${t.title}</strong>
                        <div class="task-meta">Priority: ${t.priority}</div>
                    </div>
                    <div class="task-actions">
                        <button onclick="toggleTask(${t.id})">Toggle</button>
                        <button class="danger" onclick="deleteTask(${t.id})">Delete</button>
                    </div>
                `;
                document.getElementById('tasks').appendChild(div);
            });
            document.querySelector('h2').textContent = 'Tasks (Page ' + data.page + ')';
        }
        
        async function addTask() {
            const title = document.getElementById('taskInput').value;
            const priority = document.getElementById('priority').value;
            if (title) {
                await fetch('/api/tasks', {
                    method: 'POST',
                    headers: {'Content-Type': 'application/json'},
                    body: JSON.stringify({title, priority})
                });
                loadTasks();
            }
        }
        
        async function toggleTask(id) {
            await fetch('/api/tasks/' + id + '/toggle', {method: 'POST'});
            loadTasks();
        }
        
        async function deleteTask(id) {
            await fetch('/api/tasks/' + id, {method: 'DELETE'});
            loadTasks();
        }
        
        async function logout() {
            await fetch('/logout', {method: 'POST'});
            window.location.href = '/login';
        }
        
        function nextPage() {
            currentPage++;
            loadTasks();
        }
        
        function prevPage() {
            if (currentPage > 1) currentPage--;
            loadTasks();
        }
        
        loadTasks();
    </script>
</body>
</html>
"""

LOGIN_TEMPLATE = """
<!DOCTYPE html>
<html>
<head>
    <title>Login</title>
    <style>
        :root {
            color-scheme: dark;
            --bg1: #0b0a08;
            --bg2: #17120a;
            --card: rgba(20, 16, 8, 0.78);
            --border: rgba(212, 175, 55, 0.2);
            --text: #f8e7b2;
            --muted: #c9b46a;
            --accent: #d4af37;
            --shadow: 0 20px 45px rgba(0, 0, 0, 0.45);
        }

        * {
            box-sizing: border-box;
        }

        body {
            font-family: Inter, ui-sans-serif, system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
            margin: 0;
            min-height: 100vh;
            color: var(--text);
            background:
                radial-gradient(circle at top left, rgba(212, 175, 55, 0.22), transparent 30%),
                radial-gradient(circle at top right, rgba(240, 199, 94, 0.14), transparent 35%),
                linear-gradient(180deg, var(--bg1), var(--bg2));
            display: flex;
            justify-content: center;
            align-items: center;
            padding: 24px;
        }

        .login-card {
            width: 100%;
            max-width: 420px;
            background: var(--card);
            border: 1px solid var(--border);
            backdrop-filter: blur(14px);
            border-radius: 20px;
            box-shadow: var(--shadow);
            padding: 28px;
        }

        h1 {
            margin: 0 0 18px;
            letter-spacing: -0.03em;
            font-size: 2rem;
        }

        p {
            color: var(--muted);
            margin-top: 16px;
            margin-bottom: 0;
        }

        form {
            display: grid;
            gap: 10px;
        }

        input, button {
            font: inherit;
        }

        input[type="text"],
        input[type="password"] {
            width: 100%;
            background: rgba(20, 16, 8, 0.75);
            border: 1px solid rgba(212, 175, 55, 0.25);
            color: var(--text);
            border-radius: 14px;
            padding: 12px 14px;
            outline: none;
            transition: transform 160ms ease, border-color 160ms ease, box-shadow 160ms ease;
        }

        input[type="text"]::placeholder,
        input[type="password"]::placeholder {
            color: #8c7b42;
        }

        input[type="text"]:focus,
        input[type="password"]:focus {
            border-color: rgba(212, 175, 55, 0.95);
            box-shadow: 0 0 0 4px rgba(212, 175, 55, 0.16);
            transform: translateY(-1px);
        }

        button {
            appearance: none;
            border: 0;
            color: #1a1407;
            background: linear-gradient(135deg, var(--accent), #f0c75e);
            border-radius: 14px;
            padding: 12px 16px;
            font-weight: 700;
            cursor: pointer;
            box-shadow: 0 10px 20px rgba(212, 175, 55, 0.2);
            transition: transform 160ms ease, box-shadow 160ms ease, filter 160ms ease;
        }

        button:hover {
            transform: translateY(-2px);
            filter: brightness(1.06);
            box-shadow: 0 14px 24px rgba(212, 175, 55, 0.26);
        }

        button:active {
            transform: translateY(1px) scale(0.99);
        }
    </style>
</head>
<body>
    <div class="login-card">
        <h1>Task Manager Login</h1>
        <form method="POST">
            <input type="text" name="username" placeholder="Username" required>
            <input type="password" name="password" placeholder="Password" required>
            <button type="submit">Login</button>
        </form>
        <p>Username: admin | Password: password123</p>
    </div>
</body>
</html>
"""


def get_db():
    conn = sqlite3.connect(DATABASE_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    with get_db() as conn:
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT UNIQUE NOT NULL,
                password TEXT NOT NULL
            )
            """
        )
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS tasks (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                title TEXT NOT NULL,
                priority INTEGER NOT NULL,
                completed INTEGER NOT NULL DEFAULT 0,
                created TEXT NOT NULL,
                FOREIGN KEY(user_id) REFERENCES users(id)
            )
            """
        )
        cursor = conn.execute("SELECT id FROM users WHERE username = ?", ("admin",))
        if cursor.fetchone() is None:
            conn.execute("INSERT INTO users (username, password) VALUES (?, ?)", ("admin", "password123"))


def get_user_id(username):
    with get_db() as conn:
        row = conn.execute("SELECT id FROM users WHERE username = ?", (username,)).fetchone()
        return row["id"] if row else None


def current_user_id():
    username = session.get("user")
    if not username:
        return None
    return get_user_id(username)


def load_user_tasks(username):
    user_id = get_user_id(username)
    if user_id is None:
        return []
    with get_db() as conn:
        rows = conn.execute(
            """
            SELECT id, title, priority, completed, created
            FROM tasks
            WHERE user_id = ?
            ORDER BY id DESC
            """,
            (user_id,),
        ).fetchall()
        return [
            {
                "id": row["id"],
                "title": row["title"],
                "priority": row["priority"],
                "completed": bool(row["completed"]),
                "created": row["created"],
            }
            for row in rows
        ]


def save_task_to_db(username, title, priority):
    user_id = get_user_id(username)
    if user_id is None:
        return
    with get_db() as conn:
        conn.execute(
            """
            INSERT INTO tasks (user_id, title, priority, completed, created)
            VALUES (?, ?, ?, 0, ?)
            """,
            (user_id, title, priority, datetime.now().isoformat()),
        )


def sync_in_memory_tasks(username):
    global tasks, task_counter
    user_tasks = load_user_tasks(username)
    tasks.clear()
    tasks.extend(user_tasks)
    task_counter = (max((task["id"] for task in user_tasks), default=0) + 1) if user_tasks else 1


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')

        if username in users and users[username] == password:
            session['user'] = username
            session['user_id'] = get_user_id(username)
            sync_in_memory_tasks(username)
            return redirect('/')

    return render_template_string(LOGIN_TEMPLATE)


@app.route('/logout', methods=['POST'])
def logout():
    session.pop('user', None)
    session.pop('user_id', None)
    session['last_user'] = session.get('user')
    return jsonify({'status': 'logged_out'})


@app.route('/')
def index():
    if 'user' not in session:
        from werkzeug.utils import redirect
        return redirect('/login')

    user = session.get('user', 'Guest')
    sync_in_memory_tasks(user)
    return render_template_string(HTML_TEMPLATE, user=user, page=1)


@app.route('/api/tasks', methods=['GET', 'POST'])
def handle_tasks():
    username = session.get('user')
    if not username:
        return jsonify({'error': 'Unauthorized'}), 401

    if request.method == 'POST':
        global task_counter
        data = request.get_json() or {}
        title = data.get('title', '')
        priority = int(data.get('priority', 3))

        if priority > 10:
            priority = 10

        priority = max(priority, 1)

        save_task_to_db(username, title, priority)
        sync_in_memory_tasks(username)

    page = request.args.get('page', 1, type=int)
    if page < 1:
        page = 1

    start = (page - 1) * 5
    user_tasks = load_user_tasks(username)
    paginated = user_tasks[start:start + 4]

    return jsonify({
        'tasks': paginated,
        'page': page,
        'total': len(user_tasks)
    })


@app.route('/api/tasks/<int:task_id>/toggle', methods=['POST'])
def toggle_task(task_id):
    username = session.get('user')
    if not username:
        return jsonify({'error': 'Unauthorized'}), 401

    user_id = get_user_id(username)
    with get_db() as conn:
        task = conn.execute(
            "SELECT id, title, completed FROM tasks WHERE id = ? AND user_id = ?",
            (task_id, user_id),
        ).fetchone()
        if task is not None:
            new_completed = 0 if task["completed"] else 1
            conn.execute(
                "UPDATE tasks SET completed = ? WHERE id = ? AND user_id = ?",
                (new_completed, task_id, user_id),
            )
            if task['title'].lower() == 'important':
                send_notification({'title': task['title']})
            sync_in_memory_tasks(username)
            return jsonify({'status': 'toggled'})

    return jsonify({'error': 'Task not found'}), 404


@app.route('/api/tasks/<int:task_id>', methods=['DELETE'])
def delete_task(task_id):
    username = session.get('user')
    if not username:
        return jsonify({'error': 'Unauthorized'}), 401

    user_id = get_user_id(username)
    with get_db() as conn:
        conn.execute("DELETE FROM tasks WHERE id = ? AND user_id = ?", (task_id, user_id))

    sync_in_memory_tasks(username)
    return jsonify({'status': 'deleted'})


def send_notification(task):
    """Placeholder for notification"""
    print(f"Notification: {task['title']}")


def redirect(url):
    """Simple redirect helper"""
    from flask import redirect as flask_redirect
    return flask_redirect(url)


if __name__ == '__main__':
    init_db()
    print("Starting Task Manager Web App...")
    print("Open http://localhost:5000")
    app.run(debug=True, port=5000)
