import base64
import logging

import requests

from odoo import api, fields, models
from odoo.exceptions import ValidationError

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

    @api.model
    def get_gallery_data(self, offset=0, limit=10):
        domain = []
        total = self.search_count(domain)
        artworks = self.search(domain, offset=offset, limit=limit, order='id desc')        
        return {
            'total': total,
            'artworks': [{
                'id': artwork.id,
                'name': artwork.name,
                'artist_name': artwork.artist_name or '',
                'year': artwork.year or '',
                'image_src': f'/web/image/art_gallery.artwork/{artwork.id}/image' if artwork.image else False,
            } for artwork in artworks],
        }

    @api.model
    def get_dashboard_data(self, year_from=None, year_to=None):
        """Return a list of artworks formatted for the dashboard."""

        # Intentar convertir a entero. Si el usuario escribió letras, lanzará error.
        try:
            if year_from is not None and str(year_from).strip() != '':
                year_from = int(year_from)
            else:
                year_from = None
                
            if year_to is not None and str(year_to).strip() != '':
                year_to = int(year_to)
            else:
                year_to = None
        except (ValueError, TypeError):
            raise ValidationError("Los años deben ser números enteros. No se permiten letras ni símbolos.")

        domain = []
        if year_from:
            domain.append(('year', '>=', year_from))
        if year_to:
            domain.append(('year', '<=', year_to))

        artworks = self.search(domain, limit=50, order='year asc')
        result = []
        for artwork in artworks:
            result.append({
                'id': artwork.id,
                'name': artwork.name,
                'artist_name': artwork.artist_name or '',
                'year': artwork.year,
                'image': artwork.image.decode('utf-8') if artwork.image else None,
            })
        return result
