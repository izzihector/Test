from odoo import fields, models, api
from odoo.tools.translate import _
from odoo.exceptions import UserError
from odoo.exceptions import ValidationError
from datetime import datetime

class JobExtended(models.Model):
    _name = 'hr.job'
    _inherit = ['hr.job','mail.thread','mail.activity.mixin','resource.mixin']
  
    is_published = fields.Boolean('Is Published', copy=False, default=True, index=True)
    state = fields.Selection([
        ('draft', 'Draft'),
        ('recruit', 'Recruitment in Progress'),
        ('close', 'Recruitment Done'),
        
    ], string='Status', readonly=True, required=True, tracking=True, copy=False, default='draft', help="Set whether the recruitment process is open or closed for this job position.")

    job_poisition_in_dari = fields.Char("وظیفه")

    # def send_to_hr_manager(self):
    #     for rec in self:
    #         rec.write({
    #             'state':'hr'
    #         })
    #         rec.activity_hr_manager()

    # def set_recruit(self):
    #     for record in self:
    #         no_of_recruitment = 1 if record.no_of_recruitment == 0 else record.no_of_recruitment
    #         record.write({'state': 'recruit', 'no_of_recruitment': no_of_recruitment})
    #         record.write({'is_published': True})
    #         record.activity_unlink(['nl_recruitment.mail_director_approval'])
    #     return True

    # def activity_hr_manager(self):
        
        
    #     note = _('Job Position created by %s.') % (
    #         self.create_uid.name)
    #     groups = []
    #     user = self.env['res.users']
    #     groups.extend(user.search([]).filtered(
    #         lambda x: x.has_group("hr.group_hr_manager")).ids)
    #     users = list(set(groups))
    #     print(users)
    #     for login in users:
    #         account_manager = user.browse(login)
    #         self.activity_schedule(
    #             'nl_recruitment.mail_hr_manager_approval',
    #             note=note,
    #             user_id=account_manager.id or self.env.user.id)

    # def send_to_director(self):
    #     for rec in self:
    #         rec.write({
    #             'state':'ceo'
    #         })
    #         rec.activity_director()
    #         rec.activity_unlink(['nl_recruitment.mail_hr_manager_approval'])

    # def activity_director(self):
       
        
    #     note = _('Job Position created by %s that needs your approval.') % (
    #         self.create_uid.name)
    #     groups = []
    #     user = self.env['res.users']
    #     groups.extend(user.search([]).filtered(
    #         lambda x: x.has_group("nl_contract.group_ceo")).ids)
    #     users = list(set(groups))
       
    #     for login in users:
    #         account_manager = user.browse(login)
    #         self.activity_schedule(
    #             'nl_recruitment.mail_director_approval',
    #             note=note,
    #             user_id=account_manager.id or self.env.user.id)


class SelectionCriteria(models.Model):
    _name ='selection.criteria'
    _description = 'Candidate Selection Criteria'
    
    _sql_constraints = [("unique_record", "unique(qualification, job_announcement_id)", "A Creteria with the same qualification already exits for the current announcement.")]

    qualification = fields.Selection([
        ('0','Illiterate'),
        ('1','Primary'),
        ('2','Grade 12'),
        ('3','Grade 14'),
        ('4','Bachelor'),
        ('5','Master'),
        ('6','Doctorate'),
    ],string="Qualification")

    years_of_experience = fields.Float('Years of Experience')
    job_announcement_id = fields.Many2one('hr.job.announcement')
