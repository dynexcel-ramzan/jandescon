# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import AccessDenied, AccessError, UserError, ValidationError


class HrEmployee(models.Model):
    _inherit = 'hr.employee'
    
    """
    @api.model
    def create(self, vals):
        employee = super(HrEmployee, self).create(vals)
        self.env['res.users'].create({
                'name': self.name,
                'active': True,
                'company_id': self.company_id.id,
                'login': self.name,
                'notification_type': 'email',
                'partner_id': self.address_home_id.id,
                'property_account_payable_id': self.address_home_id.property_account_payable_id.id,
                'property_account_receivable_id':self.address_home_id.property_account_receivable_id.id,
                'sel_groups_1_9_10': '9',
            })
        return employee """

    
    
    user_id = fields.Many2one('res.users', 'User', related='resource_id.user_id', store=True, readonly=False)
    line_manager = fields.Char(string='Manager', compute='_compute_manager_name')
    
    @api.depends('parent_id')
    def _compute_manager_name(self):
        for manager in self:
            manager.update({
                'line_manager': manager.parent_id.name,
            })    
    
    

    
class Users(models.Model):
    """ User class. A res.users record models an OpenERP user and is different
        from an employee.

        res.users class now inherits from res.partner. The partner model is
        used to store the data related to the partner: lang, name, address,
        avatar, ... The user model is now dedicated to technical data.
    """
    _inherit = "res.users"

    @api.constrains('groups_id')
    def _check_one_user_type(self):
        """We check that no users are both portal and users (same with public).
           This could typically happen because of implied groups.
        """
        user_types_category = self.env.ref('base.module_category_user_type', raise_if_not_found=False)
        user_types_groups = self.env['res.groups'].search(
            [('category_id', '=', user_types_category.id)]) if user_types_category else False
        if user_types_groups:  # needed at install
            if self._has_multiple_groups(user_types_groups.ids):
                pass
    