# -*- coding: utf-8 -*-
##############################################################################
#
#    odoo, Open Source Management Solution
#    Copyright (C) 2018 BroadTech IT Solutions Pvt Ltd 
#    (<http://broadtech-innovations.com>).
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################

from odoo import api, fields, models, _
import string
from odoo.exceptions import ValidationError
import copy

class BtAssetMove(models.Model):
    _name = "bt.asset.move"
    _description = "Asset Move" 
    
    name = fields.Char(string='Name', default="New", copy=False)
    from_loc_id = fields.Many2one('bt.asset.location', string='From Location', required=True)
    asset_id = fields.Many2one('bt.asset', string='Asset', required=False, copy=False)
    to_loc_id = fields.Many2one('bt.asset.location', string='To Location', required=True)
    state = fields.Selection([
            ('draft', 'Draft'),
            ('done', 'Done')], string='State',track_visibility='onchange', default='draft', copy=False)
    
    @api.model
    def create(self, vals):
        if vals.get('name', 'New') == 'New':
            vals['name'] = self.env['ir.sequence'].next_by_code('bt.asset.move') or 'New'
        result = super(BtAssetMove, self).create(vals)
        if vals.get('from_loc_id', False) or vals.get('to_loc_id', False):
            if result.from_loc_id == result.to_loc_id:
                raise ValidationError(_("From location and to location must be different."))
        if vals.get('asset_id',False):
            if result.asset_id.current_loc_id != result.from_loc_id:
                raise ValidationError(_("Current location and from location must be same while creating asset."))
        return result
    
    @api.multi
    def write(self, vals):
        result = super(BtAssetMove, self).write(vals)
        if vals.get('from_loc_id', False) or vals.get('to_loc_id', False):
            for move in self:
                if move.from_loc_id == move.to_loc_id:
                    raise ValidationError(_("From location and to location must be different."))
        if vals.get('asset_id',False):
            for asset_obj in self:
                if asset_obj.asset_id.current_loc_id != asset_obj.from_loc_id:
                    raise ValidationError(_("Current location and from location must be same while creating asset."))
        return result
    
    @api.multi
    def action_move(self):
        for move in self:
            move.asset_id.current_loc_id = move.to_loc_id and move.to_loc_id.id or False
            move.state = 'done'
        return True
    
# vim:expandtab:smartindent:tabstop=2:softtabstop=2:shiftwidth=2: