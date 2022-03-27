import distutils
from odoo import api, fields, models, _, tools
from odoo.exceptions import ValidationError, AccessError
import xlsxwriter
from odoo.addons.nl_master.helpers import master_methods, master_data

from datetime import datetime
import base64
import os
from distutils import util

class ExcelReport(models.TransientModel):
    _name = "employee.excel.report"
    _description = 'Employee Excel Report'

    employee_status = fields.Selection([
        ('True', 'Active'),
        ('False', 'Leaver'),
        ('all', 'Active/Leaver'),
        ], string="Employee Status", default="True", required=True)
    office_ids = fields.Many2many('office', string="Office")
    employmee_type = fields.Selection([
        ('regular','Regular'),
        ('field','Field Project Staff')
        ], string="Employment Type")
    employment_date = fields.Boolean(string="Employment Date")
    start_date = fields.Date(string="From")
    end_date = fields.Date(string="To")
    all = fields.Boolean(default=False)


    def generate_report(self):
        context = dict(self._context) or {}
        domain_list = []

        employee_condition = ('active','=', bool(distutils.util.strtobool(self.employee_status))) if self.employee_status != 'all' else ('active','in', (True, False))
        if self.office_ids:
            domain_list.append(('office_id', 'in', self.office_ids.ids))
        if self.employmee_type:
            domain_list.append(('employee_type', '=', self.employmee_type))
        if self.start_date:
            domain_list.append(('join_date', '>', self.start_date))
        if self.end_date:
            domain_list.append(('join_date', '<', self.end_date))
        domain_list.append(employee_condition)

        employee_ids = self.env['hr.employee'].search(domain_list)
       
        if not employee_ids:
            raise ValidationError(_("No employee exists with the given information"))
        
        main_name  = f"{'Active' if self.employee_status == 'True' else 'Leaver' if self.employee_status == 'False' else 'Active_Leaver' }-Analysis"
        sheet_name = f"{'Active' if self.employee_status == 'True' else 'Leaver' if self.employee_status == 'False' else 'Active_Leaver' } Analysis Report"
        temp_filename = '%s_%s_%s.xlsx' % (main_name, self._uid, tools.ustr(datetime.now().strftime("%d%m%Y%H%M%S")))
        temp_file_path = master_methods.get_temp_dir()
        workbook = xlsxwriter.Workbook(os.path.join(temp_file_path, temp_filename), {'tmpdir': temp_file_path})

        sheet = workbook.add_worksheet(sheet_name)
        format2 = workbook.add_format({'font_size': 12, 'bold': True, 'bg_color': '#D3D3D3'})
        format3 = workbook.add_format({'font_size': 10})
        format7 = workbook.add_format({'font_size': 10, 'bg_color': '#FFFFFF'})
        format7.set_align('center')
        
        header_col = 0
        sheet.write(0, header_col, 'Staff ID No', format2)
        header_col += 1
        sheet.write(0, header_col, 'Name', format2)
        header_col += 1
        sheet.write(0, header_col, 'Father\'s Name', format2)
        header_col += 1
        sheet.write(0, header_col, 'Designation', format2)
        header_col += 1
        sheet.write(0, header_col, 'Gender', format2)
        header_col += 1
        sheet.write(0, header_col, 'Unit', format2)
        header_col += 1
        sheet.write(0, header_col, 'Project', format2)
        header_col += 1
        sheet.write(0, header_col, 'Department', format2)
        header_col += 1
        sheet.write(0, header_col, 'Office', format2)
        header_col += 1
        sheet.write(0, header_col, 'Grade & Step', format2)
        header_col += 1
        sheet.write(0, header_col, 'Salary', format2)
        header_col += 1
        sheet.write(0, header_col, 'Employment Date', format2)
        header_col += 1
        sheet.write(0, header_col, 'Employee Type', format2)
        header_col += 1
        sheet.write(0, header_col, 'Employment Type', format2)
        header_col += 1
        sheet.write(0, header_col, 'Local/International', format2)
        header_col += 1
        if self.employee_status in ['all', 'False']:
            sheet.write(0, header_col, 'Employment End Date', format2)
            header_col += 1
            sheet.write(0, header_col, 'Separation type', format2)
            header_col += 1
            sheet.write(0, header_col, 'Separation reason', format2)
            header_col += 1
        sheet.write(0, header_col, 'Province', format2)
        header_col += 1
        sheet.write(0, header_col, 'District', format2)
        header_col += 1
        sheet.write(0, header_col, 'Village', format2)
        header_col += 1
        sheet.write(0, header_col, 'NIC No (Tazkira No)', format2)
        header_col += 1
        sheet.write(0, header_col, 'TIN', format2)
        header_col += 1
        sheet.write(0, header_col, 'Staff Type (Technical/Support)', format2)
        header_col += 1
        sheet.write(0, header_col, 'Employee Phone No', format2)
        header_col += 1
        sheet.write(0, header_col, 'Bank Name', format2)
        header_col += 1
        sheet.write(0, header_col, 'Bank Account No', format2)
        header_col += 1
        sheet.write(0, header_col, 'Birth Year', format2)
        header_col += 1
        sheet.write(0, header_col, 'Language', format2)
        header_col += 1
        sheet.write(0, header_col, 'Education', format2)
        header_col += 1
        sheet.write(0, header_col, 'Education Level', format2)
        header_col += 1
        sheet.write(0, header_col, 'Institute Name', format2)
        header_col += 1
        sheet.write(0, header_col, 'Education Completion Date', format2)

        row_number1 = 1
        for rec in employee_ids:
            col_number = 0
            if self.all or (rec.active or (not rec.active and rec.employee_history_ids)):
                contract_rec = rec.contract_id
                e_type = '' if not contract_rec else contract_rec.employment_type
                sheet.write(row_number1, col_number, rec.idc_no, format3)
                col_number += 1
                sheet.write(row_number1, col_number, rec.name, format3)
                col_number += 1
                sheet.write(row_number1, col_number, rec.father_name, format3) if rec.father_name else ' '
                col_number += 1
                sheet.write(row_number1, col_number, rec.job_id.name, format3)
                col_number += 1
                sheet.write(row_number1, col_number, master_data.GENDER_DICT.get(rec.gender, ''), format3) if rec.gender else ' '
                col_number += 1
                sheet.write(row_number1, col_number, rec.unit_id.name, format3) if rec.unit_id.name else ' '
                col_number += 1
                sheet.write(row_number1, col_number, rec.project_id.name, format3) if rec.project_id.name else ' '
                col_number += 1
                sheet.write(row_number1, col_number, rec.department_id.name, format3) if rec.department_id.name else ' '
                col_number += 1
                sheet.write(row_number1, col_number, rec.office_id.name, format3)
                col_number += 1
                
                if rec.employee_grade and rec.employee_step:
                    sheet.write(row_number1, col_number, rec.employee_grade + "-" + rec.employee_step, format3)
                    col_number += 1
                else:
                    sheet.write(row_number1, col_number, "", format3)
                    col_number += 1

                sheet.write(row_number1, col_number, rec.employee_salary, format3)
                col_number += 1

                if rec.join_date:
                    sheet.write(row_number1, col_number, rec.join_date.strftime('%d/%m/%Y'), format3)
                else:
                    sheet.write(row_number1, col_number, '', format3)
                col_number += 1
                
                sheet.write(row_number1, col_number, master_data.EMPLOYEE_TYPE_DICT.get(rec.employee_type, ''), format3) if rec.employee_type else ' '
                col_number += 1
                sheet.write(row_number1, col_number, master_data.EMPLOYEMENT_TYPE_DICT.get(e_type, ''), format3)
                col_number += 1
                sheet.write(row_number1, col_number, master_data.IS_LOCAL_DICT.get(rec.is_local, ''), format3) if rec.is_local else ' '
                col_number += 1

                if self.employee_status in ['all', 'False']:
                    emp_end_date = ''
                    emp_sep_type = ''
                    emp_sep_reason = ''
                    if rec.employee_history_ids:
                        for history in rec.employee_history_ids:
                            if history.date.strftime('%d/%m/%Y') >= emp_end_date:
                                emp_end_date = history.date.strftime('%d/%m/%Y') or ''
                                emp_sep_type =  history.employment_separation_type.name or ''
                                emp_sep_reason = history.separation_id.sudo().reason or ''
                    sheet.write(row_number1, col_number, emp_end_date, format3)
                    col_number += 1
                    sheet.write(row_number1, col_number, emp_sep_type, format3)
                    col_number += 1
                    sheet.write(row_number1, col_number, emp_sep_reason, format3)
                    col_number += 1

                sheet.write(row_number1, col_number, rec.personal_province_id.name, format3) if rec.personal_province_id.name else ' '
                col_number += 1
                sheet.write(row_number1, col_number, rec.district_id.name, format3) if rec.district_id.name else ' '
                col_number += 1
                sheet.write(row_number1, col_number, rec.village, format3) if rec.village else ' '
                col_number += 1
                sheet.write(row_number1, col_number, rec.identification_id, format3) if rec.identification_id else ' '
                col_number += 1
                sheet.write(row_number1, col_number, rec.tin_no, format3) if rec.tin_no else ' '
                col_number += 1
                sheet.write(row_number1, col_number, rec.staff_type, format3) if rec.staff_type else ' '
                col_number += 1
                sheet.write(row_number1, col_number, rec.personal_mobile , format3) if rec.personal_mobile else ' '
                col_number += 1
                sheet.write(row_number1, col_number, rec.bank_id.name, format3) if rec.bank_id.name else ' '
                col_number += 1
                sheet.write(row_number1, col_number, rec.bank_account, format3) if rec.bank_account else ' '
                col_number += 1

                if rec.birthday: 
                    sheet.write(row_number1, col_number, rec.birthday.strftime('%d/%m/%Y'), format3)
                else:
                    sheet.write(row_number1, col_number, '', format3)
                col_number += 1
                
                sheet.write(row_number1, col_number, rec.employee_language, format3)
                col_number += 1
                sheet.write(row_number1, col_number, rec.education_name, format3)
                col_number += 1
                if rec.is_illiterate:
                    sheet.write(row_number1, col_number, rec.illiteracy_value, format3)
                    col_number += 1
                else:
                    sheet.write(row_number1, col_number, master_data.EMPLOYEE_EDUCATION_LEVEL_DICT.get(rec.education_level, ''), format3)
                    col_number += 1
                sheet.write(row_number1, col_number, rec.education_institution, format3)
                col_number += 1
                
                if rec.education_end_date:
                    sheet.write(row_number1, col_number, rec.education_end_date.strftime('%d/%m/%Y'), format3)
                else:
                    sheet.write(row_number1, col_number, ' ', format3)
                col_number += 1
                row_number1 += 1
        
        workbook.close()
        with open(os.path.join(temp_file_path, temp_filename), 'rb') as f2:
                data = base64.encodestring(f2.read())
        
        report_file_name = _(main_name)
        context.update({
            'default_download_attachment': data,
            'download_file': True,
            'default_download_filename': '%s.xlsx' % report_file_name
        })
        master_methods.delete_directory(temp_file_path)
        return {
            'context': context,
        }