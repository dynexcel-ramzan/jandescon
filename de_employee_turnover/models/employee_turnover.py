from odoo import api, fields, models, _


class EmployeeTurnover(models.Model):
    _name = 'employee.turnover'
    _description = 'Employee Turnover'

    type = fields.Selection([('monthly', 'Monthly'),('yearly', 'Yearly')], string='Type', default='monthly', required=1)
    date_from = fields.Date(string='Date From', required='1', help='select start date')
    date_to = fields.Date(string='Date To', required='1', help='select end date')
    total_emp_left = fields.Integer(string='Total number of Left Employees', )
    total_emp_active = fields.Integer(string='Total number of Active Employees',)
    turnover_rate = fields.Float(string='Turn-Over Rate',)

    @api.onchange('date_from','date_to')
    def onchange_date(self):
        for record in self:
            if record.date_to and record.date_from:
                employee_active = record.env['hr.employee'].search_count([('active', '=', True)])
                record.total_emp_active = employee_active
                employee_left = record.env['hr.employee'].search_count([('active', '=', False), ('departure_date', '>=', record.date_from),('departure_date', '<=', record.date_to)])
                record.total_emp_left = employee_left
                record.turnover_rate = float(record.total_emp_left / record.total_emp_active)