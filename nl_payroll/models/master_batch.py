from odoo import api, fields, models, _
from datetime import datetime, timedelta
from odoo.exceptions import UserError
from odoo.exceptions import UserError, ValidationError
from collections import defaultdict
import pytz
from datetime import datetime, date, time
from odoo.tools.misc import format_date
from odoo.addons.nl_master.helpers import master_data


class GeneratePayrollMaster(models.Model):
    _name = 'generate.payroll.master'
    _description = 'Monthly Payroll'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _order = "start_date desc"

    payroll_sequence = fields.Char(string='Payroll Number', required=True, readonly=True, default=lambda self: _('New'), copy=False)
    name = fields.Char('Name', compute="get_custom_name")

    start_date = fields.Date('From', required=True)
    end_date = fields.Date('To', required=True)
    batch_ids = fields.One2many('hr.payslip.run','master_batch_id')
    month = fields.Selection([
        ('1', 'January'),
        ('2', 'February'),
        ('3', 'March'),
        ('4', 'April'),
        ('5', 'May'),
        ('6', 'June'),
        ('7', 'July'),
        ('8', 'August'),
        ('9', 'September'),
        ('10', 'October'),
        ('11', 'November'),
        ('12', 'December'),

    ], required=True,readonly=True)

    separation_ids = fields.Many2many('hr.separation', string='Separations',copy=False)
    employee_ids = fields.Many2many('hr.employee', string='Employees to Exclude',copy=False)
    absent_employee_ids = fields.One2many('employee.absent','master_batch_id')
    attendance_absent_employee_ids = fields.One2many('attendance.absent','master_batch_id')
    overview_item_ids = fields.One2many('monthly.allowances','master_batch_id')
    manual_allowance_deduction_ids = fields.One2many('manual.allowance.deduction','master_batch_id')
    absence_ids = fields.One2many('absence.deductions','master_batch_id')
    adjustment_allowance_ids = fields.One2many('adjustment.allowance','master_batch_id')
    pension_allowance_ids = fields.One2many('pension.allowance','master_batch_id')
    overtime_ids = fields.One2many('overtime.allowance','master_batch_id')
    topup_allowance_ids = fields.One2many('topup.allowance','master_batch_id')
    transport_allowance_ids = fields.One2many('transport.allowance','master_batch_id')
    late_hours_ids = fields.One2many('late.hours','master_batch_id')
    lunch_allowance_ids = fields.One2many('lunch.allowance','master_batch_id')
    acting_allowance_ids = fields.One2many('acting.allowance','master_batch_id')
    advance_deduction_ids = fields.One2many('advance.deduction','master_batch_id')
    transport_deduction_ids = fields.One2many('transport.deduction','master_batch_id')
    other_deduction_ids = fields.One2many('other.deduction','master_batch_id')
    other_allowance_ids = fields.One2many('other.allowance','master_batch_id')
    province_ids = fields.Many2many('province', string="Province", required=True)
    calculate_attendance = fields.Selection([
        ('1','Attendance'),
        ('2','Manual'),
    ],string="Calculate Attendance Based on", required=True)
    office_id = fields.Many2one('office', string="Office", required=True)
    total_net_salary = fields.Float('Total Net Salary', compute="_calculate_net_salary")
    pending_employee_ids = fields.One2many('employees.pending','master_batch_id', string="Pending Employees", )
    employee_pending_count = fields.Integer(compute="_payroll_employee_pending_count")
    payslip_counts = fields.Integer('Total Payslips', compute='_calculate_payroll_expense')
    allowance_deduciton_count = fields.Integer('Allowance and Deduction', compute='_payroll_allowance_deduction_count')
    abseent_employee_count = fields.Integer(compute="_payroll_absent_employees_count")
    attendance_absent_count = fields.Integer(compute="_payroll_attendance_absent_employees_count")
    state = fields.Selection([
        ('draft', 'Draft'),
        ('hr','HR Review'),
        ('finance','Finance Review'),
        ('done', 'Done'),
        ('cancel', 'Cancelled') ], string='Status',  index=True, readonly=True, copy=False, default='draft',track_visibility=True,
        help="""* When the payslip is created the status is \'Draft\'
                \n* If the payslip is under verification, the status is \'Waiting\'.
                \n* If the payslip is confirmed then status is set to \'Done\'.
                \n* When user cancel payslip the status is \'Rejected\'.""")


    
    current_user = fields.Selection([
        ('admin', 'Admin'),
        ('finance', 'Finance')
        ], compute="_get_current_user")

    @api.onchange('start_date','end_date')
    def _set_month_based_on_end_date(self):
        if self.start_date and self.end_date:
            self.month = str(self.end_date.month)

    def get_custom_name(self):
        for rec in self:
            rec.name = False
            if rec.office_id and rec.end_date:
                rec.name = f"{rec.office_id.name} Payroll - {rec.end_date.strftime('%B')}, {rec.end_date.strftime('%Y')}"

    @api.model
    def create(self, vals):
        if not vals.get('payroll_sequence') or vals['payroll_sequence'] == _('New'):
            vals['payroll_sequence'] = self.env['ir.sequence'].next_by_code('generate.payroll.master.sequence') or _('New')
        return super(GeneratePayrollMaster, self).create(vals)

    def _get_current_user(self):
        for rec in self:
            rec.current_user = False
            if self.env.user.has_group("nl_payroll.group_payroll_finance"):
                rec.current_user = 'finance'
            elif self.env.user.has_group("hr_payroll.group_hr_payroll_manager"):
                rec.current_user = 'admin'
        
    absence_page = fields.Boolean()
    adjustment_page = fields.Boolean()
    pension_page = fields.Boolean()
    overtime_page = fields.Boolean()
    topup_page = fields.Boolean()
    transport_page = fields.Boolean()
    late_hours_page = fields.Boolean()
    lunch_page = fields.Boolean()
    acting_page = fields.Boolean()
    advance_page = fields.Boolean()
    transport_deduction_page = fields.Boolean()
    other_ded_page = fields.Boolean()
    other_allowance_page = fields.Boolean()
    
    def _calculate_net_salary(self):
        self.total_net_salary = 0.0
       
        amount = 0.0
        for item in self.batch_ids.slip_ids.filtered(lambda slip: slip.state not in ['draft','cancel']):
            amount += item.net_salary
            amount = amount + item.total_net_salary
        self.total_net_salary = amount

    def _pages_visibility(self):
        if len(self.absence_ids) > 0:
            self.absence_page = True

        if len(self.adjustment_allowance_ids) > 0:
            self.adjustment_page = True

        if len(self.pension_allowance_ids) > 0:
            self.pension_page = True
        
        if len(self.overtime_ids) > 0:
            self.overtime_page = True

        if len(self.topup_allowance_ids) > 0:
            self.topup_page = True
        
        if len(self.transport_allowance_ids) > 0:
            self.transport_page = True

        if len(self.late_hours_ids) > 0:
            self.late_hours_page = True

        if len(self.other_allowance_ids) > 0:
            self.other_allowance_page = True

        if len(self.lunch_allowance_ids) > 0:
            self.lunch_page = True
            
        if len(self.acting_allowance_ids) > 0:
            self.acting_page = True

        if len(self.advance_deduction_ids) > 0:
            self.advance_page = True
        
        if len(self.transport_deduction_ids) > 0:
            self.transport_deduction_page = True
    
        if len(self.other_deduction_ids) > 0:
            self.other_ded_page = True

        if len(self.other_allowance_ids) > 0:
            self.other_allowance_page = True
  


    def reset_as_draft(self):
        self.ensure_one()
        batch_id = self.batch_ids.filtered(lambda batch: batch.master_batch_id.id == self.id)
        self._cr.execute("""DELETE FROM hr_payslip WHERE payslip_run_id = %s""", (batch_id.id,))
        self._cr.execute("""DELETE FROM hr_payslip_run WHERE id = %s""", (batch_id.id,))
        self._cr.execute("""DELETE FROM attendance_absent WHERE master_batch_id = %s""", (self.id,))
        self.pending_employee_ids.sudo().unlink()
        self.absent_employee_ids.sudo().unlink()
        self.separation_ids = False
        self.activity_ids.sudo().unlink()
        self.init_calculations()
        self.state = 'draft'

    @api.onchange('office_id')
    def return_domain_employee(self):
        if self.office_id:
            return {'domain': {'employee_ids': [('office_id', '=', self.office_id.id)]}}

    def _payroll_employee_pending_count(self):
        self.employee_pending_count = len(self.pending_employee_ids)

    def _payroll_allowance_deduction_count(self):
        self.allowance_deduciton_count = len(self.manual_allowance_deduction_ids)

    def _payroll_absent_employees_count(self):
        self.abseent_employee_count = len(self.absent_employee_ids)

    def _payroll_attendance_absent_employees_count(self):
        employees = []
        for item in self.attendance_absent_employee_ids:
            if item.employee_id.id not in employees:
                employees.append(item.employee_id.id)
        self.attendance_absent_count = len(employees)

    def action_view_employee_pending(self):
        self.ensure_one()
        return {
            'type': 'ir.actions.act_window',
            'name': 'Employee Pending',
            'view_mode': 'tree,form',
            'res_model': 'employees.pending',
            'domain': [('master_batch_id', '=', self.id)],
            'context': dict(self._context, default_master_batch_id=self.id, default_payslip_run_id=self.batch_ids.filtered(lambda batch: batch.master_batch_id.id == self.id).id, create=True),
        }
    def action_view_monthly_allowance_deduction(self):
        self.ensure_one()
        return {
            'type': 'ir.actions.act_window',
            'name': 'Allowances & Deductions',
            'view_mode': 'tree',
            'res_model': 'manual.allowance.deduction',
            'domain': [('master_batch_id', '=', self.id)],
            'context': dict(self._context, default_master_batch_id=self.id, default_payslip_run_id=self.batch_ids.filtered(lambda batch: batch.master_batch_id.id == self.id).id),
        }
    def action_view_monthly_absence(self):
        # self.ensure_one()
        return {
            'type': 'ir.actions.act_window',
            'name': str(dict(self._fields['month'].selection).get(self.month)) + ' Absent Employees',
            'view_mode': 'tree',
            'res_model': 'employee.absent',
            'domain': [('master_batch_id', '=', self.id)],
            'context': dict(self._context, default_master_batch_id=self.id, default_payslip_run_id=self.batch_ids.filtered(lambda batch: batch.master_batch_id.id == self.id).id),
        }

    def action_view_monthly_attendance_absence(self):
        self.ensure_one()
        return {
            'type': 'ir.actions.act_window',
            'name': str(dict(self._fields['month'].selection).get(self.month)) + ' Absent Employees',
            'view_mode': 'tree',
            'res_model': 'attendance.absent',
            'domain': [('master_batch_id', '=', self.id)],
            'context': {
                'search_default_group_employee': True,
                'search_default_group_employee_id': True,
            }
        }
    
    def avoid_create_sub_categories(self):
        self.ensure_one()
        return True if (self.state  == 'hr' and self.current_user == 'finance') or (self.state == 'finance' and self.current_user == 'admin') or self.state not in ['hr', 'finance', 'draft'] else False

    def action_open_payslips(self):
        self.ensure_one()
        return {
            "type": "ir.actions.act_window",
            "res_model": "hr.payslip",
            "views": [[False, "tree"], [False, "form"]],
            "domain": [['id', 'in', self.batch_ids.slip_ids.ids]],
            "name": "Payslips",
        }
    
    def init_calculations(self):
        self.overview_item_ids.unlink()
        self.absence_ids.unlink()
        self.adjustment_allowance_ids.unlink()
        self.pension_allowance_ids.unlink()
        self.other_allowance_ids.unlink()
        self.topup_allowance_ids.unlink()
        self.lunch_allowance_ids.unlink()
        self.acting_allowance_ids.unlink()
        self.transport_deduction_ids.unlink()
        self.transport_allowance_ids.unlink()
        self.late_hours_ids.unlink()
        self.overtime_ids.unlink()
        self.advance_deduction_ids.unlink()
        self.other_deduction_ids.unlink()
        self.absence_page = False
        self.adjustment_page = False
        self.pension_page = False
        self.overtime_page = False
        self.topup_page = False
        self.transport_page = False
        self.late_hours_page = False
        self.lunch_page = False
        self.acting_page = False
        self.advance_page = False
        self.transport_deduction_page = False
        self.other_ded_page = False
        self.other_allowance_page = False
        
    def _calculate_payroll_expense(self):
        self.init_calculations()
        rules_calculated = []
        net_amount = 0.0
        self.payslip_counts = len(self.batch_ids.slip_ids)
        rules = []
        for rule in self.env['hr.salary.rule'].search([('struct_id','=',1)]):
            rules.append(rule.name)
        for slip in self.batch_ids.slip_ids.filtered(lambda slip: slip.state not in ['cancel']):
            for line in slip.line_ids:
                if line.amount > 0 or line.amount < 0:
                    self.allocate_allowances_and_deductions(line,slip)
                
                for rule in rules:
                    if line.salary_rule_id.name == rule:
                        net_amount = net_amount + line.amount
                        rules_calculated.append([rule,net_amount])
                        
                        net_amount = 0.0   

        self.re_calculate_and_reconcile_allwoances_deductions(rules_calculated)
        
        self._pages_visibility()

    def re_calculate_and_reconcile_allwoances_deductions(self,rules_calculated):
        num_dict = {}
        for t in rules_calculated:
            if t[0] in num_dict:
                num_dict[t[0]] = num_dict[t[0]]+t[1]
            else:
                num_dict[t[0]] = t[1]

        for key,value in num_dict.items():
            if value > 0:
                self.env['monthly.allowances'].sudo().create({
                    'name':'Total ' + key,
                    'amount':value,
                    'master_batch_id':self.id
                })

    def allocate_allowances_and_deductions(self,line,slip):   
        if line.code == 'ADJ':
            self.env['adjustment.allowance'].sudo().create({
                'employee_id':slip.employee_id.id,
                'amount':line.amount,
                'master_batch_id':self.id,
                'slip_id':slip.id
            })

        if line.code == 'PENSION':
            self.env['pension.allowance'].sudo().create({
                'employee_id':slip.employee_id.id,
                'amount':line.amount,
                'master_batch_id':self.id,
                'slip_id':slip.id
            })

        if line.code == 'OVERTIME':
            self.env['overtime.allowance'].sudo().create({
                'employee_id':slip.employee_id.id,
                'amount':line.amount,
                'master_batch_id':self.id,
                'slip_id':slip.id
            })

        if line.code == 'TOPUP':
            self.env['topup.allowance'].sudo().create({
                'employee_id':slip.employee_id.id,
                'amount':line.amount,
                'master_batch_id':self.id,
                'slip_id':slip.id
            })

        if line.code == 'TRANSPORT':
            self.env['transport.allowance'].sudo().create({
                'employee_id':slip.employee_id.id,
                'amount':line.amount,
                'master_batch_id':self.id,
                'slip_id':slip.id
            })

        if line.code == 'LATE':
            self.env['late.hours'].sudo().create({
                'employee_id':slip.employee_id.id,
                'amount':line.amount,
                'master_batch_id':self.id,
                'slip_id':slip.id
            })

        if line.code == 'LUNCH':
            self.env['lunch.allowance'].sudo().create({
                'employee_id':slip.employee_id.id,
                'amount':line.amount,
                'master_batch_id':self.id,
                'slip_id':slip.id
            })

        if line.code == 'ACTING':
            self.env['acting.allowance'].sudo().create({
                'employee_id':slip.employee_id.id,
                'amount':line.amount,
                'master_batch_id':self.id,
                'slip_id':slip.id
            })

        if line.code == 'SALADVANCE':
            self.env['advance.deduction'].sudo().create({
                'employee_id':slip.employee_id.id,
                'amount':line.amount,
                'master_batch_id':self.id,
                'slip_id':slip.id
                
            })
        if line.code == 'OTHERDED':
            self.env['other.deduction'].sudo().create({
                'employee_id':slip.employee_id.id,
                'amount':line.amount,
                'master_batch_id':self.id,
                'slip_id':slip.id
            })
        if line.code == 'TRANSPORTDED':
            self.env['transport.deduction'].sudo().create({
                'employee_id':slip.employee_id.id,
                'amount':line.amount,
                'master_batch_id':self.id,
                'slip_id':slip.id
            })
        if line.code == 'OTHERALLOWANCE':
            self.env['other.allowance'].sudo().create({
                'employee_id':slip.employee_id.id,
                'amount':line.amount,
                'master_batch_id':self.id,
                'slip_id':slip.id
            })
        if line.code == 'ABSENCE':
            self.env['absence.deductions'].sudo().create({
                'employee_id':slip.employee_id.id,
                'amount':line.amount,
                'master_batch_id':self.id,
                'slip_id':slip.id
            })

    

    batch_count = fields.Integer(compute="_count_batch")

    def _count_batch(self):  
        batch_ids = self.env['hr.payslip.run'].search([('master_batch_id','=',self.id)]) 
        for batch in self: 
            batch.batch_ids = batch_ids
        self.batch_count = len(batch_ids)

    @api.constrains("start_date", "end_date", "office_id")
    def check_overlap(self):
        for rec in self:
            if rec.start_date and rec.end_date and rec.office_id:
                self._cr.execute("""
                    SELECT 
                        name
                    FROM
                        generate_payroll_master
                    WHERE
                    (
                        (start_date BETWEEN %s AND %s)
                    OR
                        (end_date BETWEEN %s AND %s)
                    )
                    AND
                        office_id = %s
                    AND
                        id != %s
                    AND 
                        state = 'done'
                    LIMIT 1
                """, (rec.start_date, rec.end_date, rec.start_date, rec.end_date, rec.office_id.id, rec.id))
                overlapped_record = self._cr.dictfetchone()
                if overlapped_record:
                    self.env['bus.bus'].sendone(
                        (self._cr.dbname, 'res.partner', self.env.user.partner_id.id),
                        {'type': 'simple_notification','sticky': True, 'warning': True, 'title': _('Payroll Date Overlaps'), 'message': _(f'Payroll date overlap for the office: {rec.office_id.name} with payroll ({overlapped_record.get("name")})')}
                    )


    def check_validation(self):
        for rec in self:
            if rec.start_date and rec.end_date and rec.office_id:
                self._cr.execute("""
                    SELECT 
                        name
                    FROM
                        generate_payroll_master
                    WHERE
                    (
                        (start_date BETWEEN %s AND %s)
                    OR
                        (end_date BETWEEN %s AND %s)
                    )
                    AND
                        office_id = %s
                    AND
                        id != %s
                    AND
                        state = 'done'
                    LIMIT 1
                """, (rec.start_date, rec.end_date, rec.start_date, rec.end_date, rec.office_id.id, rec.id))
                overlapped_record = self._cr.dictfetchone()
                if overlapped_record:
                    raise ValidationError(_(f"Payroll dates overlap for the office: {rec.office_id.name} with payroll ({overlapped_record.get('name')})"))

        other_master = self.search([('id', '!=', self.id), ('office_id', '=', self.office_id.id), ('state', '=', 'done')], order="end_date desc", limit=1)
        if other_master:
            # For Previous Months
            if  self.end_date < other_master.start_date: 
                raise ValidationError(_("Can not generate payroll records for previous months."))
            old_master_end_date = datetime.combine(other_master.end_date, datetime.min.time())
            old_master_month_end_date = (old_master_end_date.replace(day=1) + timedelta(days=32)).replace(day=1) - timedelta(days=1)
            # Check if current payroll start date is in same month as the prvious payroll end date.
            if not (old_master_end_date.date() < self.start_date <= old_master_month_end_date.date()):
                old_master_next_start_date = (old_master_end_date.replace(day=1) + timedelta(days=32)).replace(day=1)
                old_master_next_end_date = (old_master_next_start_date.replace(day=1) + timedelta(days=32)).replace(day=1) - timedelta(days=1)
                # Check payroll months should be in sequence
                if not (old_master_next_start_date.date() <= self.start_date <= old_master_next_end_date.date()):
                    raise ValidationError(_(f'There is no monthly payroll record for {self.office_id.name} Office for the month of {old_master_next_start_date.strftime("%B")} Month. Please make sure you create and validate monthly payrolls for this office without skipping any months'))

    def generate_master_payroll(self):
        self.check_validation()
        employee_ids = self.env['hr.employee'].sudo().search([('office_id','=',self.office_id.id),('id','not in',self.employee_ids.ids)])
        separation_ids = self.env['hr.separation'].sudo().search([('office_id','=',self.office_id.id),('state', 'in', ['in_progress']),('payslip_paid','=',False)])
        self.separation_ids = separation_ids
        if self.separation_ids:
            employee_ids = employee_ids + self.separation_ids.mapped('employee_id')
        if not employee_ids:
            raise UserError(_("You must select employee(s) to generate payslip(s)."))
        payslip_run = self.env['hr.payslip.run'].create({
                'name': self.name + ' ' + self.start_date.strftime('%B %Y'),
                'date_start': self.start_date,
                'date_end': self.end_date,
                'month':self.month,
                'master_batch_id':self.id,
                'calculate_attendance':self.calculate_attendance,
                'office_id':self.office_id.id,
        })
        payslips = self.env['hr.payslip']
        Payslip = self.env['hr.payslip']
        default_values = Payslip.default_get(Payslip.fields_get())
        for contract in employee_ids.sudo()._get_contracts_extended(self.office_id.id,payslip_run.id,self.id,
            payslip_run.date_start, payslip_run.date_end, states=['open','in_separation']).filtered(lambda c: c.active and c.wage > 0):
            lang = contract.employee_id.sudo().address_home_id.lang or self.env.user.lang
            context = {'lang': lang}
            payslip_name = contract.structure_type_id.default_struct_id.payslip_name or _('Salary Slip')
            values = dict(default_values, **{
                'employee_id': contract.employee_id.id,
                'donor_code': contract.employee_id.donor_code,
                'cost_center':contract.employee_id.cost_center,
                'credit_note': payslip_run.credit_note,
                'payslip_run_id': payslip_run.id,
                'date_from': payslip_run.date_start,
                'date_to': payslip_run.date_end,
                'contract_id': contract.id,
                'month':self.month,
                'separation_id':self.env['hr.separation'].search([('employee_id', '=', contract.employee_id.id),('state', 'in', ['in_progress'])]).id,
                'master_batch_id':self.id,
                'attendance_mode':dict(self._fields['calculate_attendance'].selection).get(self.calculate_attendance),
                'struct_id': contract.structure_type_id.default_struct_id.id,
                'name':'%s - %s - %s' % (payslip_name,contract.employee_id.name or '',format_date(self.env, payslip_run.date_end, date_format="MMMM y", lang_code=lang))
            })
            payslip = self.env['hr.payslip'].new(values)
            values = payslip._convert_to_write(payslip._cache)
            payslips += Payslip.sudo().create(values)
            
        payslips.sudo().compute_sheet_master()
        payslips.sudo().write({'state':'hr'})
        payslip_run.state = 'hr'
    
        self.write({'state':'hr'})
        self._calculate_payroll_expense()

    def action_submit_to_finance(self):
        for batch in self.batch_ids:
            batch.action_submit_to_finance()
        self.write({'state':'finance'})
        self.batch_ids.slip_ids.sudo().write({'state' : 'finance'})
        self.activity_finance_members()


    def activity_finance_members(self):
        """ Create Activity for Finance Members """
        note = _('Payroll for the month of %s has been submitted for your review. Kindly access the payroll app for further processing.') % (
            master_data.MONTHS_DICT.get(self.month))

        users = []
        office = self.office_id
        hr_contract_approver = self.env['hr.contract.approver'].sudo().search([('office_id', '=', office.id)], limit=1)
        users = hr_contract_approver.payroll_responsible_finance
        for login in users:
            self.activity_schedule(
                'nl_payroll.mail_payroll_create_notification',
                note=note,
                user_id=login.id or self.env.user.id)

    def action_view_batches(self):
        batch_ids = self.mapped('batch_ids')
        action = self.env.ref('hr_payroll.action_hr_payslip_run_tree').read()[0]
        if len(batch_ids) > 0:
            action['domain'] = [('id', 'in', batch_ids.ids)] 
        else:
            action = {'type': 'ir.actions.act_window_close'}
        return action

    def unlink(self):
        if self.env.user.has_group("nl_payroll.group_payroll_finance"):
            raise UserError(_("Only admin users can delete a payroll."))

        if any(self.filtered(lambda payslip_run: payslip_run.state not in ('draft'))):
            raise UserError(_('You cannot delete a payslip batch which is not draft!'))
        if any(self.batch_ids.mapped('slip_ids').filtered(lambda payslip: payslip.state not in ('draft','cancel'))):
            raise UserError(_('You cannot delete a payslip which is not draft or cancelled!'))
        return super(GeneratePayrollMaster, self).unlink()

    def action_payslip_done(self):
        self.check_validation()
        self.activity_ids.unlink()
        self.send_payslip_email()
        self.write({'state':'done'})
        self.batch_ids.slip_ids.write({'state': 'done'})
        self.separation_ids.write({'payslip_paid': True})

    def send_payslip_email(self):
        for slip in self.batch_ids.slip_ids.filtered(lambda slip: slip.state != 'cancel'):
            slip.nl_payslip_mail(slip.employee_id,slip.date_to)
            

    def calculate_all_payslips(self):
        slip_ids = []
        absences = []
        manual_allowance_ids = []
        payslips = self.batch_ids.slip_ids
        lines = payslips.line_ids.filtered(lambda line: line.edited == True)
        for line in lines:
            slip_ids.append(line.slip_id.id)
        for item in self.absent_employee_ids:
            absences.append(item.employee_id.id)
        for allowance in self.manual_allowance_deduction_ids:
            if not allowance.done:
                manual_allowance_ids.append(allowance.employee_id.id)
        employee_ids = absences + manual_allowance_ids
        payslips = self.env['hr.payslip'].search(['|',('id','in',slip_ids),('employee_id','in',employee_ids)])
        for slip in payslips:
            slip.compute_sheet()
        payslips.line_ids.filtered(lambda line: line in lines).unlink()
        self.exclude_employees()
        self._calculate_payroll_expense()

    def exclude_employees(self):
        payslips = self.batch_ids.slip_ids.filtered(lambda slip: slip.employee_id in self.employee_ids)
        if payslips:
            payslips.sudo().write({'state':'cancel'})
            for slip in payslips:
                self.env['employees.pending'].sudo().create({
                    'employee_id':slip.employee_id.id,
                    'master_batch_id':self.id,
                    'payslip_run_id':slip.payslip_run_id.id,
                    'reason':'Ready'
                })
            payslips.sudo().unlink()
        self.init_calculations()
        
