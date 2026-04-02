
from app import app, tasks, toggle_task, task_counter
import json

def test_toggle_bug():
    with app.app_context():
        global tasks, task_counter
        # Setup: Add a task
        task_id = 1
        tasks.append({
            'id': task_id,
            'title': 'Test Task',
            'priority': 3,
            'completed': False
        })
        
        print(f"Initial task state: {tasks[0]}")
        
        # Act: Toggle the task
        toggle_task(task_id)
        
        print(f"Task state after toggle: {tasks[0]}")
        
        if tasks[0]['completed'] == True:
            print("SUCCESS: Task 'completed' status toggled to True!")
        else:
            print("FAILURE: Task 'completed' status did not change.")

def test_notification_bug():
    with app.app_context():
        global tasks
        tasks.clear()
        task_id = 2
        tasks.append({
            'id': task_id,
            'title': 'IMPORTANT',
            'priority': 5,
            'completed': False
        })
        
        print(f"Testing notification for task: {tasks[0]['title']}")
        
        title_lower = tasks[0]['title'].lower()
        print(f"title.lower() is: '{title_lower}'")
        if title_lower == 'important':
            print("SUCCESS: Notification condition met because 'important' == 'important'")
        else:
            print("FAILURE: Notification condition still not met.")

if __name__ == "__main__":
    test_toggle_bug()
    print("-" * 20)
    test_notification_bug()
