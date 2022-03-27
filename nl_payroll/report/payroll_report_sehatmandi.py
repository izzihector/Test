from odoo import models
import string
from odoo.exceptions import UserError
from odoo.exceptions import UserError, ValidationError


class PayrollReport(models.AbstractModel):
    _name = 'report.nl_payroll.nl_payroll_report_sehatmandi' 
    _inherit = 'report.report_xlsx.abstract'


    def generate_xlsx_report(self, workbook, data, lines):
        print("lines", lines)
        format1 = workbook.add_format({'font_size':12, 'align': 'vcenter', 'bold': True, 'bg_color':'#d3dde3', 'color':'black', 'bottom': True, })
        format2 = workbook.add_format({'font_size':12, 'align': 'vcenter', 'bold': True, 'bg_color':'#edf4f7', 'color':'black','num_format': '#,##0.00'})
        format3 = workbook.add_format({'font_size':11, 'align': 'vcenter', 'bold': False, 'num_format': '#,##0.00'})
        format3_colored = workbook.add_format({'font_size':11, 'align': 'vcenter', 'bg_color':'#f7fcff', 'bold': False, 'num_format': '#,##0.00'})
        format4 = workbook.add_format({'font_size':12, 'align': 'vcenter', 'bold': True})
        format5 = workbook.add_format({'font_size':12, 'align': 'vcenter', 'bold': False})
        # sheet = workbook.add_worksheet('Payrlip Report')

        # Fetch available salary rules:
        used_structures = []
        for sal_structure in lines.slip_ids.struct_id:
            if sal_structure.id not in used_structures:
                used_structures.append([sal_structure.id,sal_structure.name])

        # Logic for each workbook, i.e. group payslips of each salary structure into a separate sheet:
        
            
        struct_count_sehat = 2
        for used_struct in used_structures:
            if used_struct[1] == 'Sehatmandi':
            # Generate Workbook
                sheet3 = workbook.add_worksheet("Payroll Sheet Sehatmandi" )
                cols = list(string.ascii_uppercase) + ['AA', 'AB', 'AC', 'AD', 'AE', 'AF', 'AG', 'AH', 'AI', 'AJ', 'AK', 'AL', 'AM', 'AN', 'AO', 'AP', 'AQ', 'AR', 'AS', 'AT', 'AU', 'AV', 'AW', 'AX', 'AY', 'AZ']
                rules = [] 
                col_no = 14
                # Fetch available salary rules:
                for item in lines.slip_ids.struct_id.rule_ids:
                    if item.struct_id.id == 2:
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
                        
        
            # print('Salary rules to be considered for structure: ' + used_struct[1])
            # print(rules)


            #Report Details:
                for item in lines.slip_ids:
                    if item.struct_id.id == 2:
                        batch_period = str(item.date_from.strftime('%B %d, %Y')) + '  To  ' + str(item.date_to.strftime('%B %d, %Y'))
                        company_name = item.company_id.name
                        break
                print(batch_period)
                print(company_name)

                #Company Name
                sheet3.write(0,0,company_name,format4)

                sheet3.write(0,2,'Payslip Period:',format4)
                sheet3.write(0,3,batch_period,format5)

                sheet3.write(1,2,'Payslip Structure:',format4)
                sheet3.write(1,3,'Sehatmandi',format5)


                sheet3.write(2,0,'Employee ID',format1)
                sheet3.write(2,1,'Employee Name',format1)
                sheet3.write(2,2,'نام',format1)
                sheet3.write(2,3,'Father Name',format1)
                sheet3.write(2,4,'Department',format1)
                sheet3.write(2,5,'Designation',format1)
                sheet3.write(2,6,'Payroll Reference',format1)
                sheet3.write(2,7,'Male/Female',format1)
                sheet3.write(2,8,'DOJ',format1)
                sheet3.write(2,9,'EOC',format1)
                sheet3.write(2,10,'Departure Date',format1)
                sheet3.write(2,11,'TIN No',format1)
                sheet3.write(2,12,'Tazkira No',format1)
                sheet3.write(2,13,'P4P Category',format1)
                sheet3.write(2,34,'Grant',format1)
                sheet3.write(2,35,'Project',format1)
                sheet3.write(2,36,'Location',format1)
                sheet3.write(2,37,'Activity',format1)
                sheet3.write(2,38,'Cost Center',format1)
                sheet3.write(2,39,'Bank account',format1)
                sheet3.write(2,40,'Bank customer',format1)
                sheet3.write(2,41,'Staff Type',format1)
                sheet3.write(2,42,'Head Count',format1)
                sheet3.write(2,43,'Charging Type (Shared/Sole)Source',format1)
                sheet3.write(2,44,'Payment Type',format1)
                sheet3.write(2,45,'Staff Status ',format1)
                sheet3.write(2,46,'Comment',format1)
                for rule in rules:

                    sheet3.write(2,rule[0],rule[2],format1)

                # Generate names, dept, and salary items:
                x = 3
                e_name = 3
                has_payslips = False
                for slip in lines.slip_ids:

                    if lines.slip_ids:
                        if slip.struct_id.id == 2:
                            has_payslips = True
                            sheet3.write(e_name, 0, slip.employee_id.idc_no, format3)
                            sheet3.write(e_name, 1, slip.employee_id.name, format3)
                            sheet3.write(e_name, 2, slip.employee_id.name_in_dari, format3)
                            sheet3.write(e_name, 3, slip.employee_id.father_name, format3)
                            sheet3.write(e_name, 4, slip.employee_id.department_id.name, format3)
                            sheet3.write(e_name, 5, slip.contract_id.budget_line_id.name, format3)
                            if slip.contract_id.name == 'MPHA08':
                                sheet3.write(e_name, 6, 'Sehatmandi - ' + slip.employee_id.work_location + ' - BAM ', format3)
                            if slip.contract_id.name == 'GAFG05':
                                sheet3.write(e_name, 6, 'Sehatmandi - ' + slip.employee_id.work_location + ' - BDK ', format3)
                            sheet3.write(e_name, 7, slip.employee_id.gender, format3)
                            sheet3.write(e_name, 8, str(slip.employee_id.join_date), format3)
                            sheet3.write(e_name, 9, str(slip.contract_id.date_end), format3)
                            if slip.separation_id:
                                sheet3.write(e_name, 10, str(slip.separation_id.relieve_date), format3)
                            else:
                                sheet3.write(e_name, 10, "", format3)
                            sheet3.write(e_name, 11, slip.employee_id.tin_no, format3)
                            sheet3.write(e_name, 12, slip.employee_id.identification_id, format3)
                            if slip.contract_id.wage == slip.contract_id.total_allocated_amount:
                                sheet3.write(e_name, 13, "5", format3)
                            else:
                                sheet3.write(e_name, 13, "1", format3)
                            
                            for line in slip.line_ids:

                                for rule in rules:
                                    if line.code == rule[1]:
                                        if line.amount > 0:
    #                                         if line.code == 'GROSS':
    #                                             sheet.write(x, rule[0], line.amount * slip.percentage, format3_colored)
    #                                         else:

                                            sheet3.write(x, rule[0], line.amount, format3_colored)
                                        else:
                                            sheet3.write(x, rule[0], line.amount, format3)

                            sheet3.write(e_name, 34, slip.grant, format3)
                            sheet3.write(e_name, 35, slip.contract_id.project_contract_id.name, format3)
                            sheet3.write(e_name, 36, slip.employee_id.work_location, format3)
                            sheet3.write(e_name, 37, slip.contract_id.activity_id.name, format3)
                            # sheet3.write(e_name, 38, slip.contract_id.cost_center_id.name, format3)
                            sheet3.write(e_name, 39, slip.employee_id.hr_bank_account, format3)
                            sheet3.write(e_name, 40, slip.employee_id.bank_customer, format3)
                            sheet3.write(e_name, 41, slip.employee_id.staff_type, format3)
                            if len(slip.contract_id.project_ids) > 1:
                                sheet3.write(e_name, 42, 0.5, format3)
                            if len(slip.contract_id.project_ids) == 1:
                                sheet3.write(e_name, 42, 1, format3)
                            sheet3.write(e_name, 43, slip.employee_id.charging_type, format3)
                            sheet3.write(e_name, 44, slip.employee_id.payment_type, format3)
                            sheet3.write(e_name, 45, slip.employee_id.is_local, format3)
                            x += 1
                            e_name += 1






                
                sum_x = e_name
                if has_payslips == True:
                    sheet3.write(sum_x,0,'Total',format2)
                    sheet3.write(sum_x,1,'',format2)
                    for i in range(2,46):
                        sum_start = cols[i] + '3'
                        sum_end = cols[i] + str(sum_x)
                        sum_range = '{=SUM(' + str(sum_start) + ':' + sum_end + ')}'
                        # print(sum_range)
                        sheet3.write_formula(sum_x,i,sum_range,format2)
                        i += 1

                # set width and height of colmns & rows:
                sheet3.set_column('A:A',35)
                sheet3.set_column('B:B',20)
                for rule in rules:
                    sheet3.set_column(rule[3],rule[4])
                sheet3.set_column('C:C',20)

            struct_count_sehat += 1
            
           
            #TAX REPORT
        
        
        
        struct_count_tax_sehatmandi = 1
        sheet5 = workbook.add_worksheet("TAX Report - Sehatmandi")
        cols = list(string.ascii_uppercase) + ['AA', 'AB', 'AC', 'AD', 'AE', 'AF', 'AG', 'AH', 'AI', 'AJ', 'AK', 'AL', 'AM', 'AN', 'AO', 'AP', 'AQ', 'AR', 'AS', 'AT', 'AU', 'AV', 'AW', 'AX', 'AY', 'AZ']
        rules = []
        col_no = 3
        # Fetch available salary rules:
        for item in lines.slip_ids.struct_id.rule_ids:
            if item.code in ['GROSS','TAX']:
                if item.struct_id.id == 2:
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
        # print('Salary rules to be considered for structure: ' + used_struct[1])
        # print(rules)


        #Report Details:
            for item in lines.slip_ids:
                if item.struct_id.id == 2:
                    batch_period = str(item.date_from.strftime('%B %d, %Y')) + '  To  ' + str(item.date_to.strftime('%B %d, %Y'))
                    company_name = item.company_id.name
                    break
            

            #Company Name
            sheet5.write(0,0,company_name,format4)

            sheet5.write(0,2,'Payslip Period:',format4)
            sheet5.write(0,3,batch_period,format5)

            sheet5.write(1,2,'Payslip Structure:',format4)
            sheet5.write(1,3,"Sehatmandi",format5)

            # List report column headers:
            sheet5.write(2,0,'Employee ID',format1)
            sheet5.write(2,1,'Employee Name',format1)
            sheet5.write(2,2,'نام',format1)
            sheet5.write(2,3,'Designation',format1)

            for rule in rules:

                sheet5.write(2,rule[0],rule[2],format1)

            # Generate names, dept, and salary items:
            x = 3
            e_name = 3
            has_payslips = False
            for slip in lines.slip_ids:
                if lines.slip_ids:
                    if slip.struct_id.id == 2:
                        has_payslips = True
                        sheet5.write(e_name, 0, slip.employee_id.idc_no, format3)
                        sheet5.write(e_name, 1, slip.employee_id.name, format3)
                        sheet5.write(e_name, 2, slip.employee_id.name_in_dari, format3)
                        sheet5.write(e_name, 3, slip.contract_id.budget_line_id.name, format3)



                        for line in slip.line_ids:
                            for rule in rules:
                                if line.code == rule[1]:
                                    if line.amount > 0:
                                        sheet5.write(x, rule[0], line.amount, format3_colored)
                                    else:
                                        sheet5.write(x, rule[0], line.amount, format3)


                        x += 1
                        e_name += 1






            # Generate summission row at report end:
            sum_x = e_name
            if has_payslips == True:
                sheet5.write(sum_x,0,'Total',format2)
                sheet5.write(sum_x,1,'',format2)
                for i in range(2,col_no):
                    sum_start = cols[i] + '3'
                    sum_end = cols[i] + str(sum_x)
                    sum_range = '{=SUM(' + str(sum_start) + ':' + sum_end + ')}'
                    # print(sum_range)
                    sheet5.write_formula(sum_x,i,sum_range,format2)
                    i += 1

            # set width and height of colmns & rows:
            sheet5.set_column('A:A',35)
            sheet5.set_column('B:B',20)
            for rule in rules:
                sheet5.set_column(rule[3],rule[4])
            sheet5.set_column('C:C',20)

            struct_count_tax_sehatmandi += 1


        
        
        
        struct_count_bank_sehatmandi = 1     #Bank Report

        

        sheet6 = workbook.add_worksheet("Bank Transfer - Sehatmandi" )
        cols = list(string.ascii_uppercase) + ['AA', 'AB', 'AC', 'AD', 'AE', 'AF', 'AG', 'AH', 'AI', 'AJ', 'AK', 'AL', 'AM', 'AN', 'AO', 'AP', 'AQ', 'AR', 'AS', 'AT', 'AU', 'AV', 'AW', 'AX', 'AY', 'AZ']
        rules = []
        col_no = 7
        # Fetch available salary rules:
        for item in lines.slip_ids.struct_id.rule_ids:
            if item.code == 'NET':
                if item.struct_id.id == 2:
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
        # print('Salary rules to be considered for structure: ' + used_struct[1])
        # print(rules)


            #Report Details:
            for item in lines.slip_ids:
                if item.struct_id.id == 2:
                    batch_period = str(item.date_from.strftime('%B %d, %Y')) + '  To  ' + str(item.date_to.strftime('%B %d, %Y'))
                    company_name = item.company_id.name
                    break
            print(batch_period)
            print(company_name)

            #Company Name
            sheet6.write(0,0,company_name,format4)

            sheet6.write(0,2,'Payslip Period:',format4)
            sheet6.write(0,3,batch_period,format5)

            sheet6.write(1,2,'Payslip Structure:',format4)
            sheet6.write(1,3,used_struct[1],format5)

            # List report column headers:
            sheet6.write(2,0,'Payroll Reference',format1)
            sheet6.write(2,1,'Employee ID',format1)
            sheet6.write(2,2,'Name',format1)
            sheet6.write(2,3,'نام',format1)
            sheet6.write(2,4,'Designation',format1)
            sheet6.write(2,5,'Bank Account',format1)
            sheet6.write(2,6,'Bank Customer',format1)

            for rule in rules:

                sheet6.write(2,rule[0],rule[2],format1)

            # Generate names, dept, and salary items:
            x = 3
            e_name = 3
            has_payslips = False
            for slip in lines.slip_ids:
                if lines.slip_ids:
                    if slip.struct_id.id == 2:
                        has_payslips = True
                        if slip.contract_id.name == 'MPHA08':
                                sheet6.write(e_name, 0, 'Sehatmandi - ' + slip.employee_id.work_location + ' - BAM ', format3)
                        if slip.contract_id.name == 'GAFG05':
                                sheet6.write(e_name, 0, 'Sehatmandi - ' + slip.employee_id.work_location + ' - BDK ', format3)
                        sheet6.write(e_name, 1, slip.employee_id.idc_no, format3)
                        sheet6.write(e_name, 2, slip.employee_id.name, format3)
                        sheet6.write(e_name, 3, slip.employee_id.name_in_dari, format3)
                        sheet6.write(e_name, 4, slip.contract_id.budget_line_id.name, format3)
                        sheet6.write(e_name, 5, slip.employee_id.hr_bank_account, format3)
                        sheet6.write(e_name, 6, slip.employee_id.bank_customer, format3)




                        for line in slip.line_ids:
                            for rule in rules:
                                if line.code == rule[1]:
                                    if line.amount > 0:
                                        sheet6.write(x, rule[0], line.amount, format3_colored)
                                    else:
                                        sheet6.write(x, rule[0], line.amount, format3)


                        x += 1
                        e_name += 1






            # Generate summission row at report end:
        sum_x = e_name
        if has_payslips == True:
            sheet6.write(sum_x,0,'Total',format2)
            sheet6.write(sum_x,1,'',format2)
            for i in range(2,col_no):
                sum_start = cols[i] + '3'
                sum_end = cols[i] + str(sum_x)
                sum_range = '{=SUM(' + str(sum_start) + ':' + sum_end + ')}'
                # print(sum_range)
                sheet6.write_formula(sum_x,i,sum_range,format2)
                i += 1

        # set width and height of colmns & rows:
        sheet6.set_column('A:A',35)
        sheet6.set_column('B:B',20)
        for rule in rules:
            sheet6.set_column(rule[3],rule[4])
        sheet6.set_column('C:C',20)

        struct_count_bank_sehatmandi += 1
        

        
        