class MonthlyAllowances(models.Model):
    _name = 'monthly.allowances'

    name = fields.Char('Item')
    amount = fields.Float('Amount')
    master_batch_id = fields.Many2one('generate.payroll.master')

class AdjustmentAllowance(models.Model):
    _name = 'adjustment.allowance'

    employee_id = fields.Many2one('hr.employee')
    father_name = fields.Char('Father Name', related='employee_id.father_name')
    unit_id = fields.Many2one('hr.unit', related='employee_id.unit_id', string='Unit')
    amount = fields.Float('Amount')
    master_batch_id = fields.Many2one('generate.payroll.master')
    slip_id = fields.Many2one('hr.payslip', string="Payslip")

class PensionAllowance(models.Model):
    _name = 'pension.allowance'

    employee_id = fields.Many2one('hr.employee')
    father_name = fields.Char('Father Name', related='employee_id.father_name')
    unit_id = fields.Many2one('hr.unit', related='employee_id.unit_id', string="Unit")
    amount = fields.Float('Amount')
    master_batch_id = fields.Many2one('generate.payroll.master')
    slip_id = fields.Many2one('hr.payslip', string="Payslip")

class OvertimeAllowance(models.Model):
    _name = 'overtime.allowance'

    employee_id = fields.Many2one('hr.employee')
    father_name = fields.Char('Father Name', related='employee_id.father_name')
    unit_id = fields.Many2one('hr.unit', related='employee_id.unit_id', string="Unit")
    amount = fields.Float('Amount')
    master_batch_id = fields.Many2one('generate.payroll.master')
    slip_id = fields.Many2one('hr.payslip', string="Payslip")

