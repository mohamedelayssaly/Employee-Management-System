from datetime import date
import pytest
from app import create_app, db
from app.models.employee import Employee
from app.services.employee_service import EmployeeService

@pytest.fixture()
def app():
    app = create_app({
        "TESTING": True,
        "SQLALCHEMY_DATABASE_URI": "sqlite://",
        "SECRET_KEY": "test-secret",
    })
    with app.app_context():
        db.create_all()
        yield app
        db.session.remove()
        db.drop_all()

@pytest.fixture()
def client(app):
    return app.test_client()

def sample_employee():
    return {
        "first_name": "Ada",
        "last_name": "Lovelace",
        "email": "ada@example.com",
        "phone": "123456",
        "department": "Engineering",
        "position": "Developer",
        "salary": 7000.0,
        "hire_date": date(2024, 1, 1),
    }

def test_employee_full_name(app):
    with app.app_context():
        employee = Employee(**sample_employee())
        assert employee.full_name == "Ada Lovelace"

def test_create_and_find_employee(app):
    with app.app_context():
        created = EmployeeService.create_employee(sample_employee())
        found = EmployeeService.get_employee(created.id)
        assert found.email == "ada@example.com"

def test_dashboard_loads(client):
    response = client.get("/")
    assert response.status_code == 200
    assert b"Dashboard" in response.data

def test_employee_form_rejects_empty_fields(client):
    response = client.post("/employees/new", data={})
    assert response.status_code == 200
    assert b"required" in response.data.lower()
