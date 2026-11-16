from odoo import api, fields, models
from odoo.exceptions import UserError

import logging
_logger = logging.getLogger(__name__)

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

    description = fields.Text(string='Description')
    artwork_image = fields.Binary(related='artwork_id.image', readonly=True)

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

    unavailable_artwork_ids = fields.Many2many(
        comodel_name='art_gallery.artwork',
        compute='_compute_unavailable_artwork_ids',
        readonly=True,
    )


    @api.depends('artwork_id')
    def _compute_display_name(self):
        for sale in self:
            if sale.artwork_id:
                sale.display_name = f"Venta: {sale.artwork_id.name}"
            else:
                sale.display_name = "Nueva Venta"
                
    @api.depends('artwork_id', 'state')
    def _compute_active_artwork_id(self):
        for sale in self:
            sale.active_artwork_id = sale.artwork_id if sale.state != 'sold' else False

    @api.depends('artwork_id', 'state')
    def _compute_unavailable_artwork_ids(self):
        # Buscamos CUALQUIER venta que ya tenga una obra asignada
        # (sin importar si está en draft, published o sold)
        existing_sales = self.env['art_marketplace.artwork_sale'].search([
            ('artwork_id', '!=', False),
        ])
        
        # IDs de TODAS las obras que ya están en el sistema de ventas
        blocked_artwork_ids = existing_sales.mapped('artwork_id').ids

        for sale in self:   
            sale.unavailable_artwork_ids = [(6, 0, blocked_artwork_ids)]

    def action_publish(self):
        self.filtered(lambda s: s.state == 'draft').write({'state': 'published'})

    def action_sell(self, buyer_id=None):
        sales = self.filtered(lambda s: s.state == 'published')
        if not sales:
            return

        vals = {
            'state': 'sold',
            'sale_date': fields.Date.context_today(self),
        }
        if buyer_id:
            buyer_id.ensure_one()
            vals['buyer_id'] = buyer_id.id

        sales.write(vals)

        for sale in sales:
            if not sale.buyer_id:
                continue
            # with_company ensures the invoice uses the sale's company journal/accounts.
            invoice = self.env['account.move'].with_company(sale.company_id).create({
                'move_type': 'out_invoice',
                'partner_id': sale.buyer_id.id,
                'invoice_date': fields.Date.context_today(sale),
                'currency_id': sale.currency_id.id,
                'invoice_line_ids': [(0, 0, {
                    'name': f"Venta de obra: {sale.artwork_id.name}",
                    'quantity': 1,
                    'price_unit': sale.price or 0.0,
                })],
            })
            sale.invoice_id = invoice

    def action_reset_to_published(self):
        for sale in self:
            # Verificamos si hay una factura asociada y si está en estado borrador
            if sale.invoice_id:
                if sale.invoice_id.state != 'draft':
                    raise UserError("No puedes revertir la venta porque la factura ya está registrada o pagada. Cancela la factura primero en Contabilidad.")
                else:
                    # Si la factura está en borrador, la eliminamos para no dejar registros huérfanos
                    sale.invoice_id.unlink()
            
            # Volvemos el estado a published y limpiamos los campos de venta
            sale.write({
                'state': 'published',
                'buyer_id': False,
                'sale_date': False,
                'invoice_id': False,
            })


    def action_open_sell_wizard(self):
        self.ensure_one()
        return {
            'type': 'ir.actions.act_window',
            'name': 'Confirm Sale',
            'res_model': 'art_marketplace.sell_wizard',
            'view_mode': 'form',
            'target': 'new',
            'context': {
                'default_sale_id': self.id,
            },
        }
