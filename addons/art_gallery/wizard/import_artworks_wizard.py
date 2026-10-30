from odoo import fields, models


class ImportArtworksWizard(models.TransientModel):
    _name = 'art_gallery.import_wizard'
    _description = 'Import Artworks by Year Range'

    year_from = fields.Integer(string='From Year', required=True)
    year_to = fields.Integer(string='To Year', required=True)
    limit = fields.Integer(string='Number of Artworks', default=5, required=True)

    def action_confirm_import(self):
        self.env['art_gallery.artwork'].action_import_artworks(
            year_from=self.year_from,
            year_to=self.year_to,
            limit=self.limit, 
        )
        return {'type': 'ir.actions.act_window_close'}