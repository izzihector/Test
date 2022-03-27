# -*- coding: utf-8 -*-
# Copyright (C) Softhealer Technologies.
from odoo import fields, models, api
from datetime import datetime, time, timedelta
import base64
import xlwt
from io import BytesIO
import calendar


class EmpAttendanceExcelExtended(models.Model):
    _name = "excel.extended"
    _description = "Excel Extended"

    excel_file = fields.Binary("Download report Excel")
    file_name = fields.Char("Excel File", size=64)

    def emp_download_report(self):
        return{
            "type": "ir.actions.act_url",
            "url": "web/content/?model=excel.extended&field=excel_file&download=true&id=%s&filename=%s" % (self.id, self.file_name),
            "target": "new",
            }


class EmployeeAttendancerWizard(models.Model):
    _name = "employee.attendance.wizard"
    _description = "Employee Attendancer Wizard"
    _rec_name = "print_by"

    date = fields.Date("Date", required=True, default=fields.Date.context_today)
    print_by = fields.Selection(
        [("weekly", "Weekly"),
         ("monthly", "Monthly")],
        default="weekly", required=True)
    employee_id = fields.Many2many("hr.employee", string="Employee")
    office_id = fields.Many2one('office', string='Office')
    unit_ids = fields.Many2many('hr.unit', string="Units")
    
    @api.onchange('office_id', 'unit_ids')
    def _onchange_office_id_unit_ids(self):
        for rec in self:
            domain = []
            if rec.office_id:
                domain.append(("office_id", '=', rec.office_id.id))
            if rec.unit_ids:
                domain.append(('unit_id', 'in', rec.unit_ids._origin.mapped('id')))
            return {'domain':{'employee_id': domain}}


    def employee_attendance_excel(self):
        if self.employee_id:
            employee_search = self.env["hr.employee"].sudo().search(
                [("id", "in", self.employee_id.ids)])
        else:
            search_domain = []
            order=""
            if self.office_id:
                search_domain.append(("office_id", "=", self.office_id.id))
            if self.unit_ids:
                search_domain.append(("unit_id", "in", self.unit_ids.mapped('id')))
                order = 'unit_name asc,name asc'
            employee_search = self.env["hr.employee"].sudo().search(search_domain, order=order)

        if employee_search:
            employee_ids = employee_search.ids

        #Weekly data excel generate
        if self.print_by in ["weekly", "monthly"]:
            if self.print_by == "weekly":
                if self.date:
                    today = self.date
                    start = today - timedelta(days=today.weekday()+1)
                    end = start + timedelta(days=6)
                    delta = end - start
                    first = datetime.strftime(start, "%Y-%m-%d 00:00:00")
                    last = datetime.strftime(end, "%Y-%m-%d 23:59:59")
                else:
                    today = datetime.now().date()
                    start = today - timedelta(days=today.weekday()+1)
                    end = start + timedelta(days=6)
                    delta = end - start
                    first = datetime.strftime(start, "%Y-%m-%d 00:00:00")
                    last = datetime.strftime(end, "%Y-%m-%d 23:59:59")
           
            if self.print_by == "monthly":
                if self.date:
                    today = self.date
                    end = today.replace(
                        day=calendar.monthrange(today.year, today.month)[1])
                    start = today.replace(day=1)
                    delta = end - start
                    first = datetime.strftime(start, "%Y-%m-%d 00:00:00")
                    last = datetime.strftime(end, "%Y-%m-%d 23:59:59")
                else:
                    end = fields.Date.today().replace(day=calendar.monthrange(
                        fields.Date.today().year, fields.Date.today().month)[1])
                    start = fields.Date.today().replace(day=1)
                    delta = end - start
                    first = datetime.strftime(start, "%Y-%m-%d 00:00:00")
                    last = datetime.strftime(end, "%Y-%m-%d 23:59:59")

            week_date = []
            workbook = xlwt.Workbook()
            
            xlwt.add_palette_colour("pl_color", 0x3d)
            workbook.set_colour_RGB(0x3d, 189, 215, 238)
            xlwt.add_palette_colour("custom_gray", 0x3c)
            workbook.set_colour_RGB(0x3c, 217, 217, 217)
            xlwt.add_palette_colour("custom_colour_ph", 0x2a)
            workbook.set_colour_RGB(0x2a, 255, 230, 153)
            xlwt.add_palette_colour("custom_colour_green", 0x3b)
            workbook.set_colour_RGB(0x3b, 198, 224,180)
            xlwt.add_palette_colour("absent_color", 0x3a)
            workbook.set_colour_RGB(0x3a, 255, 79, 79)
            xlwt.add_palette_colour("custom_colour_yellow", 0x22)
            workbook.set_colour_RGB(0x22, 240,230,140)
            

            bold = xlwt.easyxf(
                "font:bold True;pattern: pattern solid, fore_colour custom_gray; align: horiz center;align: vert center ;borders: top_color black, bottom_color black, right_color black, left_color black,\
                              left thin, right thin, top thin, bottom thin;")
            bold_rotated = xlwt.easyxf(
                "font:bold True;pattern: pattern solid, fore_colour custom_gray;align: rotation 90; align: horiz center; align: vert center;borders: top_color black, bottom_color black, right_color black, left_color black,\
                              left thin, right thin, top thin, bottom thin;")
            heading_format = xlwt.easyxf(
                "font:height 300,bold True;pattern: pattern solid, fore_colour custom_gray;align: horiz center;align: vert center;borders: top_color black, bottom_color black, right_color black, left_color black,\
                              left thin, right thin, top thin, bottom thin;")
            bold2 = xlwt.easyxf(
                "font:bold True;pattern: pattern solid, fore_colour custom_gray;align: horiz left; borders: top_color black, bottom_color black, right_color black, left_color black,\
                              left thin, right thin, top thin, bottom thin;")
            format3 = xlwt.easyxf("align: horiz left; align: vert center;borders: top_color black, bottom_color black, right_color black, left_color black,\
                              left thin, right thin, top thin, bottom thin;")
            format3_center = xlwt.easyxf("align: horiz center; align: vert center;borders: top_color black, bottom_color black, right_color black, left_color black,\
                              left thin, right thin, top thin, bottom thin;")
            format_3 = xlwt.easyxf(
                "align: horiz center; align: vert center;pattern: pattern solid, fore_colour white;borders: top_color black, bottom_color black, right_color black, left_color black,\
                              left thin, right thin, top thin, bottom thin;")
            format_pl = xlwt.easyxf(
                "align: horiz center; align: vert center;pattern: pattern solid, fore_colour pl_color;borders: top_color black, bottom_color black, right_color black, left_color black,\
                              left thin, right thin, top thin, bottom thin;")
            format_leave = xlwt.easyxf(
                "align: horiz center; align: vert center;pattern: pattern solid, fore_colour custom_colour_green;borders: top_color black, bottom_color black, right_color black, left_color black,\
                              left thin, right thin, top thin, bottom thin;")
            format_absent = xlwt.easyxf(
                "align: horiz center; align: vert center;pattern: pattern solid, fore_colour absent_color;borders: top_color black, bottom_color black, right_color black, left_color black,\
                              left thin, right thin, top thin, bottom thin;")
            format_ph = xlwt.easyxf(
                "align: horiz center; align: vert center;pattern: pattern solid, fore_colour custom_colour_ph;borders: top_color black, bottom_color black, right_color black, left_color black,\
                              left thin, right thin, top thin, bottom thin;")
            weak_day_format = xlwt.easyxf(
                "align: horiz center; align: vert center;pattern: pattern solid, fore_colour custom_gray;borders: top_color black, bottom_color black, right_color black, left_color black,\
                              left thin, right thin, top thin, bottom thin;")

            # Legend Formats
            legend_border = "borders: top_color black, bottom_color black, right_color black, left_color black, left thin, right thin, top thin, bottom thin;"
            legend_general_format = xlwt.easyxf(
                f"align: horiz left; align: vert center;pattern: pattern solid, fore_colour white;{legend_border}")
            legend_title_format = xlwt.easyxf(
                f"align: horiz center; align: vert center;pattern: pattern solid, fore_colour white;font: bold on;{legend_border}")
            legend_weekend_format = xlwt.easyxf(
                f"align: horiz center; align: vert center;pattern: pattern solid, fore_colour custom_gray;font: bold on;{legend_border}")
            legend_present_format = xlwt.easyxf(
                f"align: horiz center; align: vert center;pattern: pattern solid, fore_colour white;font: bold on;{legend_border}")
            legend_pl_format = xlwt.easyxf(
                f"align: horiz center; align: vert center;pattern: pattern solid, fore_colour pl_color;font: bold on;{legend_border}")
            legend_absent_format = xlwt.easyxf(
                f"align: horiz center; align: vert center;pattern: pattern solid, fore_colour absent_color;font: bold on;{legend_border}")
            legend_ph_format = xlwt.easyxf(
                f"align: horiz center; align: vert center;pattern: pattern solid, fore_colour custom_colour_ph;font: bold on;{legend_border}")
            legend_leave_format = xlwt.easyxf(
                f"align: horiz center; align: vert center;pattern: pattern solid, fore_colour custom_colour_green;font: bold on;{legend_border}")
            
            sub_header_format = xlwt.easyxf(
                f"align: horiz left; align: vert center;pattern: pattern solid, fore_colour white;{legend_border}")

            header = "Employee Attendance - Weekly" if self.print_by == 'weekly' else 'Employee Attendance - Monthly'
            sheet_name = "Employee Attendance - Weekly" if self.print_by == 'weekly' else 'Employee Attendance - Monthly'
            worksheet = workbook.add_sheet(sheet_name)
            worksheet.col(3).width = int(20*130)
            worksheet.col(4).width = int(20*400)
            worksheet.col(5).width = int(20*400)
            worksheet.col(6).width = int(20*400)
            worksheet.row(6).height = int(20*85)
            worksheet.write(6, 3, "ID", bold)
            worksheet.write(6, 4, "Name", bold)
            worksheet.write(6, 5, "Job", bold)
            worksheet.write(6, 6, "Unit", bold)

            col = 6
            row = 7
            dic_date = {}
            attendance_data_list = []
            
            # Write Date columns
            for i in range(delta.days + 1):
                col = col+1
                day = start + timedelta(days=i)
                day_name = day.strftime("%a")
                day_date = str(day)
                week_date.append(day_date)
                dic_date.update({day_date: col})
                worksheet.write(6, col, day_date+" ("+day_name+")", bold_rotated)
                worksheet.col(col).width = int(20*60)

                self.env.cr.execute("""SELECT he.id,he.name,min(ha.check_in),max(ha.check_out),max(ha.check_out)::timestamp -
                 min(ha.check_in)::timestamp, sum(ha.att_duration) FROM hr_attendance ha 
                 INNER JOIN hr_employee he ON he.id = ha.employee_id 
                 where ha.check_in >= %s and ha.check_out <= %s Group by ha.employee_id,he.id""", (day_date + " 00:00:00", day_date + " 23:59:59"))

                for rec in self.env.cr.dictfetchall():
                    if rec.get("id", False) in employee_ids:
                        attendance_data_list.append({day_date: dict(rec)})
            
            # Summary Headers
            summary_col_start = col + 1
            col += 1
            worksheet.write(6, col, "Present", bold)
            col += 1
            worksheet.write(6, col, "Partial Leave", bold)
            col += 1
            worksheet.write(6, col, "Absent", bold)
            col += 1
            worksheet.write(6, col, "Leave", bold)
            col += 1


            # Header and sub header
            worksheet.write_merge(1, 2, 0, col, header + " : "+str(start)+" To " + str(end), heading_format)
            if self.office_id:
                worksheet.write_merge(3, 3, 0, 1, "Office", sub_header_format)
                worksheet.write_merge(3, 3, 2, col, self.office_id.name, sub_header_format)
                worksheet.row(3).height = int(20*20)
            if self.unit_ids:
                worksheet.write_merge(4, 4, 0, 1, "Units", sub_header_format)
                worksheet.write_merge(4, 4, 2, col, ", ".join(self.unit_ids.mapped("name")), sub_header_format)
                worksheet.row(4).height = int(20*20)
           
            # Legends Part
            worksheet.write_merge(8, 8, 0, 1, "Legend", legend_title_format)
            worksheet.write(9, 0, "P", legend_present_format)
            worksheet.write(9, 1, "Present", legend_general_format)
            worksheet.write(10, 0, "PL", legend_pl_format)
            worksheet.write(10, 1, "Partial Leave", legend_general_format)
            worksheet.write(11, 0, "A", legend_absent_format)
            worksheet.write(11, 1, "Absent", legend_general_format)
            worksheet.write(12, 0, "H", legend_ph_format)
            worksheet.write(12, 1, "Holiday", legend_general_format)
            worksheet.write(13, 0, "L", legend_leave_format)
            worksheet.write(13, 1, "Leave", legend_general_format)
            worksheet.write(14, 0, "W", legend_weekend_format)
            worksheet.write(14, 1, "Weekend", legend_general_format)
            worksheet.col(0).width = int(20*60)
            worksheet.col(1).width = int(20*220)
            

            row = 7
            employee_position = {}
            leave_types = {}
            total_summary = {}
            #Get all Employee Absent(A) and Public holiday(PH) , find Employee Position(row wise) and fill all Employee in sheet
            active_working_hour = self.env['resource.calendar'].search([], limit=1)
            holiday_domain = ['&', ("holiday_id", "=", False), '|', '&', ("date_from", ">=", first), ("date_from", "<=", last), '&' ,("date_from", "<=", first), ("date_to", ">=", first)]
            days_without_off = [0, 1, 2, 3, 6]
            if active_working_hour:
                holiday_domain.append(('calendar_id', '=', active_working_hour.id))
                attendance_days_of_week = self.env['resource.calendar.attendance'].search([('calendar_id', '=', active_working_hour.id)])
                days_without_off = [int(record.dayofweek) for record in attendance_days_of_week]

            pub_holiday = self.env["resource.calendar.leaves"].sudo().search(holiday_domain)
            ph_list = []

            if pub_holiday:
                for public_holiday in pub_holiday:
                    for new_day in range((public_holiday.date_to.date() - public_holiday.date_from.date()).days + 1):
                        ph_list.append((public_holiday.date_from + timedelta(days=new_day)).strftime("%Y-%m-%d") )
                    date = public_holiday.date_from.date()
            
            for employee in employee_search:
                employee_position.update({employee.id: row})
                if employee.id not in total_summary:
                    total_summary[employee.id] = { 'p': 0, 'pl': 0, 'a': 0, 'l': 0, 'employee_row': row}
                worksheet.write(row, 3, employee.idc_no, format3_center)
                worksheet.write(row, 4, employee.name, format3)
                worksheet.write(row, 5, employee.job_id and employee.job_id.name or '', format3)
                worksheet.write(row, 6, employee.unit_id and employee.unit_id.name or '', format3)
                worksheet.row(row).height = int(20*20)
                row += 1
                for date in week_date:
                    day_of_week = datetime.strptime(date, '%Y-%m-%d').weekday()
                    if datetime.strptime(date, "%Y-%m-%d").date() <= fields.Date.context_today(self):
                        if day_of_week in days_without_off:
                            if date in ph_list:
                                worksheet.write(employee_position.get(employee.id, False), dic_date.get(
                                    date, False), "H", format_ph)
                            else:
                                self._cr.execute("""
                                    SELECT  
                                        leave.id,
                                        leave_type.leave_code as leave_code,
                                        leave_type.name as leave_type_name,
                                        leave_type.id as leave_type_id
                                    FROM
                                        hr_leave as leave
                                        INNER JOIN hr_leave_type AS leave_type ON leave.holiday_status_id = leave_type.id
                                    WHERE 
                                        state = 'validate'
                                    AND
                                        employee_id = %s
                                    AND
                                        request_date_from <= %s
                                    AND
                                        request_date_to >= %s
                                    LIMIT 1
                                """, (employee.id, date, date))
                                emp_leave = self._cr.dictfetchone()
                                if emp_leave:
                                    if  emp_leave.get('leave_type_id', '') not in leave_types:
                                        leave_types.update({ emp_leave.get('leave_type_id') : { "name": emp_leave.get('leave_type_name'), 'code': emp_leave.get('leave_code', 'L') }  })
                                        
                                    worksheet._cell_overwrite_ok = True
                                    worksheet.write(employee_position.get(employee.id, False), dic_date.get(
                                        date, False), emp_leave.get('leave_code', False) or 'L', format_leave)
                                    total_summary[employee.id]['l'] += 1
                                else:
                                    worksheet.write(employee_position.get(
                                        employee.id, False), dic_date.get(date, False), "A", format_absent)
                                    total_summary[employee.id]['a'] += 1
                        else:
                            worksheet.write(employee_position.get(employee.id, False), dic_date.get(
                                    date, False), "W", weak_day_format)
                    else:
                        worksheet.write(employee_position.get(employee.id, False), dic_date.get(
                                date, False), "", format_3)
            
            #Get Present (P) Employee with Duration
            for date_rec in attendance_data_list:
                for data_date, v in date_rec.items():
                    worksheet._cell_overwrite_ok = True
                    if datetime.strptime(data_date, "%Y-%m-%d").date() <= fields.Date.context_today(self):
                        if data_date in week_date:
                            # day_of_week = datetime.strptime(data_date, '%Y-%m-%d').weekday()
                            worksheet.write(employee_position.get(v.get("id", False), False), dic_date.get(
                                    data_date, False), "W", weak_day_format)
                            if v.get("sum", False) and v.get("sum") < 8.00:
                                worksheet.write(employee_position.get(v.get("id", False), False), dic_date.get(
                                    data_date, False), "PL", format_pl)
                                total_summary[v.get("id")]['pl'] += 1
                            else:
                                worksheet.write(employee_position.get(v.get("id", False), False), dic_date.get(
                                    data_date, False), "P", format_3)
                                total_summary[v.get("id")]['p'] += 1
                    else:
                        worksheet.write(employee_position.get(v.get("id", False), False), dic_date.get(
                                        data_date, False), "", format_3)

            # Write total summary of each row
            for summary in total_summary.values():
                summary_col = summary_col_start
                worksheet.write(summary.get('employee_row'), summary_col,  summary.get('p') , legend_present_format)
                summary_col +=1
                worksheet.write(summary.get('employee_row'), summary_col,  summary.get('pl') , legend_pl_format)
                summary_col +=1
                worksheet.write(summary.get('employee_row'), summary_col,  summary.get('a') , legend_absent_format)
                summary_col +=1
                worksheet.write(summary.get('employee_row'), summary_col,  summary.get('l') , legend_leave_format)


                


            #  Leave types legends
            if leave_types:
                l_row = 16
                worksheet.write_merge(l_row, l_row, 0, 1, "Leave Types", legend_title_format)
                l_row += 1
                for leave_type in leave_types.values():
                    worksheet.write(l_row, 0, leave_type.get('code', False) or "L"  , legend_present_format)
                    worksheet.write(l_row, 1, leave_type.get('name', '') , legend_present_format)
                    l_row += 1


        filename = (header + ".xls")
        fp = BytesIO()
        workbook.save(fp)

        export_id = self.env["excel.extended"].sudo().create({
            "excel_file": base64.encodebytes(fp.getvalue()),
            "file_name": filename,
            })

        return{
            "type": "ir.actions.act_window",
            "res_id": export_id.id,
            "res_model": "excel.extended",
            "view_type": "form",
            "view_mode": "form",
            "target": "new",
            }
