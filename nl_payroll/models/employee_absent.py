from odoo import api, fields, models, _


class EmployeeAbsent(models.Model):
    _name = 'employee.absent'
    _description = "Absent Employee"
    _inherit = ['mail.thread', 'mail.activity.mixin']

    employee_id = fields.Many2one('hr.employee', tracking=True)
    payroll_group_id = fields.Many2one('payroll.group', string='Payroll Group', related='employee_id.payroll_group_id', store=True, tracking=True)
    employee_idc_no = fields.Char(related='employee_id.identification_id',string="IDC No", store=True, tracking=True)
    department_id = fields.Many2one('hr.department',related='employee_id.department_id',string="Department", store=True, tracking=True)
    unit_id = fields.Many2one('hr.unit',string="Unit", related='employee_id.unit_id', store=True, tracking=True)
    job_id = fields.Many2one('hr.job',related='employee_id.job_id',string="Job", store=True, tracking=True)
    contract_id = fields.Many2one('hr.contract',related='employee_id.contract_id',string="Contract", store=True, tracking=True)
    contract_id_date_start = fields.Date(related='contract_id.date_start',string="Contract Start Date", store=True, tracking=True)
    contract_id_date_end = fields.Date(related='contract_id.date_end',string="Contract End Date", store=True, tracking=True)
    master_batch_id = fields.Many2one('generate.payroll.master',string="Master Batch", store=True, tracking=True)
    number_of_days = fields.Float(string="Days", tracking=True)
    current_user = fields.Selection(related="master_batch_id.current_user")
    parent_state = fields.Selection(related="master_batch_id.state")
    remarks = fields.Char(string="Remarks", tracking=True)

    @api.onchange('employee_id')
    def on_change_batch_id(self):
        return { 'domain': { 'employee_id': [('office_id', '=', self.master_batch_id.office_id.id)] }}
    
    def action_read_absent_form(self):
        self.ensure_one()
        return {
            'name': self.display_name,
            'type': 'ir.actions.act_window',
            'view_type': 'form',
            'view_mode': 'form',
            'res_model': 'employee.absent',
            'res_id': self.id,
        }


class EmployeePayslipLeaves(models.Model):
    _name = 'attendance.absent'
    
    employee_id = fields.Many2one('hr.employee')
    current_user = fields.Selection(related="master_batch_id.current_user")
    parent_state = fields.Selection(related="master_batch_id.state")
    leave_description = fields.Char("Description")
    date = fields.Char("Date")
    payslip_id = fields.Many2one(
        'hr.payslip'
    )
    master_batch_id = fields.Many2one('generate.payroll.master')