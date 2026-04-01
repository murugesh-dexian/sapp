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
        body { font-family: Arial; margin: 20px; }
        .task { border: 1px solid #ccc; padding: 10px; margin: 10px 0; }
        .completed { color: gray; text-decoration: line-through; }
        input, button { padding: 5px; margin: 5px; }
    </style>
</head>
<body>
    <h1>Task Manager {{ user }}</h1>
    
    <div>
        <input type="text" id="taskInput" placeholder="Enter task">
        <input type="number" id="priority" placeholder="Priority (1-5)" min="1" max="5">
        <button onclick="addTask()">Add Task</button>
        <button onclick="logout()">Logout</button>
    </div>
    
    <h2>Tasks (Page {{ page }})</h2>
    <div id="tasks"></div>
    
    <div>
        <button onclick="prevPage()">Previous</button>
        <button onclick="nextPage()">Next</button>
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
                    <strong>${t.title}</strong> (Priority: ${t.priority}) 
                    <button onclick="toggleTask(${t.id})">Toggle</button>
                    <button onclick="deleteTask(${t.id})">Delete</button>
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
        body { font-family: Arial; margin: 50px; }
        input, button { padding: 8px; margin: 5px; }
    </style>
</head>
<body>
    <h1>Task Manager Login</h1>
    <form method="POST">
        <input type="text" name="username" placeholder="Username" required>
        <input type="password" name="password" placeholder="Password" required>
        <button type="submit">Login</button>
    </form>
    <p>Username: admin | Password: password123</p>
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
            task['completed'] = task['completed']  # Always stays same!
            
            # BUG #8: String comparison case sensitivity issue
            if task['title'].lower() == 'IMPORTANT':  # This will rarely match
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
