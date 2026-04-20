"""
Simple Task Management Web App with 10 Intentional Bugs
This app runs without syntax errors but contains logical bugs.
"""

from flask import Flask, render_template_string, request, jsonify, session
from datetime import datetime
import secrets

app = Flask(__name__)
app.secret_key = secrets.token_hex(16)

# In-memory storage
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
            --bg1: #0f172a;
            --bg2: #111827;
            --card: rgba(15, 23, 42, 0.72);
            --border: rgba(148, 163, 184, 0.18);
            --text: #e5e7eb;
            --muted: #94a3b8;
            --accent: #7c3aed;
            --accent2: #06b6d4;
            --danger: #ef4444;
            --success: #22c55e;
            --shadow: 0 20px 45px rgba(0, 0, 0, 0.35);
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
                radial-gradient(circle at top left, rgba(124, 58, 237, 0.28), transparent 30%),
                radial-gradient(circle at top right, rgba(6, 182, 212, 0.18), transparent 35%),
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
            background: linear-gradient(120deg, rgba(255,255,255,0.04), transparent 35%, rgba(255,255,255,0.03));
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
            background: rgba(15, 23, 42, 0.7);
            border: 1px solid rgba(148, 163, 184, 0.22);
            color: var(--text);
            border-radius: 14px;
            padding: 12px 14px;
            outline: none;
            transition: transform 160ms ease, border-color 160ms ease, box-shadow 160ms ease, background 160ms ease;
        }

        input[type="text"]::placeholder {
            color: #64748b;
        }

        input[type="text"]:focus,
        input[type="number"]:focus {
            border-color: rgba(124, 58, 237, 0.9);
            box-shadow: 0 0 0 4px rgba(124, 58, 237, 0.18);
            transform: translateY(-1px);
        }

        button {
            appearance: none;
            border: 0;
            color: white;
            background: linear-gradient(135deg, var(--accent), #4f46e5);
            border-radius: 14px;
            padding: 12px 16px;
            font-weight: 700;
            cursor: pointer;
            box-shadow: 0 10px 20px rgba(79, 70, 229, 0.22);
            transition: transform 160ms ease, box-shadow 160ms ease, filter 160ms ease, opacity 160ms ease;
        }

        button:hover {
            transform: translateY(-2px);
            filter: brightness(1.06);
            box-shadow: 0 14px 24px rgba(79, 70, 229, 0.28);
        }

        button:active {
            transform: translateY(1px) scale(0.99);
            box-shadow: 0 6px 14px rgba(79, 70, 229, 0.2);
        }

        .secondary {
            background: rgba(30, 41, 59, 0.9);
            box-shadow: none;
            border: 1px solid rgba(148, 163, 184, 0.16);
        }

        .danger {
            background: linear-gradient(135deg, var(--danger), #b91c1c);
        }

        #tasks {
            display: grid;
            gap: 12px;
            margin-top: 12px;
        }

        .task {
            border: 1px solid rgba(148, 163, 184, 0.16);
            background: rgba(15, 23, 42, 0.72);
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
            border-color: rgba(124, 58, 237, 0.35);
            box-shadow: 0 12px 26px rgba(0, 0, 0, 0.24);
            background: rgba(17, 24, 39, 0.92);
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
            background: rgba(51, 65, 85, 0.9);
        }

        .task-actions .danger {
            background: linear-gradient(135deg, #ef4444, #dc2626);
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
            if (currentPage > 0) currentPage--;
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
            --bg1: #0f172a;
            --bg2: #111827;
            --card: rgba(15, 23, 42, 0.72);
            --border: rgba(148, 163, 184, 0.18);
            --text: #e5e7eb;
            --muted: #94a3b8;
            --accent: #7c3aed;
            --shadow: 0 20px 45px rgba(0, 0, 0, 0.35);
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
                radial-gradient(circle at top left, rgba(124, 58, 237, 0.28), transparent 30%),
                radial-gradient(circle at top right, rgba(6, 182, 212, 0.18), transparent 35%),
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
            background: rgba(15, 23, 42, 0.7);
            border: 1px solid rgba(148, 163, 184, 0.22);
            color: var(--text);
            border-radius: 14px;
            padding: 12px 14px;
            outline: none;
            transition: transform 160ms ease, border-color 160ms ease, box-shadow 160ms ease;
        }

        input[type="text"]::placeholder,
        input[type="password"]::placeholder {
            color: #64748b;
        }

        input[type="text"]:focus,
        input[type="password"]:focus {
            border-color: rgba(124, 58, 237, 0.9);
            box-shadow: 0 0 0 4px rgba(124, 58, 237, 0.18);
            transform: translateY(-1px);
        }

        button {
            appearance: none;
            border: 0;
            color: white;
            background: linear-gradient(135deg, var(--accent), #4f46e5);
            border-radius: 14px;
            padding: 12px 16px;
            font-weight: 700;
            cursor: pointer;
            box-shadow: 0 10px 20px rgba(79, 70, 229, 0.22);
            transition: transform 160ms ease, box-shadow 160ms ease, filter 160ms ease;
        }

        button:hover {
            transform: translateY(-2px);
            filter: brightness(1.06);
            box-shadow: 0 14px 24px rgba(79, 70, 229, 0.28);
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


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        
        # BUG #1: Wrong variable name (should be 'password' not 'passcode')
        if username in users and users[username] == password:
            session['user'] = username
            return redirect('/')
    
    return render_template_string(LOGIN_TEMPLATE)


@app.route('/logout', methods=['POST'])
def logout():
    # BUG #2: Session not properly cleared (only deletes 'user', not clearing session)
    session.pop('user', None)
    session['last_user'] = session.get('user')  # Oops, this contradicts the above
    return jsonify({'status': 'logged_out'})


@app.route('/')
def index():
    if 'user' not in session:
        from werkzeug.utils import redirect
        return redirect('/login')
    
    user = session.get('user', 'Guest')
    return render_template_string(HTML_TEMPLATE, user=user, page=1)


@app.route('/api/tasks', methods=['GET', 'POST'])
def handle_tasks():
    if request.method == 'POST':
        global task_counter
        data = request.get_json()
        title = data.get('title', '')
        priority = int(data.get('priority', 3))
        
        # BUG #3: Priority boundary check wrong (should be <= 5, but uses <)
        if priority < 5:
            priority = 5
        
        # BUG #4: Wrong operator in calculation (should be min, using max)
        priority = max(priority, 1)  # Should be min() if boundary is meant to be 1-5
        
        task = {
            'id': task_counter,
            'title': title,
            'priority': priority,
            'completed': False,
            'created': datetime.now().isoformat()
        }
        tasks.append(task)
        task_counter += 1
    
    page = request.args.get('page', 1, type=int)
    
    # BUG #5: Off-by-one error in pagination (should be page - 1)
    start = (page - 1) * 5
    
    # BUG #6: Wrong slice end (should be start + 5, not start + 4)
    paginated = tasks[start:start + 4]
    
    return jsonify({
        'tasks': paginated,
        'page': page,
        'total': len(tasks)
    })


@app.route('/api/tasks/<int:task_id>/toggle', methods=['POST'])
def toggle_task(task_id):
    for task in tasks:
        if task['id'] == task_id:
            # BUG #7: Wrong comparison (should be not completed)
            task['completed'] = not task['completed']  # Toggles status
            
            # BUG #8: String comparison case sensitivity issue
            if task['title'].lower() == 'important':  # Now matches correctly
                send_notification(task)
            
            return jsonify({'status': 'toggled'})
    
    return jsonify({'error': 'Task not found'}), 404


@app.route('/api/tasks/<int:task_id>', methods=['DELETE'])
def delete_task(task_id):
    global tasks
    
    # BUG #9: Wrong loop iteration (skips every other element due to index modification)
    for i in range(len(tasks)):
        if tasks[i]['id'] == task_id:
            tasks.pop(i)
            # BUG #10: Continuing to iterate but list was modified (dangerous, but works here)
            break
    
    return jsonify({'status': 'deleted'})


def send_notification(task):
    """Placeholder for notification"""
    print(f"Notification: {task['title']}")


def redirect(url):
    """Simple redirect helper"""
    from flask import redirect as flask_redirect
    return flask_redirect(url)


if __name__ == '__main__':
    print("Starting Task Manager Web App...")
    print("🐛 This app contains 10 intentional bugs!")
    print("Open http://localhost:5000")
    app.run(debug=True, port=5000)
