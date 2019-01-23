# -*- coding: utf-8 -*-
# Part of BrowseInfo. See LICENSE file for full copyright and licensing details.

from odoo.exceptions import Warning
from odoo import models, fields, api, _
import itertools,operator
import pytz
from datetime import datetime
from odoo.tools import DEFAULT_SERVER_DATETIME_FORMAT
import logging
_logger = logging.getLogger(__name__)
from io import StringIO
import io

try:
    import xlwt
except ImportError:
    _logger.debug('Cannot `import xlwt`.')
try:
    import cStringIO
except ImportError:
    _logger.debug('Cannot `import cStringIO`.')
try:
    import base64
except ImportError:
    _logger.debug('Cannot `import base64`.')


class template_configuration(models.Model):
    _name = "template.configuration"

    name = fields.Char('Name', required=True)
    excel_sheet_name = fields.Char('Excel Sheet Name', required=True)
    header_name = fields.Char('Header Name', required=True) 
    sum_background_color = fields.Char('Total Background Color')
    total_Font_color = fields.Char('Total Font Color')
    company_check = fields.Boolean('Print Company Detail')
    cmp_font_name = fields.Char('Font Name')
    cmp_font_size = fields.Char('Font Size')
    cmp_font_color = fields.Char('Font Color')
    cmp_background_color = fields.Char('Background Color')
    cmp_bold = fields.Boolean('Bold')
    cmp_italic = fields.Boolean('Italic')
    header_font_name = fields.Char('Font Name')
    header_font_size = fields.Char('Font Size')
    header_font_color = fields.Char('Font Color')
    header_background_color = fields.Char('Background Color')
    header_bold = fields.Boolean('Bold')
    header_italic = fields.Boolean('Italic')
    check_total = fields.Boolean('Print Total')


class field_ids_one2many(models.Model):
    _name = "field.ids.one2many"
    
    generic_id = fields.Many2one('generic.excel.report',string='Generic Excel Report')
    field_id = fields.Many2one('ir.model.fields',string='Fields Name', required=True)
    label = fields.Char('Label')

    @api.onchange('field_id')
    def onchnage_field_id(self):
        if self.field_id:
            self.label = self.field_id.field_description
        return

class sub_model_field_ids_one2many(models.Model):
    _name = "sub.model.field.ids.one2many"
    
    sub_model_generic_id = fields.Many2one('generic.excel.report',string='Generic Excel Report')
    field_id = fields.Many2one('ir.model.fields',string='Fields Name', required=True)
    label = fields.Char('Label')

    @api.onchange('field_id')
    def onchnage_field_id(self):
        if self.field_id:
            self.label = self.field_id.field_description
        return

    

class generic_excel_report(models.Model):
    _name = "generic.excel.report"
# # 
    name = fields.Char("Name" , required=True)
    model_name = fields.Many2one('ir.model', "Object", required=True)
    sub_model_name = fields.Many2one('ir.model', "Sub Model Name")
    sheet_per_page = fields.Boolean("Record Per Sheet")
    field_ids = fields.One2many('field.ids.one2many','generic_id', string='Fields')
    sub_model_field_ids = fields.One2many('sub.model.field.ids.one2many','sub_model_generic_id',string=' Sub model Fields')
    field_id = fields.Many2one('ir.model.fields', string='Group BY')
    ref_ir_act_window = fields.Many2one('ir.actions.act_window', 'Sidebar action', readonly=True, copy=False)
    template_id = fields.Many2one('template.configuration',required=True, string= 'Template')
    


    @api.one
    def create_print_action(self):
        ActWindowSudo = self.env['ir.actions.act_window'].sudo()
        data_obj = self.env['ir.model.data']
        for action in self.browse(self._ids):
            src_obj = action.model_name.model
            model_data_id = data_obj._get_id('generic_excel_reports', 'view_globle_report_wizard_form')
            res_id = data_obj.browse( model_data_id).res_id
            button_name = _('Print (%s)') % action.name
            act_id = ActWindowSudo.create({
                 'name': button_name,
                 'type': 'ir.actions.act_window',
                 'res_model': 'generic.excel.report.wizard',
                 'src_model': src_obj,
                 'view_type': 'form',
                'context': "{'globle' : %d}" % (self.id),
                 'view_mode':'form,tree',
                 'view_id': res_id,
                 'target': 'new',
                 'binding_model_id': action.model_name.id,
                 'auto_refresh':1
            })
            action.write({
                'ref_ir_act_window': act_id.id,
            })
        return True

    @api.multi
    def remove_action(self):
        for action in self.browse(self._ids):
            try:
                if action.ref_ir_act_window:
                    action.ref_ir_act_window.sudo().unlink()
            except Exception :
                raise Warning('Deletion of the action record failed.')
        return True
    
