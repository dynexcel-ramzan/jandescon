import math
from collections import defaultdict

from odoo import models, fields, api


class HrMailActivity(models.Model):
    _inherit = 'mail.activity'

    # employee_id = fields.Many2one('hr.employee')

    onboarding_lines = fields.One2many('hr.employee.onboarding', 'employee_id', string='Employee onboarding line')

    def unlink(self):
        for activity in self:
            onboard_rec = self.env['hr.employee.onboarding'].search([('activity_id', '=', activity.id)])
            if onboard_rec:
                if activity.id == onboard_rec.activity_id:
                    if onboard_rec.status != 'done':
                        onboard_rec.status = 'cancel'
            offboard_rec = self.env['hr.employee.offboarding'].search([('activity_id', '=', activity.id)])
            if offboard_rec:
                if activity.id == offboard_rec.activity_id:
                    if offboard_rec.status != 'done':
                        offboard_rec.status = 'cancel'
            if activity.date_deadline <= fields.Date.today():
                self.env['bus.bus'].sendone(
                    (self._cr.dbname, 'res.partner', activity.user_id.partner_id.id),
                    {'type': 'activity_updated', 'activity_deleted': True})
        return super(HrMailActivity, self).unlink()

    def _action_done(self, feedback=False, attachment_ids=None):
        """ Private implementation of marking activity as done: posting a message, deleting activity
            (since done), and eventually create the automatical next activity (depending on config).
            :param feedback: optional feedback from user when marking activity as done
            :param attachment_ids: list of ir.attachment ids to attach to the posted mail.message
            :returns (messages, activities) where
                - messages is a recordset of posted mail.message
                - activities is a recordset of mail.activity of forced automically created activities
        """
        # marking as 'done'
        messages = self.env['mail.message']
        next_activities_values = []

        # Search for all attachments linked to the activities we are about to unlink. This way, we
        # can link them to the message posted and prevent their deletion.
        attachments = self.env['ir.attachment'].search_read([
            ('res_model', '=', self._name),
            ('res_id', 'in', self.ids),
        ], ['id', 'res_id'])

        activity_attachments = defaultdict(list)
        for attachment in attachments:
            activity_id = attachment['res_id']
            activity_attachments[activity_id].append(attachment['id'])

        for activity in self:
            # extract value to generate next activities
            if activity.force_next:
                Activity = self.env['mail.activity'].with_context(
                    activity_previous_deadline=activity.date_deadline)  # context key is required in the onchange to set deadline
                vals = Activity.default_get(Activity.fields_get())

                vals.update({
                    'previous_activity_type_id': activity.activity_type_id.id,
                    'res_id': activity.res_id,
                    'res_model': activity.res_model,
                    'res_model_id': self.env['ir.model']._get(activity.res_model).id,
                })
                virtual_activity = Activity.new(vals)
                virtual_activity._onchange_previous_activity_type_id()
                virtual_activity._onchange_activity_type_id()
                next_activities_values.append(virtual_activity._convert_to_write(virtual_activity._cache))

            # post message on activity, before deleting it
            record = self.env[activity.res_model].browse(activity.res_id)
            record.message_post_with_view(
                'mail.message_activity_done',
                values={
                    'activity': activity,
                    'feedback': feedback,
                    'display_assignee': activity.user_id != self.env.user
                },
                subtype_id=self.env['ir.model.data'].xmlid_to_res_id('mail.mt_activities'),
                mail_activity_type_id=activity.activity_type_id.id,
                attachment_ids=[(4, attachment_id) for attachment_id in attachment_ids] if attachment_ids else [],
            )
            # print(activity.activity_type_id.id)
            # activities = self.env['mail.activity'].search([('res_id', '=', activity.res_id)])
            # print(activities)
            # print(activity.id)

            onboard_rec = self.env['hr.employee.onboarding'].search([('activity_id', '=', activity.id)])
            if activity.id == onboard_rec.activity_id:
                onboard_rec.status = 'done'
            offboard_rec = self.env['hr.employee.offboarding'].search([('activity_id', '=', activity.id)])
            if activity.id == offboard_rec.activity_id:
                offboard_rec.status = 'done'
            # rec.unlink()

            # Moving the attachments in the message
            # TODO: Fix void res_id on attachment when you create an activity with an image
            # directly, see route /web_editor/attachment/add
            activity_message = record.message_ids[0]
            message_attachments = self.env['ir.attachment'].browse(activity_attachments[activity.id])
            if message_attachments:
                message_attachments.write({
                    'res_id': activity_message.id,
                    'res_model': activity_message._name,
                })
                activity_message.attachment_ids = message_attachments
            messages |= activity_message

        next_activities = self.env['mail.activity'].create(next_activities_values)

        self.unlink()  # will unlink activity, dont access `self` after that

        return messages, next_activities


