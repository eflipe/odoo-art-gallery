from odoo import fields, models


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

    def action_confirm_sale(self):
        self.ensure_one()
        self.sale_id.action_sell(buyer_id=self.buyer_id)
        return {'type': 'ir.actions.act_window_close'}

