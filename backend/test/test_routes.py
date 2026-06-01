import time
from backend.app import app
from backend.populate_db import populate_db
from backend.routes import timetable as timetable_routes


def client():
    populate_db()
    return app.test_client()


def test_get_courses_returns_list():
    c = client()
    resp = c.get('/courses')
    assert resp.status_code == 200
    data = resp.get_json()
    assert isinstance(data, list)


def test_add_course_and_get_course():
    c = client()
    resp = c.post('/courses', json={'name': '9º', 'num_lines': 1})
    assert resp.status_code == 201
    data = resp.get_json()
    assert data['id'] == '9º'
    # fetch it
    resp2 = c.get('/courses/9º')
    assert resp2.status_code == 200


def test_get_subjects_and_add_subject():
    c = client()
    resp = c.get('/subjects')
    assert resp.status_code == 200
    before = resp.get_json()
    # add a new subject
    resp2 = c.post('/subjects', json={'id': 'TST1', 'name': 'Prueba', 'color': '#00ff00', 'weekly_hours': 2})
    assert resp2.status_code == 201
    created = resp2.get_json()
    assert created['color'] == '#00ff00'
    after = c.get('/subjects').get_json()
    assert len(after) >= len(before)


def test_get_teachers_and_add_teacher():
    c = client()
    resp = c.get('/teachers')
    assert resp.status_code == 200
    # add teacher without subjects
    resp2 = c.post('/teachers', json={'name': 'Prueba', 'max_hours_week': 5})
    assert resp2.status_code == 201
    data = resp2.get_json()
    assert data['name'] == 'Prueba'


def test_add_subject_group_with_color():
    c = client()
    resp = c.post('/subject-groups', json={'name': 'Grupo Color', 'subjects': ['REL1', 'ATE1'], 'color': '#ffaa00'})
    assert resp.status_code == 201
    data = resp.get_json()
    assert data['name'] == 'Grupo Color'
    assert data['color'] == '#ffaa00'


def test_get_and_set_config():
    c = client()
    resp = c.get('/config')
    assert resp.status_code == 200
    cfg = resp.get_json()
    # update config
    resp2 = c.post('/config', json={'classes_per_day': 4, 'days_per_week': 5, 'hour_names': ['a','b','c','d']})
    assert resp2.status_code == 200
    updated = resp2.get_json()
    assert updated['classes_per_day'] == 4


def test_timetable_endpoints_empty_and_clear():
    c = client()
    # Initially no assignments so GET should 404
    resp = c.get('/timetable')
    assert resp.status_code == 404
    # clear assignments should still return ok
    resp2 = c.delete('/timetable')
    assert resp2.status_code == 200


def test_timetable_status_current_idle_when_no_tasks():
    c = client()
    tm = timetable_routes.task_manager
    with tm._lock:
        tm._tasks.clear()
        tm._cancelled.clear()
        tm._current_task_id = None
        tm._last_task_id = None

    resp = c.get('/timetable/status/current')
    assert resp.status_code == 200
    data = resp.get_json()
    assert data['status'] == 'idle'
    assert data['task_id'] is None


def test_timetable_post_is_idempotent_with_running_task():
    c = client()
    tm = timetable_routes.task_manager
    running_task_id = 'running-task-id'
    with tm._lock:
        tm._tasks.clear()
        tm._cancelled.clear()
        tm._tasks[running_task_id] = {
            'status': 'running',
            'error': None,
            'details': None,
            'created_at': time.time(),
        }
        tm._current_task_id = running_task_id
        tm._last_task_id = running_task_id

    resp = c.post('/timetable')
    assert resp.status_code == 202
    data = resp.get_json()
    assert data['task_id'] == running_task_id
    assert data['status'] == 'running'


def test_timetable_status_current_returns_latest_terminal_task():
    c = client()
    tm = timetable_routes.task_manager
    latest_task_id = 'latest-task-id'
    with tm._lock:
        tm._tasks.clear()
        tm._cancelled.clear()
        tm._tasks[latest_task_id] = {
            'status': 'success',
            'error': None,
            'details': None,
            'created_at': time.time(),
        }
        tm._current_task_id = None
        tm._last_task_id = latest_task_id

    resp = c.get('/timetable/status/current')
    assert resp.status_code == 200
    data = resp.get_json()
    assert data['task_id'] == latest_task_id
    assert data['status'] == 'success'
