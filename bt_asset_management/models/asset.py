# -*- coding: utf-8 -*-
##############################################################################
#
#    odoo, Open Source Management Solution
#    Copyright (C) 2018-BroadTech IT Solutions (<http://www.broadtech-innovations.com/>).
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>
##############################################################################

from odoo import api, fields, tools, models, _
from odoo.exceptions import Warning
from odoo.exceptions import ValidationError
from odoo import tools
import string

class BtAsset(models.Model):   
    _name = "bt.asset"
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _description = "Asset" 
    
    @api.multi
    def _get_default_location(self):
        obj = self.env['bt.asset.location'].search([('default','=',True)])
        if not obj:
            raise Warning(_("Please create asset location first"))
        loc = obj[0]
        return loc 
    
    name = fields.Char(string='Name', required=True)
    purchase_date = fields.Date(string='Purchase Date',track_visibility='always')
    purchase_value = fields.Float(string='Purchase Value', track_visibility='always')
    asset_code = fields.Char(string='Asset Code')
    is_created = fields.Boolean('Created', copy=False)
    current_loc_id = fields.Many2one('bt.asset.location', string="Current Location", default=_get_default_location, required=True)
    model_name = fields.Char(string='Model Name')
    serial_no = fields.Char(string='Serial No', track_visibility='always')
    manufacturer = fields.Char(string='Manufacturer')
    warranty_start = fields.Date(string='Warranty Start')
    warranty_end = fields.Date(string='Warranty End')
    category_id = fields.Many2one('bt.asset.category', string='Category Id')
    note = fields.Text(string='Internal Notes')
    state = fields.Selection([
            ('active', 'Active'),
            ('scrapped', 'Scrapped')], string='State',track_visibility='onchange', default='active', copy=False)
    image = fields.Binary("Image", attachment=True,
        help="This field holds the image used as image for the asset, limited to 1024x1024px.")
    image_medium = fields.Binary("Medium-sized image", attachment=True,
        help="Medium-sized image of the asset. It is automatically "\
             "resized as a 128x128px image, with aspect ratio preserved, "\
             "only when the image exceeds one of those sizes. Use this field in form views or some kanban views.")
    image_small = fields.Binary("Small-sized image", attachment=True,
        help="Small-sized image of the asset. It is automatically "\
             "resized as a 64x64px image, with aspect ratio preserved. "\
             "Use this field anywhere a small image is required.")
    
    @api.model
    def create(self, vals):
        tools.image_resize_images(vals)
        vals.update({'is_created':True})
        lot = super(BtAsset, self).create(vals)
        lot.message_post(body=_("Asset %s created with asset code %s")% (lot.name,lot.asset_code))
        return lot      
    
    @api.multi
    def write(self, vals):
        tools.image_resize_images(vals)
        lot = super(BtAsset, self).write(vals)
        return lot
    
    @api.multi
    def action_move_vals(self):
        for asset in self:
            location_obj = self.env['bt.asset.location'].search([('default_scrap','=',True)])
            if not location_obj:
                raise Warning(_("Please set scrap location first"))
            move_vals = {
                'from_loc_id' : asset.current_loc_id.id,
                'asset_id' : asset.id,
                'to_loc_id' : location_obj.id
                }
            asset_move = self.env['bt.asset.move'].create(move_vals)
            asset_move.action_move()
            asset.current_loc_id = location_obj.id
            asset.state = 'scrapped'
            if asset.state == 'scrapped':
                asset.message_post(body=_("Scrapped"))
        return True    

class BtAssetLocation(models.Model):   
    _name = "bt.asset.location"
    _description = "Asset Location" 
    
    name = fields.Char(string='Name', required=True)
    asset_ids = fields.One2many('bt.asset','current_loc_id', string='Assets')
    default = fields.Boolean('Default', copy=False)
    default_scrap = fields.Boolean('Scrap')
    
    @api.model
    def create(self, vals):
        result = super(BtAssetLocation, self).create(vals)
        obj = self.env['bt.asset.location'].search([('default','=',True)])
        asset_obj = self.env['bt.asset.location'].search([('default_scrap','=',True)])
        if len(obj) > 1 or len(asset_obj) > 1:
            raise ValidationError(_("Default location have already set."))
        return result
    
    @api.multi
    def write(self, vals):
        res = super(BtAssetLocation, self).write(vals)
        obj = self.env['bt.asset.location'].search([('default','=',True)])
        asset_obj = self.env['bt.asset.location'].search([('default_scrap','=',True)])
        if len(obj) > 1 or len(asset_obj) > 1:
            raise ValidationError(_("Default location have already set."))
        return res
    
class BtAssetCategory(models.Model): 
    _name = "bt.asset.category"
    _description = "Asset Category"
    
    name = fields.Char(string='Name', required=True)  
    categ_no = fields.Char(string='Category No')
    
# vim:expandtab:smartindent:tabstop=2:softtabstop=2:shiftwidth=2:  