class generic_excel_report_wizard(models.TransientModel):
    _name = "generic.excel.report.wizard"
    
    state = fields.Selection([('choose', 'choose'), ('get', 'get')], default='choose')
    name = fields.Char('filename', readonly=True)
    data = fields.Binary('file', readonly=True)

    @api.multi
    def find_total(self,record,field,obj):
        total = 0
        brw_record = obj.browse(record)

        for line in brw_record:
            total += getattr(line, field.field_id.name)
        return total


    @api.multi
    def _get_sum_style(self):
        globle_excel_report_id = self.env['generic.excel.report'].browse(self._context.get('globle'))
        total_Font_color = globle_excel_report_id.template_id.total_Font_color or 'white'
        sum_background_color = globle_excel_report_id.template_id.sum_background_color or 'black'
        return xlwt.easyxf('font: bold on,color '+ total_Font_color + ';'
                        'pattern: pattern solid, pattern_fore_colour '+ sum_background_color )
        
    @api.multi
    def _get_header_style(self):
        globle_excel_report_id = self.env['generic.excel.report'].browse(self._context.get('globle'))
        header_font_color = globle_excel_report_id.template_id.header_font_color or 'black'
        header_font_name = globle_excel_report_id.template_id.header_font_name or 'Times New Roman'
        header_font_size = globle_excel_report_id.template_id.header_font_size or '300'
        header_background_color = globle_excel_report_id.template_id.header_background_color or 'white'
        if globle_excel_report_id.template_id.header_bold:
            header_bold = 'on'
        else:
            header_bold = 'off'
        if globle_excel_report_id.template_id.header_italic:
            header_italic = 'on'
        else:
            header_italic = 'off'
        
        return xlwt.easyxf("font: name "+ header_font_name + "; font: italic "+ header_italic+ "; font: bold "+ header_bold+"; font: color "+ header_font_color+ "; font:height "+header_font_size +"; align: horiz center; pattern: pattern solid, pattern_fore_colour "+ header_background_color )

    @api.multi
    def _write_header(self,worksheet):
        globle_excel_report_id = self.env['generic.excel.report'].browse(self._context.get('globle'))
        header_style = self._get_header_style()
        worksheet.write_merge(0, 1, 0, (len(globle_excel_report_id.field_ids)-1), globle_excel_report_id.template_id.header_name, style=header_style)

    @api.multi
    def _write_company_detail(self,row,col,worksheet):
        globle_excel_report_id = self.env['generic.excel.report'].browse(self._context.get('globle'))
        if globle_excel_report_id.template_id.company_check:
            cmp_font_color = globle_excel_report_id.template_id.cmp_font_color or 'black'
            cmp_font_name = globle_excel_report_id.template_id.cmp_font_name or 'Times New Roman'
            cmp_font_size = globle_excel_report_id.template_id.cmp_font_size or '200'
            cmp_background_color = globle_excel_report_id.template_id.cmp_background_color or 'white'
            if globle_excel_report_id.template_id.cmp_bold:
                cmp_bold = 'on'
            else:
                cmp_bold = 'off'
            if globle_excel_report_id.template_id.cmp_italic:
                cmp_italic = 'on'
            else:
                cmp_italic = 'off'
            
            style_company = xlwt.easyxf("font: name "+ cmp_font_name + "; font: italic "+ cmp_italic+ "; font: bold "+ cmp_bold+"; font: color "+ cmp_font_color+ "; font:height "+cmp_font_size +"; pattern: pattern solid, pattern_fore_colour "+ cmp_background_color )
            user_id = self.env['res.users'].browse(self._uid)
            cmp_address = user_id.company_id.name or ''+"\n" +user_id.company_id.street or '' + "\n" + user_id.company_id.street2 or ''  + "\n" + user_id.company_id.city or '' + "\n"+ user_id.company_id.country_id.name or ''  +"-"+str(user_id.company_id.zip) 
            worksheet.write_merge(3, 8, 0, 3,cmp_address,style_company)
            row = 10
        return row


    @api.multi
    def normal_excel_report(self):
        globle_excel_report_id = self.env['generic.excel.report'].browse(self._context.get('globle'))
        user_tz = self.env.user.tz 
        if  user_tz:
        	local_tz = pytz.timezone(user_tz) 
        else:
        	local_tz='UTC'


        local_tz = pytz.timezone(user_tz)
        workbook = xlwt.Workbook(encoding="utf-8")
        count = 0
        if not globle_excel_report_id.sheet_per_page:
            worksheet = workbook.add_sheet(globle_excel_report_id.template_id.excel_sheet_name)
            self._write_header(worksheet)
            row = self._write_company_detail(row=3,col=0,worksheet=worksheet)
        for record in self._context.get('active_ids'):
            browse_record = self.env[self._context.get('active_model')].browse(record)
            if globle_excel_report_id.sheet_per_page:
                sheet_name = globle_excel_report_id.template_id.excel_sheet_name+ "_" + str(record)
                worksheet = workbook.add_sheet(sheet_name)
                self._write_header(worksheet)
                row= self._write_company_detail(row=3,col=0,worksheet=worksheet)
            col = 0
            row += 1
            if count == 0 or globle_excel_report_id.sheet_per_page :
                for header_field in globle_excel_report_id.field_ids:
                    worksheet.write(row,col, header_field.label)
                    col += 1
                    count = 1
                row+=1
                col = 0
            if count>=1 or globle_excel_report_id.sheet_per_page:
                for field in globle_excel_report_id.field_ids:
                    record = getattr(browse_record, field.field_id.name)
                    if field.field_id.ttype=="many2one":
                        record=record.name
                    if field.field_id.ttype=="datetime":
                        record = datetime.strftime(pytz.utc.localize(datetime.strptime(str(record), DEFAULT_SERVER_DATETIME_FORMAT)).astimezone(local_tz),"%d/%m/%Y %H:%M:%S") 
                    worksheet.write(row,col, record)
                    col=col+1
        if globle_excel_report_id.template_id.check_total and not globle_excel_report_id.sheet_per_page :
            col=0
            row += 1
            sum_style = self._get_sum_style()
            for check_type in globle_excel_report_id.field_ids:
                if check_type.field_id.ttype == 'monetary' or check_type.field_id.ttype == 'integer' or check_type.field_id.ttype == 'Float':
                    sum = self.find_total(self._context.get('active_ids'),check_type,self.env[self._context.get('active_model')])
                    worksheet.write(row,col, sum,sum_style)
                col+=1
                
        file_data = io.BytesIO()
        workbook.save(file_data)
        self.write({
            'state': 'get',
            'data': base64.encodestring(file_data.getvalue()),
            'name': "generic excel report.xls"
        })
        return {
            'type': 'ir.actions.act_window',
            'name': 'Generic Excel Report',
            'res_model': 'generic.excel.report.wizard',
            'view_mode': 'form',
            'view_type': 'form',
            'res_id': self.id,
            'target': 'new'
        }

    
    @api.multi
    def groupby_excel_report(self):
        user_tz = self.env.user.tz 
        if  user_tz:
            local_tz = pytz.timezone(user_tz) 
        else:
            local_tz='UTC'

        local_tz = pytz.timezone(user_tz)
        globle_excel_report_id = self.env['generic.excel.report'].browse(self._context.get('globle'))
        workbook = xlwt.Workbook(encoding="utf-8")
        worksheet = workbook.add_sheet(globle_excel_report_id.template_id.excel_sheet_name)
        self._write_header(worksheet)
        row = self._write_company_detail(row=3,col=0,worksheet=worksheet)
        browse_record = self.env[self._context.get('active_model')].browse(self._context.get('active_ids'))
        read_record = []
        newlist = []
        style_group = xlwt.easyxf("font: bold on; font: color black; pattern: pattern solid, pattern_fore_colour gray25" )
        for record in browse_record:
            read_record.append(record.read()[0])
        newlist = sorted(read_record, key=lambda k: k[globle_excel_report_id.field_id.name])

        groups = itertools.groupby(newlist, key=operator.itemgetter(globle_excel_report_id.field_id.name))
                    
        result = [{globle_excel_report_id.field_id.name:k, 'values':[x for x in v]} for k,v in groups]
        row += 1
        col = 0
        for field_header in globle_excel_report_id.field_ids:
            worksheet.write(row,col,field_header.label)
            col += 1
        row += 1
        for val in result:
            col = 0
            if isinstance(val[globle_excel_report_id.field_id.name], tuple):
                worksheet.write_merge(row, row, 0, (len(globle_excel_report_id.field_ids)-1), val[globle_excel_report_id.field_id.name][1],style_group)
            else:
                worksheet.write_merge(row, row, 0, (len(globle_excel_report_id.field_ids)-1), val[globle_excel_report_id.field_id.name][1],style_group)
            row += 1
            col = 0
            for record in val.get('values'):
                col = 0
                for i in globle_excel_report_id.field_ids:
                    if isinstance(record[i.field_id.name], tuple):
                        if str(i.field_id.ttype) == 'datetime':
                            record[i.field_id.name][1] = datetime.strftime(pytz.utc.localize(datetime.strptime(str(record[i.field_id.name][1]), DEFAULT_SERVER_DATETIME_FORMAT)).astimezone(local_tz),"%d/%m/%Y %H:%M:%S")
                        worksheet.write(row,col, record[i.field_id.name][1])
                    else:
                        if str(i.field_id.ttype) == 'datetime':
                            record[i.field_id.name] = datetime.strftime(pytz.utc.localize(datetime.strptime(str(record[i.field_id.name]), DEFAULT_SERVER_DATETIME_FORMAT)).astimezone(local_tz),"%d/%m/%Y %H:%M:%S")
                        worksheet.write(row,col, record[i.field_id.name])
                    col += 1
                row+=1
        file_data = io.BytesIO()
        workbook.save(file_data)
        self.write({
            'state': 'get',
            'data': base64.encodestring(file_data.getvalue()),
            'name': "generic excel report.xls"
        })
        return {
            'type': 'ir.actions.act_window',
            'name': 'Generic Excel Report',
            'res_model': 'generic.excel.report.wizard',
            'view_mode': 'form',
            'view_type': 'form',
            'res_id': self.id,
            'target': 'new'
        }
            

    
    @api.multi
    def detailed_excel_report(self):
        globle_excel_report_id = self.env['generic.excel.report'].browse(self._context.get('globle'))
        user_tz = self.env.user.tz  
        if  user_tz:
            local_tz = pytz.timezone(user_tz) 
        else:
            local_tz='UTC'
        workbook = xlwt.Workbook(encoding="utf-8")
        count = 0
        style_group = xlwt.easyxf("font: bold on; font: color black; pattern: pattern solid, pattern_fore_colour gray25" )
        if not globle_excel_report_id.sheet_per_page:
            worksheet = workbook.add_sheet(globle_excel_report_id.template_id.excel_sheet_name)
            self._write_header(worksheet)
            row = self._write_company_detail(row=3,col=0,worksheet=worksheet)
        for record in self._context.get('active_ids'):
            browse_record = self.env[self._context.get('active_model')].browse(record)
            if globle_excel_report_id.sheet_per_page:
                sheet_name = globle_excel_report_id.template_id.excel_sheet_name+ "_" + str(record)
                worksheet = workbook.add_sheet(sheet_name)
                self._write_header(worksheet)
                row= self._write_company_detail(row=3,col=0,worksheet=worksheet)
            col = 0
            row += 1
            for header_row in globle_excel_report_id.field_ids:
                worksheet.write(row,col, header_row.label,style=style_group)
                col += 1
            row += 1
            col = 0
            for header_value in globle_excel_report_id.field_ids:
                record_data = getattr(browse_record, header_value.field_id.name)
                if header_value.field_id.ttype=="many2one":
                        record_data=record_data.name
                if header_value.field_id.ttype=="datetime":
                        record_data = datetime.strftime(pytz.utc.localize(datetime.strptime(str(record_data), DEFAULT_SERVER_DATETIME_FORMAT)).astimezone(local_tz),"%d/%m/%Y %H:%M:%S") 
                worksheet.write(row,col, record_data)
                col += 1
            row += 2
            col=0
            for field in globle_excel_report_id.sub_model_name.field_id:
                if field.relation == globle_excel_report_id.model_name.model:
                    relation_field = field.name
            if not relation_field:
                raise Warning('You have selected wrong submodel')
            submodel_record = self.env[globle_excel_report_id.sub_model_name.model].search([(relation_field,'=',record)])
            for sub_model_field in globle_excel_report_id.sub_model_field_ids:
                worksheet.write(row,col, sub_model_field.label,style=style_group)
                col += 1
            row += 1
            col = 0 
            for submodel in submodel_record:
                for sub_model_field_value in globle_excel_report_id.sub_model_field_ids:
                    record = getattr(submodel, sub_model_field_value.field_id.name)
                    if sub_model_field_value.field_id.ttype=="many2one":
                            record=record.name
                    if sub_model_field_value.field_id.ttype=="datetime":
                            record = datetime.strftime(pytz.utc.localize(datetime.strptime(str(record), DEFAULT_SERVER_DATETIME_FORMAT)).astimezone(local_tz),"%d/%m/%Y %H:%M:%S") 
                    worksheet.write(row,col, record)
                    col += 1
                row+=1
                col = 0
        file_data = io.BytesIO()
        workbook.save(file_data)
        self.write({
            'state': 'get',
            'data': base64.encodestring(file_data.getvalue()),
            'name': "generic excel report.xls"
        })
        return {
            'type': 'ir.actions.act_window',
            'name': 'Generic Excel Report',
            'res_model': 'generic.excel.report.wizard',
            'view_mode': 'form',
            'view_type': 'form',
            'res_id': self.id,
            'target': 'new'
        }   

    

    @api.multi
    def print_report(self):
       
        #Added style for sheet
        globle_excel_report_id = self.env['generic.excel.report'].browse(self._context.get('globle'))
        if not globle_excel_report_id.field_id and not globle_excel_report_id.sub_model_name:
            return self.normal_excel_report()
        elif globle_excel_report_id.field_id and not globle_excel_report_id.sub_model_name:
            return self.groupby_excel_report()
        else:
            return self.detailed_excel_report()  
