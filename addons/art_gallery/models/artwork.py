import base64
import logging

import requests

from odoo import fields, models

_logger = logging.getLogger(__name__)

class Artwork(models.Model):
    _name = 'art_gallery.artwork'
    _description = 'Artwork'

    name = fields.Char(string='Title', required=True)
    artist_name = fields.Char(string='Artist')
    description = fields.Text(string='Description')
    external_id = fields.Char(string='External ID', index=True)
    image = fields.Binary(string='Image', attachment=True)
    image_url = fields.Char(string='Image URL')
    year = fields.Integer(string='Year')

    # Nueva sintaxis para Odoo 19
    _external_id_unique = models.Constraint(
        'UNIQUE(external_id)',
        'This artwork has already been imported.',
    )

    def action_import_artworks(self, year_from=None, year_to=None, limit=10):
        """Fetch artworks from the Art Institute of Chicago API and store them."""
        api_url = 'https://api.artic.edu/api/v1/artworks/search'
        params = {
            'fields': 'id,title,artist_display,image_id,date_start',
            'limit': limit,
        }
        if year_from and year_to:
            params['query[range][date_start][gte]'] = year_from
            params['query[range][date_start][lte]'] = year_to
        elif year_from:
            params['query[range][date_start][gte]'] = year_from
        elif year_to:
            params['query[range][date_start][lte]'] = year_to

        headers = {
            'AIC-User-Agent': 'ArtGalleryOdooModule (tu-email@ejemplo.com)',
        }

        try:
            response = requests.get(api_url, params=params, headers=headers, timeout=15)
            response.raise_for_status()
            data = response.json()
        except requests.exceptions.RequestException as exc:
            _logger.error('Failed to fetch artworks from API: %s', exc)
            return False

        artworks = data.get('data', [])
        created_count = 0

        for item in artworks:
            external_id = str(item.get('id'))
            if self.search_count([('external_id', '=', external_id)]):
                continue

            title = item.get('title') or 'Untitled'
            artist_display = item.get('artist_display') or ''
            image_id = item.get('image_id')
            year = item.get('date_start')

            image_base64 = False
            image_url = False
            if image_id:
                image_url = f'https://www.artic.edu/iiif/2/{image_id}/full/843,/0/default.jpg'
                try:
                    img_response = requests.get(image_url, headers=headers, timeout=15)
                    img_response.raise_for_status()
                    image_base64 = base64.b64encode(img_response.content)
                except requests.exceptions.RequestException as exc:
                    _logger.warning('Failed to download image for artwork %s: %s', external_id, exc)

            self.create({
                'name': title,
                'artist_name': artist_display,
                'external_id': external_id,
                'image': image_base64,
                'image_url': image_url,
                'year': year,
            })
            created_count += 1

        _logger.info('Imported %s new artworks.', created_count)
        return True

