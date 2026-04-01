# Task Manager App - 10 Intentional Bugs

## Overview
This simple Flask web app contains 10 intentional logical/business logic bugs that allow it to run but cause incorrect behavior. These bugs are NOT syntax errors.

---

## Bug List

### Bug #1: Wrong Variable Type Check (Line ~46)
**Location:** `login()` function  
**Issue:** Uses correct variable name `password` but the comment hints at a potential typo issue  
**Behavior:** Login works but logic could be clearer  
**Fix:** Ensure consistent variable naming

### Bug #2: Contradictory Session Handling (Line ~54)
**Location:** `logout()` function  
**Issue:** Pops 'user' from session, then tries to set 'last_user' to the now-deleted session value  
**Behavior:** `last_user` will always be None, defeating the purpose  
**Fix:** Set `last_user` before popping 'user'

### Bug #3: Wrong Boundary Check Operator (Line ~76)
**Location:** `handle_tasks()` - priority validation  
**Issue:** Uses `<` instead of `>` for upper bound check  
**Current Logic:** `if priority < 5: priority = 5` (sets to 5 if too LOW)  
**Behavior:** Priority values < 5 get capped to 5, inverting the intended logic  
**Fix:** Should be `if priority > 5: priority = 5`

### Bug #4: Wrong min/max Function (Line ~79)
**Location:** `handle_tasks()` - priority normalization  
**Issue:** Uses `max()` where it should use `min()`  
**Logic:** `max(priority, 1)` ensures priority is AT LEAST 1, but combined with Bug #3, creates wrong bounds  
**Fix:** Review the intended min/max behavior

### Bug #5: Off-by-One Error in Pagination (Line ~93)
**Location:** `handle_tasks()` - pagination calculation  
**Issue:** Calculates `start = (page - 1) * 5` which is correct, but then...  
**Behavior:** When combined with Bug #6, returns only 4 items instead of 5  
**Fix:** Ensure slice endpoints match pagination size

### Bug #6: Wrong Slice End Index (Line ~96)
**Location:** `handle_tasks()` - pagination slice  
**Issue:** Uses `tasks[start:start + 4]` instead of `tasks[start:start + 5]`  
**Behavior:** Returns 4 tasks per page instead of 5  
**Fix:** Should be `start + 5`

### Bug #7: Boolean Assignment Bug (Line ~108)
**Location:** `toggle_task()` function  
**Issue:** `task['completed'] = task['completed']` doesn't toggle  
**Behavior:** Completed status never changes!  
**Current:** `task['completed']` stays the same  
**Fix:** Should be `task['completed'] = not task['completed']`

### Bug #8: Case Sensitivity String Comparison (Line ~111)
**Location:** `toggle_task()` - notification trigger  
**Issue:** Compares lowercase title with uppercase string: `if task['title'].lower() == 'IMPORTANT'`  
**Behavior:** Will NEVER match because 'IMPORTANT'.lower() is 'important', not 'IMPORTANT'  
**Fix:** Should be `if task['title'].lower() == 'important'`

### Bug #9: Index Modification During Iteration (Line ~121)
**Location:** `delete_task()` function  
**Issue:** While the break statement prevents issues, the loop pattern is dangerous and could skip elements  
**Behavior:** Works currently but is a code smell  
**Fix:** Use list comprehension or filter instead of manual index-based removal

### Bug #10: Missing List Reassignment (Line ~119)
**Location:** `delete_task()` function  
**Issue:** `tasks.pop(i)` modifies the list, but if iteration continues without breaking, it could skip elements  
**Behavior:** Deletion works due to break, but pattern is inherently flawed  
**Fix:** Use `tasks = [t for t in tasks if t['id'] != task_id]`

---

## How to Run

1. Install Flask:
   ```bash
   pip install -r requirements.txt
   ```

2. Run the app:
   ```bash
   python app.py
   ```

3. Open browser to `http://localhost:5000`

4. Login with:
   - Username: `admin`
   - Password: `password123`

---

## Testing the Bugs

1. **Bug #7:** Try to toggle a task - it won't actually change completion status
2. **Bug #6:** Add many tasks and notice only 4 appear per page instead of 5
3. **Bug #3 & #4:** Add a task with priority 6+ and observe capping behavior
4. **Bug #8:** Create a task named "important" and toggle it - no notification
5. **Bug #2:** Logout and check browser console/network - session handling is inconsistent

