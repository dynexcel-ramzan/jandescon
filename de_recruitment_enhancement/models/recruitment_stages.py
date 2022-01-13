from odoo import models, fields, api, _
# from dateutil.relativedelta import relativedelta

from odoo.exceptions import UserError


class RecruitmentEnhancementStage(models.Model):
    _inherit = 'hr.recruitment.stage'

    is_non_fixed_stage = fields.Boolean()
    is_show_employee_button = fields.Boolean()