class TopupAllowance(models.Model):
    _name = 'topup.allowance'

    employee_id = fields.Many2one('hr.employee')
    father_name = fields.Char('Father Name', related='employee_id.father_name')
    unit_id = fields.Many2one('hr.unit', related='employee_id.unit_id', string="Unit")
    amount = fields.Float('Amount')
    master_batch_id = fields.Many2one('generate.payroll.master')
    slip_id = fields.Many2one('hr.payslip', string="Payslip")

class TransportAllowance(models.Model):
    _name = 'transport.allowance'

    employee_id = fields.Many2one('hr.employee')
    father_name = fields.Char('Father Name', related='employee_id.father_name')
    unit_id = fields.Many2one('hr.unit', related='employee_id.unit_id', string="Unit")
    amount = fields.Float('Amount')
    master_batch_id = fields.Many2one('generate.payroll.master')
    slip_id = fields.Many2one('hr.payslip', string="Payslip")

class LateHours(models.Model):
    _name = 'late.hours'

    employee_id = fields.Many2one('hr.employee')
    father_name = fields.Char('Father Name', related='employee_id.father_name')
    unit_id = fields.Many2one('hr.unit', related='employee_id.unit_id', string="Unit")
    amount = fields.Float('Amount')
    master_batch_id = fields.Many2one('generate.payroll.master')
    slip_id = fields.Many2one('hr.payslip', string="Payslip")

