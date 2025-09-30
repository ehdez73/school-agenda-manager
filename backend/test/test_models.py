import json
from backend.models import Course, Subject, Teacher, Config


def test_course_to_dict():
    c = Course(id="1º", num_lines=2)
    d = c.to_dict()
    assert d["id"] == "1º"
    assert d["name"] == "1º"
    assert d["num_lines"] == 2


def test_subject_full_name_and_to_dict():
    # Subject with course relation
    course = Course(id="2º", num_lines=1)
    s = Subject(id="SUB1", name="Test", weekly_hours=3, max_hours_per_day=2, course=course)
    assert "Test (2º)" == s.full_name
    td = s.to_dict()
    assert td["id"] == "SUB1"
    assert td["full_name"] == "Test (2º)"


def test_teacher_to_dict_preferences():
    t = Teacher(id=1, name="Ana", max_hours_week=10)
    # preferences None -> empty dict
    d = t.to_dict()
    assert d["preferences"] == {}
    # preferences as json string
    t.preferences = json.dumps({"0": {"preferred": [0, 1]}})
    d2 = t.to_dict()
    assert isinstance(d2["preferences"], dict)


def test_config_to_dict():
    cfg = Config(id=1, classes_per_day=5, days_per_week=5, hour_names=json.dumps(["a","b"]), day_indices=json.dumps([0,1,2]))
    d = cfg.to_dict()
    assert d["classes_per_day"] == 5
    assert d["hour_names"] == ["a","b"]
    assert d["day_indices"] == [0,1,2]
