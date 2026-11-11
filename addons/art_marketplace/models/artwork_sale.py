from odoo import api, fields, models


class ArtworkSale(models.Model):
    _name = 'art_marketplace.artwork_sale'
    _description = 'Artwork Sale'

    company_id = fields.Many2one(
        comodel_name='res.company',
        required=True,
        default=lambda self: self.env.company,
    )
    currency_id = fields.Many2one(
        comodel_name='res.currency',
        required=True,
        default=lambda self: self.env.company.currency_id,
    )

    artwork_id = fields.Many2one(
        comodel_name='art_gallery.artwork',
        string='Artwork',
        required=True,
        index=True,
    )
    price = fields.Monetary(
        string='Price',
        currency_field='currency_id',
    )
    state = fields.Selection(
        selection=[
            ('draft', 'Draft'),
            ('published', 'Published'),
            ('sold', 'Sold'),
        ],
        string='Status',
        required=True,
        default='draft',
        index=True,
    )

    seller_id = fields.Many2one(
        comodel_name='res.partner',
        string='Seller',
        required=True,
        default=lambda self: self.env.user.partner_id,
        index=True,
    )
    buyer_id = fields.Many2one(
        comodel_name='res.partner',
        string='Buyer',
        index=True,
    )

    sale_date = fields.Date(string='Sale Date')
    invoice_id = fields.Many2one(
        comodel_name='account.move',
        string='Invoice',
        index=True,
    )

    # Helper field to enforce “one active sale per artwork” via SQL uniqueness.
    # When the sale is not sold, this field mirrors artwork_id; when sold it is NULL.
    active_artwork_id = fields.Many2one(
        comodel_name='art_gallery.artwork',
        compute='_compute_active_artwork_id',
        store=True,
        index=True,
    )

    _unique_active_sale_per_artwork = models.Constraint(
        'UNIQUE(active_artwork_id)',
        'This artwork already has an active sale (Draft/Published).',
    )

    @api.depends('artwork_id', 'state')
    def _compute_active_artwork_id(self):
        for sale in self:
            sale.active_artwork_id = sale.artwork_id if sale.state != 'sold' else False

    def action_publish(self):
        self.filtered(lambda s: s.state == 'draft').write({'state': 'published'})

    def action_sell(self):
        self.filtered(lambda s: s.state == 'published').write({
            'state': 'sold',
            'sale_date': fields.Date.context_today(self),
        })
