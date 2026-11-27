from odoo import api, fields, models
from odoo.exceptions import UserError


class PurchaseRequest(models.Model):
    _name = 'art_marketplace.purchase_request'
    _description = 'Purchase Request'

    name = fields.Char(
        string='Reference',
        readonly=True,
        default='Nuevo',
    )
    artwork_sale_id = fields.Many2one(
        comodel_name='art_marketplace.artwork_sale',
        string='Artwork',
        required=True,
        domain="[('state', '=', 'published')]",
        index=True,
    )
    partner_id = fields.Many2one(
        comodel_name='res.partner',
        string='Customer',
        index=True,
    )
    customer_name = fields.Char(string='Customer Name', required=True)
    customer_email = fields.Char(string='Email', required=True)
    customer_phone = fields.Char(string='Phone')
    message = fields.Text(string='Message / Inquiry')
    state = fields.Selection(
        selection=[
            ('new', 'New'),
            ('contacted', 'Contacted'),
            ('won', 'Won'),
            ('canceled', 'Canceled'),
        ],
        string='Status',
        required=True,
        default='new',
        index=True,
    )
    request_date = fields.Date(
        string='Request Date',
        default=fields.Date.context_today,
        required=True,
    )

    def _find_or_create_partner(self):
        self.ensure_one()
        partner = self.partner_id
        if not partner:
            partner = self.env['res.partner'].search([
                ('email', '=', self.customer_email),
            ], limit=1)
            if not partner and self.customer_phone:
                partner = self.env['res.partner'].search([
                    ('name', '=', self.customer_name),
                    ('phone', '=', self.customer_phone),
                ], limit=1)
            if not partner:
                partner_vals = {
                    'name': self.customer_name,
                    'email': self.customer_email,
                }
                if self.customer_phone:
                    partner_vals['phone'] = self.customer_phone
                partner = self.env['res.partner'].create(partner_vals)
            self.partner_id = partner
        return partner

    def action_mark_contacted(self):
        for ticket in self:
            if ticket.state != 'new':
                raise UserError('Only New tickets can be marked as Contacted.')

            ticket._find_or_create_partner()
            ticket.state = 'contacted'

    def action_win_ticket(self):
        self.ensure_one()
        if self.state not in ['new', 'contacted']:
            raise UserError("Solo puedes ganar tickets en estado Nuevo o Contactado.")
        
        sale = self.artwork_sale_id
        
        # Verificamos que la obra no se haya vendido ya por otro lado
        if sale.state == 'sold':
            raise UserError("Esta obra ya ha sido vendida.")

        partner = self._find_or_create_partner()

        # Asignamos el comprador a la venta
        sale.buyer_id = partner.id

        # ¡El cambio clave! Cerramos la venta (pasa a 'sold' y genera factura)
        # Pasamos el partner_id para que el método sepa a quién facturar
        sale.action_sell(buyer_id=partner)
        
        # Marcamos el ticket como ganado
        self.state = 'won'

    def action_cancel_ticket(self):
        self.ensure_one()
        if self.state == 'won':
            raise UserError("No puedes cancelar un ticket que ya fue ganado y facturado.")
        
        # Si la obra se le había asignado a este ticket, la liberamos
        if self.artwork_sale_id and self.artwork_sale_id.buyer_id == self.partner_id:
            # Quitamos el comprador y devolvemos la obra a Published si no estaba sold
            if self.artwork_sale_id.state != 'sold':
                self.artwork_sale_id.write({
                    'buyer_id': False,
                    'state': 'published'
                })
        
        self.state = 'canceled'