class LunchAllowance(models.Model):
    _name = 'lunch.allowance'

    employee_id = fields.Many2one('hr.employee')
    father_name = fields.Char('Father Name', related='employee_id.father_name')
    unit_id = fields.Many2one('hr.unit', related='employee_id.unit_id', string="Unit")
    amount = fields.Float('Amount')
    master_batch_id = fields.Many2one('generate.payroll.master')
    slip_id = fields.Many2one('hr.payslip', string="Payslip")

class ActingAllowance(models.Model):
    _name = 'acting.allowance'

    employee_id = fields.Many2one('hr.employee')
    father_name = fields.Char('Father Name', related='employee_id.father_name')
    unit_id = fields.Many2one('hr.unit', related='employee_id.unit_id', string="Unit")
    amount = fields.Float('Amount')
    master_batch_id = fields.Many2one('generate.payroll.master')
    slip_id = fields.Many2one('hr.payslip', string="Payslip")

class AdvanceDeduction(models.Model):
    _name = 'advance.deduction'

    employee_id = fields.Many2one('hr.employee')
    father_name = fields.Char('Father Name', related='employee_id.father_name')
    unit_id = fields.Many2one('hr.unit', related='employee_id.unit_id', string="Unit")
    amount = fields.Float('Amount')
    master_batch_id = fields.Many2one('generate.payroll.master')
    slip_id = fields.Many2one('hr.payslip', string="Payslip")
