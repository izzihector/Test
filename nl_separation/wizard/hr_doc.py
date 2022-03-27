# -*- coding: utf-8 -*-

from odoo import models


class HRDocWiz(models.TransientModel):

    _inherit = 'hr.doc.wiz'

    def print_report(self):
        for wiz in self:
            if wiz.app_doc_id:
                return wiz.print_app_doc()
        return super(HRDocWiz, self).print_report()

    def print_app_doc(self):
        """
        This method will print the Document letter
        ------------------------------------------------
        @param self : object pointer
        """
        context = self.env.context
        if context is None:
            context = {}
        data = {
            'ids': self.ids,
            'model': self._context.get('active_model'),
            'form': self.read([])[0]
        }
        return self.env.ref("hr_doc.report_app").report_action(self, data=data)
