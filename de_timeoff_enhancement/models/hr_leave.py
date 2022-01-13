from odoo import models, fields, api, _

class HrLeave(models.Model):
    _inherit = 'hr.leave'

    fiscal_year = fields.Char(related='holiday_status_id.fiscal_year')

#for Hr.leave.report additional Fields target date
class HrLeaveReport(models.Model):
    _inherit = 'hr.leave.report'

    fiscal_year = fields.Char(related='holiday_status_id.fiscal_year')
