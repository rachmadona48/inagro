from odoo import models, fields, api
from dateutil.relativedelta import relativedelta

class inagro_FleetVehicleLogContract(models.Model):
    _inherit = 'fleet.vehicle.log.contract'

    state = fields.Selection([
        ('futur', 'Incoming'),
        ('sent', 'Sent to Progress'),
        ('open', 'In Progress'),
        # ('diesoon', 'Expiring Soon'),
        ('expired', 'Expired'),
        ('closed', 'Closed')
        ], 'Status', default='futur', readonly=True,
        help='Choose whether the contract is still valid or not',
        track_visibility="onchange",
        copy=False)

    seats = fields.Integer('Seats Number of Vehicle',related="vehicle_id.seats", help='Number of seats vehicle')
    purchaser_id = fields.Many2one('res.partner', 'Driver',related="vehicle_id.driver_id",
        help='Person to which the contract is signed for')

    passenger_ids = fields.One2many('vehicle.passenger', 'parent_id', 'Passenger', copy=False, readonly=True, states={'futur': [('readonly', False)]})
    
    # @api.onchange('cost_subtype_id')
    # def onchange_cost_subtype_id(self):
    #     # self.vehicle_id = self.env['fleet.vehicle'].search([('user_id', '=', self.user_id.id)])
    #     print('tes')
        

    @api.depends('passenger_ids.t_pass')
    def _sum_all(self):
        for order in self:
            sum_pass = 0.0
            for line in order.passenger_ids:
                sum_pass += line.t_pass
            order.sum_pass = sum_pass
            order.update({
                'sum_pass': (int(sum_pass))
            })
            print(order.sum_pass,' order.sum_pass')
    sum_pass = fields.Integer('Total Passenger', store=True, readonly=True, compute='_sum_all')

    vehicle_type_id = fields.Many2one('fleet.vehicle.state', 'Vehicle Type', required=True,readonly=True,
                              states={'futur': [('readonly', False)]})

    @api.onchange('vehicle_type_id')
    def onchange_vehicle_type_id(self):
        # self.vehicle_id = self.env['fleet.vehicle'].search([('state_id', '=', self.vehicle_type_id.id)])
        res = {}
        res['domain']={'vehicle_id':[('state_id', '=', self.vehicle_type_id.id)]}
        return res
        # print(self.vehicle_id,' ddd')


    @api.model
    def scheduler_manage_contract_expiration(self):
        # This method is called by a cron task
        # It manages the state of a contract, possibly by posting a message on the vehicle concerned and updating its status
        # date_today = fields.Date.from_string(fields.Date.today())
        # in_fifteen_days = fields.Date.to_string(date_today + relativedelta(days=+15))
        # nearly_expired_contracts = self.search([('state', '=', 'open'), ('expiration_date', '<', in_fifteen_days)])

        # nearly_expired_contracts.write({'state': 'diesoon'})
        # for contract in nearly_expired_contracts.filtered(lambda contract: contract.user_id):
        #     contract.activity_schedule(
        #         'fleet.mail_act_fleet_contract_to_renew', contract.expiration_date,
        #         user_id=contract.user_id.id)

        expired_contracts = self.search([('state', '!=', 'expired'), ('expiration_date', '<',fields.Date.today() )])
        expired_contracts.write({'state': 'expired'})

        # futur_contracts = self.search([('state', 'not in', ['futur', 'closed']), ('start_date', '>', fields.Date.today())])
        # futur_contracts.write({'state': 'futur'})

        # now_running_contracts = self.search([('state', '=', 'futur'), ('start_date', '<=', fields.Date.today())])
        # now_running_contracts.write({'state': 'open'})



class inagro_Fleet_passenger(models.Model):
    _name = 'vehicle.passenger'

    name = fields.Many2one('vehicle.request','Request Number',ondelete='cascade')
    user_req_name = fields.Char('User Request',readonly=True,store=True)
    state = fields.Selection([('draft', 'Draft'), ('request', 'Request'), ('confirm', 'Confirm'),
                              ('cancel', 'Cancel')],
                             'State', related="name.state", store=True)
    # department_id = fields.Many2one('hr.department', string='Department',required=True,readonly=True,related="name.department_id", store=True)
    date_start = fields.Datetime('Date Start', related="name.date_start", store=True)
    date_end = fields.Datetime('Date End', related="name.date_end", store=True)
    destination = fields.Text('Destination',related="name.destination", store=True)
    info = fields.Text('Information',related="name.info", store=True)
    t_pass = fields.Integer('Total Passenger',related="name.t_pass", store=True)
    vehicle_type_id = fields.Many2one('fleet.vehicle.state', 'Vehicle Type', related="name.vehicle_type_id", store=True)

    parent_id = fields.Many2one('fleet.vehicle.log.contract',
                                 'Contract',
                                 ondelete='cascade', readonly=True)

    @api.onchange('name')
    def onchange_name(self):
        self.user_req_name = self.name.create_uid.partner_id.name

