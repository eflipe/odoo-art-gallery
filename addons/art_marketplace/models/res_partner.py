from odoo import models

class ResPartner(models.Model):
    _inherit = 'res.partner'

    def _compute_display_name(self):
        # 1. Ejecutamos la lógica original de Odoo primero
        super()._compute_display_name()
        
        # 2. Verificamos si nuestro módulo pidió el "modo limpio"
        if self.env.context.get('show_only_name'):
            for partner in self:
                # Si es una persona (no empresa) y tiene una empresa padre, 
                # le quitamos el nombre de la empresa.
                if not partner.is_company and partner.parent_id:
                    partner.display_name = partner.name