from odoo import api, fields, models, _
from odoo.exceptions import ValidationError

class HrRecruitmentStage(models.Model):
    _inherit = "hr.recruitment.stage"
    _description = "Recruitment Stages"

    state_mode = fields.Selection([
        ('not_qualified', 'Not Qualified'),
        ('qualified', 'Qualified'),
        ('shortlisted', 'Shortlisted'),
        ('written_test', 'Written Test'),
        ('interview', 'Interview'),
        ('offer_proposal', 'Offer Proposal'),
        ('offer_signed', 'Offer Signed'),
        ('disqualified', 'Disqualified'),
        ('refused', 'Refused'),
        ('blacklisted', 'Blacklisted'),
        ('none', 'None')
        ],default="none",required=True)

    @api.constrains("state_mode")
    def check_state_mode_unique(self):
        for rec in self:
            if rec.state_mode and rec.state_mode != 'none' and self.search_count([('state_mode', '=', rec.state_mode), ('id', '!=', rec.id)]) > 0:
                raise ValidationError(_("You can not configure two stages with the same state mode."))