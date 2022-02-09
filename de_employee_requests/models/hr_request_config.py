from odoo import api, fields, models, _


class HrRequestConfig(models.Model):
    _name = 'hr.request.config'
    _description = ''

    @api.model
    def create(self, values):
        if values.get('name', _('New')) == _('New'):
            values['name'] = self.env['ir.sequence'].next_by_code('hr.request.config.name') or _('New')
        return super(HrRequestConfig, self).create(values)

    name = fields.Char('Sequence', required=True, copy=False, readonly=True, index=True,
                       default=lambda self: _('New'))

    request_type = fields.Char('Request Type')
    category = fields.Selection([('hr', 'HR'), ('management', 'Management'), ('operations', 'Operations'),
                                 ('security', 'Security'), ('technical', 'Technical'), ('it', 'IT'),
                                 ('marketing', 'Marketing'), ('accounts', 'Accounts'), ('others', 'Others')], string='Category')
    concerned_person_id = fields.Many2one('hr.employee', 'Concerned Person for this type')
    company_id = fields.Many2one('res.company', string='Company', default=lambda self: self.env.company)
