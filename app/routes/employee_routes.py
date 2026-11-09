from datetime import date
from flask import Blueprint, flash, redirect, render_template, request, url_for
from sqlalchemy.exc import IntegrityError
from app.services.employee_service import EmployeeService

employee_bp = Blueprint("employees", __name__)

def employee_form_data():
    """Read and validate form fields. Returns (data, errors)."""
    data = {
        "first_name": request.form.get("first_name", "").strip(),
        "last_name": request.form.get("last_name", "").strip(),
        "email": request.form.get("email", "").strip().lower(),
        "phone": request.form.get("phone", "").strip(),
        "department": request.form.get("department", "").strip(),
        "position": request.form.get("position", "").strip(),
    }
    errors = []
    for field in ("first_name", "last_name", "email", "department", "position"):
        if not data[field]:
            errors.append(f"{field.replace('_', ' ').title()} is required.")

    try:
        data["salary"] = float(request.form.get("salary", ""))
        if data["salary"] < 0:
            errors.append("Salary cannot be negative.")
    except ValueError:
        data["salary"] = 0
        errors.append("Salary must be a valid number.")

    try:
        data["hire_date"] = date.fromisoformat(request.form.get("hire_date", ""))
    except ValueError:
        data["hire_date"] = date.today()
        errors.append("Please provide a valid hire date.")

    if "@" not in data["email"] or "." not in data["email"].split("@")[-1]:
        errors.append("Please provide a valid email address.")

    return data, errors

@employee_bp.get("/")
def dashboard():
    stats = EmployeeService.dashboard_stats()
    recent_employees = EmployeeService.list_employees()[:5]
    return render_template("dashboard.html", stats=stats, recent_employees=recent_employees)

@employee_bp.get("/employees")
def employee_list():
    search = request.args.get("search", "")
    department = request.args.get("department", "")
    employees = EmployeeService.list_employees(search, department)
    departments = sorted({e.department for e in EmployeeService.list_employees()})
    return render_template(
        "employees/list.html", employees=employees, departments=departments,
        search=search, selected_department=department
    )

@employee_bp.route("/employees/new", methods=["GET", "POST"])
def employee_create():
    if request.method == "POST":
        data, errors = employee_form_data()
        if errors:
            for error in errors:
                flash(error, "error")
            return render_template("employees/form.html", employee=None, today=date.today().isoformat())
        try:
            EmployeeService.create_employee(data)
            flash("Employee created successfully.", "success")
            return redirect(url_for("employees.employee_list"))
        except IntegrityError:
            from app import db
            db.session.rollback()
            flash("That email address is already registered.", "error")
    return render_template("employees/form.html", employee=None, today=date.today().isoformat())

@employee_bp.route("/employees/<int:employee_id>/edit", methods=["GET", "POST"])
def employee_edit(employee_id):
    employee = EmployeeService.get_employee(employee_id)
    if employee is None:
        return render_template("404.html"), 404
    if request.method == "POST":
        data, errors = employee_form_data()
        if errors:
            for error in errors:
                flash(error, "error")
            return render_template("employees/form.html", employee=employee, today=date.today().isoformat())
        try:
            EmployeeService.update_employee(employee, data)
            flash("Employee updated successfully.", "success")
            return redirect(url_for("employees.employee_list"))
        except IntegrityError:
            from app import db
            db.session.rollback()
            flash("That email address is already used by another employee.", "error")
    return render_template("employees/form.html", employee=employee, today=date.today().isoformat())

@employee_bp.get("/employees/<int:employee_id>")
def employee_detail(employee_id):
    employee = EmployeeService.get_employee(employee_id)
    if employee is None:
        return render_template("404.html"), 404
    return render_template("employees/detail.html", employee=employee)

@employee_bp.post("/employees/<int:employee_id>/delete")
def employee_delete(employee_id):
    employee = EmployeeService.get_employee(employee_id)
    if employee is None:
        return render_template("404.html"), 404
    EmployeeService.delete_employee(employee)
    flash("Employee deleted.", "success")
    return redirect(url_for("employees.employee_list"))
