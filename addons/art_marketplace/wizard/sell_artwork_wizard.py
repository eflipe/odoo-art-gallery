from odoo import api, fields, models


class SellArtworkWizard(models.TransientModel):
    _name = 'art_marketplace.sell_wizard'
    _description = 'Sell Artwork Wizard'

    sale_id = fields.Many2one(
        comodel_name='art_marketplace.artwork_sale',
        required=True,
        readonly=True,
    )
    buyer_id = fields.Many2one(
        comodel_name='res.partner',
        required=True,
    )
    valid_buyer_ids = fields.Many2many(
        comodel_name='res.partner',
        compute='_compute_valid_buyer_ids',
        string='Valid Buyers',
    )

    @api.depends('sale_id')
    def _compute_valid_buyer_ids(self):
        for wizard in self:
            tickets = wizard.env['art_marketplace.purchase_request']
            if wizard.sale_id:
                tickets = wizard.env['art_marketplace.purchase_request'].search([
                    ('artwork_sale_id', '=', wizard.sale_id.id),
                    ('state', '=', 'contacted'),
                    ('partner_id', '!=', False),
                ])
            wizard.valid_buyer_ids = tickets.mapped('partner_id')

    def action_confirm_sale(self):
        self.ensure_one()
        self.sale_id.action_sell(buyer_id=self.buyer_id)
        return {'type': 'ir.actions.act_window_close'}

