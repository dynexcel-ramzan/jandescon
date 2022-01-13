# -*- coding: utf-8 -*-

from odoo import models, fields, api, _

class HrPayslip(models.Model):
    _inherit = 'hr.payslip'
    
    @api.onchange('employee_id')
    def onchange_employee_input(self):
        for other_input in self.input_line_ids:
            other_input.unlink()
        data = []
        if self.employee_id and self.contract_id:
            contract_type = self.env['hr.contract'].search([('id','=', self.contract_id.id),('state','=', 'open')])

            for contract in contract_type:            
                for cont_line in contract.contract_lines:               
                    data.append((0,0,{
                                    'input_type_id': cont_line.input_type_id.id,
                                    'amount': cont_line.amount,
                                    }))
                self.input_line_ids = data
    
                   
#     @api.onchange('contract_id')
#     def onchange_contract(self):

#         data = []
#         contract_type = self.env['hr.contract'].search([('name','=', self.contract_id.name)])
#         for contract in contract_type:            
#             for cont_line in contract.contract_lines:               
#                 data.append((0,0,{
#                                 'input_type_id': cont_line.input_type_id,
#                                 'amount': cont_line.amount,
#                                 }))
#             self.contract_lines = data
            

class HrContract(models.Model):
    _inherit = 'hr.contract'

    contract_lines = fields.One2many('hr.contract.line', 'contract_id' ,string='Contract Lines')
    
                
    
    @api.onchange('structure_type_id')
    def onchange_structure(self):
        for cont_input in self.contract_lines:
            cont_input.unlink()
        data = []
        structure_type = self.env['hr.payroll.structure.type'].search([('name','=', self.structure_type_id.name)])
        print(structure_type)       
        for rec in structure_type:            
            for struc_line in rec.structure_lines:               
                data.append((0,0,{
                                'input_type_id': struc_line.input_type_id,
#                                 'amount': 0.0,
                                }))
            self.contract_lines = data

    
    

class HrPayrollStructureExt(models.Model):
    _inherit = 'hr.payroll.structure.type'
#     _description = 'This is Structure Lines'

    structure_lines = fields.One2many('hr.payroll.structure.line', 'struct_id', string='Structure Lines')

class HrPayrollStructureLine(models.Model):
    _name = 'hr.payroll.structure.line'
    _description = 'This is Structure Lines'

    input_type_id = fields.Many2one('hr.payslip.input.type', string='Input Type')
    struct_id = fields.Many2one('hr.payroll.structure.type', string='Structure')

class HrContractLines(models.Model):
    _name = 'hr.contract.line'
    _description = 'This is Structure Lines'

    input_type_id = fields.Many2one('hr.payslip.input.type', string='Input Type')
    contract_id = fields.Many2one('hr.contract', string='Structure')
    amount = fields.Float(string='Amount', store=True, required=True)


