from odoo import api, models


class IrUiMenu(models.Model):
    _inherit = 'ir.ui.menu'

    @api.model
    def get_app_launcher_data(self):
        apps = []
        for menu in self.search([('parent_id', '=', False)], order='sequence, id'):
            action_id = menu.action.id if menu.action else False
            if not action_id:
                child = menu.child_id.filtered('action')[:1]
                action_id = child.action.id if child else False

            if menu.web_icon or action_id:
                apps.append({
                    'id': menu.id,
                    'name': menu.name,
                    'action': action_id,
                    'icon': menu.web_icon or ''
                })
        return apps

