from odoo import api, fields, models
from odoo.exceptions import UserError

import logging
_logger = logging.getLogger(__name__)

class ArtworkSale(models.Model):
    _name = 'art_marketplace.artwork_sale'
    _description = 'Artwork Sale'

    purchase_request_ids = fields.One2many(
        comodel_name='art_marketplace.purchase_request',
        inverse_name='artwork_sale_id',
        string='Purchase Requests',
    )
    purchase_request_count = fields.Integer(
        string='Purchase Request Count',
        compute='_compute_purchase_request_count',
    )

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

    artist_id = fields.Many2one(
        comodel_name='art_gallery.artist',
        string='Artist',
        required=True,
    )
    artwork_id = fields.Many2one(
        comodel_name='art_gallery.artwork',
        string='Select Artwork',
        required=True,
        index=True,
    )
    price = fields.Monetary(
        string='Price',
        currency_field='currency_id',
    )
    artist_commission_percentage = fields.Float(
        related='artwork_id.artist_id.commission_percentage',
        readonly=True,
        string='Artist Commission (%)',
    )
    artist_commission_amount = fields.Monetary(
        compute='_compute_commission',
        string='Artist Commission Amount',
        currency_field='currency_id',
    )
    gallery_net_income = fields.Monetary(
        compute='_compute_commission',
        string='Gallery Net Income',
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
    artist_invoice_id = fields.Many2one(
        comodel_name='account.move',
        string='Artist Invoice',
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

    @api.onchange('artist_id')
    def _onchange_artist_id(self):
        if self.artwork_id.artist_id != self.artist_id:
            self.artwork_id = False

        if not self.artist_id:
            domain = [('id', '=', False)]
        else:
            domain = [
                ('artist_id', '=', self.artist_id.id),
                ('id', 'not in', self.unavailable_artwork_ids.ids),
            ]
        return {'domain': {'artwork_id': domain}}

    @api.onchange('artwork_id')
    def _onchange_artwork_id(self):
        if self.artwork_id:
            self.artist_id = self.artwork_id.artist_id
            if not self.description:
                self.description = self.artwork_id.description


    @api.depends('artwork_id')
    def _compute_display_name(self):
        for sale in self:
            if sale.artwork_id:
                sale.display_name = f"Venta: {sale.artwork_id.name}"
            else:
                sale.display_name = "Nueva Venta"

    @api.depends('price', 'artist_commission_percentage')
    def _compute_commission(self):
        for sale in self:
            sale.artist_commission_amount = (
                sale.price * (sale.artist_commission_percentage / 100)
            )
            sale.gallery_net_income = sale.price - sale.artist_commission_amount

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

    @api.depends('purchase_request_ids')
    def _compute_purchase_request_count(self):
        for sale in self:
            sale.purchase_request_count = len(sale.purchase_request_ids)

    def action_view_purchase_requests(self):
        self.ensure_one()
        return {
            'type': 'ir.actions.act_window',
            'name': 'Purchase Requests',
            'res_model': 'art_marketplace.purchase_request',
            'view_mode': 'list,form',
            'domain': [('artwork_sale_id', '=', self.id)],
            'context': {'default_artwork_sale_id': self.id},
        }

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
                'invoice_line_ids': [
                    (0, 0, {
                        'name': f"Venta de obra: {sale.artwork_id.name}",
                        'quantity': 1,
                        'price_unit': sale.price,
                    }),
                ],
            })
            sale.invoice_id = invoice

            artist_partner = sale.artwork_id.artist_id.partner_id
            if artist_partner and sale.artist_commission_amount > 0:
                artist_invoice = (
                    self.env['account.move']
                    .with_company(sale.company_id)
                    .create({
                        'move_type': 'in_invoice',
                        'partner_id': artist_partner.id,
                        'invoice_date': fields.Date.context_today(sale),
                        'currency_id': sale.currency_id.id,
                        'invoice_line_ids': [(0, 0, {
                            'name': (
                                f"Comisión de venta: "
                                f"{sale.artwork_id.name}"
                            ),
                            'quantity': 1,
                            'price_unit': sale.artist_commission_amount,
                        })],
                    })
                )
                sale.artist_invoice_id = artist_invoice

        purchase_requests = self.env['art_marketplace.purchase_request'].search([
            ('artwork_sale_id', 'in', sales.ids),
            ('state', 'in', ('new', 'contacted')),
        ])
        for purchase_request in purchase_requests:
            vals = {'state': 'won'}
            if (
                not purchase_request.partner_id
                and purchase_request.artwork_sale_id.buyer_id
            ):
                vals['partner_id'] = (
                    purchase_request.artwork_sale_id.buyer_id.id
                )
            purchase_request.write(vals)

    def action_reset_to_published(self):
        for sale in self:
            # Verificamos si hay una factura asociada y si está en estado borrador
            invoices = sale.invoice_id | sale.artist_invoice_id
            if any(invoice.state != 'draft' for invoice in invoices):
                raise UserError(
                    "No puedes revertir la venta porque una factura ya está "
                    "registrada o pagada. Cancela las facturas primero en "
                    "Contabilidad."
                )
            if invoices:
                # Si las facturas están en borrador, las eliminamos para no
                # dejar registros huérfanos.
                invoices.unlink()

            # Volvemos el estado a published y limpiamos los campos de venta
            sale.write({
                'state': 'published',
                'buyer_id': False,
                'sale_date': False,
                'invoice_id': False,
                'artist_invoice_id': False,
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
