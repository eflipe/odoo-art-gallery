import re

from odoo import http
from odoo.addons.phone_validation.tools import phone_validation
from odoo.http import request


class ArtGalleryWebsite(http.Controller):
    @http.route('/gallery', auth='public', website=True)
    def gallery(self, **kwargs):
        artworks = request.env['art_marketplace.artwork_sale'].sudo().search([
            ('state', '=', 'published'),
        ])
        return request.render('art_marketplace.gallery_template', {'artworks': artworks})

    @http.route(
        '/gallery/request/<int:sale_id>',
        auth='public',
        website=True,
        methods=['GET', 'POST'],
    )
    def gallery_request(self, sale_id, **kwargs):
        sale = request.env['art_marketplace.artwork_sale'].sudo().browse(sale_id)
        if not sale.exists() or sale.state != 'published':
            return request.not_found()

        if request.httprequest.method == 'POST':
            customer_name = request.params.get('customer_name')
            customer_email = request.params.get('customer_email')
            phone = (request.params.get('customer_phone') or '').strip()
            message = request.params.get('message')

            prefill = {
                'customer_name': customer_name,
                'customer_email': customer_email,
                'customer_phone': phone,
                'message': message,
            }

            phone_to_validate = phone
            if phone_to_validate:
                if phone_to_validate.startswith('+'):
                    digits_only = ''.join(char for char in phone_to_validate[1:] if char.isdigit())
                    phone_to_validate = f'+{digits_only}' if digits_only else phone_to_validate
                else:
                    digits_only = ''.join(char for char in phone_to_validate if char.isdigit())
                    if len(digits_only) >= 11:
                        phone_to_validate = f'+{digits_only}'

            customer_phone = phone
            if phone:
                try:
                    customer_phone = phone_validation.phone_format(phone_to_validate, raise_exception=True)
                except Exception:
                    if re.fullmatch(r'\+\d{7,20}', phone_to_validate):
                        customer_phone = phone_to_validate
                    else:
                        return request.render(
                            'art_marketplace.request_form_template',
                            {
                                'sale': sale,
                                'prefill': prefill,
                                'error': (
                                        'El número de teléfono no es válido. Por favor, ingresa un número con el código de país. '
                                        'Ejemplos: +54 11 1234-1234 (fijo), +54 9 11 1234-5678 (móvil AR) o +1 555-555-5555. '
                                        'También podés ingresarlo sin espacios: +541112341234.'
                                ),
                            },
                        )

            request.env['art_marketplace.purchase_request'].sudo().create({
                'artwork_sale_id': sale.id,
                'customer_name': customer_name,
                'customer_email': customer_email,
                'customer_phone': customer_phone,
                'message': message,
            })
            return request.redirect('/gallery/thank-you')

        return request.render(
            'art_marketplace.request_form_template',
            {
                'sale': sale,
                'prefill': {},
                'error': False,
            },
        )

    @http.route('/gallery/thank-you', auth='public', website=True)
    def gallery_thank_you(self, **kwargs):
        return request.render('art_marketplace.thank_you_template', {})

