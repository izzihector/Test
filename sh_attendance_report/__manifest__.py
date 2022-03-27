# -*- coding: utf-8 -*-
# Part of Softhealer Technologies.
{
    "name": "Attendance Excel Report - Daily, Weekly, Monthly",
    "author": "Softhealer Technologies",
    "website": "https://www.softhealer.com",
    "license": "OPL-1",
    "support": "support@softhealer.com",
    "version": "14.0.1",
    "category": "Human Resources",
    "summary": """
manage monthly attendance app,find employee present module,
user weekly attendance,attendance with year,date wise attendance,
sick leave attendance report, public holiday attendance,
manage daily attendance, attendance management odoo
""",
    "description": """
The Attendance Report provides a flexible way of looking
at each employee with attendance.
Select a date and see all attendance records are regarding
with daily/weekly/monthly for all employees in the excel sheet.
You can print the attendance report for only one or selected employees.
Just select the name of the employee,
select "Print By" daily/weekly/monthly/ and print excel report.
This module provides the attendance report with all details like a present,
absent, sick leave, public holiday(PH), partial leave, etc.
You can see the employee present,
partial leave with it"s working hours of each day in excel report.
In the excel sheet report you can easily identify the present, absent,
public holiday, partial leave with it different background colors,
like a present - green, absent - red, partial leave - yellow,
public holiday - blue.
manage monthly attendance app, find employee absent module,
find employee present odoo, handle user weekly attendance,
get attendance in excel year, find date wise attendance,
sick leave attendance report, public holiday attendance,
get partial leave attendance, manage daily attendance odoo
""",
    "depends": ["hr", "hr_holidays", "hr_attendance"],

    "data": [
        "security/ir.model.access.csv",
        "views/hr_attendance_ineherit.xml",
        "wizards/employee_attendance_wizard.xml",
        "views/hr_attendance_report_xls.xml",
    ],
    "images": ["static/description/background.png", ],
    "installable": True,
    "application": True,
    "auto_install": False,
    "price": "40",
    "currency": "EUR"
}