#        stylePC = xlwt.XFStyle()
#        alignment = xlwt.Alignment()
#        alignment.horz = xlwt.Alignment.HORZ_CENTER
#        fontP = xlwt.Font()
#        fontP.bold = True
#        stylePC.font = fontP
#        stylePC.num_format_str = '@'
#        stylePC.alignment = alignment
#           
#            #Added sheet
#        workbook = xlwt.Workbook(encoding="utf-8")
#        cur = self._context["active_model"]
#        globle_obj = self.env['generic.excel.report']
#        curr_obj = self.env[cur]
#        globle_id = self._context.get('globle')
#        id = self._context.get('active_ids')
#        f = globle_obj.browse(globle_id).field_ids
#        worksheet = workbook.add_sheet(globle_obj.browse(globle_id).template_id.excel_sheet_name)
#        
#        '''
#            Dynamic header font name,size, color and background color
#        '''
#        header_font_color = globle_obj.browse(globle_id).template_id.header_font_color or 'black'
#        header_font_name = globle_obj.browse(globle_id).template_id.header_font_name or 'Times New Roman'
#        header_font_size = globle_obj.browse(globle_id).template_id.header_font_size or '300'
#        header_background_color = globle_obj.browse(globle_id).template_id.header_background_color or 'white'
#        if globle_obj.browse(globle_id).template_id.header_bold:
#            header_bold = 'on'
#        else:
#            header_bold = 'off'
#        if globle_obj.browse(globle_id).template_id.header_italic:
#            header_italic = 'on'
#        else:
#            header_italic = 'off'
#        
#        style_header = xlwt.easyxf("font: name "+ header_font_name + "; font: italic "+ header_italic+ "; font: bold "+ header_bold+"; font: color "+ header_font_color+ "; font:height "+header_font_size +"; align: horiz center; pattern: pattern solid, pattern_fore_colour "+ header_background_color )
#        
#        
#        '''
#            Dynamic Total color and background color
#        '''
#        total_Font_color = globle_obj.browse(globle_id).template_id.total_Font_color or 'white'
#        sum_background_color = globle_obj.browse(globle_id).template_id.sum_background_color or 'black'
#        sum_style = xlwt.easyxf('font: bold on,color '+ total_Font_color + ';'
#                                'pattern: pattern solid, pattern_fore_colour '+ sum_background_color )
#        
#        worksheet.write_merge(0, 1, 0, (len(f)-1), globle_obj.browse(globle_id).template_id.header_name, style=style_header)
#        row=0
#        col=3
#        no= 0
#        count = 0
#        if globle_obj.browse(globle_id).template_id.company_check:
#            cmp_font_color = globle_obj.browse(globle_id).template_id.cmp_font_color or 'black'
#            cmp_font_name = globle_obj.browse(globle_id).template_id.cmp_font_name or 'Times New Roman'
#            cmp_font_size = globle_obj.browse(globle_id).template_id.cmp_font_size or '200'
#            cmp_background_color = globle_obj.browse(globle_id).template_id.cmp_background_color or 'white'
#            if globle_obj.browse(globle_id).template_id.cmp_bold:
#                cmp_bold = 'on'
#            else:
#                cmp_bold = 'off'
#            if globle_obj.browse(globle_id).template_id.cmp_italic:
#                cmp_italic = 'on'
#            else:
#                cmp_italic = 'off'
#            
#            style_company = xlwt.easyxf("font: name "+ cmp_font_name + "; font: italic "+ cmp_italic+ "; font: bold "+ cmp_bold+"; font: color "+ cmp_font_color+ "; font:height "+cmp_font_size +"; pattern: pattern solid, pattern_fore_colour "+ cmp_background_color )
#            user_id = self.env['res.users'].browse(self._uid)
#            cmp_address = user_id.company_id.name+"\n" +user_id.company_id.street + "\n" + user_id.company_id.street2  + "\n" + user_id.company_id.city + "\n"+ user_id.company_id.country_id.name  +"-"+str(user_id.company_id.zip) 
#            worksheet.write_merge(3, 8, 0, 3,cmp_address,style_company)
#            count +=1
#            col = 10
#        row = 1
#        if not globle_obj.browse(globle_id).field_id and not globle_obj.browse(globle_id).sub_model_name:
#            for i in id:
#                if count == 1 or count == 0:
#                    worksheet.write(col,row-1, 'No #',style=stylePC)
#                    for dummy_field in f:
#                        worksheet.write(col,row,dummy_field.field_description , style=stylePC)
#                        row=row+1
#                        count = 2
#                col=col+1
#                row=1
#                no +=1
#                worksheet.write(col,row-1, no,style=stylePC)
#                for dummy_field1 in f:
#                    record = getattr(curr_obj.browse(i), dummy_field1.name)
#                    if dummy_field1.ttype=="many2one":
#                        record=record.name
#                    worksheet.write(col,row, record)
#                    row=row+1
#            if globle_obj.browse(globle_id).template_id.check_total:
#                row=1
#                col=col+1
#                worksheet.write(col,row-1, 'Total',style=stylePC)
#                for check_type in f:
#                    if check_type.ttype == 'monetary' or check_type.ttype == 'integer' or check_type.ttype == 'Float':
#                        sum = self.find_total(id,check_type,curr_obj)
#                        worksheet.write(col,row, sum,sum_style)
#                    row += 1
#        elif globle_obj.browse(globle_id).field_id and not globle_obj.browse(globle_id).sub_model_name:
#            read_record = []
#            newlist = []
#            header = []
#            style_group = xlwt.easyxf("font: bold on; font: color black; pattern: pattern solid, pattern_fore_colour gray25" )
#            for record in id:
#                read_record.append(curr_obj.browse(record).read()[0])
#            newlist = sorted(read_record, key=lambda k: k[globle_obj.browse(globle_id).field_id.name])
#
#            groups = itertools.groupby(newlist, key=operator.itemgetter(globle_obj.browse(globle_id).field_id.name))
#                        
#            result = [{globle_obj.browse(globle_id).field_id.name:k, 'values':[x for x in v]} for k,v in groups]
#            for dummy_field in f:
#                worksheet.write(col,row-1,dummy_field.field_description , style=stylePC)
#                header.append(dummy_field.name)
#                row=row+1
#            for val in result:
#                col=col+1
#                row = 1
#                if isinstance(val[globle_obj.browse(globle_id).field_id.name], tuple):
#                    worksheet.write_merge(col, col, 0, (len(f)-1), val[globle_obj.browse(globle_id).field_id.name][1],style_group)
#                else:
#                    worksheet.write_merge(col, col, 0, (len(f)-1), val[globle_obj.browse(globle_id).field_id.name][1],style_group)
#                for record in val.get('values'):
#                    col=col+1
#                    row=1
#                    no +=1
#                    for i in header:
#                        if isinstance(record[i], tuple):
#                            worksheet.write(col,row-1, record[i][1])
#                        else:
#                            worksheet.write(col,row-1, record[i])
#                        row += 1
#        else:
#            for record in id:
#                row = 0
#                col+=1
#                relation_field = False
#                submodel_field_count = 0
#                row = 0
#                header = False
#                count = 1
#                for field in f:
#                        if count % 3 != 0:
#                            worksheet.write(col,row,field.field_description , style=stylePC)
#                            record_value = getattr(curr_obj.browse(record), field.name)
#                            if field.ttype=="many2one":
#                                record_value=record_value.name
#                            worksheet.write(col,row+1, record_value)
#                            row += 2
#                        else:
#                            row=0
#                            col+=1
#                            worksheet.write(col,row,field.field_description , style=stylePC)
#                            record_value = getattr(curr_obj.browse(record), field.name)
#                            if field.ttype=="many2one":
#                                record_value=record_value.name
#                            worksheet.write(col,row+1, record_value)
#                            row+=2
#                        count += 1
#                for field in globle_obj.browse(globle_id).sub_model_name.field_id:
#                    if field.relation == globle_obj.browse(globle_id).model_name.model:
#                        relation_field = field.name
#                if not relation_field:
#                    continue
#                submodel_record = self.env[globle_obj.browse(globle_id).sub_model_name.model].search([(relation_field,'=',record)])
#                header_row = 0
#                header_col = col +2
#                row = 0
#                col += 2
#                
#                for sub_record in submodel_record:
#                    for field_name in globle_obj.browse(globle_id).sub_model_field_ids:
#                        if not header:
#                            for header_data in globle_obj.browse(globle_id).sub_model_field_ids:
#                                worksheet.write(header_col,header_row,header_data.field_description , style=stylePC)
#                                header_row=header_row+1
#                            header = True
#                        record_data = getattr(sub_record, field_name.name)
#                        if field_name.ttype=="many2one":
#                            record_data=record_data.name
#                        worksheet.write(col+1,row, record_data)
#                        row += 1
#                    col+=1
#                    row = 0
#                row = 0
#                col+=1
#                
#        file_data = cStringIO.StringIO()
#        workbook.save(file_data)
#        self.write({
#            'state': 'get',
#            'data': base64.encodestring(file_data.getvalue()),
#            'name': "generic excel report.xls"
#        })
#        return {
#            'type': 'ir.actions.act_window',
#            'name': 'Generic Excel Report',
#            'res_model': 'generic.excel.report.wizard',
#            'view_mode': 'form',
#            'view_type': 'form',
#            'res_id': self.id,
#            'target': 'new'
#        }

