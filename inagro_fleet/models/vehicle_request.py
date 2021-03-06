# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import UserError, AccessError
from datetime import datetime

class inagro_vehicle_request(models.Model):
    _name = 'vehicle.request'
    _inherit = ['mail.thread']

    name = fields.Char('Name',readonly=True,default="New")
    state = fields.Selection([('draft', 'Draft'), ('request', 'Request'), ('confirm', 'Confirm'),
                              ('cancel', 'Cancel')],
                             'State', readonly=True,
                             default=lambda *a: 'draft')
    # partner_id = fields.Many2one('res.user', 'User',default=lambda self: self.env.user.name, readonly=True,
    #                              index=True,
    #                              required=True,
    #                              states={'draft': [('readonly', False)]})

    department_id = fields.Many2one('hr.department', string='Department',required=True,readonly=True,
                              states={'draft': [('readonly', False)]}, store=True)
    date_start = fields.Datetime('Date Start', required=True,default=datetime.today(),
                              readonly=True,
                              states={'draft': [('readonly', False)]})
    date_end = fields.Datetime('Date End', required=True,readonly=True,
                              states={'draft': [('readonly', False)]})
    destination = fields.Text('Destination',readonly=True,
                              states={'draft': [('readonly', False)]})
    info = fields.Text('Information',readonly=True,
                              states={'draft': [('readonly', False)]})
    t_pass = fields.Integer('Total Passenger',readonly=True,states={'draft': [('readonly', False)]})

    vehicle_type_id = fields.Many2one('fleet.vehicle.state', 'Vehicle Type', required=True,readonly=True,
                              states={'draft': [('readonly', False)]})

    contract_id = fields.One2many('vehicle.passenger', 'name', 'contract', copy=False, readonly=True)

    @api.multi
    def button_request(self):
        self.name = self.env['ir.sequence'].next_by_code('vehicle.request')
        return self.write({'state': 'request'})

    @api.multi
    def button_cancel(self):
        return self.write({'state': 'cancel'})

    @api.multi
    def button_draft(self):
        return self.write({'state': 'draft'})

    @api.multi
    def unlink(self):
        for record in self:
            if record.state != 'draft':
                raise UserError(_('You cannot delete this data !!!'))
            return super(inagro_vehicle_request, self).unlink()

