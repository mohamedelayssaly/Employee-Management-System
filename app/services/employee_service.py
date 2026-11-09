from sqlalchemy import String, cast, or_
from app import db
from app.models.employee import Employee

class EmployeeService:
    """Business logic for employee operations."""

    @staticmethod
    def list_employees(search="", department=""):
        query = Employee.query
        if search:
            term = f"%{search.strip()}%"
            query = query.filter(or_(
                Employee.first_name.ilike(term),
                Employee.last_name.ilike(term),
                Employee.email.ilike(term),
                Employee.department.ilike(term),
                cast(Employee.id, String).ilike(term)
            ))
        if department:
            query = query.filter(Employee.department == department)
        return query.order_by(Employee.last_name, Employee.first_name).all()

    @staticmethod
    def get_employee(employee_id):
        return db.session.get(Employee, employee_id)

    @staticmethod
    def create_employee(data):
        employee = Employee(**data)
        db.session.add(employee)
        db.session.commit()
        return employee

    @staticmethod
    def update_employee(employee, data):
        for field, value in data.items():
            setattr(employee, field, value)
        db.session.commit()
        return employee

    @staticmethod
    def delete_employee(employee):
        db.session.delete(employee)
        db.session.commit()

    @staticmethod
    def dashboard_stats():
        employees = Employee.query.all()
        return {
            "total": len(employees),
            "departments": len({e.department for e in employees}),
            "average_salary": (
                sum(e.salary for e in employees) / len(employees)
                if employees else 0
            ),
            "total_payroll": sum(e.salary for e in employees),
        }