class HrEmployee(models.Model):
    _inherit = 'hr.employee'
    # foreign key concept

    onboarding_lines = fields.One2many('hr.employee.onboarding', 'employee_id', string='Employee onboarding line')
    offboarding_lines = fields.One2many('hr.employee.offboarding', 'employee_id', string='Employee Offboarding line')

    progress = fields.Float(string="Progress", compute='calculate_progress', default=0.0)

    def calculate_progress(self):
        for records in self:
            onboard_record = records.env['hr.employee.onboarding'].search([('employee_id', '=', records.id)])
            offboard_record = records.env['hr.employee.offboarding'].search([('employee_id', '=', records.id)])

            onboard_count = records.env['hr.employee.onboarding'].search_count([('employee_id', '=', records.id)])
            offboard_count = records.env['hr.employee.offboarding'].search_count([('employee_id', '=', records.id)])
            count_done = 0
            if onboard_count or offboard_count:
                total = 100/(onboard_count + offboard_count)
                count_todo = 0
                count_cancel = 0
                if onboard_record:
                    for rec in onboard_record:
                        if rec.status:
                            if rec.status == 'to-do':
                                pass
                                # self.progress = 50.0
                            elif rec.status == 'done':
                                # self.progress = 100.0
                                count_done = (count_done + (1 * total))
                            else:
                                pass
                if offboard_record:
                    for rec in offboard_record:
                        if rec.status:
                            if rec.status == 'to-do':
                                pass
                                # self.progress = 50.0
                            elif rec.status == 'done':
                                # self.progress = 100.0
                                count_done = (count_done + (1 * total))
                            else:
                                pass
            records.progress = count_done
        # return self.progress


class EmployeeOnboarding(models.Model):
    _name = 'hr.employee.onboarding'
    # _inherit = 'mail.activity'
    _description = 'Employee Onboarding'

    employee_id = fields.Many2one('hr.employee', string='Onboarding Id', index=True)
    activity_type_id = fields.Many2one('hr.plan.activity.type')
    mail_activity_id = fields.Many2one('mail.activity')
    summary = fields.Text(string='Summary')
    activity_id = fields.Integer('Activity')
    # plan_id = fields.Many2one('hr.plan')
    status = fields.Selection([
        ('to-do', 'To-Do'),
        ('done', 'Done'),
        ('cancel', 'Cancelled'),
    ], string='Status', readonly=True, copy=False, index=True, tracking=3, default='to-do')


class EmployeeOffboarding(models.Model):
    _name = 'hr.employee.offboarding'
    _description = 'Employee Offboarding'

    employee_id = fields.Many2one('hr.employee', string='Offboarding Id', index=True)
    activity_type_id = fields.Many2one('hr.plan.activity.type')
    mail_activity_id = fields.Many2one('mail.activity')
    summary = fields.Text(string='Summary')
    activity_id = fields.Integer('Activity')
    # plan_id = fields.Many2one('hr.plan')
    status = fields.Selection([
        ('to-do', 'To-Do'),
        ('done', 'Done'),
        ('cancel', 'Canceled'),
    ], string='Status', readonly=True, copy=False, index=True, tracking=3, default='to-do')


class HrPlanWizardInherited(models.TransientModel):
    _inherit = 'hr.plan.wizard'
    _description = 'Plan Wizard'

    def action_launch(self):
        rec = super(HrPlanWizardInherited, self).action_launch()
        activities = self.env['mail.activity'].search([('res_id', '=', self.employee_id.id)])

        if self.plan_id.name == 'Onboarding':
            offboard_list = []
            onboard_all_activities = []
            offboard_activities_ids = self.env['hr.employee.offboarding'].search(
                [('employee_id', '=', self.employee_id.id)])

            for onboard_id in offboard_activities_ids:
                offboard_list.append(onboard_id.activity_id)

            for onboard_activity_type in activities:
                onboard_all_activities.append(onboard_activity_type.id)
            new_list = []
            for i in onboard_all_activities:
                if i not in offboard_list:
                    new_list.append(i)
            print(new_list)
            # for activity_type in self.plan_id.plan_activity_type_ids:
            for activity_type in activities:
                for list in new_list:
                    if list == activity_type.id:
                        print('Hello')
                        # responsible = activity_type.get_responsible_id(self.employee_id)
                        # print(self.id)
                        record = self.env['hr.employee.onboarding'].create({
                            # 'id': rec['res_id'],
                            'employee_id': rec['res_id'],
                            # 'employee_id': self.employee_id.id,
                            # 'activity_type_id': activity_type.activity_type_id.id,
                            'summary': activity_type.summary,
                            'activity_id': activity_type.id,
                            # 'plan_id': self.plan_id.id
                            # 'mail_activity_id': activity_type.activity_type_id.id,
                        })
        if self.plan_id.name == 'Offboarding':
            onboard_list = []
            offboard_all_activities = []
            # for activity_type in activities:
            onboard_activities_ids = self.env['hr.employee.onboarding'].search(
                [('employee_id', '=', self.employee_id.id)])

            for onboard_id in onboard_activities_ids:
                onboard_list.append(onboard_id.activity_id)

            for offboard_activity_type in activities:
                offboard_all_activities.append(offboard_activity_type.id)
            new_list = []
            for i in offboard_all_activities:
                if i not in onboard_list:
                    new_list.append(i)
            print(new_list)
            # activities_ids = self.env['mail.activity'].search([('employee_id', '=', self.employee_id.id)])

            for activity_type in activities:
                for list in new_list:
                    if list == activity_type.id:
                        record = self.env['hr.employee.offboarding'].create({
                            # 'id': rec['res_id'],
                            'employee_id': rec['res_id'],
                            # 'employee_id': self.employee_id.id,
                            # 'activity_type_id': activity_type.activity_type_id.id,
                            'summary': activity_type.summary,
                            'activity_id': activity_type.id,
                            # 'plan_id': self.plan_id.id
                            # 'mail_activity_id': activity_type.activity_type_id.id,
                        })
        self.env.cr.commit()

