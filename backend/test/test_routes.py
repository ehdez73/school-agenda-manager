import json
from backend.app import app
from backend.populate_db import populate_db
from backend.models import Session


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
    resp2 = c.post('/subjects', json={'id': 'TST1', 'name': 'Prueba', 'weekly_hours': 2})
    assert resp2.status_code == 201
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
    resp = c.get('/api/timetable')
    assert resp.status_code == 404
    # clear assignments should still return ok
    resp2 = c.delete('/api/timetable')
    assert resp2.status_code == 200
