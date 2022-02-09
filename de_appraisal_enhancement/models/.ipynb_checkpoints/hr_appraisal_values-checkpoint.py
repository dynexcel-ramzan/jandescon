from odoo import api, fields, models, _
from odoo.exceptions import UserError

class HrAppraisalValues(models.Model):
    _name = 'hr.appraisal.values'
    _rec_name = 'company_id'
    
    company_id = fields.Many2one('res.company', default=lambda self:self.env.company.id)
    description = fields.Char('Description')
    state = fields.Selection([
        ('draft', 'Draft'),
        ('confirm', 'Confirmed'),
        
    ], string='State', index=True, copy=False, default='draft', track_visibility='onchange')
    values_lines = fields.One2many('hr.appraisal.values.line', 'value_id')
    total_weightage = fields.Float("Total Weightage", compute = 'limit_weightage')
    readonly_status = fields.Selection([
        ('make_readonly', 'Readonly'),
        ('make_editable', 'Editable')], compute = 'compute_readonly')
    
    def unlink(self):
        for rec in self:
            if rec.state in ['confirm']:
                raise UserError(('Deletion is Not Allowed!'))
            return super(HrAppraisalValues, self).unlink()
    
    @api.onchange('company_id')
    def compute_readonly(self):
        for rec in self:
            if rec.state == 'confirm' and rec.env.user.has_group('de_appraisal_enhancement.group_allow_edit_objectives'):
                rec.readonly_status = 'make_editable'
            if rec.state == 'confirm' and not rec.env.user.has_group('de_appraisal_enhancement.group_allow_edit_objectives'):
                rec.readonly_status = 'make_readonly'
            else:
                rec.readonly_status = 'make_editable'
   

     

    @api.constrains('weightage')
    def limit_weightage(self):
        for rec in self:
            count = 0.0
            for line in rec.values_lines:
                count = count + line.weightage
            rec.total_weightage = count
            
    
    
    @api.model
    def create(self,vals):
        res = super(HrAppraisalValues, self).create(vals)
        if res.total_weightage != 100:
            raise UserError('Total Weightage should be equal 100')
        return res
    
    def write(self, vals):
        res = super(HrAppraisalValues, self).write(vals)
        if self.total_weightage != 100:
            raise UserError('Total Weightage must be equal 100')
        return res
    

    
    def action_submit(self):
        self.state = 'confirm'


    
class HrAppraisalValuesline(models.Model):
    _name = 'hr.appraisal.values.line'
    
    value_id = fields.Many2one('hr.appraisal.values')
    core_value= fields.Char('Core Value')
    description = fields.Char('Description')
    weightage = fields.Float('Weightage')
    priority = fields.Selection([
        ('low', 'Low'),
        ('medium', 'Medium'),
        ('high', 'High'),
        ('very_high', 'Very High'),
    ], string='Priority', index=True, copy=False, default='low', required = True,track_visibility='onchange')
    
    @api.onchange('weightage')
    def limit_weightage(self):
        if self.weightage:
            for rec in self:
                if int(rec.weightage) > 100 or int(rec.weightage) < 1 or rec.weightage == 0.00:
                    raise UserError('Weightage Cannot be greater than 100 or less than 1')