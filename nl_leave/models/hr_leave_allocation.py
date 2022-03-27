# -*- coding: utf-8 -*-

import logging

from datetime import datetime, time, date, timedelta
from dateutil.relativedelta import relativedelta

from odoo import api, fields, models
from odoo.addons.resource.models.resource import HOURS_PER_DAY
from odoo.exceptions import AccessError, UserError, ValidationError
from odoo.tools.translate import _
from odoo.tools.float_utils import float_round

_logger = logging.getLogger(__name__)



class HolidaysAllocation(models.Model):
    _inherit = "hr.leave.allocation"

    _sql_constraints = [
        ('type_value',
         "CHECK((holiday_type='employee' AND employee_id IS NOT NULL) or "
         "(holiday_type='company' AND mode_company_id IS NOT NULL) or "
         "(holiday_type='office' AND office_id IS NOT NULL) or "
         "(holiday_type='category' AND category_id IS NOT NULL) or "
         "(holiday_type='department' AND department_id IS NOT NULL) )",
         "The employee, department, company, office or employee category of this request is missing. Please make sure that your user login is linked to an employee."),
        ('date_check2', "CHECK ((date_from <= date_to))", "The start date must be anterior to the end date."),
        ('duration_check', "CHECK ( number_of_days >= 0 )", "If you want to change the number of days you should use the 'period' mode"),
    ]


    created_by_carry_over = fields.Boolean(defualt=False, readonly=True, string="Created From Carry Over")
    holiday_type = fields.Selection(selection = [
        ('employee', 'By Employee'),
        ('company', 'By Company'),
        ('office', 'By Office'),
        ('department', 'By Department'),
        ('category', 'By Employee Tag')],
        string='Allocation Mode', readonly=True, required=True, default='employee',
        states={'draft': [('readonly', False)], 'confirm': [('readonly', False)]},
        help="Allow to create requests in batchs:\n- By Employee: for a specific employee"
             "\n- By Company: all employees of the specified company"
             "\n- By Office: all employees of the specified office"
             "\n- By Department: all employees of the specified department"
             "\n- By Employee Tag: all employees of the specific employee group category")

    office_id = fields.Many2one('office', compute='_compute_office_id', store=True, readonly=False, string='Office')
    unit_id = fields.Many2one('hr.unit', compute='_compute_unit_id', store=True, readonly=False, string='Unit')

    def _get_responsible_for_approval(self):
        self.ensure_one()
        responsible = self.env.user
        if self.validation_type == 'manager' or (self.validation_type == 'both' and self.state == 'confirm'):
            if self.employee_id.leave_manager_id:
                responsible = self.employee_id.leave_manager_id
        elif self.validation_type == 'hr' or (self.validation_type == 'both' and self.state == 'validate1'):
            emp_office_id = self.employee_id.office_id
            responsible_rec = self.env['hr.contract.approver'].search([('office_id', '=', emp_office_id.id)])
            if responsible_rec and responsible_rec.leave_approver_id:
                responsible = responsible_rec.leave_approver_id
            elif self.holiday_status_id.responsible_id:
                responsible = self.holiday_status_id.responsible_id

        return responsible


    def action_validate(self):
        context = dict(self._context) or {}
        current_employee = self.env.user.employee_id
        for holiday in self:
            if holiday.state not in ['confirm', 'validate1'] and not context.get('bypass_rules', False):
                raise UserError(_('Allocation request must be confirmed in order to approve it.'))

            holiday.write({'state': 'validate'})
            if holiday.validation_type == 'both':
                holiday.write({'second_approver_id': current_employee.id})
            else:
                holiday.write({'first_approver_id': current_employee.id})

            holiday._action_validate_create_childs()
        self.activity_update()
        return True

    @api.depends('employee_id')
    def _compute_unit_id(self):
        for rec in self:
            rec.unit_id = rec.employee_id and rec.employee_id.unit_id or False

    @api.depends('employee_id', 'holiday_type')
    def _compute_office_id(self):
        for holiday in self:
            if holiday.employee_id:
                holiday.office_id = holiday.employee_id.office_id
            elif holiday.holiday_type == 'office':
                if not holiday.office_id:
                    holiday.office_id = self.env.user.employee_id.office_id
            else:
                holiday.office_id = False

    @api.depends('holiday_type')
    def _compute_from_holiday_type(self):
        for holiday in self:
            if holiday.holiday_type == 'employee':
                if not holiday.employee_id:
                    holiday.employee_id = self.env.user.employee_id
                    holiday.office_id =  holiday.employee_id.office_id.id
                holiday.mode_company_id = False
                holiday.category_id = False
            elif holiday.holiday_type == 'company':
                holiday.employee_id = False
                if not holiday.mode_company_id:
                    holiday.mode_company_id = self.env.company.id
                holiday.category_id = False
            elif holiday.holiday_type == 'department':
                holiday.employee_id = False
                holiday.mode_company_id = False
                holiday.category_id = False
            elif holiday.holiday_type == 'category':
                holiday.employee_id = False
                holiday.mode_company_id = False
            elif holiday.holiday_type == 'office':
                holiday.employee_id = False
                holiday.mode_company_id = False
                holiday.category_id = False
            else:
                holiday.employee_id = self.env.context.get('default_employee_id') or self.env.user.employee_id
    

    def _action_validate_create_childs(self):
        childs = self.env['hr.leave.allocation']
        if self.state == 'validate' and self.holiday_type in ['category', 'department', 'company', 'office']:
            if self.holiday_type == 'category':
                employees = self.category_id.employee_ids
            elif self.holiday_type == 'office':
                employees = self.env['hr.employee'].search([('office_id', '=', self.office_id.id)])
            elif self.holiday_type == 'department':
                employees = self.department_id.member_ids
            else:
                employees = self.env['hr.employee'].search([('company_id', '=', self.mode_company_id.id)])
            for employee in employees:
                holiday_values =  self._prepare_holiday_values(employee)
                holiday_values.update({'office_id': employee.office_id.id})
                childs += self.with_context(
                    mail_notify_force_send=False,
                    mail_activity_automation_skip=True
                ).create(holiday_values)
            # TODO is it necessary to interleave the calls?
            childs.action_approve()
            if childs and self.validation_type == 'both':
                childs.action_validate()
        return childs




    def create_new_allocation_records_for_new_year(self):
        """ This function deactivete old leave type records and create new one for the new year with new allocations. """
        leave_types = self.env['hr.leave.type'].search([('allow_carry_over', '=', True), ("maximum_transfer", '>', 0), ('validity_start', '!=', False), ('validity_stop', '!=', False)])
        if not leave_types:
            raise ValidationError(_("You cannot run the carry over scheduler at this time. Try again at the begining of the next leave year"))
            
        self.env['employee.leave.balance'].with_context(not_return_view=True).action_time_off_balance_extended_all()
        for leave_type in leave_types:
            if leave_type.validity_start.year != datetime.today().year:
                new_year = leave_type.validity_start.year + 1
                old_name = leave_type.name.split(' ')
                new_name = ''.join(i + ' ' for i in old_name if not i.isdigit()) + str(new_year) 
                new_leave_type = leave_type.copy({ 
                    "name": new_name,
                    "validity_start": datetime(new_year, 1,1),
                    "validity_stop":  datetime(new_year, 12,31)
                    })

                leave_balance_records = self.env['employee.leave.balance'].search([('leave_type', '=', leave_type.id), ('total_balance', '>', 0)])
                for leave_balance_record in leave_balance_records:
                    self.env['hr.leave.allocation'].create({
                        'name': leave_balance_record.employee_id.name + "- Carry Over Allocation for " + str(new_year),
                        'holiday_status_id': new_leave_type.id,
                        'number_of_days': leave_balance_record.total_balance if leave_balance_record.total_balance <= leave_type.maximum_transfer else  leave_type.maximum_transfer,
                        'employee_id': leave_balance_record.employee_id.id,
                        'state': 'validate',
                        'date_from': datetime(new_year, 1,1),
                        'date_to': datetime(new_year, 12,31),
                        'created_by_carry_over': True,
                        })
                leave_type.active = False
        
    @api.model
    def _update_accrual(self):
        print("sadflkjhadsklfjadsklfjasldk")
        """
            Method called by the cron task in order to increment the number_of_days when
            necessary.
        """
        today = fields.Date.from_string(fields.Date.today())

        holidays = self.search([('allocation_type', '=', 'accrual'), ('employee_id.active', '=', True), ('state', '=', 'validate'), ('holiday_type', '=', 'employee'),
                                '|', ('date_to', '=', False), ('date_to',
                                                               '>', fields.Datetime.now()),
                                '|', ('nextcall', '=', False), ('nextcall', '<=', today)])

        for holiday in holidays:
            values = {}

            delta = relativedelta(days=0)

            if holiday.interval_unit == 'weeks':
                delta = relativedelta(weeks=holiday.interval_number)
            if holiday.interval_unit == 'months':
                delta = relativedelta(months=holiday.interval_number)
            if holiday.interval_unit == 'years':
                delta = relativedelta(years=holiday.interval_number)

            values['nextcall'] = (
                holiday.nextcall if holiday.nextcall else today) + delta

            period_start = datetime.combine(today, time(0, 0, 0)) - delta
            period_end = datetime.combine(today, time(0, 0, 0))

            # We have to check when the employee has been created
            # in order to not allocate him/her too much leaves
            start_date = holiday.employee_id._get_date_start_work()
            # If employee is created after the period, we cancel the computation
            # if period_end <= start_date:
            #     holiday.write(values)
            #     continue

            # If employee created during the period, taking the date at which he has been created
            # if period_start <= start_date:
            #     period_start = start_date

            worked = holiday.employee_id._get_work_days_data(period_start, period_end, domain=[(
                'holiday_id.holiday_status_id.unpaid', '=', True), ('time_type', '=', 'leave')])['days']
            left = holiday.employee_id._get_leave_days_data(period_start, period_end, domain=[(
                'holiday_id.holiday_status_id.unpaid', '=', True), ('time_type', '=', 'leave')])['days']
            prorata = worked / (left + worked) if worked else 0
            
            #first date of last month.
            
            last_day_of_prev_month = date.today().replace(day = 1) - timedelta(days = 1)
            start_day_of_prev_month = date.today().replace(day = 1) - timedelta(days = last_day_of_prev_month.day)
            print(start_day_of_prev_month)
            print(last_day_of_prev_month)
            last_month_leaves = self.get_previous_month_leave(holiday.employee_id, start_day_of_prev_month, last_day_of_prev_month)
            print("-----------------------------")
            last_month_leave_days = 0
            print(last_month_leaves)
            for leave in last_month_leaves:
                if leave.holiday_status_id.include_in_leave_allocation_balance == True:
                    last_month_leave_days = last_month_leave_days + leave.number_of_days
            print(last_month_leave_days)
            last_month_leave_days = last_month_leave_days * (holiday.number_per_interval / 22 ) 
            print("last_month_leave_days", last_month_leave_days)
            print('empployee', holiday.employee_id.name)
            if last_month_leave_days > 0:
                days_to_give = holiday.number_per_interval - last_month_leave_days
            else:
                days_to_give = holiday.number_per_interval
            print(holiday.employee_id.name + " - " + str(days_to_give))
            print("-----------------------------")
            if holiday.unit_per_interval == 'hours':
                # As we encode everything in days in the database we need to convert
                # the number of hours into days for this we use the
                # mean number of hours set on the employee's calendar
                days_to_give = days_to_give / \
                    (holiday.employee_id.resource_calendar_id.hours_per_day or HOURS_PER_DAY)
               
            values['number_of_days'] = holiday.number_of_days + \
                days_to_give * prorata
            if holiday.accrual_limit > 0:
                values['number_of_days'] = min(
                    values['number_of_days'], holiday.accrual_limit)

            holiday.write(values)


    def get_previous_month_leave(self, employee_id, date_from, date_to):
        """
            Method to get the leave days of the previous month
        """
        # Get the previous month
        # date_from = date_from - relativedelta(months=1)
        # date_to = date_to - relativedelta(months=1)

        # Get the leave days of the previous month
        leaves = self.env['hr.leave'].sudo().search([('employee_id', '=', employee_id.id), ('date_from', '>=', date_from),
                              ('date_to', '<=', date_to), ('state', '=', 'validate')])

        return leaves


    @api.depends('holiday_status_id', 'allocation_type', 'number_of_hours_display', 'number_of_days_display')
    def _compute_from_holiday_status_id(self):
        for allocation in self:
            allocation.number_of_days = allocation.number_of_days_display
            if allocation.type_request_unit == 'hour':
                allocation.number_of_days = allocation.number_of_hours_display / (allocation.employee_id.sudo().resource_calendar_id.hours_per_day or HOURS_PER_DAY)

            # set default values
            if not allocation.interval_number and not allocation._origin.interval_number:
                allocation.interval_number = 1
            if not allocation.number_per_interval and not allocation._origin.number_per_interval:
                allocation.number_per_interval = self.env.user.company_id.number_per_interval
            if not allocation.unit_per_interval and not allocation._origin.unit_per_interval:
                allocation.unit_per_interval = 'hours'
            if not allocation.interval_unit and not allocation._origin.interval_unit:
                allocation.interval_unit = 'months'

            if allocation.holiday_status_id.validity_stop and allocation.date_to:
                new_date_to = datetime.combine(allocation.holiday_status_id.validity_stop, time.max)
                if new_date_to < allocation.date_to:
                    allocation.date_to = new_date_to
            
            if allocation.allocation_type == 'accrual':
                if allocation.holiday_status_id.request_unit == 'hour':
                    allocation.unit_per_interval = 'hours'
                else:
                    allocation.unit_per_interval = 'days'
            else:
                allocation.interval_number = 1
                allocation.interval_unit = 'months'
                allocation.number_per_interval = self.env.user.company_id.number_per_interval
                allocation.unit_per_interval = 'hours'

class ResCompanyLeave(models.Model):
    _inherit = 'res.company'

    number_per_interval = fields.Float("Number of unit per interval", required=True,  default=1.67)
    