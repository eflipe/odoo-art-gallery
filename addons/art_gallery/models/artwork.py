from odoo import models, fields


class Artwork(models.Model):
    _name = 'art_gallery.artwork'
    _description = 'Artwork'

    name = fields.Char(string='Title', required=True)
    artist_name = fields.Char(string='Artist')
    description = fields.Text(string='Description')

