from odoo import api, fields, models


class Artist(models.Model):
    _name = 'art_gallery.artist'
    _description = 'Artist'
    _order = 'artwork_count desc, name asc'

    name = fields.Char(string='Artist Name', required=True)
    email = fields.Char(string='Email')
    biography = fields.Text(string='Biography / Details')
    commission_percentage = fields.Float(
        string='Commission (%)',
        default=50.0,
    )
    active = fields.Boolean(default=True)
    partner_id = fields.Many2one(
        comodel_name='res.partner',
        string='Related Contact',
        ondelete='restrict',
    )
    artwork_ids = fields.One2many(
        comodel_name='art_gallery.artwork',
        inverse_name='artist_id',
        string='Artworks',
    )
    artwork_count = fields.Integer(
        string='Artwork Count',
        compute='_compute_artwork_count',
        store=True,
    )

    @api.model_create_multi
    def create(self, vals_list):
        partner_model = self.env['res.partner']
        prepared_vals = []
        for vals in vals_list:
            vals = dict(vals)
            if not vals.get('partner_id'):
                partner_vals = {'name': vals.get('name')}
                if vals.get('email'):
                    partner_vals['email'] = vals['email']
                vals['partner_id'] = partner_model.create(partner_vals).id
            prepared_vals.append(vals)
        return super().create(prepared_vals)

    def write(self, vals):
        result = super().write(vals)
        partner_vals = {}
        if 'name' in vals:
            partner_vals['name'] = vals['name']
        if 'email' in vals:
            partner_vals['email'] = vals['email']
        if partner_vals:
            for artist in self:
                if artist.partner_id:
                    artist.partner_id.write(partner_vals)
        return result

    def _get_or_create_partner(self):
        self.ensure_one()
        if not self.partner_id:
            partner_vals = {'name': self.name}
            if self.email:
                partner_vals['email'] = self.email
            self.partner_id = self.env['res.partner'].create(partner_vals)
        return self.partner_id

    @api.depends('artwork_ids')
    def _compute_artwork_count(self):
        for artist in self:
            artist.artwork_count = len(artist.artwork_ids)

    def action_view_artworks(self):
        self.ensure_one()
        return {
            'type': 'ir.actions.act_window',
            'name': 'Artworks',
            'res_model': 'art_gallery.artwork',
            'view_mode': 'kanban,list,form',
            'domain': [('artist_id', '=', self.id)],
            'context': {'default_artist_id': self.id},
        }
