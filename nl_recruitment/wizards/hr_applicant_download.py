from odoo import fields, models, api
from odoo.tools.translate import _
import os, base64, zipfile
from odoo.addons.nl_master.helpers import master_methods
from datetime import datetime


class HRApplicantDownload(models.TransientModel):
    _name = 'hr.applicant.download'
    _description = 'HR Applicant Download Attachments'

    job_announcement_id = fields.Many2one('hr.job.announcement')
    applicant_ids = fields.Many2many('hr.applicant')

    def download(self):
        self.ensure_one()
        if not self.applicant_ids:
            return
            
        context = dict(self._context) or {}
        temp_filename = f'{datetime.now()}.zip' 
        temp_file_path = master_methods.get_temp_dir()

        with zipfile.ZipFile(os.path.join(temp_file_path, temp_filename), 'w') as zipF:
            for rec in self.applicant_ids:
                for att in rec.attachment_ids:
                    try:
                        key_path = att._full_path(att.store_fname)
                        zipF.write(key_path, f'{rec.name}_{rec.partner_mobile}_{rec.id}/{att.name}', compress_type=zipfile.ZIP_DEFLATED)
                    except:
                        pass

            zipF.close()

        with open(os.path.join(temp_file_path, temp_filename), 'rb') as f2:
                data = base64.encodestring(f2.read())
        context.update({
            'default_download_attachment': data,
            'download_file': True,
            'default_download_filename': 'Attachments_of_%s_%s.zip' % (self.job_announcement_id.job_id.name, self.job_announcement_id.vacancy_start_date)
        })

        return {
            'context': context
        }