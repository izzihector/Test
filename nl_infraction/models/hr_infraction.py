# -*- coding: utf-8 -*-

from datetime import date, datetime
from odoo import models, fields, api, _
from odoo.exceptions import ValidationError, UserError


class HrInfraction(models.Model):
    _name = 'hr.infraction'
    _inherit = ['mail.activity.mixin','mail.thread']
    _description = 'HR Infraction'

    name = fields.Char(
        string='Subject',
        size=256
    )

    subject = fields.Char(
        string="Subject",
        size=256
    )
    employee_id = fields.Many2one('hr.employee',string="Employee")
    employee_type = fields.Selection([

    ],related='employee_id.employee_type')
    infraction_date = fields.Date(string="Date",default=date.today())
    state = fields.Selection([
        ('draft','Draft'),
        ('hr','HR Manager'),
        ('action', 'Action'),
        ('noaction', 'No Action'),
    ],default='draft',string="Status")
    warning = fields.Selection([
        ('1','Written Reminder'),
        ('2','First Warning'),
        ('3','Second Warning'),
        ('4','Transfer or Demotion'),
        ('5',' Dismissal and Abrogation of labor contract')
    ],string="Warning")
    category_id = fields.Many2one(
        'hr.infraction.category',
        string='Category'
    )
    action_ids = fields.One2many(
        'hr.infraction.action',
        'infraction_id',
        string='Actions'
    )
    memo = fields.Html(
        string='Description'
    )

    @api.model
    def create(self, vals):
        sequence = self.env['ir.sequence'].next_by_code('hr.infraction')
        vals['name'] = sequence or _('New')
        infraction = super(HrInfraction, self).create(vals)
        return infraction

    
    def unlink(self):
        """
        This method will raise warning if infraction is \
        deleted without being in draft state.
        ------------------------------------------------
        @param self : object pointer
        """
        for inf in self:
            if inf.state != 'draft':
                raise ValidationError(_('Infractions that have progressed \
                                    beyond "Draft" state may not be removed.'))
        return super(HrInfraction, self).unlink()


    def submit(self):
        """
        This method will change the state to confirm when \
        the button is clicked.
        ------------------------------------------------
        @param self : object pointer
        """
        for rec in self:
            rec.state = 'hr'
            rec.activity_hr_manager()

    
    def confirm(self):
        for rec in self:
            rec.update({
                'state': 'ceo'
            })
            rec.activity_director()
            self.activity_unlink(['nl_infraction.mail_hr_manager_activity'])
    

    def noaction(self):
        """
        This method will change the state to no action \
        when the button is clicked.
        ------------------------------------------------
        @param self : object pointer
        """
        for rec in self:
            rec.state = 'noaction'
            rec.activity_unlink(['nl_infraction.mail_ceo_warning_activity'])

    
    def activity_hr_manager(self):
        
        note = _('Warning Raised Against %s.') % (
            self.employee_id.name)

        users = []
        office = self.employee_id.office_id
        hr_contract_approver = self.env['hr.contract.approver'].sudo().search([('office_id', '=', office.id)], limit=1)
        if not hr_contract_approver:
            raise UserError(_("There is no approval configuration setup for infractions for the office of the selected employee: %s. Contact your administrator to resolve the issue."% (office.name, )))
        users = hr_contract_approver.infraction_approver_ids
        for login in users:
            self.activity_schedule(
                'nl_infraction.mail_hr_manager_activity',
                note=note,
                user_id=login.id or self.env.user.id)

    def activity_director(self):
        
        note = _('The HR department has issued a warning to %s that needs your review and approval. ') % (
            self.employee_id.name)
        groups = []
        user = self.env['res.users']
        groups.extend(user.search([]).filtered(
            lambda x: x.has_group("nl_contract.group_ceo")).ids)
        users = list(set(groups))
       
        for login in users:
            account_manager = user.browse(login)
            self.activity_schedule(
                'nl_infraction.mail_ceo_warning_activity',
                note=note,
                user_id=account_manager.id or self.env.user.id)


ACTION_TYPE_SELECTION = [
    ('written_reminder','Written Reminder'),
    ('first_warning','First Warning'),
    ('second_warning','Second Warning'),
    ('transfer', 'Transfer or Demotion'),
    ('dismissal', 'Dismissal and Abrogation of Labor Contract'),

]


class HrInfractionCategory(models.Model):
    _name = 'hr.infraction.category'
    _description = 'HR Infraction Type'

    name = fields.Char(
        string='Name'
    )
    code = fields.Char(
        string='Code'
    )


class HrInfractionAction(models.Model):
    _name = 'hr.infraction.action'
    _description = 'Action Based on Infraction'
    _rec_name = 'type'

    infraction_id = fields.Many2one(
        'hr.infraction', 
        string='Infraction',
        ondelete='cascade'
    )
    type = fields.Selection(
        ACTION_TYPE_SELECTION,
        string='Action Type'
    )
    memo = fields.Text(
        string='Notes'
    )
    employee_id = fields.Many2one(
        'hr.employee',
        string='Employee'
    )
    warning = fields.Selection([
        ('1','Written Reminder'),
        ('2','First Warning'),
        ('3','Second Warning'),
        ('4','Transfer or Demotion'),
        ('5',' Dismissal and Abrogation of labor contract')
    ],string="Warning")
    date = fields.Date(
        string='Date',
        default=datetime.now()
    )


class InfractionDocument(models.Model):
    _name = 'infraction.document'
    _description = 'Infraction Document'

    name = fields.Binary(
        string='Document'
    )
    file_name = fields.Char(
        string='Document name'
    )
    infraction_id = fields.Many2one(
        'hr.infraction'
    )


class HrEmployee(models.Model):
    _name = 'hr.employee'
    _inherit = 'hr.employee'

    infraction_action_ids = fields.One2many(
        'hr.infraction.action', 'employee_id',
        string='Disciplinary Actions'
    )

