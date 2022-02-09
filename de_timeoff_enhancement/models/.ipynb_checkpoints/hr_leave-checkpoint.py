from odoo import models, fields, api, _

class HrLeave(models.Model):
    _inherit = 'hr.leave'

    fiscal_year_id = fields.Many2one(related='holiday_status_id.fiscal_year_id')

#for Hr.leave.report additional Fields target date
class HrLeaveReport(models.Model):
    _inherit = 'hr.leave.report'

    fiscal_year_id = fields.Many2one(related='holiday_status_id.fiscal_year_id')
