# -*- coding: utf-8 -*-


from odoo import models, _
from odoo.exceptions import UserError


# class HrExpense(models.Model):
#     _inherit = "hr.expense"

#     def _get_expense_account_destination(self):
#         self.ensure_one()
#         account_dest = self.env['account.account']
#         if self.payment_mode == 'company_account':
#             if not self.sheet_id.bank_journal_id.default_credit_account_id:
#                 raise UserError(_("No credit account found for the %s journal, please configure one.") % (
#                     self.sheet_id.bank_journal_id.name))
#             account_dest = self.sheet_id.bank_journal_id.default_credit_account_id.id
#         else:
#             # if not self.employee_id.address_home_id:
#             #     raise UserError(_("No Home Address found for the employee %s, please configure one.") % (self.employee_id.name))
#             partner = self.employee_id.address_id.with_context(
#                 force_company=self.company_id.id)
#             account_dest = partner.property_account_payable_id.id or partner.parent_id.property_account_payable_id.id
#         return account_dest
