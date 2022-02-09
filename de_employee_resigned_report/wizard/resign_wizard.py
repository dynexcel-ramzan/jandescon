 -*- coding: utf-8 -*-
class ResignedWizard(models.TransientModel):
    _name = 'resigned.wizard'
    _description = 'Resigned Wizard'
    
    date_from = fields.Date(string='Date from', required=True)
    date_to = fields.Date(string='Date to', required=True)
    
    
    
        def action_check_report(self):
        data = {}
        data['form'] = self.read(['date_from', 'date_to'])[0]
        return self._print_report(data)

    def _print_report(self, data):
        data['form'].update(self.read(['date_from', 'date_to'])[0])
        return self.env.ref('de_employee_resigned_report.employee_resign_report').report_action(self,
                                                                                   data=data,config=False)