class PayrollReportMaster(models.AbstractModel):
    _name = 'report.nl_payroll.nl_payroll_report_sehatmandi_master' 
    _inherit = 'report.report_xlsx.abstract'


    def generate_xlsx_report(self, workbook, data, lines):
        print("lines", lines)
        format1 = workbook.add_format({'font_size':12, 'align': 'vcenter', 'bold': True, 'bg_color':'#d3dde3', 'color':'black', 'bottom': True, })
        format2 = workbook.add_format({'font_size':12, 'align': 'vcenter', 'bold': True, 'bg_color':'#edf4f7', 'color':'black','num_format': '#,##0.00'})
        format3 = workbook.add_format({'font_size':11, 'align': 'vcenter', 'bold': False, 'num_format': '#,##0.00'})
        format3_colored = workbook.add_format({'font_size':11, 'align': 'vcenter', 'bg_color':'#f7fcff', 'bold': False, 'num_format': '#,##0.00'})
        format4 = workbook.add_format({'font_size':12, 'align': 'vcenter', 'bold': True})
        format5 = workbook.add_format({'font_size':12, 'align': 'vcenter', 'bold': False})
        # sheet = workbook.add_worksheet('Payrlip Report')

        # Fetch available salary rules:
        used_structures = []
        for sal_structure in lines.batch_ids.slip_ids.struct_id:
            if sal_structure.id not in used_structures:
                used_structures.append([sal_structure.id,sal_structure.name])

        # Logic for each workbook, i.e. group payslips of each salary structure into a separate sheet:
        
            
        struct_count_sehat = 2
        for used_struct in used_structures:
            if used_struct[1] == 'Sehatmandi':
            # Generate Workbook
                sheet3 = workbook.add_worksheet("Payroll Sheet Sehatmandi" )
                cols = list(string.ascii_uppercase) + ['AA', 'AB', 'AC', 'AD', 'AE', 'AF', 'AG', 'AH', 'AI', 'AJ', 'AK', 'AL', 'AM', 'AN', 'AO', 'AP', 'AQ', 'AR', 'AS', 'AT', 'AU', 'AV', 'AW', 'AX', 'AY', 'AZ']
                rules = [] 
                col_no = 14
                # Fetch available salary rules:
                for item in lines.batch_ids.slip_ids.struct_id.rule_ids:
                    if item.struct_id.id == 2:
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
                        
        
            # print('Salary rules to be considered for structure: ' + used_struct[1])
            # print(rules)


            #Report Details:
                for item in lines.batch_ids.slip_ids:
                    if item.struct_id.id == 2:
                        batch_period = str(item.date_from.strftime('%B %d, %Y')) + '  To  ' + str(item.date_to.strftime('%B %d, %Y'))
                        company_name = item.company_id.name
                        break
                print(batch_period)
                print(company_name)

                #Company Name
                sheet3.write(0,0,company_name,format4)

                sheet3.write(0,2,'Payslip Period:',format4)
                sheet3.write(0,3,batch_period,format5)

                sheet3.write(1,2,'Payslip Structure:',format4)
                sheet3.write(1,3,'Sehatmandi',format5)


                sheet3.write(2,0,'Employee ID',format1)
                sheet3.write(2,1,'Employee Name',format1)
                sheet3.write(2,2,'نام',format1)
                sheet3.write(2,3,'Father Name',format1)
                sheet3.write(2,4,'Department',format1)
                sheet3.write(2,5,'Designation',format1)
                sheet3.write(2,6,'Payroll Reference',format1)
                sheet3.write(2,7,'Male/Female',format1)
                sheet3.write(2,8,'DOJ',format1)
                sheet3.write(2,9,'EOC',format1)
                sheet3.write(2,10,'Departure Date',format1)
                sheet3.write(2,11,'TIN No',format1)
                sheet3.write(2,12,'Tazkira No',format1)
                sheet3.write(2,13,'P4P Category',format1)
                sheet3.write(2,34,'Grant',format1)
                sheet3.write(2,35,'Project',format1)
                sheet3.write(2,36,'Location',format1)
                sheet3.write(2,37,'Activity',format1)
                sheet3.write(2,38,'Cost Center',format1)
                sheet3.write(2,39,'Bank account',format1)
                sheet3.write(2,40,'Bank customer',format1)
                sheet3.write(2,41,'Staff Type',format1)
                sheet3.write(2,42,'Head Count',format1)
                sheet3.write(2,43,'Charging Type (Shared/Sole)Source',format1)
                sheet3.write(2,44,'Payment Type',format1)
                sheet3.write(2,45,'Staff Status ',format1)
                sheet3.write(2,46,'Comment',format1)
                for rule in rules:

                    sheet3.write(2,rule[0],rule[2],format1)

                # Generate names, dept, and salary items:
                x = 3
                e_name = 3
                has_payslips = False
                for slip in lines.batch_ids.slip_ids:

                    if lines.batch_ids.slip_ids:
                        if slip.struct_id.id == 2:
                            has_payslips = True
                            sheet3.write(e_name, 0, slip.employee_id.idc_no, format3)
                            sheet3.write(e_name, 1, slip.employee_id.name, format3)
                            sheet3.write(e_name, 2, slip.employee_id.name_in_dari, format3)
                            sheet3.write(e_name, 3, slip.employee_id.father_name, format3)
                            sheet3.write(e_name, 4, slip.employee_id.department_id.name, format3)
                            sheet3.write(e_name, 5, slip.contract_id.budget_line_id.name, format3)
                            if slip.contract_id.name == 'MPHA08':
                                sheet3.write(e_name, 6, 'Sehatmandi - ' + slip.employee_id.work_location + ' - BAM ', format3)
                            if slip.contract_id.name == 'GAFG05':
                                sheet3.write(e_name, 6, 'Sehatmandi - ' + slip.employee_id.work_location + ' - BDK ', format3)
                            sheet3.write(e_name, 7, slip.employee_id.gender, format3)
                            sheet3.write(e_name, 8, str(slip.employee_id.join_date), format3)
                            sheet3.write(e_name, 9, str(slip.contract_id.date_end), format3)
                            if slip.separation_id:
                                sheet3.write(e_name, 10, str(slip.separation_id.relieve_date), format3)
                            else:
                                sheet3.write(e_name, 10, "", format3)
                            sheet3.write(e_name, 11, slip.employee_id.tin_no, format3)
                            sheet3.write(e_name, 12, slip.employee_id.identification_id, format3)
                            if slip.contract_id.wage == slip.contract_id.total_allocated_amount:
                                sheet3.write(e_name, 13, "5", format3)
                            else:
                                sheet3.write(e_name, 13, "1", format3)
                            
                            for line in slip.line_ids:

                                for rule in rules:
                                    if line.code == rule[1]:
                                        if line.amount > 0:
    #                                         if line.code == 'GROSS':
    #                                             sheet.write(x, rule[0], line.amount * slip.percentage, format3_colored)
    #                                         else:

                                            sheet3.write(x, rule[0], line.amount, format3_colored)
                                        else:
                                            sheet3.write(x, rule[0], line.amount, format3)

                            sheet3.write(e_name, 34, slip.grant, format3)
                            sheet3.write(e_name, 35, slip.contract_id.project_contract_id.name, format3)
                            sheet3.write(e_name, 36, slip.employee_id.work_location, format3)
                            sheet3.write(e_name, 37, slip.contract_id.activity_id.name, format3)
                            # sheet3.write(e_name, 38, slip.contract_id.cost_center_id.name, format3)
                            sheet3.write(e_name, 39, slip.employee_id.hr_bank_account, format3)
                            sheet3.write(e_name, 40, slip.employee_id.bank_customer, format3)
                            sheet3.write(e_name, 41, slip.employee_id.staff_type, format3)
                            if len(slip.contract_id.project_ids) > 1:
                                sheet3.write(e_name, 42, 0.5, format3)
                            if len(slip.contract_id.project_ids) == 1:
                                sheet3.write(e_name, 42, 1, format3)
                            sheet3.write(e_name, 43, slip.employee_id.charging_type, format3)
                            sheet3.write(e_name, 44, slip.employee_id.payment_type, format3)
                            sheet3.write(e_name, 45, slip.employee_id.is_local, format3)
                            x += 1
                            e_name += 1






                
                sum_x = e_name
                if has_payslips == True:
                    sheet3.write(sum_x,0,'Total',format2)
                    sheet3.write(sum_x,1,'',format2)
                    for i in range(2,46):
                        sum_start = cols[i] + '3'
                        sum_end = cols[i] + str(sum_x)
                        sum_range = '{=SUM(' + str(sum_start) + ':' + sum_end + ')}'
                        # print(sum_range)
                        sheet3.write_formula(sum_x,i,sum_range,format2)
                        i += 1

                # set width and height of colmns & rows:
                sheet3.set_column('A:A',35)
                sheet3.set_column('B:B',20)
                for rule in rules:
                    sheet3.set_column(rule[3],rule[4])
                sheet3.set_column('C:C',20)

            struct_count_sehat += 1
            
           
            #TAX REPORT
        
        
        
        struct_count_tax_sehatmandi = 1
        sheet5 = workbook.add_worksheet("TAX Report - Sehatmandi")
        cols = list(string.ascii_uppercase) + ['AA', 'AB', 'AC', 'AD', 'AE', 'AF', 'AG', 'AH', 'AI', 'AJ', 'AK', 'AL', 'AM', 'AN', 'AO', 'AP', 'AQ', 'AR', 'AS', 'AT', 'AU', 'AV', 'AW', 'AX', 'AY', 'AZ']
        rules = []
        col_no = 3
        # Fetch available salary rules:
        for item in lines.batch_ids.slip_ids.struct_id.rule_ids:
            if item.code in ['GROSS','TAX']:
                if item.struct_id.id == 2:
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
        # print('Salary rules to be considered for structure: ' + used_struct[1])
        # print(rules)


        #Report Details:
            for item in lines.batch_ids.slip_ids:
                if item.struct_id.id == 2:
                    batch_period = str(item.date_from.strftime('%B %d, %Y')) + '  To  ' + str(item.date_to.strftime('%B %d, %Y'))
                    company_name = item.company_id.name
                    break
            

            #Company Name
            sheet5.write(0,0,company_name,format4)

            sheet5.write(0,2,'Payslip Period:',format4)
            sheet5.write(0,3,batch_period,format5)

            sheet5.write(1,2,'Payslip Structure:',format4)
            sheet5.write(1,3,"Sehatmandi",format5)

            # List report column headers:
            sheet5.write(2,0,'Employee ID',format1)
            sheet5.write(2,1,'Employee Name',format1)
            sheet5.write(2,2,'نام',format1)
            sheet5.write(2,3,'Designation',format1)

            for rule in rules:

                sheet5.write(2,rule[0],rule[2],format1)

            # Generate names, dept, and salary items:
            x = 3
            e_name = 3
            has_payslips = False
            for slip in lines.batch_ids.slip_ids:
                if lines.batch_ids.slip_ids:
                    if slip.struct_id.id == 2:
                        has_payslips = True
                        sheet5.write(e_name, 0, slip.employee_id.idc_no, format3)
                        sheet5.write(e_name, 1, slip.employee_id.name, format3)
                        sheet5.write(e_name, 2, slip.employee_id.name_in_dari, format3)
                        sheet5.write(e_name, 3, slip.contract_id.budget_line_id.name, format3)



                        for line in slip.line_ids:
                            for rule in rules:
                                if line.code == rule[1]:
                                    if line.amount > 0:
                                        sheet5.write(x, rule[0], line.amount, format3_colored)
                                    else:
                                        sheet5.write(x, rule[0], line.amount, format3)


                        x += 1
                        e_name += 1






            # Generate summission row at report end:
            sum_x = e_name
            if has_payslips == True:
                sheet5.write(sum_x,0,'Total',format2)
                sheet5.write(sum_x,1,'',format2)
                for i in range(2,col_no):
                    sum_start = cols[i] + '3'
                    sum_end = cols[i] + str(sum_x)
                    sum_range = '{=SUM(' + str(sum_start) + ':' + sum_end + ')}'
                    # print(sum_range)
                    sheet5.write_formula(sum_x,i,sum_range,format2)
                    i += 1

            # set width and height of colmns & rows:
            sheet5.set_column('A:A',35)
            sheet5.set_column('B:B',20)
            for rule in rules:
                sheet5.set_column(rule[3],rule[4])
            sheet5.set_column('C:C',20)

            struct_count_tax_sehatmandi += 1


        
        
        
        struct_count_bank_sehatmandi = 1     #Bank Report

        

        sheet6 = workbook.add_worksheet("Bank Transfer - Sehatmandi" )
        cols = list(string.ascii_uppercase) + ['AA', 'AB', 'AC', 'AD', 'AE', 'AF', 'AG', 'AH', 'AI', 'AJ', 'AK', 'AL', 'AM', 'AN', 'AO', 'AP', 'AQ', 'AR', 'AS', 'AT', 'AU', 'AV', 'AW', 'AX', 'AY', 'AZ']
        rules = []
        col_no = 7
        # Fetch available salary rules:
        for item in lines.batch_ids.slip_ids.struct_id.rule_ids:
            if item.code == 'NET':
                if item.struct_id.id == 2:
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
        # print('Salary rules to be considered for structure: ' + used_struct[1])
        # print(rules)


            #Report Details:
            for item in lines.batch_ids.slip_ids:
                if item.struct_id.id == 2:
                    batch_period = str(item.date_from.strftime('%B %d, %Y')) + '  To  ' + str(item.date_to.strftime('%B %d, %Y'))
                    company_name = item.company_id.name
                    break
            print(batch_period)
            print(company_name)

            #Company Name
            sheet6.write(0,0,company_name,format4)

            sheet6.write(0,2,'Payslip Period:',format4)
            sheet6.write(0,3,batch_period,format5)

            sheet6.write(1,2,'Payslip Structure:',format4)
            sheet6.write(1,3,used_struct[1],format5)

            # List report column headers:
            sheet6.write(2,0,'Payroll Reference',format1)
            sheet6.write(2,1,'Employee ID',format1)
            sheet6.write(2,2,'Name',format1)
            sheet6.write(2,3,'نام',format1)
            sheet6.write(2,4,'Designation',format1)
            sheet6.write(2,5,'Bank Account',format1)
            sheet6.write(2,6,'Bank Customer',format1)

            for rule in rules:

                sheet6.write(2,rule[0],rule[2],format1)

            # Generate names, dept, and salary items:
            x = 3
            e_name = 3
            has_payslips = False
            for slip in lines.batch_ids.slip_ids:
                if lines.batch_ids.slip_ids:
                    if slip.struct_id.id == 2:
                        has_payslips = True
                        if slip.contract_id.name == 'MPHA08':
                                sheet6.write(e_name, 0, 'Sehatmandi - ' + slip.employee_id.work_location + ' - BAM ', format3)
                        if slip.contract_id.name == 'GAFG05':
                                sheet6.write(e_name, 0, 'Sehatmandi - ' + slip.employee_id.work_location + ' - BDK ', format3)
                        sheet6.write(e_name, 1, slip.employee_id.idc_no, format3)
                        sheet6.write(e_name, 2, slip.employee_id.name, format3)
                        sheet6.write(e_name, 3, slip.employee_id.name_in_dari, format3)
                        sheet6.write(e_name, 4, slip.contract_id.budget_line_id.name, format3)
                        sheet6.write(e_name, 5, slip.employee_id.hr_bank_account, format3)
                        sheet6.write(e_name, 6, slip.employee_id.bank_customer, format3)




                        for line in slip.line_ids:
                            for rule in rules:
                                if line.code == rule[1]:
                                    if line.amount > 0:
                                        sheet6.write(x, rule[0], line.amount, format3_colored)
                                    else:
                                        sheet6.write(x, rule[0], line.amount, format3)


                        x += 1
                        e_name += 1






            # Generate summission row at report end:
        sum_x = e_name
        if has_payslips == True:
            sheet6.write(sum_x,0,'Total',format2)
            sheet6.write(sum_x,1,'',format2)
            for i in range(2,col_no):
                sum_start = cols[i] + '3'
                sum_end = cols[i] + str(sum_x)
                sum_range = '{=SUM(' + str(sum_start) + ':' + sum_end + ')}'
                # print(sum_range)
                sheet6.write_formula(sum_x,i,sum_range,format2)
                i += 1

        # set width and height of colmns & rows:
        sheet6.set_column('A:A',35)
        sheet6.set_column('B:B',20)
        for rule in rules:
            sheet6.set_column(rule[3],rule[4])
        sheet6.set_column('C:C',20)

        struct_count_bank_sehatmandi += 1

