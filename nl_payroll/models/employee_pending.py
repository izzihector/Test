
# -*- coding: utf-8 -*-

from odoo import api, fields, models, _
from datetime import datetime, timedelta
from odoo.exceptions import UserError
from odoo.exceptions import UserError, ValidationError
from collections import defaultdict
import pytz
from datetime import datetime, date, time
from odoo.tools.misc import format_date


class EmployeesPending(models.Model):
    _name = 'employees.pending'
    
    employee_id = fields.Many2one('hr.employee')
    payroll_group_id = fields.Many2one('payroll.group', string='Payroll Group', related='employee_id.payroll_group_id', store=True)
    employee_idc_no = fields.Char(related='employee_id.identification_id',string="IDC No", store=True)
    department_id = fields.Many2one('hr.department',related='employee_id.department_id',string="Department", store=True)
    unit_id = fields.Many2one('hr.unit',string="Unit", related='employee_id.unit_id', store=True)
    job_id = fields.Many2one('hr.job',related='employee_id.job_id',string="Job", store=True)
    contract_id = fields.Many2one('hr.contract',related='employee_id.contract_id',string="Contract", store=True)
    contract_id_date_start = fields.Date(related='contract_id.date_start',string="Contract Start Date", store=True)
    contract_id_date_end = fields.Date(related='contract_id.date_end',string="Contract End Date", store=True)
    master_batch_id = fields.Many2one('generate.payroll.master',string="Master Batch", store=True)
    name = fields.Char("Name", related="employee_id.name")
    payslip_run_id = fields.Many2one('hr.payslip.run')
    reason = fields.Char("Reason",compute="_get_payslip_pending_reason")
    
    def compute_sheet(self):
        Payslip = self.env['hr.payslip']
        lang = self.contract_id.employee_id.sudo().address_home_id.lang or self.env.user.lang
        context = {'lang': lang}
        default_values = Payslip.default_get(Payslip.fields_get())
        payslip_name = self.contract_id.structure_type_id.default_struct_id.payslip_name or _('Salary Slip')
        values = dict(default_values, **{
            'employee_id': self.contract_id.employee_id.id,
            'credit_note': self.payslip_run_id.credit_note,
            'payslip_run_id': self.payslip_run_id.id,
            'date_from': self.payslip_run_id.date_start,
            'date_to': self.payslip_run_id.date_end,
            'contract_id': self.contract_id.id,
            'month':self.payslip_run_id.month,
            'attendance_mode':dict(self.master_batch_id._fields['calculate_attendance'].selection).get(self.master_batch_id.calculate_attendance),
            'struct_id': self.contract_id.structure_type_id.default_struct_id.id,
            'name':'%s - %s - %s' % (payslip_name,self.contract_id.employee_id.name or '',format_date(self.env, self.payslip_run_id.date_start, date_format="MMMM y", lang_code=lang))
        })
        
        payslip = self.env['hr.payslip'].new(values)
        values = payslip._convert_to_write(payslip._cache)
        payslip = Payslip.sudo().create(values)
        payslip.compute_sheet_master()
            
        
    
    def _get_payslip_pending_reason(self):
        self.reason = ' '
        for rec in self:
            if rec.contract_id.state != 'open':
                rec.reason = 'Contract Not Running'
            elif rec.contract_id.wage == 0:
                rec.reason = 'Wage is 0'
            elif rec.contract_id.state =='close':
                rec.reason = 'Contract Expired'
            elif rec.contract_id.date_start > rec.payslip_run_id.date_end:
                rec.reason = "Contract Start Date is after this month's payroll end date"
            elif rec.contract_id.date_end:
                if rec.contract_id.date_end < rec.payslip_run_id.date_start:
                    rec.reason = "Contract End Date is before this month's payroll start date"
            else:
                rec.reason = 'Ready'
    
    
    def unlink_pending_employee(self):
        payslip_run = self.env['hr.payslip'].search([('payslip_run_id','=',self.payslip_run_id.id)])
        payslip_employee_ids = []
        for slip in payslip_run:
            payslip_employee_ids.append(slip.employee_id.id)
        if self.employee_id.id in payslip_employee_ids:
            self.unlink()

    def _generate_payslip(self):
        for rec in self:
            if rec.reason == 'Ready':    
                rec.compute_sheet()
                rec.unlink()
            else:
                raise UserError(_('Payslip can not be generated due to %s') % (rec.reason))