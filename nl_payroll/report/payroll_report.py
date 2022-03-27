from odoo import models
import string
from odoo.exceptions import UserError
from odoo.exceptions import UserError, ValidationError
from odoo.addons.nl_master.helpers import master_data

            
            
class PayrollReportMaster(models.AbstractModel):
    _name = 'report.nl_payroll.nl_payroll_report_master' 
    _inherit = 'report.report_xlsx.abstract'

    def generate_xlsx_report(self, workbook, data, lines):
        format1 = workbook.add_format({'font_size':12, 'align': 'vcenter', 'bold': True, 'bg_color':'#B3DCE7', 'color':'black', 'bottom': True,'border': 1 })
        format2 = workbook.add_format({'font_size':12, 'align': 'vcenter', 'bold': True, 'bg_color':'#edf4f7', 'color':'black','border': 1,'num_format': '#,##0.00'})
        format3 = workbook.add_format({'font_size':11, 'align': 'vcenter', 'bold': False,'border': 1,})
        format7 = workbook.add_format({'font_size':11, 'align': 'vcenter', 'bold': False,'num_format': 'd-mmm-yyyy','border': 1})
        format3_colored = workbook.add_format({'font_size':11, 'align': 'vcenter', 'bg_color':'#f7fcff', 'bold': False,'border': 1 })
        format4 = workbook.add_format({'font_size':11, 'align': 'vcenter', 'bold': True,'border': 1})
        format5 = workbook.add_format({'font_size':11, 'align': 'vcenter', 'bold': False,'border': 1})
        format9 = workbook.add_format({'font_size':12, 'align': 'vcenter', 'bold': False, 'num_format': '#,##0.00','border': 1})

        # Bank orders formats
        band_order_title = workbook.add_format({'font_size':11, 'align': 'vcenter', 'bold': True, 'bg_color':'#B3DCE7', 'color':'black', 'bottom': True,'border': 2 })
        band_order_content_sequence = workbook.add_format({'font_size':10, 'align': 'vcenter', 'align': 'center', 'bold': False })
        band_order_content_amount = workbook.add_format({'font_size':10, 'align': 'vcenter', 'align': 'right', 'bold': False, 'num_format': '"AFN" #,##0.00' })
        band_order_content = workbook.add_format({'font_size':10, 'align': 'vcenter', 'bold': False })
        header_format1 = workbook.add_format({'font_size':12, 'bold': True, 'color':'black', 'bottom': True,'border': 0 })
        header_format2 = workbook.add_format({'font_size':11, 'align': 'vcenter', 'bold': True, 'color':'black', 'bottom': True,'border': 0 })
        header_format3 = workbook.add_format({'font_size':10, 'align': 'vcenter', 'bold': True, 'bg_color':'#B3DCE7', 'color':'black', 'bottom': True,'border': 2 })
        footer_format1 = workbook.add_format({'font_size':12, 'valign': 'vcenter', 'align': 'center', 'bg_color':'#B3DCE7', 'bold': True, 'color':'black', 'bottom': True,'border': 2 })
        footer_format2 = workbook.add_format({'font_size':12, 'valign': 'vcenter', 'align': 'right', 'bg_color':'#B3DCE7', 'bold': True, 'color':'black', 'bottom': True,'border': 2, 'num_format': '"AFN" #,##0.00'})

        # Bank Data
        bank_data = {}
        office_name = ', '.join(name for name in set([line.office_id.name for line in lines]))

        # Fetch available salary rules:
        used_structures = []
        for sal_structure in lines.batch_ids.slip_ids.struct_id:
            if sal_structure.id not in used_structures:
                used_structures.append([sal_structure.id,sal_structure.name])

        # Logic for each workbook, i.e. group payslips of each salary structure into a separate sheet:
        # money_format = workbook.add_format({'num_format': '$#,##0.00'})
        struct_count = 1
        for used_struct in used_structures:
            # Generate Workbook
            sheet = workbook.add_worksheet(str(struct_count)+ ' - ' + str(used_struct[1]) + ' AFN' )
            cols = list(string.ascii_uppercase) + ['AA', 'AB', 'AC', 'AD', 'AE', 'AF', 'AG', 'AH', 'AI', 'AJ', 'AK', 'AL', 'AM', 'AN', 'AO', 'AP', 'AQ', 'AR', 'AS', 'AT', 'AU', 'AV', 'AW', 'AX', 'AY', 'AZ']
            rules = []
            col_no = 16
            # Fetch available salary rules:
            for item in lines.batch_ids.slip_ids.struct_id.rule_ids:
                if item.struct_id.id == used_struct[0]:
                    col_title = ''
                    row = [None,None,None,None,None]
                    row[0] = col_no
                    row[1] = item.code
                    row[2] = item.name
                    col_title = str(cols[col_no]) + ':' + str(cols[col_no])
                    row[3] = col_title
                    if len(item.name) < 8:
                        row[4] = 12
                    else:
                        row[4] = len(item.name) + 2
                    rules.append(row)
                    col_no += 1

            #Report Details:
            for item in lines.batch_ids.slip_ids:
                if item.struct_id.id == used_struct[0]:
                    batch_period = str(item.date_from.strftime('%B %d, %Y')) + '  To  ' + str(item.date_to.strftime('%B %d, %Y'))
                    company_name = item.company_id.name
                    break
        
            #Company Name
            sheet.write(0,0,company_name,format4)
    
            sheet.write(0,2,'Payslip Period:',format4)
            sheet.write(0,3,batch_period,format5)

            sheet.write(1,2,'Payslip Structure:',format4)
            sheet.write(1,3,used_struct[1],format5)
       
            # List report column headers:
            sheet.write(2,0,'SR.No',format1)
            sheet.write(2,1,'Employee ID',format1)
            sheet.write(2,2,'Employee Name',format1)
            sheet.write(2,3,'Father Name',format1)
            sheet.write(2,4,'Designation',format1)
            sheet.write(2,5,'Unit',format1)
            sheet.write(2,6,'Statistic No',format1)
            sheet.write(2,7,'Contract Starting Date',format1)
            sheet.write(2,8,'Contract Ending Date',format1)
            sheet.write(2,9,'Grade/Step',format1)
            sheet.write(2,10,'Bank Name',format1)
            sheet.write(2,11,'Bank Account',format1)
            sheet.write(2,12,'TIN Number',format1)
            sheet.write(2,13,'Email Address',format1)
            sheet.write(2,14,'Cost Center',format1)
            sheet.write(2,15,'Donor Code',format1)
            header_col = 15
            for rule in rules:
                sheet.write(2,rule[0],rule[2],format1)
                header_col = rule[0] + 1
            sheet.write(2, header_col, 'Remarks', format1)

            # Generate names, dept, and salary items:
            x = 3
            e_name = 3
            has_payslips = False
            counter = 1
            for slip in lines.batch_ids.slip_ids.filtered(lambda c: c.state not in ['cancel']):
                current_net = 0
                if lines.batch_ids.slip_ids:
                    if slip.struct_id.id == used_struct[0]:
                        has_payslips = True
                        sheet.write(e_name, 0, str(counter), format3)
                        sheet.write(e_name, 1, slip.employee_id.idc_no or 'N/A', format3)
                        sheet.write(e_name, 2, slip.employee_id.name or 'N/A', format3)
                        sheet.write(e_name, 3, slip.employee_id.father_name or 'N/A', format3)
                        sheet.write(e_name, 4, slip.employee_id.job_id.name or 'N/A', format3)
                        sheet.write(e_name, 5, slip.employee_id.unit_id.name or 'N/A', format3)
                        sheet.write(e_name, 6, slip.employee_id.statistic_number or 'N/A', format3)
                        sheet.write(e_name, 7, slip.contract_id.date_start or 'N/A', format7)
                        if slip.contract_id.date_end:
                            sheet.write(e_name, 8, slip.contract_id.date_end, format7)
                        else:
                            sheet.write(e_name, 8, master_data.EMPLOYEMENT_TYPE_DICT.get(slip.contract_id.employment_type, 'N/A'), format3)
                        sheet.write(e_name, 9, slip.contract_id.grade_and_step or 'N/A', format3)
                        sheet.write(e_name, 10, slip.employee_id.bank_id.name or 'N/A', format3)
                        sheet.write(e_name, 11, slip.employee_id.bank_account or 'N/A', format3)
                        sheet.write(e_name, 12, slip.employee_id.tin_no or 'N/A', format3)
                        sheet.write(e_name, 13, slip.employee_id.work_email or 'N/A', format3)
                        sheet.write(e_name, 14, slip.cost_center or 'N/A', format3)
                        sheet.write(e_name, 15, slip.donor_code or 'N/A', format3)
                        header_col_content = 15
                        for line in slip.line_ids:
                            for rule in rules:
                                if rule[1] == 'NET':
                                    current_net = line.amount

                                if line.code == rule[1]:
                                    if line.amount > 0:
                                        sheet.write(x, rule[0], line.amount , format9)
                                    else:
                                        sheet.write(x, rule[0], line.amount, format9)
                                    header_col_content = rule[0] + 1
                        
                        sheet.write(e_name, header_col_content, slip.remarks or 'N/A', format3)
                        if slip.employee_id.bank_id:
                            name_to_write = f"{slip.employee_id.bank_id.id}-{slip.employee_id.bank_id.name}"
                            if not name_to_write in bank_data:
                                bank_data[name_to_write] = []
                            bank_data[name_to_write].append({
                                "account_name": slip.employee_id.name,
                                "bank_account": slip.employee_id.bank_account,
                                "net_ammount": current_net,
                                })
                        
                        x += 1
                        e_name += 1
                        counter += 1

            # Generate summission row at report end:
            sum_x = e_name
            if has_payslips == True:
                sheet.write(sum_x,0,'Total',format2)
                for y in range(1,col_no-1):
                    sheet.write(sum_x,y,'',format2)
                    y += 1
                for i in range(16,col_no):
                    sum_start = cols[i] + '3'
                    sum_end = cols[i] + str(sum_x)
                    sum_range = '{=SUM(' + str(sum_start) + ':' + sum_end + ')}'
                    sheet.write_formula(sum_x,i,sum_range,format2)
                    i += 1
                    
    
            # set width and height of colmns & rows:
            sheet.set_column('A:A',20)
            sheet.set_column('B:B',20)
            for rule in rules:
                sheet.set_column(rule[3],rule[4])
            sheet.set_column('C:C',20)
            
            struct_count += 1
            
            
        struct_count = 1


        #  Write Bank orders
        for key, bank_info in bank_data.items():
            sheet = workbook.add_worksheet(f"{key.split('-')[1]} Order")
            sheet.merge_range(0, 0, 3, 3, 'Swedish Committee for Afghaistan (SCA) - Staff Salary Transfer Form', header_format1)
            sheet.write(4, 0, "Office Name:", header_format2)
            sheet.write(4, 1, office_name, header_format3)
            sheet.write(4, 3, f"Bank Name: {key.split('-')[1]}", header_format3)
            sheet.set_row(4, 28)

            sheet.write(6, 0, "SR No", band_order_title)
            sheet.write(6, 1, "Account Name", band_order_title)
            sheet.write(6, 2, "Bank Account #", band_order_title)
            sheet.write(6, 3, "Net Amount", band_order_title)
            sheet.set_row(6, 28)
            sheet.set_column(0, 0, 14)
            sheet.set_column(1, 1, 28)
            sheet.set_column(2, 2, 28)
            sheet.set_column(3, 3, 28)
            b_row = 7
            b_sequence = 1
            grand_total = 0
            for record in bank_info:
                b_col = 0
                sheet.write(b_row, b_col, b_sequence, band_order_content_sequence)
                b_col += 1
                sheet.write(b_row, b_col, record.get('account_name', ''), band_order_content)
                b_col += 1
                sheet.write(b_row, b_col, record.get('bank_account', ''), band_order_content)
                b_col += 1
                sheet.write(b_row, b_col, record.get('net_ammount', 0), band_order_content_amount)
                grand_total += record.get('net_ammount', 0)
                b_row += 1
                b_sequence += 1
            sheet.merge_range(b_row, 0, b_row+1, 2, 'Grand Total', footer_format1)
            sheet.merge_range(b_row, 3, b_row+1, 3, grand_total, footer_format2)
        
        
        



