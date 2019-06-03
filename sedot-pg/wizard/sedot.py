from odoo import api, fields, models, _
import time
from odoo.exceptions import UserError
import logging
_logger = logging.getLogger(__name__)

class SedotPgConfirm(models.TransientModel):
    _name = 'vit.sedot_pg_wizard'
    _description = 'Sedot Confirmation'
    

    @api.multi
    def confirm_button(self):
        self.ensure_one()        
        emp = self.env['hr.employee']
        emp.action_sedot_pg()
        return {'type': 'ir.actions.act_window_close'}
