# -*- coding: utf-8 -*-

from datetime import datetime
from odoo.tools import DEFAULT_SERVER_DATETIME_FORMAT
from odoo import fields, models
from odoo.addons.nl_infraction.models.hr_infraction import ACTION_TYPE_SELECTION


class ActionWizard(models.TransientModel):
    _name = 'hr.infraction.action.wizard'
    _description = 'Choice of Actions for Infraction'

    action_type = fields.Selection(
        ACTION_TYPE_SELECTION,
        string='Action'
    )
    memo = fields.Text(
        string='Notes'
    )
    new_job_id = fields.Many2one(
        'hr.job',
        string='New Job'
    )
    effective_date = fields.Date(
        string='Effective Date',
        default=datetime.now().date()
    )

    def wiz_action(self):
        """
        This method will create an action to no action against employee \
        when clicked on Take Action Button and will write the job_id of the \
        respective employee.
        ------------------------------------------------
        @param self : object pointer
        """
        infraction = self.env['hr.infraction'].search([('id','=',self._context.get('active_id'))])
        inf_id = infraction.id

        print("+++++++++++++++",inf_id)
        ac_type = self.action_type
        act_memo = self.memo
        curr_dt = datetime.now()
        cr_dt = curr_dt.strftime(DEFAULT_SERVER_DATETIME_FORMAT)
        warning_rec = infraction.warning

        if warning_rec:
            act_obj = self.env['hr.infraction.action']
            act_vals = {
                'date': cr_dt,
                'memo': act_memo,
                'type': ac_type,
                'infraction_id': inf_id,
                'employee_id': infraction.employee_id.id,
                'warning': warning_rec,

            }
            act_obj.create(act_vals)
        infraction.state = 'action'
        # if self.action_type == 'transfer' and self.new_job_id != '':
        #     emp_id = warning_rec.employee_id
        #     emp_id.job_id = self.new_job_id
