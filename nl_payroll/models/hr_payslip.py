# -*- coding: utf-8 -*-

from odoo import api, fields, models, _
from datetime import datetime, timedelta
from odoo.exceptions import UserError
from odoo.exceptions import UserError, ValidationError
from collections import defaultdict
import pytz
from datetime import datetime, date, time
from odoo.tools.misc import format_date
from odoo.tools import DEFAULT_SERVER_DATETIME_FORMAT, date_utils

class HrPayslip(models.Model):
    _name = 'hr.payslip'
    _inherit = ['hr.payslip','mail.thread','mail.activity.mixin','resource.mixin']
    
    donor_code = fields.Char(string="Donor Code", tracking=True, store=True)
    cost_center = fields.Char(string="Cost Center", tracking=True,store =True)
    office_id = fields.Many2one('office', string="Office", related="employee_id.office_id",store=True)
    department_id = fields.Many2one('hr.department', string="Department", related="employee_id.department_id",store=True)
    unit_id = fields.Many2one('hr.unit', string="Unit", related="employee_id.unit_id",store=True)
    project_id = fields.Many2one('contract.project', string="Project", related="employee_id.project_id",store=True)
    employee_type = fields.Selection(related="employee_id.employee_type", string="Employee Type", store=True)
    job_id = fields.Many2one('hr.job', string="Job", related="employee_id.job_id",store=True)
    bank_id = fields.Many2one('bank.bank', string="Bank", related="employee_id.bank_id",store=True)
    bank_account = fields.Char(string="Bank Account", related="employee_id.bank_account",store=True)
    contract_start_date = fields.Date(string="Start Date", related="contract_id.date_start",store=True)
    contract_end_date = fields.Date(string="End Date", related="contract_id.date_end",store=True)
    grade_and_step = fields.Char(string="Grade and Step", related="contract_id.grade_and_step",store=True)
    payroll_group_id = fields.Many2one('payroll.group', string="Payroll Group", related="employee_id.payroll_group_id",store=True)
    employment_type = fields.Selection(related="contract_id.employment_type", string="Employment Type", store=True)
    total_absence_from_separation = fields.Float('Separation Absence', readonly=True)
    total_absence = fields.Float("Total Absent Days")
    total_late_hours = fields.Float(string="Late Hours")
    attendance_mode = fields.Char(string="Attendance Mode")
    pdf_result = fields.Binary('Payslip PDF')
    pension_amount = fields.Float(string="Pension Amount") 
    total_net_salary = fields.Float(string="Total Net Salary", compute="_get_total_net_salary")
    master_batch_id = fields.Many2one('generate.payroll.master', string="Master Batch", tracking=True, store=True)
    state = fields.Selection([
        ('draft', 'Draft'),
        ('hr','HR Review'),
        ('finance','Finance Review'),
        ('verify', 'Waiting'),
        ('done', 'Done'),
        ('cancel', 'Cancelled'),
    ], string='Status',  index=True, readonly=True, copy=False, default='draft',track_visibility=True,
        help="""* When the payslip is created the status is \'Draft\'
                \n* If the payslip is under verification, the status is \'Waiting\'.
                \n* If the payslip is confirmed then status is set to \'Done\'.
                \n* When user cancel payslip the status is \'Rejected\'.""")
    not_in_contract_days = fields.Float(string="New Hires Absence", readonly=True)

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

    ])
    leave_ids = fields.One2many(
        'attendance.absent',
        'payslip_id',
        string="Absence"
    )
    attendance_hour_ids = fields.One2many(
        'employee.payslip.attendance',
        'payslip_id',
        string="Late Hours"
    )

    probation_months = fields.Integer(string="Pension Months")
    probation_status = fields.Char(string="Probation Status", readonly=True)
    total_pension_payable = fields.Float(string="Total Pension Payable")
    remarks = fields.Text()
    separation_id = fields.Many2one('hr.separation')

    @api.onchange('employee_id', 'struct_id', 'contract_id', 'date_from', 'date_to')
    def _onchange_employee(self):
        if (not self.employee_id) or (not self.date_from) or (not self.date_to):
            return

        employee = self.employee_id
        date_from = self.date_from
        date_to = self.date_to

        self.company_id = employee.company_id
        if not self.contract_id or self.employee_id != self.contract_id.employee_id: # Add a default contract if not already defined
            contracts = employee._get_contracts(date_from, date_to)

            if not contracts or not contracts[0].structure_type_id.default_struct_id:
                self.contract_id = False
                self.struct_id = False
                return
            self.contract_id = contracts[0]
            self.struct_id = contracts[0].structure_type_id.default_struct_id

        lang = employee.sudo().address_home_id.lang or self.env.user.lang
        context = {'lang': lang}
        payslip_name = self.struct_id.payslip_name or _('Salary Slip')
        del context

        self.name = '%s - %s - %s' % (
            payslip_name,
            self.employee_id.name or '',
            format_date(self.env, self.date_to, date_format="MMMM y", lang_code=lang)
        )

        if date_to > date_utils.end_of(fields.Date.today(), 'month'):
            self.warning_message = _(
                "This payslip can be erroneous! Work entries may not be generated for the period from %(start)s to %(end)s.",
                start=date_utils.add(date_utils.end_of(fields.Date.today(), 'month'), days=1),
                end=date_to,
            )
        else:
            self.warning_message = False

        self.worked_days_line_ids = self._get_new_worked_days_lines()

    def unlink(self):
        if self.env.user.has_group("nl_payroll.group_payroll_finance"):
            raise UserError(_("Only admin users can delete a payslip."))

        if any(payslip.state not in ('draft') for payslip in self):
            raise UserError(_('You cannot delete a payslip which is not draft!'))
        return super(HrPayslip, self).unlink()


    def _get_total_net_salary(self):
        self.total_net_salary = 0.0
        for item in self.line_ids:
            if item.salary_rule_id.code == 'NET' and item.amount > 0:
                self.total_net_salary = item.amount
       


    def get_weekdays(self, date):
        return str(datetime.strptime(str(date), "%Y-%m-%d").date().weekday())

    def _get_from_and_to_timestamp_as_utc(self, date):
        mytz = pytz.timezone(self._context.get('tz') or self.env.user.tz)
        display_date_result = datetime.strftime(pytz.utc.localize(datetime.strptime(
            str(date), DEFAULT_SERVER_DATETIME_FORMAT)).astimezone(mytz), "%H:%M")
        return display_date_result


    def _get_full_date_from_timestamp(self, date):
        mytz = pytz.timezone(self._context.get('tz') or self.env.user.tz)
        display_date_result = datetime.strftime(pytz.utc.localize(datetime.strptime(
            str(date), DEFAULT_SERVER_DATETIME_FORMAT)).astimezone(mytz), "%Y-%m-%d")
        return display_date_result


    def calculate_employee_attendance_info(self, employee_id, date_start, date_end,payslip):
        """" This function calculates attendance information for an employee.

            Parameters:
                employee_id (int): ID of employee to get attendance information for.
                date_start, date_end (Datetime/Date): Range of date for which the attendance information are calculated.
                payslip, (Record): payslip record for which the attendance information are calculated.

            Returns:
                Employee Attendance Information (Dictionary): containing:
                    late_check_in_hours: Number of hours employee has checked in late compared to standard check-in hour.
                    early_check_in_hours: Number of hours employee has checked in early compared to standard check-in hour.
                    late_check_out_hours: Number of hours employee has checked out late compared to standard check-out hour.
                    early_check_out_hours: Number of hours employee has checked out early compared to standard check-out hour.
                    total_not_check_in: Total Number of times employee has not checked in.
                    total_no_check_out: Total Number of times employee has not checked out.
                    total_not_same_day_check_out: Total number of times employee has not checked out the same day he/she checked in.

            Behaviour:
                Standard check-in and check-out hours must be configured in employees working hour.
                Only in range of (date_start) and (date_end) attendance records will be processed.
                If attendance records does not have check_in it will be calculated as (total_not_checked in).
                If attendance records does not have check_out it will be calculated as (total_not_checked out).
                if attendance check-in hours are greather compared to Standard configuration check-in hours, it means employee has checked-in late.
                if attendance check-in hours are smaller compared to Standard configuration check-in hours, it means employee has checked-in early.
                if attendance check-out hours are greather compared to Standard configuration check-out hours, it means employee has checked-out late.
                if attendance check-out hours are smaller compared to Standard configuration check-out hours, it means employee has checked-out early.
                if attendance check-out is not in same date as check-in day, it will find difference between those dates and add it to (late_check_out_hours),
                    and adds up to (total_not_same_day_check_out);
        """
        self.attendance_hour_ids.unlink()
        if employee_id and date_start and date_end:
            employee = self.env['hr.employee'].browse(employee_id)
            employee_attendance = self.env['hr.attendance'].search([('employee_id', '=', employee_id), ('check_in', '>=', date_start), ('check_in', '<=', date_end)])
            calender = employee.resource_calendar_id
            late_data = {}
            for late in calender.late_hours_exception_ids:
                late_data.update({late.date: [late.skip_late_check_in, late.skip_early_check_out]})
            final_data = {
                'total_not_same_day_check_out': 0,
                'early_check_out_hours': 0,
                'early_check_in_hours': 0,
                'late_check_out_hours': 0,
                'late_check_in_hours': 0,
                'total_not_check_out': 0,
                'total_not_check_in': 0,
                'date': ''
                }
            final_db_data = []

            if calender.early_check_in and calender.early_check_out:
                calendar_start = datetime.strptime(calender.early_check_in, "%H:%M")
                calendar_end = datetime.strptime(calender.early_check_out, "%H:%M")
                for attendance in employee_attendance:
                    db_data = {
                        'payslip_id':payslip.id,
                        'employee_id': employee_id,
                        'date': str(attendance.check_in.strftime("%Y-%m-%d")),
                        'late_check_in_hours': 0.0,
                        'early_check_out_hours': 0.0,
                        }
                    if attendance.check_in:
                        attendance_start = datetime.strptime(self._get_from_and_to_timestamp_as_utc(attendance.check_in), "%H:%M")
                        attendance_full_date = datetime.strptime(self._get_full_date_from_timestamp(attendance.check_in), "%Y-%m-%d").date()
                        if (attendance_full_date in late_data and not late_data[attendance_full_date][0]) or not attendance_full_date in late_data:
                            if (attendance_start - calendar_start).days >= 0:
                                final_data['late_check_in_hours'] += (attendance_start - calendar_start).seconds / 3600
                                db_data.update({'late_check_in_hours': (attendance_start - calendar_start).seconds / 3600,
                                                'early_check_out_hours': 0.0})
                                final_data['date'] += str((attendance.check_in).date())
                                self.env['employee.payslip.attendance'].create(db_data)
                            else:
                                final_data['early_check_in_hours'] += (calendar_start - attendance_start).seconds / 3600
                    else:
                        final_data['total_not_check_in'] +=1

                    if attendance.check_out:
                        attendance_end = datetime.strptime(self._get_from_and_to_timestamp_as_utc(attendance.check_out), "%H:%M")
                        attendance_full_date = datetime.strptime(self._get_full_date_from_timestamp(attendance.check_in), "%Y-%m-%d").date()
                        if (attendance_full_date in late_data and not late_data[attendance_full_date][1]) or not attendance_full_date in late_data:
                            if (attendance_end - calendar_end).days >= 0:
                                # find if user has checked-out not in same day
                                if not attendance.check_in.strftime("%Y-%m-%d") == attendance.check_out.strftime("%Y-%m-%d"): 
                                    final_data['total_not_same_day_check_out'] +=1
                                    final_data['late_check_out_hours'] += (attendance.check_out - attendance.check_in).days * 24
                                final_data['late_check_out_hours'] += (attendance_end - calendar_end).seconds / 3600
                            else:
                                final_data['early_check_out_hours'] += (calendar_end - attendance_end).seconds / 3600
                                db_data.update({"early_check_out_hours":  (calendar_end - attendance_end).seconds / 3600,
                                                "late_check_in_hours": 0.0})
                            
                                self.env['employee.payslip.attendance'].create(db_data)
                    else:
                        final_data['total_not_check_out'] +=1

                    final_db_data.append(final_data)
            
            # if final_db_data:
            #     print(final_db_data)
            #     for emp_payslip_rec in final_db_data:
            #         created_rec = self.env['employee.payslip.attendance'].create(emp_payslip_rec)
                # print(created_rec)
            self.total_late_hours = float(final_data['late_check_in_hours']) + float(final_data['early_check_out_hours'])
            return final_data



    def absent_employees_master(self, employee_id,date_start,date_end,payslip):
        self._cr.execute("""DELETE FROM attendance_absent WHERE payslip_id = %s""", (payslip.id,))
        model_holidays = self.env['resource.calendar']
        payroll_date = []
        public_holidays = []
        leaves_taken = []
        employee_attendance = []
        weekday_lst = []
        work_schedule = employee_id.resource_calendar_id
        for attendance in work_schedule.attendance_ids:
            weekday_lst.append(attendance.dayofweek)
        delta = date_end - date_start
        for i in range(delta.days + 1):
            day = date_start + timedelta(days=i)
            if self.get_weekdays(day) in weekday_lst:
                payroll_date.append(str(day))
        
        for holiday in model_holidays.search([]):
            for public_holiday in holiday.global_leave_ids:
                day_count = (public_holiday.date_to - public_holiday.date_from).days + 1
                for h in [d for d in (public_holiday.date_from + timedelta(n) for n in range(day_count)) if d <= public_holiday.date_to]:
                    holiday_date = h.strftime('%Y-%m-%d')
                    if h.month == date_start.month or h.month == date_end.month:
                        print(holiday_date)
                        public_holidays.append(holiday_date)
        
        leaves = self.env['hr.leave'].search([
                            ('request_date_from', 'in', payroll_date),
                            ('employee_id', '=', employee_id.id),
                            ('state','=','validate')
                        ])
        for leave in leaves:
            delta = leave.request_date_to - leave.request_date_from
            for i in range(delta.days + 1):
                day = leave.request_date_from + timedelta(days=i)
                if self.get_weekdays(day) in weekday_lst:
                    leaves_taken.append(str(day))

        attendance = self.env['hr.attendance'].search([
            ('employee_id','=',employee_id.id)
        ])
        
        for item in attendance:
            if item.check_in.month == date_start.month or item.check_in.month == date_end.month:
                employee_attendance.append(str(item.check_in.date()))
        
        for item in payroll_date:
            if item not in employee_attendance:
                if item not in public_holidays:
                    if item not in leaves_taken:
                        self.env['attendance.absent'].sudo().create({
                            'employee_id':employee_id.id,
                            'leave_description':'Absent',
                            'date':item,
                            'payslip_id':payslip.id,
                            'master_batch_id':self.master_batch_id.id,
                        })
        self.total_absence = len(self.leave_ids)

    
    def nl_payslip_mail(self, employee, record):
        month = datetime.strptime(str(record), "%Y-%m-%d").date().strftime('%B')
        user = self.env['res.users']
        from_mail = user.browse(self._uid) and user.login or ''
        from_mail = from_mail.encode('utf-8')
        if employee.work_email and employee.work_email != 'N/A' and employee.work_email != 'n/a' and employee.work_email != 'NA':
            to_mail = (employee.work_email).encode('utf-8')
            if to_mail:

                email_template = self.env.ref(
                    'nl_payroll.mail_template_new_payslip_extended')
                if email_template:
                    if to_mail:
                        email_template.sudo().write({
                            'email_from': from_mail,
                            'email_to': to_mail
                        })
                        email_template.send_mail(self.id, force_send=False)


    def action_email_payslip(self):
        for record in self:
            record.nl_payslip_mail(record.employee_id, record.date_to)

    def calculate_manual_absent_days(self,employee_id):
        total = 0
        if self.separation_id:
            self.calculate_absence_days_from_separation()
        self.total_absence = 0.0
        self.not_in_contract_days = 0.0
        if self.check_if_date_is_in_range(self.date_from, self.date_to,self.contract_id.date_start):
            self.not_in_contract_days = self.get_differce_between_two_dates_in_days(self.date_from, self.contract_id.date_start)
            
        for item in self.master_batch_id.absent_employee_ids:
            if item.employee_id.id == employee_id:
                total = total + item.number_of_days
        
        self.total_absence = total
        
    def get_differce_between_two_dates_in_days(self,date_from,date_to):
        date_from = datetime.strptime(str(date_from), "%Y-%m-%d").date()
        date_to = datetime.strptime(str(date_to), "%Y-%m-%d").date()
        delta = date_to - date_from
        return delta.days

    def check_if_date_is_in_range(self,date_start,date_end,date):
        if date_start <= date <= date_end:
            return True
        else:
            return False
    
    def calculate_absence_days_from_separation(self):
        difference_interval = self.date_to - self.separation_id.relieve_date
        if float(difference_interval.days) > 0:
            self.total_absence_from_separation = difference_interval.days
        else:
            self.total_absence_from_separation = 0
           
    def get_differce_between_two_dates_in_months(self,date1,date2):
        date1 = datetime.strptime(date1, "%Y-%m-%d")
        date2 = datetime.strptime(date2, "%Y-%m-%d")
        return (date2.year - date1.year) * 12 + date2.month - date1.month

    def calculate_pension(self,contract):
        pension_data = contract.get_contraction_probation_info(self.date_from)
        if pension_data:
            self.probation_status = pension_data['probation_status']
            if pension_data['probation_status'] == 'Probation Ended':
                self.probation_months = pension_data['duration']
            

            
    def compute_sheet_master(self):
        payslips = self.filtered(lambda slip: slip.state not in ['cancel', 'done'])
        payslips.line_ids.filtered(lambda line: line.edited == False).unlink()
        for payslip in payslips:
            if payslip.attendance_mode == 'Attendance':
                payslip.absent_employees_master(payslip.employee_id, payslip.date_from, payslip.date_to,payslip)
                payslip.calculate_employee_attendance_info(payslip.employee_id.id, payslip.date_from, payslip.date_to,payslip)
            if payslip.attendance_mode == 'Manual':
                payslip.calculate_manual_absent_days(payslip.employee_id.id)
                
            else:
                if payslip.separation_id:
                    payslip.calculate_absence_days_from_separation()
            payslip.calculate_pension(payslip.contract_id)
            number = payslip.number or self.env['ir.sequence'].next_by_code('salary.slip')
            lines = [(0, 0, line) for line in payslip._get_payslip_lines()]
            if payslip.state == 'finance':
                payslip.write({'line_ids': lines, 'number': number, 'state': 'finance', 'compute_date': fields.Date.today()})
            elif payslip.state =='hr':
                payslip.write({'line_ids': lines, 'number': number, 'state': 'hr', 'compute_date': fields.Date.today()})
            elif payslip.state =='ready':
                payslip.write({'line_ids': lines, 'number': number, 'state': 'ready', 'compute_date': fields.Date.today()})
            else:
                payslip.write({'line_ids': lines, 'number': number, 'state': 'hr', 'compute_date': fields.Date.today()})
        return True

    def compute_sheet(self):

        if self.env.user.has_group("nl_payroll.group_payroll_finance") and self.state =='hr':
           raise UserError(_("Only admin users can compute the sheet in hr stage."))
        if self.env.user.has_group("hr_payroll.group_hr_payroll_manager") and not self.env.user.has_group("nl_payroll.group_payroll_finance") and self.state =='finance':
            raise UserError(_("Only finance users can compute the sheet in finance stage."))

        payslips = self.filtered(lambda slip: slip.state not in ['cancel', 'done'])
        print("calleled")
        payslips.line_ids.filtered(lambda line: line.edited == False).unlink()
        for payslip in payslips:
            if payslip.attendance_mode == 'Attendance':
                payslip.absent_employees_master(payslip.employee_id, payslip.date_from, payslip.date_to,payslip)
                payslip.calculate_employee_attendance_info(payslip.employee_id.id, payslip.date_from, payslip.date_to,payslip)
            if payslip.attendance_mode == 'Manual':
                payslip.calculate_manual_absent_days(payslip.employee_id.id)
                
            else:
                if payslip.separation_id:
                    payslip.calculate_absence_days_from_separation()
            payslip.calculate_pension(payslip.contract_id)
            number = payslip.number or self.env['ir.sequence'].next_by_code('salary.slip')
            get_edited_payslip_lines = self.line_ids.filtered(lambda line: line.edited == True)
            if get_edited_payslip_lines:
                lines = [(0, 0, line) for line in payslip._get_payslip_lines_recompute(get_edited_payslip_lines)]
            else:
                lines = [(0, 0, line) for line in payslip._get_payslip_lines_recompute(get_edited_payslip_lines=False)]
            payslips.line_ids.filtered(lambda line: line.edited == True).unlink()
            if payslip.state == 'finance':
                payslip.write({'line_ids': lines, 'number': number, 'state': 'finance', 'compute_date': fields.Date.today()})
            elif payslip.state =='hr':
                payslip.write({'line_ids': lines, 'number': number, 'state': 'hr', 'compute_date': fields.Date.today()})
            elif payslip.state =='ready':
                payslip.write({'line_ids': lines, 'number': number, 'state': 'ready', 'compute_date': fields.Date.today()})
            else:
                payslip.write({'line_ids': lines, 'number': number, 'state': 'hr', 'compute_date': fields.Date.today()})
        return True
    
    def get_payslip_lines_codes_already_computed(self,lines):
        rules = []
        for line in lines:
            if line.edited == True:
                rules.append(line.code)
    def change_payslip_state_to_finance(self):
        for payslip in self.filtered(lambda slip: slip.state not in ['cancel', 'done']):
            payslip.write({'state': 'finance'})
        return True

    def resend_to_hr_stage(self):
        for payslip in self.filtered(lambda slip: slip.state not in ['cancel', 'done']):
            payslip.write({'state': 'hr'})
        return True

    def resend_to_finance_stage(self):
        for payslip in self.filtered(lambda slip: slip.state not in ['cancel', 'done']):
                payslip.write({'state': 'finance'})  
        return True

    def set_payslips_as_draft(self):
        for payslip in self.filtered(lambda slip: slip.state not in ['cancel', 'done']):
                payslip.write({'state': 'draft'})   
        return True


    def _get_payslip_lines_recompute(self,get_edited_payslip_lines):
        self.ensure_one()
        
        localdict = self.env.context.get('force_payslip_localdict', None)
        if localdict is None:
            localdict = self._get_localdict()

        rules_dict = localdict['rules'].dict
        result_rules_dict = localdict['result_rules'].dict

        blacklisted_rule_ids = self.env.context.get('prevent_payslip_computation_line_ids', [])

        result = {}

        

        for rule in sorted(self.struct_id.rule_ids, key=lambda x: x.sequence):
            if rule.id in blacklisted_rule_ids:
                continue
            localdict.update({
                'result': None,
                'result_qty': 1.0,
                'result_rate': 100})
            if rule._satisfy_condition(localdict):
                if get_edited_payslip_lines:
                    if rule in get_edited_payslip_lines.mapped('salary_rule_id'):
                        amount = get_edited_payslip_lines.filtered(lambda x: x.code == rule.code).amount
                        qty = 1.0
                        rate = 100
                        
                    else:
                        amount, qty, rate = rule._compute_rule(localdict)
                else:
                    amount, qty, rate = rule._compute_rule(localdict)

                #check if there is already a rule computed with that code
                previous_amount = rule.code in localdict and localdict[rule.code] or 0.0
                
                #set/overwrite the amount computed for this rule in the localdict
                tot_rule = amount * qty * rate / 100.0
                localdict[rule.code] = tot_rule
                result_rules_dict[rule.code] = {'total': tot_rule, 'amount': amount, 'quantity': qty}
                rules_dict[rule.code] = rule
                # sum the amount for its salary category
                localdict = rule.category_id._sum_salary_rule_category(localdict, tot_rule - previous_amount)
                # Retrieve the line name in the employee's lang
                employee_lang = self.employee_id.sudo().address_home_id.lang
                # This actually has an impact, don't remove this line
                context = {'lang': employee_lang}
                if rule.code in ['BASIC', 'GROSS', 'NET']:  # Generated by default_get (no xmlid)
                    if rule.code == 'BASIC':
                        rule_name = _('Basic Salary')
                    elif rule.code == "GROSS":
                        rule_name = _('Gross')
                    elif rule.code == 'NET':
                        rule_name = _('Net Salary')
                else:
                    rule_name = rule.with_context(lang=employee_lang).name
                # create/overwrite the rule in the temporary results
                
                result[rule.code] = {
                    'sequence': rule.sequence,
                    'code': rule.code,
                    'edited':True if get_edited_payslip_lines and rule in get_edited_payslip_lines.mapped('salary_rule_id') else False,
                    'name': rule_name, 
                    'note': rule.note,
                    'salary_rule_id': rule.id,
                    'contract_id': localdict['contract'].id,
                    'employee_id': localdict['employee'].id,
                    'amount': amount,
                    'quantity': qty,
                    'rate': rate,
                    'slip_id': self.id,
                }
        return result.values()





    @api.onchange('salary_rule_id','payslip_id')
    def return_related_rules(self):
        related_budget_lines = []
        budget_lines = None
        
        budget_lines = self.env['hr.salary.rule'].search([('struct_id','=',self.payslip_id.struct_id.id)])
        for item in budget_lines:
            related_budget_lines.append(item.id)
        return {'domain': {'salary_rule_id': [('id', 'in', related_budget_lines)]}}
    
                    
class HrSalaryRuleExtended(models.Model):
    _inherit = 'hr.salary.rule'

    importable = fields.Boolean("Importable")

    

class HrPayslipLine(models.Model):
    _name = 'hr.payslip.line'
    _inherit = ['hr.payslip.line','mail.thread']

    edited = fields.Boolean("Edited")
    amount = fields.Float(digits='Payroll', tracking=True)


    def _track_subtype(self, init_values):
        self.ensure_one()
        if 'amount' in init_values:
            self.slip_id.message_post(body=f"{self.name}: {init_values.get('amount')} -> {self.amount}")
        return super(HrPayslipLine, self)._track_subtype(init_values)

    @api.onchange('amount','qty','rate')
    def _update_line_edited(self):
        for line in self:
            line.edited = True


class ResourceCalendarInhrit(models.Model):

    _inherit = "resource.calendar"

    early_check_in = fields.Char(string="Late Check In")
    early_check_out = fields.Char()

# class PayslipAttendanceLateHours(mdoels.Model):
