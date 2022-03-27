from odoo import fields, models, api
from odoo.tools.translate import _

class MailComposerCustom(models.TransientModel):
    _name = 'mail.compose.message.applicants'
    _description = 'Email composition Applicants wizard'
    _rec_name = "subject"

    subject = fields.Char('Subject')
    body = fields.Html('Contents', default='', required=True)
    attachment_ids = fields.Many2many(
        'ir.attachment', 'mail_compose_applicant_message_ir_attachments_rel',
        'mail_wizard_id', 'attachment_id', 'Attachments')
    applicant_ids = fields.Many2many(
        'hr.applicant', 'mail_compose_message_hr_applicant_rel',
        'applicant_wizard_id', 'applicant_id', 'Additional Contacts')
    applicant_selected_state = fields.Char()
    job_announcement_id = fields.Many2one('hr.job.announcement')
    

    @api.model
    def default_get(self, fields):
        vals = super(MailComposerCustom, self).default_get(fields)
        context = dict(self._context) or {}
        if context.get("default_job_announcement_id", False):
            announcement = self.env['hr.job.announcement'].browse(context.get("default_job_announcement_id", False))
            if context.get('applicant_notify_mode', False) and context.get('applicant_notify_mode', False) == 'written_test':
                vals['applicant_selected_state'] = 'written_test'
                vals['subject'] = 'Call for Written Test'
                vals['body'] = self.get_body_default(type="test", data=announcement)
                vals['applicant_ids'] = [applicant.id  for applicant in list(filter(lambda x: x.stage_state_mode == 'written_test', announcement.application_ids))]
            if context.get('applicant_notify_mode', False) and context.get('applicant_notify_mode', False) == 'interview':
                vals['applicant_selected_state'] = 'interview'
                vals['subject'] = 'Call for Interview'
                vals['body'] = self.get_body_default(type="interview", data=announcement)
                vals['applicant_ids'] = [applicant.id  for applicant in list(filter(lambda x: x.stage_state_mode == 'interview', announcement.application_ids))]
        return vals


    def action_send_mail(self):
        for rec in self:
            data = {
                'subject': rec.subject,
                'body': rec.body,
                'attachment_ids': rec.attachment_ids,
                'job_announcement_id': rec.job_announcement_id,
                'recipients': rec.applicant_ids 
                }
            if rec.applicant_selected_state == 'written_test':
                rec.job_announcement_id.written_test_invite(data)
            else:
                rec.job_announcement_id.interview_invite(data)


    
    def get_body_default(self, type, data):
        if type == 'test':
            body = """
                You are hereby notified in response to your application for the position of %s. We are glad to let you know that your application has successfully passed our first phase of screening. 
                <br/>
                In order to proceed to the next stage, a written test is being held on %s at %s. <br/>
                You are advised to reach at least 15 minutes before the decided time. <br/>
                Our colleague will reach you over phone for a follow-up call.
            """
            date = data.written_test_date.strftime('%A, %B %d, %Y') if data.written_test_date else ''
        else:
            body = """
                We are pleased to inform you that based on initial review of your written test, you are shortlisted for interview to %s position; 
                <br/>
                hereby, we are kindly requesting you to attend the interview which is scheduled on %s at %s.
                Our colleague will reach you over phone to share the exact timing.
            """
            date = data.interview_date.strftime('%A, %B %d, %Y') if data.interview_date else ''
        return f"""
                <![CDATA[<div style="font-family: 'Lucica Grande',
                Ubuntu, Arial, Verdana, sans-serif; font-size: 14px;
                color: rgb(34, 34, 34); background-color: #FFF; ">
                
                <div style="margin-top: 15px"></div>
                Dear Applicant,

                <br/>

                {body}   

                <br/><br/>

                <p>Best Regards,<br/>
                <p>Human Resources Unit<br /></p>
                <hr/>
                <img src="/logo.png?company=%s" style="padding: 0px; margin: 0px; height: auto; width: 190px;margin-bottom: 13px" alt="%s"/>
        """% (data.job_id.name, date, self.env.user.company_id.name ,self.env.user.company_id.id, self.env.user.partner_id.company_id.name)