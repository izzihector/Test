# -*- coding: utf-8 -*-

from odoo import fields, models,api
from odoo.exceptions import ValidationError
# from datetime import datetime, date, timedelta


class HrEmployeeBase(models.AbstractModel):
    _inherit = "hr.employee.base"
    last_check_in = fields.Datetime(related='last_attendance_id.check_in', store=True, tracking=False)
    last_check_out = fields.Datetime(related='last_attendance_id.check_out', store=True, tracking=False)

class HrAttendance(models.Model):
    _name = 'hr.attendance'
    _description = 'HR Attendance'
    _inherit = ['hr.attendance','mail.thread','mail.activity.mixin',]

    def _default_employee(self):
        return self.env.user.employee_id

    login = fields.Date(
        string="Login",
        default=fields.Date.context_today
    )
    is_generated = fields.Boolean(
        string='Generated Automatically',
        default=False
    )
    action = fields.Char(
        string='Action'
    )
    VerifyMethod = fields.Selection([
        ('FING', 'Fingerprint'), ('RFID', 'RFID'), ('PWD', 'Password'),
        ('FING_OR_PWD', 'Fingerprint or Password'), ('FING_OR_PWD_OR_RFID', 'Password')
    ], string='Verify Method')
    
    check_in = fields.Datetime(
        string="Check In",
        required=False,
        default=False
        
    )
    check_out = fields.Datetime(string="Check Out", tracking=True)
    employee_id = fields.Many2one('hr.employee', string="Employee", required=False, default=_default_employee, ondelete='cascade', index=True)
    idc_no = fields.Char(string="ID No")
    
    @api.constrains('check_in', 'check_out', 'employee_id')
    def _check_validity(self):
        """ Verifies the validity of the attendance record compared to the others from the same employee.
            For the same employee we must have :
                * maximum 1 "open" attendance record (without check_out)
                * no overlapping time slices with previous employee records
        """
        for attendance in self:
            # we take the latest attendance before our check_in time and check it doesn't overlap with ours
            last_attendance_before_check_in = self.env['hr.attendance'].search([
                ('employee_id', '=', attendance.employee_id.id),
                ('check_in', '<=', attendance.check_in),
                ('id', '!=', attendance.id),
            ], order='check_in desc', limit=1)
            if last_attendance_before_check_in and last_attendance_before_check_in.check_out and last_attendance_before_check_in.check_out > attendance.check_in:
                raise exceptions.ValidationError(_("Cannot create new attendance record for %(empl_name)s, the employee was already checked in on %(datetime)s") % {
                    'empl_name': attendance.employee_id.name,
                    'datetime': format_datetime(self.env, attendance.check_in, dt_format=False),
                })

            
            else:
                # we verify that the latest attendance with check_in time before our check_out time
                # is the same as the one before our check_in time computed before, otherwise it overlaps
                last_attendance_before_check_out = self.env['hr.attendance'].search([
                    ('employee_id', '=', attendance.employee_id.id),
                    ('check_in', '<', attendance.check_out),
                    ('id', '!=', attendance.id),
                ], order='check_in desc', limit=1)
                if last_attendance_before_check_out and last_attendance_before_check_in != last_attendance_before_check_out:
                    raise exceptions.ValidationError(_("Cannot create new attendance record for %(empl_name)s, the employee was already checked in on %(datetime)s") % {
                        'empl_name': attendance.employee_id.name,
                        'datetime': format_datetime(self.env, last_attendance_before_check_out.check_in, dt_format=False),
                    })


    @api.constrains('idc_no', 'employee_id')
    def idc_constrains(self):
        for rec in self:
            if rec.idc_no and not rec.employee_id:
                self._cr.execute("""SELECT
                                        id
                                    FROM
                                        hr_employee
                                    WHERE
                                        idc_no = %s
                                    AND
                                        active = 't'
                                    LIMIT 1""", (rec.idc_no.strip(),))
                employee = self._cr.dictfetchone()
                if employee:
                    rec.employee_id = employee.get('id')
            if not rec.employee_id:
                raise ValidationError('Employee not found! Please select an Employee.')


    @api.depends('check_in', 'check_out')
    def _compute_worked_hours(self):
        for attendance in self:
            if attendance.check_in and attendance.check_out:

                delta = attendance.check_out - attendance.check_in
                attendance.worked_hours = delta.total_seconds() / 3600.0
            else:
                attendance.worked_hours = False
   

    def action_read_attendance(self):
        self.ensure_one()
        return {
            'name': self.display_name,
            'type': 'ir.actions.act_window',
            'view_type': 'form',
            'view_mode': 'form',
            'res_model': 'hr.attendance',
            'res_id': self.id,
        } 