class OtherDeduction(models.Model):
    _name = 'other.deduction'

    employee_id = fields.Many2one('hr.employee')
    father_name = fields.Char('Father Name', related='employee_id.father_name')
    unit_id = fields.Many2one('hr.unit', related='employee_id.unit_id', string="Unit")
    amount = fields.Float('Amount')
    master_batch_id = fields.Many2one('generate.payroll.master')
    slip_id = fields.Many2one('hr.payslip', string="Payslip")

class TransportDeduction(models.Model):
    _name = 'transport.deduction'

    employee_id = fields.Many2one('hr.employee')
    father_name = fields.Char('Father Name', related='employee_id.father_name')
    unit_id = fields.Many2one('hr.unit', related='employee_id.unit_id', string="Unit")
    amount = fields.Float('Amount')
    master_batch_id = fields.Many2one('generate.payroll.master')
    slip_id = fields.Many2one('hr.payslip', string="Payslip")
class OtherAllowance(models.Model):
    _name = 'other.allowance'

    employee_id = fields.Many2one('hr.employee')
    father_name = fields.Char('Father Name', related='employee_id.father_name')
    unit_id = fields.Many2one('hr.unit', related='employee_id.unit_id', string="Unit")
    amount = fields.Float('Amount')
    master_batch_id = fields.Many2one('generate.payroll.master')
    slip_id = fields.Many2one('hr.payslip', string="Payslip")
class AbsenceDeduction(models.Model):
    _name = 'absence.deductions'

    employee_id = fields.Many2one('hr.employee')
    father_name = fields.Char('Father Name', related='employee_id.father_name')
    unit_id = fields.Many2one('hr.unit', related='employee_id.unit_id', string="Unit")
    amount = fields.Float('Amount')
    master_batch_id = fields.Many2one('generate.payroll.master')
    slip_id = fields.Many2one('hr.payslip')


