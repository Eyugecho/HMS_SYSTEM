import random
from odoo import fields,models,api, _ 
from odoo.exceptions import ValidationError
from datetime import datetime, date,time,timedelta

from odoo.release import description

class DrogaShareHolder(models.Model):
    _name="droga.physio"
    _rec_name="description"
    _order = "create_date desc"
    _inherit = ['mail.thread', 'mail.activity.mixin', 'image.mixin']


    
    mrn = fields.Char(string="MRN",required=True, copy=False, readonly=True,default=lambda self: _('New'))

    full_name=fields.Char("Full Name", tracking=True)
    sex=fields.Selection([('male','Male'),('female','Female')],"Gender", tracking=True)
    # age=fields.Integer("Age", compute="_calculate_age")
    birth_date = fields.Date('Birth Date', tracking=True)

    # age = fields.Integer(string='Age')
    age = fields.Integer(string='Age', tracking=True)
    # birth_year = fields.Integer(string='Birth Year', compute='_calculate_birth_year', store=True), compute='_calculate_birth_year'
    birth_year = fields.Integer(string='Birth Year', compute='_calculate_birth_year', tracking=True)
    move_year = fields.Integer(string='Birth Year', compute='_calculate_birth_year',store=True, tracking=True)
    current_year = fields.Integer(string='Current Year', default=date.today().year)
    register_date = fields.Date('Register Date')
    customer = fields.Many2one("customer.class")
    customer_grade = fields.Many2one("customer.class", string="Customer Grade")
    customer_type = fields.Many2one("customer.class", string="Customer Type")
    area = fields.Many2one("customer.class",string="Area")
    location = fields.Many2one("customer.class", string="Location")

    employee_name = fields.Char("Employee Name")
    company_name = fields.Many2one("customer.class",string="Company name" )
    employee_id = fields.Char("Employee ID")
    region=fields.Many2one(related="city2.region",string="Subcity")
    city2=fields.Many2one(comodel_name="droga.city",string="City")

    phone=fields.Char("Phone" )


    
    subcity=fields.Selection([('ca1','CA1'),('ca2','CA2'),('ca3','CA3'),('ca4','CA4')],"Subcity")

    wereda=fields.Char("Wereda")
    office_tel=fields.Char("Office Tell")

    refered_by=fields.Many2one(comodel_name="hr.employee",string="Refered By")
    house_no=fields.Char("House No.")
    tin_no=fields.Char("Tin No.")
    tin_company=fields.Char(related='organization.tin_no',string="Tin No.")
    company=fields.Many2one(comodel_name="customer.class",string="company") 
    contract=fields.Many2one(comodel_name="droga.contract",string="contract") 
    appointed_to=fields.Many2one(comodel_name="hr.employee",string="Appointed To")
    current_age=fields.Integer("Current Age", compute="_calculate_birth_age")
    # register_date = fields.Date('Register Date')
  
    age_in_months = fields.Integer(string='Age in Months', tracking=True)
    age_type = fields.Selection([
        ('years', 'Years'),
        ('months', 'Months'),
    ], string='Age Type in', default='years', tracking=True)

    # sequence_no = fields.Char(string='Sequence', readonly=True)
    sequence_no = fields.Char(string='Sequence Number', readonly=True, copy=False, default=lambda self: _('New'))

    
    # description = fields.Text(string="Description")
    document = fields.Binary(string='Document')
    tags_s= fields.Many2many('patient.tag',string="Case")
    tags_cata= fields.Many2many('catagories.tag',string="Catagories")
    tags_services = fields.Many2many('services.tag',string="Service")
    tags_medek = fields.Many2many('medek.tag', string='Medek')
    
    is_individual = fields.Boolean(string='Individual', default=True)
    is_company = fields.Boolean(string='Company', default=False)
    is_organization = fields.Boolean(string='Organization', default=False)
    organization= fields.Many2one(comodel_name="customer.class",string="Organization")
    state = fields.Selection([ ('draft', 'Draft'), ('done', 'Done'), ('cancel', 'Cancelled')], default='draft', index=True, required=True, string="Status")

    company_id = fields.Many2one('res.company', required=True , default=lambda  self: self.env.user.company_id)
    

    @api.model
    def _search(self, args, offset=0, limit=None, order=None, count=False, access_rights_uid=None):
        user = self.env['res.users'].browse(self.env.uid)
        if self.env.context.get('user_company_id'):
            user_company_id = user.company_id.id
            args += ['|', ('company_id', '=', False), ('company_id', 'child_of', user_company_id)]
        return super(DrogaShareHolder, self)._search(args, offset=offset, limit=limit, order=order, count=count, access_rights_uid=access_rights_uid)


    @api.onchange('is_organization')
    def _onchange_is_organization(self):
        if not self.is_organization:
            self.organization = False

    def action_confirm(self):
        self.state = 'done'
    def action_cancel(self):
        self.state = 'cancel'
    @api.model
    def create(self, vals):

        # if vals.get('sequence_no', _('New')) == _('New'):
        #     vals['sequence_no'] = self.env['ir.sequence'].next_by_code('seq_droga_physio') or _('New')
        # result = super(DrogaShareHolder, self).create(vals)
        # return result
        if vals.get('sequence_no', _('New')) == _('New'):
            sequence = self.env['ir.sequence'].next_by_code('droga.physio') or _('New')
            vals['sequence_no'] = sequence
        result = super(DrogaShareHolder, self).create(vals)
        return result
    physio_custoemer = fields.Many2one('customer.class' )
    notebook_ids_sesstion = fields.One2many('notebook.class', 'droga_physio_id', string="Notebook")
    notebook_ids_employee = fields.One2many('notebook.class', 'droga_physio_id', string="Notebook")
  
    
    # @api.depends('birth_date')
    # def _calculate_age(self):
    #     for records in self:
    #         age=0
            
    #         birth_date=records.birth_date
    #         current_date=datetime.today().date()
    #         if birth_date:
    #             age=(current_date-birth_date)/timedelta(days=365)
    #         records.age=age


    @api.depends('age', 'age_type')
    def _calculate_birth_year(self):
        for record in self:
            birth_year = 0
            move_year = 0

            if record.age_type == 'years':
                birth_year = date.today().year - record.age
            elif record.age_type == 'months':
                birth_year = date.today().year - (record.age_in_months // 12)

            record.birth_year = birth_year
            record.move_year = birth_year

            if not record.register_date:
                record.register_date = record.create_date
    @api.onchange('birth_year',	)   
    def _calculate_birth_age(self):   
        current_age=0
        for record in self:
            if record.age and record.register_date:
                current_age= date.today().year-record.register_date.year
                if current_age != record.age:
                    record.current_age=record.age+current_age
            

    # @api.onchange('register_date')   
    # def _calculate_birth_age(self):   
    #  for record in self:
    #     if record.age and record.register_date:
    #         birth_year = date.today().year - record.age
    #         current_age = date.today().year - birth_year
    #         record.age = current_age



    
    def add_new_line(self):
        self.env['notebook.class'].create({
           'time':fields.Datetime("Date and Time"),
        })
    @api.onchange('is_individual')
    def _onchange_individual(self):
        if self.is_individual:
            self.is_company = False

    @api.onchange('is_company')
    def _onchange_company(self):
        if self.is_company:
            self.is_individual = False
  
    description = fields.Char("Description", compute="_compute_description")

    @api.onchange('sequence_no', 'full_name', 'company')
    def _compute_description(self):
        for record in self:
            mrn=""
            company=""
            name=""
            if record.mrn:
                mrn=record.sequence_no
            if record.full_name:
                name=record.full_name
            if record.company:
                company=record.company.company_name      

            a=mrn+" "" "+company
            record.description = a


    
    # @api.onchange()('tin_no')
    # def _check_tin(self):
    #     for records in self:
            
    #         if records.tin_no or not records.is_organization  :
    #             if not records.tin_no:
    #                  raise ValidationError("You should add tin number")
    #             tin_no= len(records.tin_no)
    #             if tin_no >13 or tin_no < 10:
    #                 raise ValidationError("The tin number sholud have digits b/n 10 up to 13")
    
    def action_cancel_appointment_wizard(self):
        # This method opens the CancelAppointmentWizard
        return {
            'type': 'ir.actions.act_window',
            'res_model': 'cancel.appointment.wizard',
            'view_mode': 'form',
            'target': 'new',
        }


class ExerciseExercise(models.Model):
    _name = 'exercise.exercise'
    _rec_name = 'full_name'
    _inherit = ['mail.thread', 'mail.activity.mixin', 'image.mixin']
    _order = "create_date desc"


    
    examin=fields.Many2one("examination.form",string="MRN", ondelete="cascade") 
    # examin = fields.Many2one('examination.form', string="Appointment", ondelete="cascade")


    examinnote=fields.One2many('exercise.note', 'noteexamin', string='Notebook')

    mrn=fields.Many2one(related='examin.mrn',string="MRN",store=True)
    age = fields.Integer(related='mrn.age',string='Age',store=True, tracking=True)
    full_name=fields.Char(related='mrn.full_name',string="Name",store=True, tracking=True)
    clinical_name=fields.Many2one(related="examin.clinician1", string="Clinicial Name",store=True, tracking=True)

    nurs_act = fields.One2many('nursingactivity.tag','nursact_e',string="Nursing Activities", tracking=True)
    nurs_act_2 = fields.One2many('nursingactivity2.tag','nursact_e_2',string="Nursing Activities 2", tracking=True)
    nurs_act_3 = fields.One2many('nursingactivity3.tag','nursact_e_3',string="Nursing Activities 3", tracking=True)

    # clinician_ex=fields.Char(related='mrn.clinician1' ,string="Clinician")
    Nurses=fields.Many2one(comodel_name="hr.employee",string="Avialiable Nurse") 

    exercise_precausion = fields.Html(string='Exercise Precautions', tracking=True)
    exercise_name = fields.Html(string='Exercise Name', tracking=True)
    exe_reptition = fields.Char(string='Repetition', tracking=True)
    exe_duration = fields.Char(string='Duration', tracking=True)
    exe_set = fields.Char(string='Sets', tracking=True)
    exe_core_phase = fields.Char( string='Core Phase', tracking=True)
    exe_load = fields.Char(string='Load/Resistance', tracking=True)
    exe_color = fields.Char(string='Color', tracking=True)
   

    state = fields.Selection([ ('draft', 'Draft'), ('exercise', 'In Exercise'),  ('done', 'Done'),('cancel', 'Cancelled')], default='draft', index=True, required=True, string="Status")
    # exe_name=fields.Many2one('examination.form', string="Exercise", ondelete="cascade")
    progress =fields.Integer(string="Progress", compute="_calculate_progress")	
    def action_confirm(self):
        self.state = 'exercise'
    def action_done(self):
        self.state = 'done'
    def action_cancel(self):
        self.state = 'cancel'

    @api.depends('state')
    def _calculate_progress(self):
        for record in self:
            progress=0
            if record.state == 'exercise':
                progress=random.randrange(25, 70)
            if record.state == 'done':
                progress=100
            if record.state == 'cancel':
                progress=0
            record.progress=progress
            
    def compute_create_fi(self):
        nurse_acti = self.env['nursingact.tag.config'].search([('catagories_nurs', '=', 'fi')])
        for record in nurse_acti:
            check_acti = self.env['nursingactivity.tag'].search([('nursing_activity_name', '=', record.name), ('nursact_e', '=', self.id)])
            if not check_acti:
                self.env['nursingactivity.tag'].create({
                    'nursing_activity_name': record.name,
                    'nursact_e': self.id,
                    
                })

    def compute_create_nurse_activities_sia(self):
        nurse_acti = self.env['nursingact.tag.config'].search([('catagories_nurs', '=', 'sia')])
        for record in nurse_acti:
            check_acti = self.env['nursingactivity2.tag'].search([('nursing_activity_name_2', '=', record.name), ('nursact_e_2', '=', self.id)])
            if not check_acti:
                self.env['nursingactivity2.tag'].create({
                    'nursing_activity_name_2': record.name,
                    'nursact_e_2': self.id,
                   
                })

    def compute_create_sgma(self):
        nurse_acti = self.env['nursingact.tag.config'].search([('catagories_nurs', '=', 'sgma')])
        for record in nurse_acti:
            check_acti = self.env['nursingactivity3.tag'].search([('nursing_activity_name_3', '=', record.name), ('nursact_e_3', '=', self.id)])
            if not check_acti:
                self.env['nursingactivity3.tag'].create({
                    'nursing_activity_name_3': record.name,
                    'nursact_e_3': self.id,
                    
                })
        

        

    
class GroupUser(models.Model):
    _name = 'group.user'
    _inherit = 'hr.employee'
    _description = 'Group User Model'

    work_permit_name = fields.Char(string='Work Permit Name', help='Name of the work permit')

    category_ids = fields.Many2many(
        'hr.employee.category', 
        relation='group_user_category_rel', 
        column1='group_user_id',
        column2='category_id',
        string='Categories'
    )
    group_type = fields.Selection([
        ('receptionist', 'Receptionist'),
        ('nurse', 'Nurse'),
        ('clinician', 'Clinician'),
    ], string='Group Type', default='receptionist')
    
class DrogaCity(models.Model):
    _name='droga.city'
    name=fields.Char(string="City")
    region=fields.Many2one('res.region',string="Region",required=True)

class DrogaRegion(models.Model):
    _name='res.region'
    # physio=fields.Many2one('droga.physio', string="droga physio")
    name=fields.Char(string="Region")
    
class NotebookClass(models.Model):
    _name = 'notebook.class'
    _rec_name = 'time'
    droga_physio_id = fields.Many2one('droga.physio', string="droga physio")
    prescription_paitent_id = fields.Many2one('prescription.paitent', string="Main Class")
    full_name=fields.Char(related='droga_physio_id.full_name', string='Full name') 
    register_date = fields.Date(related='droga_physio_id.register_date', string='Register Date')
    phone=fields.Char(related='droga_physio_id.phone',string="Phone" )
    # city=fields.Char(related='droga_physio_id.city',string="City")
    subcity=fields.Selection(related='droga_physio_id.subcity',string="Subcity")
    wereda=fields.Char(related='droga_physio_id.wereda',string="Wereda")

    droga_medical_id = fields.Many2one('droga.medicalcertifcates', string="droga medical Certifcate")
    birth_date_1 = fields.Date(related='droga_medical_id.birth_date', string="Birth")
    con=fields.Many2one(related='droga_medical_id.time_1' , string="cond")

    office_tel=fields.Char(related='droga_physio_id.office_tel',string="Office Tell")

    refered_by=fields.Many2one(comodel_name="hr.employee",string="Refered By")
    # refered_by=fields.Char(related='droga_physio_id.refered_by',string="Refered By")
    house_no=fields.Char(related='droga_physio_id.house_no',string="House No.")
    tin_no=fields.Char(related='droga_physio_id.tin_no',string="Tin No.")
    
    customer_class_id = fields.Many2one('customer.class', string="customer class")
    print_date = fields.Date(string="Print Date")
    time=fields.Datetime("Date and Time")
   
    remark=fields.Selection([('arrived','Arrived'),('holiday','Holiday'),('absent','Absent'),('reschedule','Reschedule')],"Remark")
    service_type=fields.Selection([('club foot','Club Foot'),('eval','Eval'),('general physical teraphy','General Physical Teraphy'),('speech teraphy','Speech Teraphy')])
    price=fields.Char("Price")
    paid_Amount=fields.Char("Paid Amount")
    condition=fields.Selection([('ankle','Ankle'),('cervical','Cervical'),('elbow','Elbow'),('elbow wrist','Elbow Wrist'),('hand','Hand'),('knee','Knee'),('lumber','Lumber'),('neuro doc','Nuro Doc'),('neuro pt','Nuro PT'),('post strock','Post Strok'),('shoulder','Shoulder'),('thoractic','Thoractic'),('wrist','Wrist')],"Condition")

    attachment = fields.Binary(string= 'Attachment')
 
    employee_name=fields.Char("Employee Name")
    profession=fields.Char("Profession")
    employee_id=fields.Char("Employee Id")
    
    birth_date = fields.Date('Birth Date')
    age=fields.Integer("Age", compute="_calculate_age")
   
    sex=fields.Selection([('male','Male'),('female','Female')],"Gender")

    sequence_no = fields.Char(related='droga_physio_id.sequence_no', string='Sequence Number', readonly=True)
    
    


    @api.depends('birth_date')
    def _calculate_age(self):
        for records in self:
            age=0
            
            birth_date=records.birth_date
            current_date=datetime.today().date()
            if birth_date:
                age=(current_date-birth_date)/timedelta(days=365)
            records.age=age



class CustomerClass(models.Model):
    
    _name = 'customer.class'
    _rec_name = 'company_name'
    _inherit = ['mail.thread', 'mail.activity.mixin', 'image.mixin']
    droga_physio_id = fields.One2many('droga.physio', string="droga physio",inverse_name="physio_custoemer")
    # Service_id = fields.Integer(String ='ID')
    # customer = fields.Char(string="Custom" )
    # res.user sholud sbstituted b
    

    company_name = fields.Char(String = 'Company Name')
    company_grade = fields.Char(String="Company Grade")
    tin_no = fields.Char(string="Tin No")
    contract=fields.Many2one(comodel_name="droga.contract",string="contract") 


    area = fields.Char(string="Area")
    location = fields.Char(string="Location")

    employee_name=fields.Char("Employee Name")
    profession=fields.Char("Profession")
    employee_id=fields.Char("Employee Id")
    birth_date = fields.Date('Birth Date')
    age=fields.Integer("Age", compute="_calculate_age")

    sex=fields.Selection([('male','Male'),('female','Female')],"Gender")

    phone =fields.Char("Phone")
    mobile = fields.Char("Mobile")

    is_individual = fields.Boolean(string='Individual', default=True)
    is_company = fields.Boolean(string='Company', default=False)

    sequence_no = fields.Char(string='Sequence Number', readonly=True, copy=False, default=lambda self: _('New'))

    notebook_ids_sesstion = fields.One2many('notebook.class', 'customer_class_id', string="Notebook")
    
    notebook_ids_employee = fields.One2many('notebook.class', 'customer_class_id', string="Notebook")
    company_id=fields.One2many(comodel_name="droga.physio",inverse_name="organization",string="Company")

    @api.depends('birth_date')
    def _calculate_age(self):
        for records in self:
            age=0
            
            birth_date=records.birth_date
            current_date=datetime.today().date()
            if birth_date:
                age=(current_date-birth_date)/timedelta(days=365)
            records.age=age
   
    @api.model
    def create(self, vals):

        # if vals.get('sequence_no', _('New')) == _('New'):
        #     vals['sequence_no'] = self.env['ir.sequence'].next_by_code('seq_droga_physio') or _('New')
        # result = super(DrogaShareHolder, self).create(vals)
        # return result
        if vals.get('sequence_no', _('New')) == _('New'):
            sequence = self.env['ir.sequence'].next_by_code('customer.class') or _('New')
            vals['sequence_no'] = sequence
        result = super(CustomerClass, self).create(vals)
        return result

    @api.onchange('is_individual')
    def _onchange_individual(self):
        if self.is_individual:
            self.is_company = False

    @api.onchange('is_company')
    def _onchange_company(self):
        if self.is_company:
            self.is_individual = False
 
class Exercisenote(models.Model):
    
    _name="exercise.note"
    _rec_name="patient_name"
    _inherit = ['mail.thread', 'mail.activity.mixin', 'image.mixin']

    noteexamin=fields.Many2one(comodel_name="exercise.exercise",string="Exerc")
    patient_name=fields.Char(related='patient_mrn.full_name',string="Patient Name")
    patient_mrn=fields.Many2one(related='noteexamin.mrn',string="MRN")
    exe_name = fields.Html(related='noteexamin.exercise_name', string='Exercise Name')
    assigned_to_me = fields.Boolean(string="Assigned to Me", default=False)
    assigned_nurse = fields.Many2one(comodel_name="res.users", string="Assigned Nurse", readonly=True, store=True)
    due_date = fields.Date('Due Date')
    @api.onchange('assigned_to_me')
    def _onchange_assigned_to_me(self):
        if self.assigned_to_me and not self.assigned_nurse:
            # Set the assigned nurse to the logged-in user if not already assigned
            self.assigned_nurse = self.env.user
        elif not self.assigned_to_me:
            # Reset the assigned nurse field when the toggle is turned off
            self.assigned_nurse = False

    @api.depends('assigned_to_me')
    def _compute_assigned_to_me_readonly(self):
        for record in self:
            record.assigned_to_me_readonly = record.assigned_to_me

    assigned_to_me_readonly = fields.Boolean(compute='_compute_assigned_to_me_readonly', string="Assigned to Me Readonly")

    @api.model
    def create(self, vals_list):
        records = super(Exercisenote, self).create(vals_list)
        for record in records:
            if record.assigned_to_me:
                # Set the assigned nurse to the logged-in user if not already assigned
                record.assigned_nurse = self.env.user
        return records

    def write(self, vals):
        if 'assigned_to_me' in vals:
            # Update the assigned nurse field when the toggle is changed
            if vals['assigned_to_me'] and not self.assigned_nurse:
                vals['assigned_nurse'] = self.env.user.id
            elif not vals['assigned_to_me']:
                # Reset the assigned nurse field when the toggle is turned off
                vals['assigned_nurse'] = False
        return super(Exercisenote, self).write(vals)
#    maria code
class Appointment (models.Model): 
     
    _name="appointment.set"
    _rec_name='mrn'
    _inherit = ['mail.thread', 'mail.activity.mixin', 'image.mixin']
    _order = "create_date desc"

    start_date=fields.Datetime(" Date of Appointment") 
    # end_date= fields.Datetime("End Date") 
    # clinician=fields.Char("Clinician") 
    clinician1=fields.Many2one(comodel_name="hr.employee",string="Clincian",domain="[('clinicians', '=', True)]") 
    # mrn=fields.Integer("MRN") 
    appointment=fields.Many2one(comodel_name="examination.form",string="Examination")
    # mrn=fields.Many2one(comodel_name="droga.physio",string="MRN") 
    clincian=fields.Many2one(related='appointment.clinician1',string="Clincian") 
    mrn=fields.Many2one ( related='appointment.mrn',string="MRN")

    name=fields.Char(related='mrn.full_name',string="Patients Name") 
    phone=fields.Char(related='mrn.phone',string="Phone")
    status = fields.Selection([ ('scheduled', 'Scheduled'),('arrived', 'Arrived'),('reschduled', 'Reschduled'), ('cancel', 'Cancelled')], default='arrived', index=True, required=True, string="Status")
    dur_ation=fields.Float(string="Duration")
    # state_ap=fields.Selection(related='appointment.state',string="State")

    company_id = fields.Many2one('res.company', required=True , default=lambda  self: self.env.user.company_id)
    

    @api.model
    def _search(self, args, offset=0, limit=None, order=None, count=False, access_rights_uid=None):
        user = self.env['res.users'].browse(self.env.uid)
        if self.env.context.get('user_company_id'):
            user_company_id = user.company_id.id
            args += ['|', ('company_id', '=', False), ('company_id', 'child_of', user_company_id)]
        return super(Appointment, self)._search(args, offset=offset, limit=limit, order=order, count=count, access_rights_uid=access_rights_uid)

    def presc(self):
        return {
            'name': 'Prescription',
            'view_type': 'form',
            'view_mode': 'form',
            'res_model': 'prescription.paitent',
            'view_id': False,
            'type': 'ir.actions.act_window',
            'context': {
                'default_mrn': self.id,
            },
            'domain':
                ([('mrn', '=', self.id)])
        }

class NursingEvaluation(models.Model):
    _name = 'nursing.evaluation'
    _rec_name = 'patient_name'
    _inherit = ['mail.thread', 'mail.activity.mixin', 'image.mixin']
    _order = "create_date desc"

    mrn = fields.Many2one( string="MRN", related='appointment_nursing.mrn',store=True)
    clinician_id = fields.Many2one( string="Clinician", related='appointment_nursing.clinician1', readonly=True)
    patient_name =fields.Char(related="mrn.full_name",string="Patient Name",store=True, tracking=True)
    #clinician_id = fields.Many2one('hr.employee', string="Clinician", readonly=True)
    # patient_name = fields.Char(related="mrn.patient_name", string="Patient Name", readonly=True)
    Nurses=fields.Many2one(comodel_name="hr.employee",string="Avialiable Nurse") 

    age = fields.Integer(string='Age', related='appointment_nursing.age',store=True, tracking=True)
    chief_complaint = fields.Text(string='Chief Complaint', tracking=True)
    neck = fields.Boolean(string='Neck', default=False, tracking=True)
    shoulder = fields.Boolean(string='Shoulder', default=False, tracking=True)
    elbow = fields.Boolean(string='Elbow', default=False, tracking=True)
    wrist = fields.Boolean(string='Wirst', default=False, tracking=True)
    hand = fields.Boolean(string='Hand', default=False, tracking=True)
    chiled_age_nursing = fields.Integer(related="appointment_nursing.chiled_age",string="Chiled Age in Month", tracking=True)
    chiled_age_year_nusing = fields.Integer(related="appointment_nursing.chiled_age_year",string="Chiled Age in Year", tracking=True)
    # clinician_id = fields.Many2one('hr.employee', string="Clinician")
    fingers = fields.Boolean(string='Fingers', default=False, tracking=True)
    fingers_R = fields.Boolean(string="fingers Right", tracking=True)
    fingers_L = fields.Boolean(string='fingers Left', tracking=True)
    show_fingers_details = fields.Boolean(string='Show Fingers Details', compute='_compute_show_fingers_details', store=False, tracking=True)



    appointment_nursing = fields.Many2one('examination.form', string="Appointment", ondelete="cascade")
    
    company_id = fields.Many2one('res.company', required=True , default=lambda  self: self.env.user.company_id)
    

    @api.model
    def _search(self, args, offset=0, limit=None, order=None, count=False, access_rights_uid=None):
        user = self.env['res.users'].browse(self.env.uid)
        if self.env.context.get('user_company_id'):
            user_company_id = user.company_id.id
            args += ['|', ('company_id', '=', False), ('company_id', 'child_of', user_company_id)]
        return super(NursingEvaluation, self)._search(args, offset=offset, limit=limit, order=order, count=count, access_rights_uid=access_rights_uid)

    @api.depends('fingers')
    def _compute_show_fingers_details(self):
        for record in self:
            record.show_fingers_details = record.fingers

    @api.onchange('fingers')
    def _onchange_fingers(self):
        if not self.fingers:
            self.fingers = False


    back_pain = fields.Boolean(string='Back Pain', default=False, tracking=True)
    back_pain_u = fields.Boolean(string='Back Pain Upper', tracking=True)
    back_pain_m = fields.Boolean(string="Back Pain Mid", tracking=True)
    back_pain_L = fields.Boolean(string='Back Pain Lower', tracking=True)
    show_back_pain_details = fields.Boolean(string='Show Back Pain Details', compute='_compute_show_back_pain_details', store=False, tracking=True)

    @api.depends('back_pain')
    def _compute_show_back_pain_details(self):
        for record in self:
            record.show_back_pain_details = record.back_pain

    @api.onchange('back_pain')
    def _onchange_back_pain(self):
        if not self.back_pain:
            self.back_pain = False



    hip = fields.Boolean(string='Hip', default=False, tracking=True)
    knee = fields.Boolean(string='Knee', default=False, tracking=True)
    ankle = fields.Boolean(string='Ankle', default=False, tracking=True)
    foot = fields.Boolean(string='Foot', default=False, tracking=True)
 

    toes = fields.Boolean(string='Toes', default=False, tracking=True)
    toes_r = fields.Boolean(string='Toes Right', tracking=True)   
    toes_l = fields.Boolean(string="Toes Left", tracking=True)
    show_toes_details = fields.Boolean(string='Show Back Pain Details', compute='_compute_show_toes_details', store=False, tracking=True)

    @api.depends('toes')
    def _compute_show_toes_details(self):
        for record in self:
            record.show_toes_details = record.toes

    @api.onchange('toes')
    def _onchange_toes(self):
        if not self.toes:
            self.toes = False


    hemi = fields.Boolean(string='Hemi(R)', default=False, tracking=True)
    hemi_L = fields.Boolean(string='Hemi(L)', default=False, tracking=True)
    paraplegia = fields.Boolean(string='Paraplegia', default=False, tracking=True)
    quadriplegia = fields.Boolean(string='Quadriplegia', default=False, tracking=True)
    sci = fields.Boolean(string='Sci', default=False, tracking=True)

    hypertension = fields.Boolean(string='Hypertension', default=False, tracking=True)
    diabetes = fields.Boolean(string='Diabetes', default=False, tracking=True)
    heart_disease = fields.Boolean(string='Heart Disease', default=False, tracking=True)
    kidney_disease = fields.Boolean(string='Kidney Disease', default=False, tracking=True)
    blood_disorder = fields.Boolean(string='Blood Disorder', default=False, tracking=True)
    gi_disorder = fields.Boolean(string='Gi Disorder', default=False, tracking=True)
    lung_cancer = fields.Boolean(string='Lung Cancer', default=False, tracking=True)
    cancer = fields.Boolean(string='Cancer', default=False, tracking=True)

    blood_pressure = fields.Char(string='Blood Pressure', tracking=True)
    heart_rate = fields.Char(string='Heart Rate', tracking=True)
    respiratory_rate = fields.Char(string='Respiratory Rate', tracking=True)
    oxygen_saturation = fields.Char(string='Oxygen Saturation', tracking=True)
    pulse_rate = fields.Char(string='Pulse Rate', tracking=True)
    temprature = fields.Char(string='Temprature', tracking=True)
    related_disease = fields.Text(string='Related Disease', tracking=True)
    allergies = fields.Boolean(string='Allergies', default=False, tracking=True)
    a_yes = fields.Boolean(string='Yes',  tracking=True)   
    a_no = fields.Boolean(string="No", tracking=True)
    a_text = fields.Char(string="Note", tracking=True)
    body_type = fields.Char(string='Body Type', tracking=True)
    any_assistive = fields.Char(string='Any Assistive Device', tracking=True)
    medication = fields.Char(string='Medication', tracking=True)

    @api.onchange('a_yes')
    def _onchange_a_yes(self):
        if self.a_yes:
            self.a_no = False

    @api.onchange('a_no')
    def _onchange_a_no(self):
        if self.a_no:
            self.a_yes = False

    @api.constrains('a_yes', 'a_no')
    def _check_yes_no_selection(self):
        for record in self:
            if record.a_yes and record.a_no:
                raise ValidationError("Both 'Yes' and 'No' cannot be selected simultaneously.")
    show_allergies_details = fields.Boolean(string='Show allergies Details', compute='_compute_show_allergies_details', store=False, tracking=True)

    @api.depends('allergies')
    def _compute_show_allergies_details(self):
        for record in self:
            record.show_allergies_details = record.allergies

    @api.onchange('allergies')
    def _onchange_allergies(self):
        if not self.allergies:
            self.allergies = False

    weight = fields.Float(string='Weight (kg)', tracking=True)
    height = fields.Float(string='Height (m)', tracking=True)
    bmi = fields.Float(string='BMI', compute='_compute_bmi', store=True , tracking=True)


    waist_circumference = fields.Float(string='Waist Circumference (cm)', tracking=True)
    hip_circumference = fields.Float(string='Hip Circumference (cm)', tracking=True)
    whr = fields.Float(string='Waist to Hip Ratio', compute='_compute_whr', store=True, tracking=True)

    
    
    blood_glucose_level = fields.Boolean(string='Blood Glucose', default=False, tracking=True)
    blood_glucose_level_rbs = fields.Boolean(string="Blood Glucose(RBS)", tracking=True)
    blood_glucose_level_fbs = fields.Boolean(string='Blood Glucose(FBS)', tracking=True)
    show_blood_glucose_details = fields.Boolean(string='Show Blood Glucose Details', compute='_compute_show_blood_glucose_details', store=False, tracking=True)

    @api.depends('blood_glucose_level')
    def _compute_show_blood_glucose_details(self):
        for record in self:
            record.show_blood_glucose_details = record.blood_glucose_level

    @api.onchange('blood_glucose_level')
    def _onchange_blood_glucose_level(self):
        if not self.blood_glucose_level:
            self.blood_glucose_level = False

    @api.depends('waist_circumference', 'hip_circumference')
    def _compute_whr(self):
        for record in self:
            if record.waist_circumference and record.hip_circumference:
                record.whr = record.waist_circumference / record.hip_circumference
            else:
                record.whr = 0.0

    @api.depends('weight', 'height')
    def _compute_bmi(self):
        for record in self:
            if record.weight and record.height:
                record.bmi = record.weight / (record.height ** 2)
            else:
                record.bmi = 0.0
    
    assigned_to_me = fields.Boolean(string="Assigned to Me", default=False)
    assigned_nurse = fields.Many2one(comodel_name="res.users", string="Assigned Nurse", readonly=True, store=True)

    @api.onchange('assigned_to_me')
    def _onchange_assigned_to_me(self):
        if self.assigned_to_me and not self.assigned_nurse:
            # Set the assigned nurse to the logged-in user if not already assigned
            self.assigned_nurse = self.env.user
        elif not self.assigned_to_me:
            # Reset the assigned nurse field when the toggle is turned off
            self.assigned_nurse = False

    @api.depends('assigned_to_me')
    def _compute_assigned_to_me_readonly(self):
        for record in self:
            record.assigned_to_me_readonly = record.assigned_to_me

    assigned_to_me_readonly = fields.Boolean(compute='_compute_assigned_to_me_readonly', string="Assigned to Me Readonly")

    @api.model
    def create(self, vals_list):
        records = super(NursingEvaluation, self).create(vals_list)
        for record in records:
            if record.assigned_to_me:
                # Set the assigned nurse to the logged-in user if not already assigned
                record.assigned_nurse = self.env.user
        return records

    def write(self, vals):
        if 'assigned_to_me' in vals:
            # Update the assigned nurse field when the toggle is changed
            if vals['assigned_to_me'] and not self.assigned_nurse:
                vals['assigned_nurse'] = self.env.user.id
            elif not vals['assigned_to_me']:
                # Reset the assigned nurse field when the toggle is turned off
                vals['assigned_nurse'] = False
        return super(NursingEvaluation, self).write(vals)

class BehaviourAssessment(models.Model):
    _name = 'behaviour.assessment'
    _rec_name = 'patient_name_behaviour'
    _inherit = ['mail.thread', 'mail.activity.mixin', 'image.mixin']
    _order = "create_date desc"
    

    exa_behaviour = fields.Many2one('examination.form', string="Examination Behaviour", ondelete="cascade")
    mrn_behaviour = fields.Many2one( string="MRN", related='exa_behaviour.mrn',store=True)
    clinician_id_behaviour = fields.Many2one( string="Clinician", related='exa_behaviour.clinician1', readonly=True)
    patient_name_behaviour =fields.Char(related="mrn_behaviour.full_name",string="Patient Name",store=True, tracking=True)
    chiled_age_behaviour = fields.Integer(related="exa_behaviour.chiled_age",string="Chiled Age in Month", tracking=True)
    chiled_age_year_behivour = fields.Integer(related="exa_behaviour.chiled_age_year",string="Chiled Age in Year", tracking=True)
    b_chiled = fields.One2many('chiled.behavior.tag','chiled_b',string="Child Behaviour", tracking=True)
    b_chiled_2 = fields.One2many('chiled.behavior.tag2','chiled_b_2',string="Child Behaviour 2", tracking=True)
    b_chiled_3 = fields.One2many('chiled.behavior.tag3','chiled_b_3',string="Child Behaviour 3", tracking=True)
    b_chiled_4 = fields.One2many('chiled.behavior.tag4','chiled_b_4',string="Child Behaviour 4", tracking=True)
    b_chiled_5 = fields.One2many('chiled.behavior.tag5','chiled_b_5',string="Child Behaviour 5", tracking=True)

    def compute_create_attension(self):
        child_att = self.env['chiled.behavior.config'].search([('catagories_assess', '=', 'att')])
        for record in child_att:
            check_att = self.env['chiled.behavior.tag'].search([('chiled_assesment', '=', record.name), ('chiled_b', '=', self.id)])
            if not check_att:
                self.env['chiled.behavior.tag'].create({
                    'chiled_assesment': record.name,
                    'chiled_b': self.id,
                    
                })
    def compute_create_attension_2(self):
        child_att_2 = self.env['chiled.behavior.config'].search([('catagories_assess', '=', 'rea')])
        for record in child_att_2:
            check_att_2 = self.env['chiled.behavior.tag2'].search([('chiled_assesment_2', '=', record.name), ('chiled_b_2', '=', self.id)])
            if not check_att_2:
                self.env['chiled.behavior.tag2'].create({
                    'chiled_assesment_2': record.name,
                    'chiled_b_2': self.id,
                    
                })

    def compute_create_attension_3(self):
        child_att_3 = self.env['chiled.behavior.config'].search([('catagories_assess', '=', 'ma')])
        for record in child_att_3:
            check_att_3 = self.env['chiled.behavior.tag3'].search([('chiled_assesment_3', '=', record.name), ('chiled_b_3', '=', self.id)])
            if not check_att_3:
                self.env['chiled.behavior.tag3'].create({
                    'chiled_assesment_3': record.name,
                    'chiled_b_3': self.id,
                    
                })

    def compute_create_attension_4(self):
        child_att_4 = self.env['chiled.behavior.config'].search([('catagories_assess', '=', 'lan')])
        for record in child_att_4:
            check_att_4 = self.env['chiled.behavior.tag4'].search([('chiled_assesment_4', '=', record.name), ('chiled_b_4', '=', self.id)])
            if not check_att_4:
                self.env['chiled.behavior.tag4'].create({
                    'chiled_assesment_4': record.name,
                    'chiled_b_4': self.id,
                    
                })

    def compute_create_attension_5(self):
        child_att_5 = self.env['chiled.behavior.config'].search([('catagories_assess', '=', 'oth')])
        for record in child_att_5:
            check_att_5 = self.env['chiled.behavior.tag5'].search([('chiled_assesment_5', '=', record.name), ('chiled_b_5', '=', self.id)])
            if not check_att_5:
                self.env['chiled.behavior.tag5'].create({
                    'chiled_assesment_5': record.name,
                    'chiled_b_5': self.id,
                    
                })

class PhysicalTherapy(models.Model):
    _name = 'physical.therapy'
    _rec_name = 'patient_name_physical'
    _inherit = ['mail.thread', 'mail.activity.mixin', 'image.mixin']
    _order = "create_date desc"

    exa_physical = fields.Many2one('examination.form', string="Examination Physical", ondelete="cascade")
    mrn_physical = fields.Many2one( string="MRN", related='exa_physical.mrn',store=True)
    clinician_id_physical = fields.Many2one( string="Clinician", related='exa_physical.clinician1', readonly=True)
    patient_name_physical =fields.Char(related="mrn_physical.full_name",string="Patient Name",store=True, tracking=True)
    chiled_age_physical = fields.Integer(related="exa_physical.chiled_age",string="Chiled Age in Month", tracking=True)
    chiled_age_year_physical = fields.Integer(related="exa_physical.chiled_age_year",string="Chiled Age in Year", tracking=True)


    physio_diagnosis = fields.Html(string='Diagnosis', tracking=True)
    current_motor_age = fields.Char(string='Current Motor Age', tracking=True)
    major_problem = fields.Html(string='Major Problem Identified On Recent Physical Evaluation', tracking=True)
    current_physical = fields.Html(string='Current Physical Functional Limitation', tracking=True)
    recent_physical = fields.Html(string='Recent Physical Therapy Intervention Under', tracking=True)
    future_intervention = fields.Html(string='Future Intervention Recommendation', tracking=True)
    precaution = fields.Html(string='Precaution', tracking=True)
    indication = fields.Html(string='Indication', tracking=True)
    contraindication = fields.Html(string='Contraindication', tracking=True)


class PhysicanConsultation(models.Model):
    _name = 'physician.consultation'
    _rec_name = 'patient_name_physician'
    _inherit = ['mail.thread', 'mail.activity.mixin', 'image.mixin']
    _order = "create_date desc"

    exa_physician_cons = fields.Many2one('examination.form', string="Examination Physical", ondelete="cascade")
    mrn_physician = fields.Many2one( string="MRN", related='exa_physician_cons.mrn',store=True)
    clinician_id_physician = fields.Many2one( string="Clinician", related='exa_physician_cons.clinician1', readonly=True)
    patient_name_physician =fields.Char(related="mrn_physician.full_name",string="Patient Name",store=True, tracking=True)
    chiled_age_physician = fields.Integer(related="exa_physician_cons.chiled_age",string="Chiled Age in Month", tracking=True)
    chiled_age_year_physician = fields.Integer(related="exa_physician_cons.chiled_age_year",string="Chiled Age in Year", tracking=True)

    physican_diagnosis_physician_con = fields.Html(string='Diagnosis', tracking=True)
    treatment_given_physician_con = fields.Html(string='Treatment Given', tracking=True)
    reasone_for_consultation_physician_con = fields.Html(string='Reason For Consultation', tracking=True)
    physician_feedback_physician_con = fields.Html(string='Physician Feedback', tracking=True)

class SetReminder (models.Model): 
     
    _name="set.reminder" 
    date=fields.Datetime("Date") 
    birth_date=fields.Date("Birth Date") 
    age=fields.Integer("Age") 
    appointed=fields.Many2one(comodel_name="hr.employee",string="Appointed To")    
    mrn=fields.Many2one(comodel_name="droga.physio",string="MRN") 
    name=fields.Many2one(comodel_name="droga.physio",string="Patients Name") 
    phone=fields.Char("Phone") 
    reason = fields.Text(string="Reason") 
     
    # def _compute_commercial_partner(self): 
    #     for records in self: 
    #         a=0 
    # appointment_ids = fields.One2many('cancle.appointment.wizard' , 'reason_id') 
    # reminider_ids = fields.One2many('set', 'set_reminder_id') 
class reminder(models.Model): 
    _name="set" 
    set_reminder_id = fields.Many2one( 
        'set.reminder', 
        string='set_reminder', 
        ) 
    date=fields.Date("Date") 
    appointed=fields.Char("Appointed To")    
    mrn=fields.Integer("MRN") 
    name=fields.Char("Patients Name") 
    phone=fields.Char("Phone") 
     
class CancelAppointmentWizard(models.TransientModel): 
    _name="cancle.appointment.wizard" 
    _description="Cancel Appointment Wizard" 
     
    appointment_id=fields.Many2one('set.reminder') 
    reason_id = fields.Text(string="Reason") 
     
    def action_cancel(self): 
        return 

class prescription(models.Model): 
    _name="prescription.paitent" 
    _rec_name="patient_name"
    _inherit = ['mail.thread', 'mail.activity.mixin', 'image.mixin']
    notebook_ids = fields.One2many('notebook.class', 'prescription_paitent_id', string="Notebook") 
    # prescription_no = fields.Integer('no')
    patient_name =  fields.Many2one(comodel_name='droga.physio', string='Patient')
    full_name = fields.Char(related='patient_name.full_name', string='Full name')
    sex = fields.Selection(related='patient_name.sex' ,string="Gender")
    age = fields.Integer(related='patient_name.age' , string='Age')

    weight = fields.Integer(string='Weight')
    # Region = fields.Char(string='Region')
    town = fields.Char(string='Town')
    woreda = fields.Char(related='patient_name.wereda' ,string='Woreda')
    kebele = fields.Char(string='Kebele')
    house_no = fields.Char(related='patient_name.house_no' ,string='House No')
    tel_no = fields.Char(related='patient_name.office_tel' ,string='Tel No')
    inpatient = fields.Boolean(string='Inpatient')
    outpatient = fields.Boolean(string='Outpatient')
    Diagnosis = fields.Char(string='Diagnosis')
    # pre_session = fields.One2many('note.preclass' ,'prej', string='Notebook')
    birth_date=fields.Date("Birth Date")
    prescriber =fields.Many2one(related='patient_name.appointed_to',string="Prescriber")

    @api.depends("birth_date") 
    def _calculate_age(self): 
        for records in self: 
            age=0 
            birth_date=records.birth_date 
            current_date = datetime.today().date() 
            # current_date=datetime.date().today() 
            if birth_date: 
                age=(current_date-birth_date)/timedelta(days=365) 
            records.age=age 
    age=fields.Integer(string="Age", compute = "_calculate_age")


class ProductCalculate(models.Model):
    _name = 'product.calculate.product'
    _rec_name = 'product_id'
    _description = 'Product Calculate'

    product_id = fields.Many2one(comodel_name="product.template", string="Product")
    quantity = fields.Float(string="Quantity")
    total = fields.Float(string="Total", compute="_calculate_total")
    # tax_ids = fields.Many2many(comodel_name="account.tax", string="Tax")
    unit_price = fields.Float(string="Unit Price", compute="_calculate_unit_price")
    pro_pro = fields.Many2one('examination.form', string='Sessions')

    @api.depends('product_id.list_price')
    def _calculate_unit_price(self):
        for record in self:
            record.unit_price = record.product_id.list_price

    @api.depends('unit_price', 'quantity')
    def _calculate_total(self):
        for record in self:
            record.total = record.unit_price * record.quantity
    @api.model
    def get_total_price_of_all_products(self):

        product_calculate_records = self.search([])
        # Sum up the 'total' field of each record
        total_price = sum(record.total for record in product_calculate_records)
        return total_price

class notepreclass(models.Model):

    _name = 'note.preclass'
    _rec_name = 'drug_name'
    _description = 'Note Book'
    drug_name = fields.Html(string="Drug Name, Strength, DosagefromDose, Frequency, Duration, Quantity, How to use & other Info")
    price = fields.Char(string="Price(dispenses use only)") 
    prej = fields.Many2one('examination.form', string='Sessions')

class recommendation(models.Model):

    _name = 'clinician.recommendation'
    _rec_name = 'clinician_recommendation_hand_wrist_elbow'
    _description = 'Note Book for clinician recommendation of elbow'
    clinician_recommendation_hand_wrist_elbow = fields.Selection([('modalities','Modalities as Indicated'),('postural_education','Postural Education and Awareness Training'),('soft_tissue','Soft Tissue Mobilization'),('scar_mob','Scar Mobilization'),('joint_mob','Joint Mobilization'),('splinting','Splinting'),('neural_mob','Neural Mobilization'),('upper_extremity','Upper Extremity Strengthening'),('general_cardio','General/Cardiovascular conditioning'),('therapeutic_exrecise','Therapeutic Exercise'),('imaging_study','Image Studies'),('trigger_point','Trigger Point Injection'),('interaarticular','Interaarticular Joint Injection'),('dry_needling','Dry Needling Procedure')],string='Clinician recommendation', tracking=True)
    remark_hand_wrist_elbow_clin_6 = fields.Text(string='Remark', tracking=True)
    pres_freq = fields.Char(string='Prescribed Frequency',tracking=True)
    time_per_week = fields.Char(string = 'Time Per Week',tracking=True)
    rom_recommendation = fields.Many2one('examination.form', string='Recommendation Exam', tracking=True)
class clinicianimpressionElbow(models.Model):

    _name = 'clinician.impressionelbow'
    _rec_name = 'clinician_imperssion_hand_wrist_elbow'
    _description = 'Note Book for clinician impression of elbow'
    clinician_imperssion_hand_wrist_elbow = fields.Selection([('postural','Postural Imbalance'),('decreased active','Decreased active range of motion'),('decreased passive','Decreased passive range of motion'),('decreased strength','Decreased Strength'),('adaptive shortening','Adaptive Shortening of Muscles'),('adverse neural','Adverse Neural Tension'),('decreased joint','Decreased joint mobility'),('decreased scar','Decreased scar mobility')],string='Clinician Impression', tracking=True)
    remark_hand_wrist_elbow_clin_1 = fields.Text(string='Remark', tracking=True)
    rom_impression = fields.Many2one('examination.form', string='Immpression Exam', tracking=True)

class muscleflexiability(models.Model):

    _name = 'muscle.flexiability'
    _rec_name = 'muscle_fexiability_hand_wrist_elbow'
    _description = 'Muscle Flexiability'
    muscle_fexiability_hand_wrist_elbow = fields.Selection([('normal_flexibility','Normal Flexibility'),('right_wrist_extensors','Right Wrist Extensors'),('left_wrist_extensors','Left Wrist Extensors'),('right_finger_flexors','Right Finger Flexors'),('left_finger_flexor','Left Finger Flexor'),('right_finger_extensors','Right Finger Extensors'),('left_finger_extensors','Left Finger Extensors'),('right_thumb_extensors','Right Thumb Extensors'),('right_thumb_extensors','Left Thumb Extensors')],string='Muscle Flexiability', tracking=True)
    remark_hand_wrist_elbow_clin_2 = fields.Text(string='Remark', tracking=True)
    rom_muscle = fields.Many2one('examination.form', string='Muscle Exam', tracking=True)

class structural(models.Model):

    _name = 'structural.hand'
    _rec_name = 'muscle_fexiability_hand_wrist_elbow'
    _description = 'Muscle Flexiability'
    muscle_fexiability_hand_wrist_elbow = fields.Selection([('no_structure','No Structure abnomalities'),('elbow_flexion','Elbow Flexion Contracture'),('elbow_extension','Elbow Extension Contracture'),('wrist_radial','Wrist Radial Deviation Deformity'),('wrist_ulnar','Wrist Ulnar Deviation Deformity'),('mcp_ulnar','MCP Ulnar Deviation Deformity'),('mcp_radial','MCP Radial Deviation Deformity'),('thumb_cmc','Thumb CMC Subluxation'),('boutonniere_deformity','Boutonniere Deformity'),('mallet_finger','Mallet Finger')],string='Structural', tracking=True)
    remark_hand_wrist_elbow_clin_3 = fields.Text(string='Remark', tracking=True)

    rom_struct = fields.Many2one('examination.form', string='Structural Exam', tracking=True)

class rom(models.Model):

    _name = 'rom.hand'
    _rec_name = 'rom_hand_wrist_elbow_right'
    _description = 'ROM'
    rom_hand_wrist_elbow_right = fields.Selection([
        ('elbow_flex', 'Elbow Flex(N=150°)'),
        ('elbow_extension', 'Elbow Extension(N=0°)'),
        ('suspination', 'Supination (N=80°)'),
        ('pronation', 'Pronation (N=80°)'),
        ('wrist_flexion', 'Wrist Flexion (N=60°)'),
        ('wrist_extension', 'Wrist Extension (N=70°)'),
        ('radial_dev', 'Radial Deviation (N=20°)'),
        ('ulnar_dev', 'Ulnar Deviation (N=30°)'),
        ], string='ROM', tracking=True,ondelete="cascade")

    rom_hand_wrist_elbow_left = fields.Selection([('right','Right'),('left','Left')], string=' Right/Left', tracking=True)
    rom_hand_wrist_elbow_describtion = fields.Text(string='Description', tracking=True)
    remark_hand_wrist_elbow_clin_4 = fields.Text(string='Remark', tracking=True)
    
    rom_exam = fields.Many2one('examination.form', string='Rom Exam', tracking=True)




    # @api.onchange('rom_hand_wrist_elbow_right')
    # def _onchange_rom_hand_wrist_elbow_right(self):
    #     if self.rom_hand_wrist_elbow_right:
      
    #         right_to_left_mapping = {
    #             'elbow_flex': 'elbow_flex_l',
    #             'elbow_extension' : 'elbow_extension_l',
    #             'suspination' : 'suspination_l',
    #             'pronation' : 'pronation_l',
    #             'wrist_flexion' : 'wrist_flexion_l',
    #             'wrist_extension' : 'wrist_extension_l',
    #             'radial_dev' : 'radial_dev_l',
    #             'ulnar_dev' : 'ulnar_dev_l',
                
    #         }
   
    #         self.rom_hand_wrist_elbow_left = right_to_left_mapping.get(self.rom_hand_wrist_elbow_right)

    # @api.onchange('rom_hand_wrist_elbow_left')
    # def _onchange_rom_hand_wrist_elbow_left(self):
    #     if self.rom_hand_wrist_elbow_left:
     
    #         left_to_right_mapping = {
    #             'elbow_flex_l': 'elbow_flex',
    #             'elbow_extension' : 'elbow_extension_l',
    #             'suspination' : 'suspination_l',
    #             'pronation' : 'pronation_l',
    #             'wrist_flexion' : 'wrist_flexion_l',
    #             'wrist_extension' : 'wrist_extension_l',
    #             'radial_dev' : 'radial_dev_l',
    #             'ulnar_dev' : 'ulnar_dev_l',
    #         }
     
    #         self.rom_hand_wrist_elbow_right = left_to_right_mapping.get(self.rom_hand_wrist_elbow_left)

class strength(models.Model):

    _name = 'strength.hand'
    _rec_name = 'strength_hand_wrist_elbow_right'
    _description = 'ROM'
    strength_hand_wrist_elbow_right = fields.Selection([
        ('elbow_extension', 'Elbow Extension'),
        ('elbow_flex', 'Elbow Flex'),
        ('grip_strength', 'Grip Strength'),
        ('radial_deviation', 'Radial Deviation'),
        ('wrist_flexion', 'Wrist Flexion'),
        ('wrist_extension', 'Wrist Extension'),
        ('ulnar_deviation', 'Ulnar Deviation'),
        ], string='Strength', tracking=True,ondelete="cascade")

    strength_hand_wrist_elbow_left = fields.Selection([('right','Right'),('left','Left')], string=' Right/Left', tracking=True)
    rom_hand_wrist_elbow_describtion = fields.Text(string='Description', tracking=True)
    remark_hand_wrist_elbow_clin_5 = fields.Text(string='Remark', tracking=True)
    
    strength_exam = fields.Many2one('examination.form', string='Strength Exam', tracking=True)
    elbow_extension_hand_wris = fields.Selection([('0/5','0/5'),('1/5','1/5'),('1+/5','1+/5'),('2-/5','2-/5'),('2/5','2/5'),('2+/5','2+/5'),('3-/5','3-/5'),('3/5','3/5'),('3+/5','3+/5'),('4-/5','4-/5'),('4/5','4/5'),('4+/5','4+/5'),('5/5','5/5'),('n/t','N/T')],string='Select', tracking=True)
   
class lumbarstrength(models.Model):
    _name ='lumbar.strength'
    _rec_name = 'strength_hand_wrist_elbow_right'
    _description ='Lumbar Strength'

    strength_hand_wrist_elbow_right = fields.Selection([
        ('hip_adduction', 'Hip Adducation'),
        ('knee_flexion', 'Knee Flexion'),
        ('hip_extension', 'Hip Extension'),
        ('hip_flexion', 'Hip Flexion'),
        ('hip_abduction', 'Hip Abduction'),
  
        ], string='Strength', tracking=True,ondelete="cascade")  

    strength_lumbar = fields.Selection([('right','Right'),('left','Left')], string=' Right/Left', tracking=True)
    remark_hand_wrist_elbow_clin_6= fields.Text(string='Remark', tracking=True)
    lumbar_selection = fields.Selection([('0/5','0/5'),('1/5','1/5'),('1+/5','1+/5'),('2-/5','2-/5'),('2/5','2/5'),('2+/5','2+/5'),('3-/5','3-/5'),('3/5','3/5'),('3+/5','3+/5'),('4-/5','4-/5'),('4/5','4/5'),('4+/5','4+/5'),('5/5','5/5'),('n/t','N/T')],string='Select', tracking=True)

   

    lumbar_strength_exam = fields.Many2one('examination.form', string='Lumbar Strength Exam', tracking=True)
   

class lumbarprotect(models.Model):
    _name = 'lumbar.protective'
    _rec_name = 'lumbar_mech'
    _description = 'Lumbar protective'

    lumbar_mech = fields.Selection([('multifidus muscle','Multifidus Muscle Recuitment'),('transversus abdominus','Transversus Abdomenus Muscle Recruitment'),('glueteal muscle','Glueteal Muscle Recruitment')],string='Lumbar Protective Mechanism', tracking=True)
    lumbar_protective = fields.Selection([('poor','Poor'),('fair','Fair'),('good','Good'),('normal','Normal')],string='Status', tracking=True)

    lumbar_protect_exam = fields.Many2one('examination.form', string='Lumbar Protect Exam', tracking=True)

class lumbarrom(models.Model):
    _name = 'lumbar.rom'
    _rec_name = 'rom_lumbar'
    _description = 'Lumbar Rom'

    rom_lumbar = fields.Selection([('Forward Bend','Forward Bend(N=60°)'),('backward bend','Backward Bend(N=25°)'),('side bend','Side Bend(l)(N=25°)'),('side bend right','Side Bend(R)(N=25°)')],string='Rom Lumbar', tracking=True)
    remark_lum = fields.Text(string='Remark', tracking=True)

    lumbar_rom_exam = fields.Many2one('examination.form', string='Lumbar Rom Exam', tracking=True)

class lumbarbio(models.Model):
    _name = 'lumbar.bio'
    _rec_name = 'bio_lumbar'
    _description = 'Lumbar Bio'

    bio_lumbar = fields.Selection([('normal mobi','Normal Mobility'),('stiff through','Stiff Throughout'),('restricted right','Restricted Right Rotation'),('restricted left','Restricted Left Rotation')],string='Biomechanical Lumbar Spine', tracking=True)

    remark_lum_bio = fields.Text(string='Remark', tracking=True)

    lumbar_bio_exam = fields.Many2one('examination.form', string='Lumbar Rom Exam', tracking=True)

class lumbarextremity(models.Model):
    _name = 'lumbar.exterimity'
    _rec_name = 'extermity_lumbar'
    _description = 'Lumbar Extermity'
    extermity_lumbar = fields.Selection([('gastroc','Gastroc Soleus'),('quadricps','Quadriceps'),('lliacus','lliacus/psoas'),('hamstrings','Hamstrings'),('gluteus','Gluteus Max'),('pinformis','Pinformis'),('hip adductors','Hip Adductors')],string=' Lower Extermity Flexiability', tracking=True)

    remark_lum_exterm = fields.Text(string='Remark', tracking=True)

    lumbar_exterm_exam = fields.Many2one('examination.form', string='Lumbar Rom Exam', tracking=True)

class clinicianimpressionlumbar(models.Model):

    _name = 'clinician.impressionlumbar'
    _rec_name = 'clinician_imperssion_lumbar'
    _description = 'clinician impression of lumbar'
    clinician_imperssion_lumbar = fields.Selection([('functional instability','Functional Insatbility of Lumbopelvic Region'),('lumbar spine','Lumbar Spine Disfunction'),('decreased lumbar spine','Decreased Lumbar Spine Active Range of Motion'),('Lumbar Hipermobility','Lumbar Hipermobility'),('facet joint','Facet Hypermobilty Lumbar/Thoracic Spine'),('s-1 disfunction','S-1 Disfunction With Possible Hypermobility/With pubic joint involvement'),('sensetive thoracic','Sensitive Thoracic and Lumbar Vertabrae to p-a Oscillations'),('rotoscolo','Rotoscoliosis'),('hip capsule','Hip Capsule Restriction'),('hip flexior','Hip Flexior Muscle Disfunction'),('soft tissue','Soft Tissue Disfunction of Pelvic Girul Musculature And Erector Spine'),('hypertonic musculature','Hypertonic Musculature'),('decrease lower','Decrease Lower Exterimity Muscle Lengths'),('Lower Exterimity Muscle weakness','Lower Exterimity Muscle Weakness'),('adverse neural','Adverse Neural Tension Signs'),('gait disfunction','Giat Disfunction'),('long quadrant','Long Quadrant'),('altered mechanics','Altered Mechanics '),('altered mechanics ankle','Altered Mechanics Ankle Joint'),('generaliazed physical','Generalized Physical Deconditioning')],string='Clinician Impression', tracking=True)
    remark_lumbar_imperssion = fields.Text(string='Remark', tracking=True)
    lumbar_impression = fields.Many2one('examination.form', string='Immpression Exam', tracking=True)

class recommendationlumbar(models.Model):

    _name = 'clinician.recommendationlumbar'
    _rec_name = 'clinician_recommendation_lumbar'
    _description = 'clinician recommendation of lumbar'
    clinician_recommendation_lumbar = fields.Selection([('lumbo','Lumbo Pelvic Stabilization Program'),('taping','Taping/bracing lumbar spine as needed for stability'),('range of motion','Range of motion exercises to lumbar spine to enhance joint mobility and improve nutrition to spinal segments'),('Range of','Range of motion exercises to thoracic spine to improve mobility and nutrition to spinal segments'),('Segmental','Segmental lumbar stabilization'),('Thoracic','Thoracic mobilization'),('Lumbar','Lumbar mobilization'),('Hip mobilization','Hip mobilization'),('Lumbar traction','Lumbar traction'),('Stabilization belt','Stabilization belt for pelvis if necessary'),('S-1 mobilization','S-1 mobilization to normalize mechanics'),('Hip range','Hip range of motion exercises'),('Soft tissue','Soft tissue mobilization pelvic girdle musculature'),('Inhibition and lengthening','Inhibition and lengthening and stretching of hip musculature to restore normal tone, length, and mobility'),('Lower extremity stretching','Lower extremity stretching exercise in clinic and at home to normalize muscle length'),('Lift short','Lift short quadrant according to radiographic findings'),('Neural mobilization','Neural mobilization'),('Posture education and awareness exercise','Posture education and awareness exercise'),('Instruction in body mechanics: lifting bending, and sitting','Instruction in body mechanics: lifting bending, and sitting'),('Gait training','Gait training when muscle control')],string='Clinician recommendation', tracking=True)
    remark_recommend_lumbar = fields.Text(string='Remark', tracking=True)
    pres_freq_lumbar = fields.Char(string='Prescribed Frequency',tracking=True)
    time_per_week_lumbar = fields.Char(string = 'Time Per Week',tracking=True)
    lumbar_recommendation = fields.Many2one('examination.form', string='Recommendation Exam', tracking=True)

class anklestrength(models.Model):
    _name ='ankel.strength'
    _rec_name = 'strength_ankle'
    _description ='Ankle Strength'

    strength_ankle = fields.Selection([
        ('eversion', 'Eversion'),
        ('inversion', 'Inversion'),
        ('dorsiflexion', 'Dorsiflexion'),
        ('planter', 'Planter Flexion'),
   
  
        ], string='Strength', tracking=True,ondelete="cascade")  

    # strength_lumbar = fields.Selection([('right','Right'),('left','Left')], string=' Right/Left', tracking=True)
    remark_ankel= fields.Text(string='Remark', tracking=True)
    ankel_selection = fields.Selection([('0/5','0/5'),('1/5','1/5'),('1+/5','1+/5'),('2-/5','2-/5'),('2/5','2/5'),('2+/5','2+/5'),('3-/5','3-/5'),('3/5','3/5'),('3+/5','3+/5'),('4-/5','4-/5'),('4/5','4/5'),('4+/5','4+/5'),('5/5','5/5'),('n/t','N/T')],string='Select', tracking=True)

   

    ankel_strength_exam = fields.Many2one('examination.form', string='Ankel Strength Exam', tracking=True)

class anklerom(models.Model):
    _name = 'ankle.rom'
    _rec_name = 'rom_ankle'
    _description = 'Ankle Rom'

    rom_ankle = fields.Selection([('ankle plantar','Ankle Plantar Flexion(N=40°)'),('ankle dorsiflexion','Ankle Dorsiflexion(N=20°)'),('calcaneal','Calcaneal Eversion(N=10°)'),('calcaneal inversion','Calcaneal Inversion(N=20°)'),('1st MTP','1st MTP Dorsiflexion(N=70°)')],string='Rom Ankle', tracking=True)
    strength_ankle = fields.Selection([('right','Right'),('left','Left')], string=' Right/Left', tracking=True)

    remark_ankle_2 = fields.Text(string='Remark', tracking=True)

    ankle_rom_exam = fields.Many2one('examination.form', string='Ankle Rom Exam', tracking=True)
class anklebiomechanical(models.Model):
    _name = 'ankle.biomechanical'
    _rec_name = 'biomech_ankle'
    _description = 'Ankle Biomechanical'

    biomech_ankle = fields.Selection([('early','Early'),('mid','Mid'),('terminal','Terminal'),('throughout','Throughout Stance phase on'),('1st MTP','1st MTP Dorsiflexion(N=70°)')],string='Patient demonstrates abnormal pronation during', tracking=True)

    remark_ankle_3 = fields.Text(string='Remark', tracking=True)

    ankle_bio_exam = fields.Many2one('examination.form', string='Ankle bio Exam', tracking=True)
class anklemuscleflexibility(models.Model):
    _name = 'ankle.muscleflexibility'
    _rec_name = 'remark_ankle_4'
    _description = 'Ankle Muscle Flexibility'


    remark_ankle_4 = fields.Text(string='Remark', tracking=True)

    ankle_muscleflexi_exam = fields.Many2one('examination.form', string='Ankle muscleflexi Exam', tracking=True)

class anklepalpation(models.Model):
    _name = 'ankle.palpation'
    _rec_name = 'palpation_ankle'
    _description = 'Ankle Palpation'

    palpation_ankle = fields.Selection([('ant. Tal','ant. Tal FibLig'),('mid Tal.','mid. Tal. FibLig'),('Perorial Brav','Perorial Bravis'),('Perorial','Perorial Longus'),('Tibialis Anterior','Tibialis Anterior'),('Tibialis Post','Tibialis Posterior'),('Achilles ten','Achilles tenden'),('Deltoid ','Deltoid Ligaments'),('Plantar fas ','Plantar fascia')],string='Palpation', tracking=True)

    remark_ankle_5 = fields.Text(string='Remark', tracking=True)

    ankle_palpation_exam = fields.Many2one('examination.form', string='Ankle Paplation Exam', tracking=True)

class clinicianimpressionankle(models.Model):

    _name = 'clinician.impressionankle'
    _rec_name = 'clinician_imperssion_ankle'
    _description = 'clinician impression of lumbar'
    clinician_imperssion_ankle = fields.Selection([('Decreased AROM','Decreased AROM'),('Decreased PROM and accessory','Decreased PROM and accessory motions'),('Decreased muscle ','Decreased muscle lengths'),('Decreased balance proprioception','Decreased balance and proprioception'),('Abnormal/compensatory pronation during stance','Abnormal/compensatory pronation during stance'),('Inadequate rear foot pronation','Inadequate rear foot pronation at loading response'),('Gait dysfun','Gait dysfunction'),('Adverse neural','Adverse neural tension signs')], string='Clinician Impression', tracking=True)
    remark_ankle_imperssion = fields.Text(string='Remark', tracking=True)
    ankle_impression = fields.Many2one('examination.form', string='Immpression Exam', tracking=True)

class recommendationankle(models.Model):

    _name = 'clinician.recommendationankle'
    _rec_name = 'clinician_recommendation_ankle'
    _description = 'clinician recommendation of ankle'
    clinician_recommendation_ankle = fields.Selection([('Imaging studies','Imaging studies'),('Trigger point injection','Trigger point injection'),('Intraarticular joint injection','Intraarticular joint injection'),('Dry needling procedure','Dry needling procedure'),('AROM AAROM, and PROM exercce','AROM AAROM, and PROM exercce'),('Joint mobilization to increase accessory motions','Joint mobilization to increase accessory motions'),('Progressive concentric and eccentric strengthening exercises','Progressive concentric and eccentric strengthening exercises'),('Stretching in clinic and home to maximize muscle lengths','Stretching in clinic and home to maximize muscle lengths'),('Fabrication of custom orthotics to normalize foot function','Fabrication of custom orthotics to normalize foot function'),('issue pre-fabricated molded insoles for arch support','issue pre-fabricated molded insoles for arch support'),('Ankle and foot taping to reduce swelling and or control foot and ankle function','Ankle and foot taping to reduce swelling and or control foot and ankle function'),('Modalities to include heat, ice, ultrasound, and lontophoresis','Modalities to include heat, ice, ultrasound, and lontophoresis'),('Home exercises','Home exercises')],string='Clinician recommendation', tracking=True)
    remark_recommend_ankle = fields.Text(string='Remark', tracking=True)
    pres_freq_ankle = fields.Char(string='Prescribed Frequency',tracking=True)
    time_per_week_ankle = fields.Char(string = 'Time Per Week',tracking=True)
    ankle_recommendation = fields.Many2one('examination.form', string='Recommendation Exam', tracking=True)


class cervicalstrength(models.Model):
    _name ='cervical.strength'
    _rec_name = 'strength_cervical'
    _description ='Ankle Strength'

    strength_cervical = fields.Selection([
        ('elbow flex', 'Elbow flex'),
        ('finger add', 'Finger add'),
        ('finger flex(Kg)', 'Finger flex(Kg)'),
        ('shoulder abd', 'Shoulder abd'),
        ('wrist ext', 'Wrist ext'),
        ('wrist flex', 'Wrist flex'),
        ('wrist flex', 'Wrist flex'),
   
  
        ], string='Strength', tracking=True,ondelete="cascade")  

    # strength_lumbar = fields.Selection([('right','Right'),('left','Left')], string=' Right/Left', tracking=True)
    remark_cervical= fields.Text(string='Remark', tracking=True)
    cervical_selection = fields.Selection([('0/5','0/5'),('1/5','1/5'),('1+/5','1+/5'),('2-/5','2-/5'),('2/5','2/5'),('2+/5','2+/5'),('3-/5','3-/5'),('3/5','3/5'),('3+/5','3+/5'),('4-/5','4-/5'),('4/5','4/5'),('4+/5','4+/5'),('5/5','5/5'),('n/t','N/T')],string='Select', tracking=True)
    strength_cervical_right_left = fields.Selection([('right','Right'),('left','Left')], string=' Right/Left', tracking=True)

   

    cervical_strength_exam = fields.Many2one('examination.form', string='cervical Strength Exam', tracking=True)

class cervicalrom(models.Model):
    _name = 'cervical.rom'
    _rec_name = 'rom_cervical'
    _description = 'cervical Rom'

    rom_cervical = fields.Selection([('Rotation (N=90°)','Rotation (N=90°)'),('Sidebend (N=45)','Sidebend (N=45)')],string='Rom Cervical', tracking=True)
    strength_cervical_rom = fields.Selection([('right','Right'),('left','Left')], string=' Right/Left', tracking=True)

    remark_cervical_2 = fields.Text(string='Remark', tracking=True)

    cervical_rom_exam = fields.Many2one('examination.form', string='cervical Rom Exam', tracking=True)

class cervicalbiomechanical(models.Model):
    _name = 'cervical.biomechanical'
    _rec_name = 'biomech_cervical'
    _description = 'cervical Biomechanical'

    biomech_cervical = fields.Selection([('facet upglide','Facet Upglide'),('facet downglide','Facet Downglide'),('suboccipital restriction','Suboccipital Restriction')],string='Cervical Biomechanical', tracking=True)
    cervical_selection_2 = fields.Selection([('0/5','0/5'),('1/5','1/5'),('1+/5','1+/5'),('2-/5','2-/5'),('2/5','2/5'),('2+/5','2+/5'),('3-/5','3-/5'),('3/5','3/5'),('3+/5','3+/5'),('4-/5','4-/5'),('4/5','4/5'),('4+/5','4+/5'),('5/5','5/5'),('n/t','N/T')],string='Select', tracking=True)

    remark_cervical_3 = fields.Text(string='Remark', tracking=True)

    cervical_bio_exam = fields.Many2one('examination.form', string='Cervical bio Exam', tracking=True)

class cervicaltest(models.Model):
    _name = 'cervical.test'
    _rec_name = 'test_cervical'
    _description = 'cervical Test'

    test_cervical = fields.Selection([('cervical compression','Cervical Compression'),('cervical distraction','Cervical Distraction'),('cranial nerve Test','Cranial Nerve Test'),('Thoracic: 1123 Restricted rotation','Thoracic: 1123 Restricted rotation')],string='Cervical Test', tracking=True)
    cervical_selection_3 = fields.Selection([('0/5','0/5'),('1/5','1/5'),('1+/5','1+/5'),('2-/5','2-/5'),('2/5','2/5'),('2+/5','2+/5'),('3-/5','3-/5'),('3/5','3/5'),('3+/5','3+/5'),('4-/5','4-/5'),('4/5','4/5'),('4+/5','4+/5'),('5/5','5/5'),('n/t','N/T')],string='Select', tracking=True)

    remark_cervical_4 = fields.Text(string='Remark', tracking=True)

    cervical_test_exam = fields.Many2one('examination.form', string='Cervical test Exam', tracking=True)

class cervicalmuscleflexibility(models.Model):
    _name = 'cervical.muscleflexibility'
    _rec_name = 'muscle_cervical'
    _description = 'cervical Muscle Flexibility'

    muscle_cervical = fields.Selection([('Upp Trap','Lev. Scap'),('SCM','SCM'),('Superior  trapezius','Superior  trapezius'),('Scalen','Scalen'),('Infraspinatus','Infraspinatus'),('Supraspinatus','Supraspinatus'),('Suboccipital Muscle','Suboccipital Muscle')],string='Muscle Flexibility', tracking=True)
    cervical_selection_4 = fields.Selection([('0/5','0/5'),('1/5','1/5'),('1+/5','1+/5'),('2-/5','2-/5'),('2/5','2/5'),('2+/5','2+/5'),('3-/5','3-/5'),('3/5','3/5'),('3+/5','3+/5'),('4-/5','4-/5'),('4/5','4/5'),('4+/5','4+/5'),('5/5','5/5'),('n/t','N/T')],string='Select', tracking=True)

    remark_cervical_5 = fields.Text(string='Remark', tracking=True)

    cervical_muscleflexi_exam = fields.Many2one('examination.form', string='cervical muscleflexi Exam', tracking=True)

class cervicalpalpation(models.Model):
    _name = 'cervical.palpation'
    _rec_name = 'palpation_cervical'
    _description = 'Cervical Palpation'

    palpation_cervical = fields.Selection([('Upp Trap','Lev. Scap'),('SCM','SCM'),('Superior  trapezius','Superior  trapezius'),('Scalen','Scalen'),('Infraspinatus','Infraspinatus'),('Supraspinatus','Supraspinatus'),('Suboccipital Muscle','Suboccipital Muscle')],string='Palpation', tracking=True)
    cervical_selection_5 = fields.Selection([('0/5','0/5'),('1/5','1/5'),('1+/5','1+/5'),('2-/5','2-/5'),('2/5','2/5'),('2+/5','2+/5'),('3-/5','3-/5'),('3/5','3/5'),('3+/5','3+/5'),('4-/5','4-/5'),('4/5','4/5'),('4+/5','4+/5'),('5/5','5/5'),('n/t','N/T')],string='Select', tracking=True)

    remark_cervical_6 = fields.Text(string='Remark', tracking=True)

    cervical_palpation_exam = fields.Many2one('examination.form', string='Cervical Paplation Exam', tracking=True)

class clinicianimpressioncervical(models.Model):

    _name = 'clinician.impressioncervical'
    _rec_name = 'clinician_imperssion_cervical'
    _description = 'clinician impression of cervical'
    clinician_imperssion_cervical = fields.Selection([('postural imbalance','Postural imbalance'),('Decreased AROM','Decreased AROM'),('Decreased passive intervertebral motion','Decreased passive intervertebral motion'),('Hypermobility on passive intervertebral motion','Hypermobility on passive intervertebral motion'),('Decreased strength of Cervical and UQ muscles','Decreased strength of Cervical and UQ muscles'),('Hypertonic upper quarter musculature','Hypertonic upper quarter musculature'),('Adaptive shortening of muscles','Adaptive shortening of muscles'),('Adverse neural tension','Adverse neural tension'),('Decreased facet joint mobility','Decreased facet joint mobility'),('Decreased mobility upper thoracic spine','Decreased mobility upper thoracic spine'),('Restricted mobility suboccipital','Restricted mobility suboccipital')], string='Clinician Impression', tracking=True)
    remark_cervical_imperssion = fields.Text(string='Remark', tracking=True)
    cervical_impression = fields.Many2one('examination.form', string='cervical Immpression Exam', tracking=True)

class recommendationcervical(models.Model):

    _name = 'clinician.recommendationcervical'
    _rec_name = 'clinician_recommendation_cervical'
    _description = 'clinician recommendation of cervical'
    clinician_recommendation_cervical = fields.Selection([('Imaging studies','Imaging studies'),('Trigger point injection','Trigger point injection'),('Intraarticular joint injection','Intraarticular joint injection'),('Dry needling procedure','Dry needling procedure'),('AROM AAROM, and PROM exercce','AROM AAROM, and PROM exercce'),('Joint mobilization to increase accessory motions','Joint mobilization to increase accessory motions'),('Progressive concentric and eccentric strengthening exercises','Progressive concentric and eccentric strengthening exercises'),('Stretching in clinic and home to maximize muscle lengths','Stretching in clinic and home to maximize muscle lengths'),('Fabrication of custom orthotics to normalize foot function','Fabrication of custom orthotics to normalize foot function'),('issue pre-fabricated molded insoles for arch support','issue pre-fabricated molded insoles for arch support'),('Ankle and foot taping to reduce swelling and or control foot and ankle function','Ankle and foot taping to reduce swelling and or control foot and ankle function'),('Modalities to include heat, ice, ultrasound, and lontophoresis','Modalities to include heat, ice, ultrasound, and lontophoresis'),('Home exercises','Home exercises')],string='Clinician recommendation', tracking=True)
    remark_recommend_cervical = fields.Text(string='Remark', tracking=True)
    # pres_freq_cervical = fields.Char(string='Prescribed Frequency',tracking=True)
    # time_per_week_cervical = fields.Char(string = 'Time Per Week',tracking=True)
    cervical_recommendation = fields.Many2one('examination.form', string='Recommendation Exam', tracking=True)

class shoulderrom(models.Model):
    _name = 'shoulder.rom'
    _rec_name = 'rom_shoulder'
    _description = 'Shoulder Rom'

    # strength_shoulder = fields.Selection([('right','Right'),('left','Left')], string=' Right/Left', tracking=True)
    
    rom_shoulder = fields.Selection([('flexion (N=180°)','Flexion (N=180°)'),('abduction (N=180°)','Abduction (N=180°)'),('Internal Rotation (N=70)','Internal Rotation (N=70)'),('External Rotation (N-90°)','External Rotation (N-90°)')],string='Rom', tracking=True)
    
   
    
    remark_shoulder_1 = fields.Text(string='Remark', tracking=True)
  

    shoulder_rom_exam = fields.Many2one('examination.form', string='Shoulder Rom Exam', tracking=True)
class shoulderaccessory(models.Model):
    _name = 'shoulder.accessory'
    _rec_name = 'accessory_shoulder'
    _description = 'Shoulder accessory'

    accessory_shoulder = fields.Selection([('Anterior Glides','Anterior Glides'),('Posterior Glide','Posterior Glide'),('Inferior Glide','Inferior Glide'),('Distraction','Distraction')],string='Accessory Motion', tracking=True)
    remark_shoulder_2 = fields.Text(string='Remark', tracking=True)
    shoulder_selection = fields.Selection([('0/5','0/5'),('1/5','1/5'),('1+/5','1+/5'),('2-/5','2-/5'),('2/5','2/5'),('2+/5','2+/5'),('3-/5','3-/5'),('3/5','3/5'),('3+/5','3+/5'),('4-/5','4-/5'),('4/5','4/5'),('4+/5','4+/5'),('5/5','5/5'),('n/t','N/T')],string='Select', tracking=True)

    shoulder_accessory_exam = fields.Many2one('examination.form', string='Shoulder Accessory Exam', tracking=True)

class shouldermmt(models.Model):
    _name = 'shoulder.mmt'
    _rec_name = 'mmt_shoulder'
    _description = 'Shoulder MMT'

    mmt_shoulder = fields.Selection([('ext. rotation','Ext. Rotation'),('int. rotation','Int. Rotation'),('extension','Extension'),('elevation','Elevation'),('retraction','Retraction'),('depression','Depression'),('protraction','Protraction')],string='MMT', tracking=True)
    shoulder_selection_2 = fields.Selection([('0/5','0/5'),('1/5','1/5'),('1+/5','1+/5'),('2-/5','2-/5'),('2/5','2/5'),('2+/5','2+/5'),('3-/5','3-/5'),('3/5','3/5'),('3+/5','3+/5'),('4-/5','4-/5'),('4/5','4/5'),('4+/5','4+/5'),('5/5','5/5'),('n/t','N/T')],string='Select', tracking=True)
    remark_shoulder_3 = fields.Text(string='Remark', tracking=True)

    shoulder_mmt_exam = fields.Many2one('examination.form', string='Shoulder MMT Exam', tracking=True)

class shoulderpalpation(models.Model):
    _name = 'shoulder.palpation'
    _rec_name = 'palpation_shoulder'
    _description = 'Shoulder Palpation'

    remark_shoulder_4 = fields.Text(string='Remark', tracking=True)
    palpation_shoulder = fields.Selection([('Erector Spinea','Erector Spinea'),('Rhomboid','Rhomboid'),('Mid traps','Mid traps'),('Inter costal muscles','Inter costal muscles'),('Upper traps','Upper traps'),('Infra','Infra')],string='Palpation', tracking=True)
    shoulder_palpation_exam = fields.Many2one('examination.form', string='Shoulder Palpation Exam', tracking=True)

class shoulderisometric(models.Model):
    _name = 'shoulder.isometric'
    _rec_name = 'isometric_shoulder'
    _description = 'Shoulder Isometric'

    isometric_shoulder = fields.Selection([('flexion','Flexion'),('Extension','Extension (from 90 flex)'),('Triceps','Triceps (full flex)'),('Abduction','Abduction'),('Adduction','Adduction'),('Int. Rotation','Int. Rotation'),('Ext. Rotation','Ext. Rotation')],string='Resisted Isometric', tracking=True)
    shoulder_selection_3 = fields.Selection([('0/5','0/5'),('1/5','1/5'),('1+/5','1+/5'),('2-/5','2-/5'),('2/5','2/5'),('2+/5','2+/5'),('3-/5','3-/5'),('3/5','3/5'),('3+/5','3+/5'),('4-/5','4-/5'),('4/5','4/5'),('4+/5','4+/5'),('5/5','5/5'),('n/t','N/T')],string='Select', tracking=True)
    remark_shoulder_5 = fields.Text(string='Remark', tracking=True)
    shoulder_isometric_exam = fields.Many2one('examination.form', string='Shoulder Isometric Exam', tracking=True)

class shoulderimpressions(models.Model):
    _name = 'shoulder.impressions'
    _rec_name = 'impressions_shoulder'
    _description = 'Shoulder Impressions'

    impressions_shoulder = fields.Selection([('Decreased AROM','Decreased AROM'),('Decreased PROM and accessory','Decreased PROM and accessory motions'),('Decreased strength/coordination','Decreased strength/coordination of glenohumeral muscles'),('Decreased soft tissue mobili','Decreased soft tissue mobility at scar and fascial planes'),('Adverse neural','Adverse neural tension'),('Decreased strength/coordination','Decreased strength/coordination of scapular stabilizers'),('Hypermobility','Hypermobility of the GH joint'),('A/C or S/C','A/C or S/C dysfunction'),('Thoracic spine dysfunction','Thoracic spine dysfunction'),('Hypertonic upper','Hypertonic upper quarter musculature'),('Postural','Postural dysfunction'),('Hypomobility','Hypomobility of glenohumeral joint'),('Tendonitis','Tendonitis of associated musculature'),('Ligament stress test positive for superior','Ligament stress test positive for superior glenohumeral, coracohumeral, anterior inferior glenohumeral posterior inferior glenohumeral ligaments')], string='Clinician Impression', tracking=True)
    remark_shoulder_6 = fields.Text(string='Remark', tracking=True)
    shoulder_impression_exam = fields.Many2one('examination.form', string='Shoulder Impression Exam', tracking=True)

class shoulderrecommendation(models.Model):
    _name = 'shoulder.recommendation'
    _rec_name = 'recommendation_shoulder'
    _description = 'Shoulder Recommendation'

    recommendation_shoulder = fields.Selection([('Imaging studies','Imaging studies'),('Trigger','Trigger point injection'),('Intraarticular','Intraarticular joint injection'),('Dry n','Dry needling procedure'),('AROM AAROM','AROM AAROM, and PROM exercce'),('Friction','Friction to the following'),('Joint mobilization: A-C,S-C, GH','Joint mobilization: A-C,S-C, GH Scapulothoracis, Thoracic'),('Soft tissue','Soft tissue mobilization'),('Isometric ','Isometric strengthening exercises'),('Progressive concentric','Progressive concentric and eccentric strengthening exercises'),('Upper extremity ergometer','Upper extremity ergometer for general conditioning'),('Scapular stabilization exercises','Scapular stabilization exercises Taping to enhance scapulothoracic mechanics'),('Progression','Progression of functional activities'),('Home exercise program','Home exercise program for ROM, strength and functional enhancement'),('Posture','Posture reeducation'),('Neural','Neural mobilization'),('Inhibition','Inhibition of hypertonic musculature'),('Rotator Cuff','Rotator Cuff rehabilitation protocol')],string='Clinician Recommendation', tracking=True)
    remark_shoulder_7 = fields.Text(string='Remark', tracking=True)
    shoulder_recommednation_exam = fields.Many2one('examination.form', string='Shoulder Recommendation Exam', tracking=True)
    pres_freq_shoulder = fields.Char(string='Prescribed Frequency',tracking=True)
    time_per_week_shoulder = fields.Char(string = 'Time Per Week',tracking=True)

class kneestrength(models.Model):
    _name = 'knee.strength'
    _rec_name = 'strength_knee'
    _description = 'Knee Strength'

    strength_knee = fields.Selection([('Hip ','Hip Flexion'),('Hip Exe','Hip Extension'),('Hip Abd','Hip Abduction'),('Hamst','Hamstrings'),('Hip Adduction','Hip Adduction'),('Qua','Quads'),('Dorsi','Dorsiflexion'),('Planter Flex','Planter Flexion')],string='Strength', tracking=True)
    knee_selection = fields.Selection([('0/5','0/5'),('1/5','1/5'),('1+/5','1+/5'),('2-/5','2-/5'),('2/5','2/5'),('2+/5','2+/5'),('3-/5','3-/5'),('3/5','3/5'),('3+/5','3+/5'),('4-/5','4-/5'),('4/5','4/5'),('4+/5','4+/5'),('5/5','5/5'),('n/t','N/T')],string='Select', tracking=True)
    remark_knee = fields.Text(string='Remark', tracking=True)
    knee_strength_exam = fields.Many2one('examination.form', string='knee strength Exam', tracking=True)

class kneerom(models.Model):
    _name = 'knee.rom'
    _rec_name = 'rom_knee'
    _description = 'Knee ROM'

    rom_knee = fields.Selection([('Supine Knee Extension','Supine Knee Extension to Flexion '),('Prone Knee Extension ','Prone Knee Extension to Flexion')],string='Rom', tracking=True)
    knee_rl= fields.Selection([('right','Right'),('left','Left')], string=' Right/Left', tracking=True)
    remark_knee_2 = fields.Text(string='Remark', tracking=True)
    knee_rom_exam = fields.Many2one('examination.form', string='knee rom Exam', tracking=True)

class kneebiomechanical(models.Model):
    _name = 'knee.biomechanical'
    _rec_name = 'biomechanical_knee'
    _description = 'Knee Biomechanical'

    biomechanical_knee = fields.Selection([('Genu recurvatum','Genu recurvatum at terminal stance on'),('Varus instability','Varus instability during stance phase on'),('Excessive knee ','Excessive knee valgus bilaterally on')],string='Biomechanical Gait', tracking=True)
    knee_selection_2 = fields.Selection([('0/5','0/5'),('1/5','1/5'),('1+/5','1+/5'),('2-/5','2-/5'),('2/5','2/5'),('2+/5','2+/5'),('3-/5','3-/5'),('3/5','3/5'),('3+/5','3+/5'),('4-/5','4-/5'),('4/5','4/5'),('4+/5','4+/5'),('5/5','5/5'),('n/t','N/T')],string='Select', tracking=True)
    remark_knee_3 = fields.Text(string='Remark', tracking=True)
    knee_biomechanical_exam = fields.Many2one('examination.form', string='knee Biomechanical Exam', tracking=True)

class kneespecialtest(models.Model):
    _name = 'knee.specialtest'
    _rec_name = 'specialtest_knee'
    _description = 'Knee Special Test'

    specialtest_knee = fields.Selection([('Lachman','Lachman s'),('Varus Stres','Varus Stress 30° & 0°'),('Valgus Stress','Valgus Stress 30° & 0°'),('Ober s ','Ober s Test'),('McMurray','McMurray s'),('Pivot','Pivot Shift')],string='Special Test', tracking=True)
    knee_selection_3 = fields.Selection([('0/5','0/5'),('1/5','1/5'),('1+/5','1+/5'),('2-/5','2-/5'),('2/5','2/5'),('2+/5','2+/5'),('3-/5','3-/5'),('3/5','3/5'),('3+/5','3+/5'),('4-/5','4-/5'),('4/5','4/5'),('4+/5','4+/5'),('5/5','5/5'),('n/t','N/T')],string='Select', tracking=True)
    remark_knee_4 = fields.Text(string='Remark', tracking=True)
    knee_specialtest_exam = fields.Many2one('examination.form', string='knee Special Test Exam', tracking=True)

class kneegirth(models.Model):
    _name = 'knee.girth'
    _rec_name = 'girth_knee'
    _description = 'Knee Girth'

    girth_knee = fields.Selection([('Patel','Patella'),('6 above','6 above(cm)'),('6" below','6" below(cm)')],string='Girth', tracking=True)
    knee_rl_2= fields.Selection([('right','Right'),('left','Left')], string=' Right/Left', tracking=True)
    remark_knee_5 = fields.Text(string='Remark', tracking=True)
    knee_girth_exam = fields.Many2one('examination.form', string='knee Girth Exam', tracking=True)

class kneeimpressions(models.Model):
    _name = 'knee.impressions'
    _rec_name = 'impressions_knee'
    _description = 'knee Impressions'

    impressions_knee = fields.Selection([('Decreased AROM','Decreased AROM'),('Decreased soft','Decreased soft tissue mobility'),('Decreased accessory','Decreased accessory motions tibiofemoral and/or patellofemoral joints'),('Hypermobility/instability of the','Hypermobility/instability of the Knee'),('Decreased strength','Decreased strength of hip/knee'),('Adaptive shortening','Adaptive shortening of muscles'),('Decreased balance/kinesthetic','Decreased balance/kinesthetic awareness'),('Faulty foot mechanics contributin','Faulty foot mechanics contributing to anterior knee pain'),('Decreased quad ','Decreased quad control'),('Post operative','Post operative swelling')], string='Clinician Impression', tracking=True)
    remark_knee_6 = fields.Text(string='Remark', tracking=True)
    knee_impressions_exam = fields.Many2one('examination.form', string='Knee Impression Exam', tracking=True)

class kneeincision(models.Model):
    _name = 'knee.incision'
    _rec_name = 'incision_knee'
    _description = 'knee Incision'

    incision_knee = fields.Selection([('healing','Healing'),('Minor','Minor Scabbing'),('No Inci','No Incision')],string='Incision', tracking=True)
    remark_knee_8 = fields.Text(string='Remark', tracking=True)
    knee_incision_exam = fields.Many2one('examination.form', string='Knee Incision Exam', tracking=True)

class kneerecommendation(models.Model):
    _name = 'knee.recommendation'
    _rec_name = 'recommendation_knee'
    _description = 'Knee Recommendation'

    recommendation_knee = fields.Selection([('Imaging studies','Imaging studies'),('Trigger','Trigger point injection'),('Intraarticular','Intraarticular joint injection'),('Modalities ','Modalities as indicated for pain and edema management, muscle reducation'),('AROM AAROM','AROM AAROM, and PROM exercce'),('Friction','Friction to the following'),('Joint mobili','Joint mobilization'),('Soft tissue','Soft tissue mobilization'),('Lengthening ','Lengthening and graduated stretching of involved musculature'),('Open and clos','Open and closed chain kinesthetic/strengthening exercises'),('Balance','Balance training'),('Progression','Progression of ACL rehabilitation protocol'),('Foot orthoses','Foot orthoses to control adverse patellofemoral mechanics'),('Home exercise program','Home exercise program'),('Patella tap','Patella taping'),('VMO','VMO activation and retraining'),('Total knee','Total knee replacement protocol'),('Postoperative rehab','Postoperative rehab protocol'),('Isokinetic trai','Isokinetic training when tolerated')],string='Clinician Recommendation', tracking=True)
    remark_knee_7 = fields.Text(string='Remark', tracking=True)
    knee_recommednation_exam = fields.Many2one('examination.form', string='Knee Recommendation Exam', tracking=True)
    pres_freq_knee = fields.Char(string='Prescribed Frequency',tracking=True)
    time_per_week_knee = fields.Char(string = 'Time Per Week',tracking=True)

class thoracicstrength(models.Model):
    _name = 'thoracic.strength'
    _rec_name = 'strength_thoracic'
    _description = 'thoracic strength'
    
    strength_thoracic = fields.Selection([('C5 Deltoid','C5 Deltoid, Supra'),('C5-6 ','C5-6 Biceps'),('C6 Wrist','C6 Wrist ext'),('C7 Wrist','C7 Wrist flex'),('C8 Finger flex.','C8 Finger flex.( Grip strength) (Kg)'),('T1 Intero','T1 Interosse')], string='Strength', tracking=True)
    thoracic_rl= fields.Selection([('right','Right'),('left','Left')], string=' Right/Left', tracking=True)
    remark_thoracic = fields.Text(string='Remark', tracking=True)
    thoracic_strength_exam = fields.Many2one('examination.form', string='thoracic strength Exam', tracking=True)
class thoracicrom(models.Model):
    _name = 'thoracic.rom'
    _rec_name = 'rom_thoracic'
    _description = 'thoracic rom'

    rom_thoracic = fields.Selection([('Forward Be','Forward Bend (N=60°)'),('Backward Bend','Backward Bend (N=60°)'),('Rotation','Rotation (N=90°)'),('Sidebend','Sidebend (N=45°)')],string='Rom', tracking=True)
    thoracic_rl_2= fields.Selection([('right','Right'),('left','Left')], string=' Right/Left', tracking=True)
    remark_thoracic_2 = fields.Text(string='Remark', tracking=True)
    thoracic_rom_exam = fields.Many2one('examination.form', string='thoracic rom Exam', tracking=True)

class thoracicbiomechanical(models.Model):
    _name = 'thoracic.biomechanical'
    _rec_name = 'biomechanical_thoracic'
    _description = 'thoracic Biomechanical'

    biomechanical_thoracic = fields.Selection([('Normal mob','Normal mobility'),('Stiff thro','Stiff throughout')],string='Biomechanical Thoracic', tracking=True)
    # thoracic_selection = fields.Selection([('0/5','0/5'),('1/5','1/5'),('1+/5','1+/5'),('2-/5','2-/5'),('2/5','2/5'),('2+/5','2+/5'),('3-/5','3-/5'),('3/5','3/5'),('3+/5','3+/5'),('4-/5','4-/5'),('4/5','4/5'),('4+/5','4+/5'),('5/5','5/5'),('n/t','N/T')],string='Select', tracking=True)
    remark_thoracic_3 = fields.Text(string='Remark', tracking=True)
    thoracic_biomechanical_exam = fields.Many2one('examination.form', string='knee Biomechanical Exam', tracking=True)

class thoracicbiomechanical(models.Model):
    _name = 'thoracic.lumbar'
    _rec_name = 'lumbar_thoracic'
    _description = 'thoracic lumbar'

    lumbar_thoracic = fields.Selection([('Normal mob','Normal mobility'),('Stiff thro','Stiff throughout'),('Restricted rotatio','Restricted rotation on'),('Hypermobility noted','Hypermobility noted in the following')],string='Lumbar', tracking=True)
    thoracic_selection = fields.Selection([('0/5','0/5'),('1/5','1/5'),('1+/5','1+/5'),('2-/5','2-/5'),('2/5','2/5'),('2+/5','2+/5'),('3-/5','3-/5'),('3/5','3/5'),('3+/5','3+/5'),('4-/5','4-/5'),('4/5','4/5'),('4+/5','4+/5'),('5/5','5/5'),('n/t','N/T')],string='Select', tracking=True)
    remark_thoracic_lumbar_4 = fields.Text(string='Remark', tracking=True)
    thoracic_lumbar_exam = fields.Many2one('examination.form', string='thoracic Lumbar Exam', tracking=True)

class thoracicT(models.Model):
    _name = 'thoracic.tho'
    _rec_name = 'tho_thoracic'
    _description = 'thoracic Tho'

    tho_thoracic = fields.Selection([('Restricted rot','Restricted rotation on'),('Hypermobility noted','Hypermobility noted in the following segments')],string='Thoracic', tracking=True)
    thoracic_selection_2 = fields.Selection([('0/5','0/5'),('1/5','1/5'),('1+/5','1+/5'),('2-/5','2-/5'),('2/5','2/5'),('2+/5','2+/5'),('3-/5','3-/5'),('3/5','3/5'),('3+/5','3+/5'),('4-/5','4-/5'),('4/5','4/5'),('4+/5','4+/5'),('5/5','5/5'),('n/t','N/T')],string='Select', tracking=True)
    remark_thoracic_5 = fields.Text(string='Remark', tracking=True)
    thoracic_tho_exam = fields.Many2one('examination.form', string='thoracic Tho Exam', tracking=True)

class thoracicpalpation(models.Model):
    _name = 'thoracic.palpation'
    _rec_name = 'palpation_thoracic'
    _description = 'thoracic palpation'

    palpation_thoracic = fields.Selection([('Erector Spinea','Erector Spinea'),('Rhomboid','Rhomboid'),('Mid traps','Mid traps'),('Inter costal muscles','Inter costal muscles'),('Upper traps','Upper traps'),('Infra','Infra')],string='Palpation', tracking=True)
    # thoracic_selection_3 = fields.Selection([('0/5','0/5'),('1/5','1/5'),('1+/5','1+/5'),('2-/5','2-/5'),('2/5','2/5'),('2+/5','2+/5'),('3-/5','3-/5'),('3/5','3/5'),('3+/5','3+/5'),('4-/5','4-/5'),('4/5','4/5'),('4+/5','4+/5'),('5/5','5/5'),('n/t','N/T')],string='Select', tracking=True)
    remark_thoracic_6 = fields.Text(string='Remark', tracking=True)
    thoracic_palpation_exam = fields.Many2one('examination.form', string='thoracic Palpation Exam', tracking=True)

class thoracicimpressions(models.Model):
    _name = 'thoracic.impressions'
    _rec_name = 'impressions_thoracic'
    _description = 'thoracic Impressions'

    impressions_thoracic = fields.Selection([('Postural imba','Postural imbalance'),('Decreased AROM','Decreased AROM'),('Decreased passive','Decreased passive intervertebral motion'),('Hyper mobility on','Hyper mobility on passive intervertebral motion'),('Decreased str','Decreased strength'),('Hypertonic upper','Hypertonic upper quarter musculature'),('Adaptive shortening','Adaptive shortening of muscles'),('Adverse neura','Adverse neural tension'),('Decreased facet','Decreased facet joint mobility'),('Decreased costovertebral','Decreased costovertebral mobility'),('Rib dys','Rib dysfunction'),('Decreased mobility','Decreased mobility thoracic/cervical/lumbar spine'),('Sensitivity thorac','Sensitivity thoracic and lumbar vertebrae to p-a oscillations'),('Roto','Rotoscoliosis'),('Scapulothoracic','Scapulothoracic dysfunction'),('Sternocost','Sternocostal dysfunction')], string='Clinician Impression', tracking=True)
    remark_thoracic_7 = fields.Text(string='Remark', tracking=True)
    thoracic_impressions_exam = fields.Many2one('examination.form', string='thoracic Impression Exam', tracking=True)

class thoracicrecommendation(models.Model):
    _name = 'thoracic.recommendation'
    _rec_name = 'recommendation_thoracic'
    _description = 'thoracic Recommendation'

    recommendation_thoracic = fields.Selection([('Modalities','Modalities as indicated'),('Postural education','Postural education and awareness training'),('Inhibition techniqu','Inhibition techniques to reduce hyper tonicity'),('lengthening and graduated','lengthening and graduated stretching of involved musculature'),('Range of motion exercises to cervical/thoracic spine ','Range of motion exercises to cervical/thoracic spine to improve range of motion and nutrition to involved segments'),('Manual a','Manual and or mechanical traction'),('Soft tissue','Soft tissue mobilization'),('Joint mobilization','Joint mobilization to'),('Cervical stabilization','Cervical stabilization training'),('Neural mobi','Neural mobilization'),('Upper extremity','Upper extremity strengthening'),('Thoracic stre','Thoracic strengthening'),('General/cardiovascular','General/cardiovascular conditioning'),('Instruction in home','Instruction in home exercise program'),('Imaging stud','Imaging studies'),('Trigger point','Trigger point injection'),('Intraarticular joint','Intraarticular joint injection'),('Dry needling','Dry needling procedure')],string='Clinician Recommendation', tracking=True)
    remark_thoracic_8 = fields.Text(string='Remark', tracking=True)
    thoracic_recommednation_exam = fields.Many2one('examination.form', string='thoracic Recommendation Exam', tracking=True)
    pres_freq_thoracic = fields.Char(string='Prescribed Frequency',tracking=True)
    time_per_week_thoracic = fields.Char(string = 'Time Per Week',tracking=True)

class nuroptmuscletone(models.Model):
    _name = 'nuropt.muscletone'
    _rec_name = 'muscletone_nuropt'
    _description = 'nuropt muscletone'

    muscletone_nuropt = fields.Selection([('Normal','Normal'),('Hypotonic','Hypotonic'),('Hypertonic','Hypertonic')],string='Muscle Tone', tracking=True)
    remark_nuropt = fields.Text(string='Remark', tracking=True)
    nuropt_muscletone_exam = fields.Many2one('examination.form', string='nuropt muscletone Exam', tracking=True)

class nuroptsensation(models.Model):
    _name = 'nuropt.sensation'
    _rec_name = 'remark_nuropt_2'
    _description = 'nuropt sensation'

    remark_nuropt_2 = fields.Text(string='Remark', tracking=True)
    nuropt_sensation_exam = fields.Many2one('examination.form', string='nuropt sensation Exam', tracking=True)

class nuroptconsciousness(models.Model):
    _name = 'nuropt.consciousness'
    _rec_name = 'remark_consciousness_3'
    _description = 'nuropt consciousness'

    remark_consciousness_3 = fields.Text(string='Remark', tracking=True)
    nuropt_consciousness_exam = fields.Many2one('examination.form', string='nuropt consciousness Exam', tracking=True)

class nuroptmotor(models.Model):
    _name = 'nuropt.motor'
    _rec_name = 'remark_nuropt_3'
    _description = 'nuropt consciousness'

    remark_nuropt_3 = fields.Text(string='Remark', tracking=True)
    nuropt_motor_exam = fields.Many2one('examination.form', string='nuropt motor Exam', tracking=True)

class nuroptlistoffunction(models.Model):
    _name = 'nuropt.listoffunction'
    _rec_name = 'remark_nuropt_4'
    _description = 'nuropt List of Function'

    remark_nuropt_4 = fields.Text(string='Remark', tracking=True)
    nuropt_listoffunction_exam = fields.Many2one('examination.form', string='nuropt List of Function Exam', tracking=True)


class nuroptbalance(models.Model):
    _name = 'nuropt.balance'
    _rec_name = 'balance_nuropt'
    _description = 'nuropt List of Function'

    balance_nuropt = fields.Selection([('Finger to','Finger to nose'),('Heel to ','Heel to Shin'),('Sitt','Sitting'),('Stand','Standing'),('Ambulation','Ambulation-time'),('up and go','up and go test'),('Four stage','Four stage balance'),('test (n=10 sec)','test (n=10 sec): Side by side'),('Instep of','Instep of one foot'),('Tandem','Tandem stance'),('One foot','One foot standing')],string='Balance and Coordination', tracking=True)
    remark_nuropt_5 = fields.Text(string='Remark', tracking=True)
    nuropt_balance_exam = fields.Many2one('examination.form', string='nuropt Balance and Coordination Exam', tracking=True)

class nuroptmusclepow(models.Model):
    _name = 'nuropt.musclepow'
    _rec_name = 'musclepow_nuropt'
    _description = 'nuro pt musclepow'

    musclepow_nuropt = fields.Selection([('Shoulder','Shoulder abd.'),('Elbow','Elbow flex'),('Wrist','Wrist ext'),('Wrist','Wrist flex'),('Finger','Finger flex'),('Finger a','Finger add'),('Knee Ext','Knee Extension'),('Knee fle','Knee flexion'),('Hip exten','Hip extension'),('Hip flex','Hip flexion'),('Hip abduct','Hip abduction'),('Hip adducti','Hip adduction')],string='Muscle Power', tracking=True)
    musclepow_rl= fields.Selection([('right','Right'),('left','Left')], string=' Right/Left', tracking=True)

    remark_nuropt_6 = fields.Text(string='Remark', tracking=True)
    nuropt_musclepow_exam = fields.Many2one('examination.form', string='nuropt Muscle Power Exam', tracking=True)

class nuroptreflex(models.Model):
    _name = 'nuropt.reflex'
    _rec_name = 'reflex_nuropt'
    _description = 'nuro pt Reflex'

    reflex_nuropt = fields.Selection([('Bice','Biceps'),('Tri','Triceps'),('Brach','Brachioradialis'),('Pate','Patella'),('Babinski','Babinski sign')],string='Reflex', tracking=True)

    remark_nuropt_7 = fields.Text(string='Remark', tracking=True)
    nuropt_reflex_exam = fields.Many2one('examination.form', string='nuropt Reflex Exam', tracking=True)

class nuroptasia(models.Model):
    _name = 'nuropt.asia'
    _rec_name = 'asia_nuropt'
    _description = 'nuro pt asia'

    asia_nuropt = fields.Selection([('Grade A','Grade A-Complete sensory or motor function loss below the level of injury'),('B','Grade B-Sensation is preserved below the level of injury, but motor function is lost'),('C','Grade C Motor function below the level of injury is preserved, with more than half of the main muscles receiving a less than 3 grade on the ASIA motor score'),('D','Grade D-Motor function below the level of injury is preserved, with more than half of the main muscles receiving at least a 3 or greater grade on the ASIA motor score'),('E','Grade E-Normal sensation and motor function')],string='ASIA Impairment Scale' , tracking=True)
    nuropt_asia_exam = fields.Many2one('examination.form', string='nuropt ASIA Exam', tracking=True) 

class nuroptimpression(models.Model):
    _name = 'nuropt.immpression'
    _rec_name = 'immpression_nuropt'
    _description = 'nuro pt immpression'

    immpression_nuropt = fields.Selection([('Functional instab','Functional instability of lumbopelvic region'),('Lumbar spine','Lumbar spine dysfunctions'),('Decreased lumbar','Decreased lumbar spine active range of motion'),('Lumbar hyper','Lumbar hypermobility'),('Facet joint hypo mobility','Facet joint hypo mobility lumbar/thoracic spine'),('S-1 dysfunctions with','S-1 dysfunctions with possible hypermobility/with pubic joint involvement'),('Sensitivity thoracic','Sensitivity thoracic and lumbar vertebrae to p-a oscillations'),('Root sc','Root scoliosis'),('Hip capsule','Hip capsule restriction'),('Hip flexor muscle','Hip flexor muscle dysfunction'),('Soft tissue dy','Soft tissue dysfunction of pelvic girdle musculature and erector spine'),('Hypertoni','Hypertonic musculatures'),('Decreased lower extremity','Decreased lower extremity muscle lengths'),('Lower extremity','Lower extremity muscle weakness'),('Adverse neural tension signs night','Adverse neural tension signs night/left sciatic and right/left fernoral tract bilaterally'),('Gait dys','Gait dysfunction'),('Long quad','Long quadrant'),('Altered mechanics','Altered mechanics superior tit/fib joint'),('Altered mechanics','Altered mechanics ankles joint'),('Generalized physica','Generalized physical deconditioning')],string='Clinican Impression' , tracking=True)
    
    remark_nuropt_8 = fields.Text(string='Remark', tracking=True)

    nuropt_immpression_exam = fields.Many2one('examination.form', string='nuropt impression Exam', tracking=True)

class nuroptrecommendation(models.Model):
    _name = 'nuropt.recommendation'
    _rec_name = 'recommendation_nuropt'
    _description = 'nuro pt recommendation'

    recommendation_nuropt = fields.Selection([('Lumbopelvic stabi','Lumbopelvic stabilization program'),('Taping bracing lumbar','Taping bracing lumbar spine as needed for stability'),('Range of motion exercises to lumbar spine','Range of motion exercises to lumbar spine to enhance joint mobility and improve nutrition to spinal segments'),('Range of motion exercises to thora','Range of motion exercises to thoracic spine to improve mobility and nutrition to spinal segments'),('Segmental lumbar st','Segmental lumbar stabilization'),('Thoracic mobi','Thoracic mobilizations'),('Lumbar mobil','Lumbar mobilizations'),('Hip mobili','Hip mobilizations'),('Lumbar trac','Lumbar tractions'),('Stabilization','Stabilization belt for pelvis if necessary'),('S-1 mobilizations','S-1 mobilizations to normalize mechanics'),('Hip range of mot','Hip range of motion exercise'),('Soft tissue mobilization','Soft tissue mobilization pelvic girdle musculature'),('Inhibition and lengthening and stretching of hip','Inhibition and lengthening and stretching of hip musculature to restore normal tone, length, and mobility'),('Lower extremity stretching exercise','Lower extremity stretching exercise in chnic and at home to normalize muscle length'),('Lift short quadrant according','Lift short quadrant according to radiographic findings'),('Natural mobi','Natural mobilization'),('Posture education','Posture education and awareness exercise'),('Instruction in body mechanic','Instruction in body mechanics: lifting, bending, and sitting'),('Gait training when muscle','Gait training when muscle control allows to stabilize pelvis functionally'),('Lower extremity stretching exercise','Lower extremity stretching exercise in chnic and at home to normalize muscle length'),('Lift short quadrant according','Lift short quadrant according to radiographic findings'),('Natural mobi','Natural mobilization'),('Posture education','Posture education and awareness exercise'),('Instruction in body mechanic','Instruction in body mechanics: lifting, bending, and sitting'),('Molded insole','Molded insoles to control foot function'),('Custom orthotics ','Custom orthotics to control abnormal fool function'),('Obtain 3 weight bearings X-rays to determine leg length discrepan','Obtain 3 weight bearings X-rays to determine leg length discrepancy, type and extent of pubic symphysis hypermobility'),('Exercise strength, aerobic capacity, and','Exercise strength, aerobic capacity, and general condition')],string='Clinican Recommendation' , tracking=True)
    pres_freq_nuropt_3 = fields.Char(string='Prescribed Frequency',tracking=True)
    time_per_week_nurop_3 = fields.Char(string = 'Time Per Week',tracking=True)
    remark_nuropt_9 = fields.Text(string='Remark', tracking=True)

    nuropt_recommendation_exam = fields.Many2one('examination.form', string='nuropt recommendation Exam', tracking=True)

class drogaservice(models.Model):
    _inherit = 'product.template'
    detailed_type = fields.Selection([
        ('consu', 'Consumable'),
        ('service', 'Service')], string='Product Type', default='service', required=True,
        help='A storable product is a product for which you manage stock. The Inventory app has to be installed.\n'
             'A consumable product is a product for which stock is not managed.\n'
             'A service is a non-material product you provide.')
    purchase_ok = fields.Boolean('Can be Purchased', default=False)

    service_types = fields.Selection([('evaluation', 'Evaluation'),('Checking','Check')])

    

class drogaCustomerContract(models.Model):
    _name = 'droga.contract'

    compp =  fields.Many2one('customer.class', string='CompCust')
    
    start_date = fields.Date (string = "Start Date")
    end_date = fields.Date("End Date")
    payment_terms = fields.Selection([('yearly', 'Yearly'),('monthly', 'Monthly')])
    service_avaliable = fields.Many2many(comodel_name='product.template',string = 'Services Avaliable')

class drogaMedicalCertifcates(models.Model):
    _name = 'droga.medicalcertifcates'
    _rec_name='mrn'
    _inherit = ['mail.thread', 'mail.activity.mixin', 'image.mixin']
    _order = "create_date desc"


    examination_form = fields.Many2one('examination.form', string='Examination Form')
    
    patient =  fields.Many2one('droga.physio', string='Patient')
    condition=fields.Selection([('ankle','Ankle'),('cervical','Cervical'),('elbow','Elbow'),('elbow wrist','Elbow Wrist'),('hand','Hand'),('knee','Knee'),('lumber','Lumber'),('neuro doc','Nuro Doc'),('neuro pt','Nuro PT'),('post strock','Post Strok'),('shoulder','Shoulder'),('thoractic','Thoractic'),('wrist','Wrist')],"Condition")

    #   patient_name = _id = fields.Many2one('',string='', )
    date = fields.Date()
    # clinicians = fields.Many2one('',string='',)
    sessions = fields.Text(string = "Sessions")
    diagnosis = fields.Text(string = "Diagnosis of Injury")
    recommendation = fields.Text(string = "Physiotherapist's Recommendation")
    clinicians = fields.Many2many('res.users', string='Clinicians')
    date_of_examination = fields.Date("Date of Examination")
    age=fields.Integer("Age", compute="_calculate_age")

    birth_date = fields.Date(related='mrn.birth_date',string="Birth Date")
    sex = fields.Selection(related='mrn.sex', string='Sex')
    
    appointed_t_o=fields.Selection(related='time_1.condition',string="con")
    mrn=fields.Many2one(comodel_name="droga.physio",string="MRN") 
    time_1=fields.Many2one(comodel_name="notebook.class", string="Appointed")

    full_name=fields.Char(related='mrn.full_name',string="Name") 
    Examine_date = fields.Datetime(related='time_1.time', string='Register Date')
    rest_required = fields.Integer(string='Rest Required')
    
    notebook_ids_previous_sesstion = fields.One2many('notebook.class', 'droga_medical_id', string="Notebook")
    @api.depends('birth_date')
    def _calculate_age(self):
        for records in self:
            age=0
            
            birth_date=records.birth_date
            current_date=datetime.today().date()
            if birth_date:
                age=(current_date-birth_date)/timedelta(days=365)
            records.age=age




class drogaClinicians(models.Model):

    _inherit = 'hr.employee'
    clinicians = fields.Boolean(string = "Clinicians")

class referalForm(models.Model):

    _name = 'referal.form'
    _inherit = ['mail.thread', 'mail.activity.mixin', 'image.mixin']
    _order = "create_date desc"


    patient =  fields.Many2one('droga.physio', string='Patient')
    examination_ref=fields.Many2one(comodel_name="examination.form",string="MRN") 
    # mrn=fields.Many2one(comodel_name="droga.physio",string="MRN") 
    mrn=fields.Many2one(related='examination_ref.mrn',string="MRN")
    full_name=fields.Char(related='mrn.full_name',string="Name")

    clinician_refer = fields.Many2one( string="Referring Clinician", related='examination_ref.clinician1', readonly=True)
    chiled_age_in_month = fields.Integer(related='examination_ref.chiled_age',string='Chiled Age In Month')
    chiled_age_in_year = fields.Integer(related='examination_ref.chiled_age_year',string='Chiled Age In Year')
    age = fields.Integer(related='mrn.age',string='Age')
    sex=fields.Selection(related='mrn.sex',string="Gender")
    date = fields.Date("Date")  
    investigation = fields.Text(string = "History, Examination & Investigation")
    physiotherapy_diagnosis = fields.Text(string = "Physiotherapy Diagnosis")
    medical_diagnosis = fields.Text(string="Medical Diagnosis")
    treatment_given = fields.Text(string="Treatment Given")
    reasons_for_referral = fields.Text(string="Reasons for Refferral")
    # clinician1=fields.Many2one(related='patient.appointed_to',string="Clincian") 
    clinician1=fields.Many2one(related="examination_ref.clinician1", string="Clinicial Name")



    sign=fields.Char(string="Sign")
    feed_back=fields.Text(string="Feed Back")

class patientTag(models.Model):
    _name = 'patient.tag'
    _rec_name='name'
    _description = 'Patient Tag'

    name = fields.Char(string='Name', required=True)
    color = fields.Integer(string='Color Index', default=0)
    color_2 = fields.Char(string='Color', default=0)

    active = fields.Boolean(string='Active', default=True)

class catagoriesTag(models.Model):
    _name = 'catagories.tag'
    _rec_name='cata_name'
    _description = 'Catagories Tag'
    

    cata_name = fields.Char(string='Name', required=True)
    cata_color = fields.Integer(string='Color Index', default=0)
    cata_color_2 = fields.Char(string='Color', default=0)

    cata_active = fields.Boolean(string='Active', default=True)

class servicesTag(models.Model):
    _name = 'services.tag'
    _rec_name='service_name'
    _description = 'Services Tag'
    

    service_name = fields.Char(string='Name', required=True)
    service_color = fields.Integer(string='Color Index', default=0)
    service_color_2 = fields.Char(string='Color', default=0)

    service_active = fields.Boolean(string='Active', default=True)


class medekTag(models.Model):
    _name = 'medek.tag.config'
    
    

    name = fields.Char(string='Item or Motor Function', required=True)
    description=fields.Text(string='Description')

class medekTag(models.Model):
    _name = 'medek.tag'
    _rec_name='medek_name'
    _description = 'Medek Tag'
    


    medek_name = fields.Char(string='Item or Motor Function', required=True)
    medek_asses = fields.Selection([('0','No Response'),('1','Minimal Response'),('2','Incomplete Response'),('3','Complete Response')],string='Assessment',default=False)
    medek_control = fields.Char(string='Control', default='')

    medek_e = fields.Many2one('examination.form', string='Examination Form')
    
    functional_age = fields.Float(string="Score", compute="_compute_functional_age", store=True, default="")

    @api.depends('medek_asses')
    def _compute_functional_age(self):
        for record in self:
            total_score = 0
            if record.medek_asses:
                selected_assessments = record.medek_asses.split(',')
                for assessment in selected_assessments:
                    total_score += int(assessment)
            record.functional_age = total_score 
    
class nusingactTag(models.Model):
    _name = 'nursingact.tag.config'
    
    

    name = fields.Char(string='Nursing Activities Prescription', required=True)
    catagories_nurs=fields.Selection([('fi','Fine Motors Skill Activities'),('sia','Sensory Integration Activities'),('sgma','Specific Gross Motor Activities')],string='Catagories',default=False)
    description=fields.Text(string='Description')


class NursingActivitiesTag(models.Model):
    _name = 'nursingactivity.tag'
    _rec_name='nursing_activity_name'
    _description = 'Nursing Activity Tag'
    


    nursing_activity_name = fields.Char(string='Nursing Activities Prescription', required=True)
    wee1 = fields.Text(string='Week 1', default='')
    wee2 = fields.Text(string='Week 2', default='')
    wee3 = fields.Text(string='Week 3', default='')
    wee4 = fields.Text(string='Week 4', default='')
    wee5 = fields.Text(string='Week 5', default='')
    wee6 = fields.Text(string='Week 6', default='')
    wee7 = fields.Text(string='Week 7', default='')
    wee8 = fields.Text(string='Week 8', default='') 
    due_date = fields.Date('Due Date')
    # assigned_to_me = fields.Boolean(string="Assigned to Me", default=False)
    # assigned_nurse = fields.Many2one(comodel_name="res.users", string="Assigned Nurse", readonly=True, store=True)
    nursact_e = fields.Many2one('exercise.exercise', string='Exercise Form')

    @api.depends('due_date')
    def _compute_due_date_state(self):
                today = date.today()
                for record in self:
                    if record.due_date:
                        if record.due_date < today:
                            record.due_date_state = 'overdue'
                        elif record.due_date == today:
                            record.due_date_state = 'due_today'
                        else:
                            record.due_date_state = 'future'
                    else:
                        record.due_date_state = 'no_due_date'

    due_date_state = fields.Selection([
        ('overdue', 'Overdue'),
        ('due_today', 'Due Today'),
        ('future', 'Future'),
        ('no_due_date', 'No Due Date')
    ], compute='_compute_due_date_state', string='Due Date State', store=True)


    # @api.onchange('assigned_to_me')
    # def _onchange_assigned_to_me(self):
    #     if self.assigned_to_me and not self.assigned_nurse:
    #         # Set the assigned nurse to the logged-in user if not already assigned
    #         self.assigned_nurse = self.env.user
    #     elif not self.assigned_to_me:
    #         # Reset the assigned nurse field when the toggle is turned off
    #         self.assigned_nurse = False

    # @api.depends('assigned_to_me')
    # def _compute_assigned_to_me_readonly(self):
    #     for record in self:
    #         record.assigned_to_me_readonly = record.assigned_to_me

    # assigned_to_me_readonly = fields.Boolean(compute='_compute_assigned_to_me_readonly', string="Assigned to Me Readonly")

    # @api.model
    # def create(self, vals_list):
    #     records = super(NursingActivitiesTag, self).create(vals_list)
    #     for record in records:
    #         if record.assigned_to_me:
    #             # Set the assigned nurse to the logged-in user if not already assigned
    #             record.assigned_nurse = self.env.user
    #     return records

    # def write(self, vals):
    #     if 'assigned_to_me' in vals:
    #         # Update the assigned nurse field when the toggle is changed
    #         if vals['assigned_to_me'] and not self.assigned_nurse:
    #             vals['assigned_nurse'] = self.env.user.id
    #         elif not vals['assigned_to_me']:
    #             # Reset the assigned nurse field when the toggle is turned off
    #             vals['assigned_nurse'] = False
    #     return super(NursingActivitiesTag, self).write(vals)
class NursingActivities2Tag(models.Model):
    _name = 'nursingactivity2.tag'
    _rec_name='nursing_activity_name_2'
    _description = 'Nursing Activity Tag'
    


    nursing_activity_name_2 = fields.Char(string='Nursing Activities Prescription 2', required=True)
    wee1 = fields.Html(string='Week 1', default='')
    wee2 = fields.Html(string='Week 2', default='')
    wee3 = fields.Html(string='Week 3', default='')
    wee4 = fields.Html(string='Week 4', default='')
    wee5 = fields.Html(string='Week 5', default='')
    wee6 = fields.Html(string='Week 6', default='')
    wee7 = fields.Html(string='Week 7', default='')
    wee8 = fields.Html(string='Week 8', default='')

    nursact_e_2 = fields.Many2one('exercise.exercise', string='Exercise Form')

    due_date = fields.Date('Due Date')

    @api.depends('due_date')
    def _compute_due_date_state(self):
                today = date.today()
                for record in self:
                    if record.due_date:
                        if record.due_date < today:
                            record.due_date_state = 'overdue'
                        elif record.due_date == today:
                            record.due_date_state = 'due_today'
                        else:
                            record.due_date_state = 'future'
                    else:
                        record.due_date_state = 'no_due_date'

    due_date_state = fields.Selection([
        ('overdue', 'Overdue'),
        ('due_today', 'Due Today'),
        ('future', 'Future'),
        ('no_due_date', 'No Due Date')
    ], compute='_compute_due_date_state', string='Due Date State', store=True)

class NursingActivities3Tag(models.Model):
    _name = 'nursingactivity3.tag'
    _rec_name='nursing_activity_name_3'
    _description = 'Nursing Activity Tag'
    


    nursing_activity_name_3 = fields.Char(string='Nursing Activities Prescription 3', required=True)
    wee1 = fields.Html(string='Week 1', default='')
    wee2 = fields.Html(string='Week 2', default='')
    wee3 = fields.Html(string='Week 3', default='')
    wee4 = fields.Html(string='Week 4', default='')
    wee5 = fields.Html(string='Week 5', default='')
    wee6 = fields.Html(string='Week 6', default='')
    wee7 = fields.Html(string='Week 7', default='')
    wee8 = fields.Html(string='Week 8', default='')

    nursact_e_3 = fields.Many2one('exercise.exercise', string='Exercise Form')
    due_date = fields.Date('Due Date')

    @api.depends('due_date')
    def _compute_due_date_state(self):
                today = date.today()
                for record in self:
                    if record.due_date:
                        if record.due_date < today:
                            record.due_date_state = 'overdue'
                        elif record.due_date == today:
                            record.due_date_state = 'due_today'
                        else:
                            record.due_date_state = 'future'
                    else:
                        record.due_date_state = 'no_due_date'

    due_date_state = fields.Selection([
        ('overdue', 'Overdue'),
        ('due_today', 'Due Today'),
        ('future', 'Future'),
        ('no_due_date', 'No Due Date')
    ], compute='_compute_due_date_state', string='Due Date State', store=True)
    
class chiledbehaviourconfi(models.Model):
    _name = 'chiled.behavior.config'
    
    

    name = fields.Char(string='Activity', required=True)
    catagories_assess=fields.Selection([('att','Attention'),('rea','Reading'),('ma','Math'),('lan','Language'),('oth','Others')],string='Catagories',default=False)
    description=fields.Text(string='Description')


class chiledbehavior(models.Model):
    _name = 'chiled.behavior.tag'
    _rec_name='chiled_assesment'
    _description = 'Child Behaviour Assessment'
    


    chiled_assesment= fields.Char(string='Activity', required=True)
    chiled_condition= fields.Selection([('not','Not True'),('swt','Somewhat True'),('ct','Certainly True')],string='Condition',default=False)
    chiled_b = fields.Many2one('behaviour.assessment', string='child Form')

class chiledbehavior2(models.Model):
    _name = 'chiled.behavior.tag2'
    _rec_name='chiled_assesment_2'
    _description = 'Child Behaviour Assessment 2'
    


    chiled_assesment_2= fields.Char(string='Activity', required=True)
    chiled_condition_2= fields.Selection([('not','Not True'),('swt','Somewhat True'),('ct','Certainly True')],string='Condition',default=False)
    chiled_b_2 = fields.Many2one('behaviour.assessment', string='child Form 2')

class chiledbehavior3(models.Model):
    _name = 'chiled.behavior.tag3'
    _rec_name='chiled_assesment_3'
    _description = 'Child Behaviour Assessment 3'
    


    chiled_assesment_3= fields.Char(string='Activity', required=True)
    chiled_condition_3= fields.Selection([('not','Not True'),('swt','Somewhat True'),('ct','Certainly True')],string='Condition',default=False)
    chiled_b_3 = fields.Many2one('behaviour.assessment', string='child Form 3')

class chiledbehavior4(models.Model):
    _name = 'chiled.behavior.tag4'
    _rec_name='chiled_assesment_4'
    _description = 'Child Behaviour Assessment 4'
    


    chiled_assesment_4= fields.Char(string='Activity', required=True)
    chiled_condition_4= fields.Selection([('not','Not True'),('swt','Somewhat True'),('ct','Certainly True')],string='Condition',default=False)
    chiled_b_4 = fields.Many2one('behaviour.assessment', string='child Form 4')

class chiledbehavior5(models.Model):
    _name = 'chiled.behavior.tag5'
    _rec_name='chiled_assesment_5'
    _description = 'Child Behaviour Assessment 5'
    


    chiled_assesment_5= fields.Char(string='Activity', required=True)
    chiled_condition_5= fields.Selection([('not','Not True'),('swt','Somewhat True'),('ct','Certainly True')],string='Condition',default=False)
    chiled_b_5 = fields.Many2one('behaviour.assessment', string='child Form 5')


class examinationForm(models.Model):


    _name = 'examination.form'
    _rec_name='mrn'
    _inherit = ['mail.thread', 'mail.activity.mixin', 'image.mixin']
    _order = "create_date desc"




    # appo = fields.One2many('appointment.set', 'mrn', string='Notebook')
    appo=fields.One2many('appointment.set', 'appointment', string='Notebook')
    nurse=fields.One2many('nursing.evaluation', 'appointment_nursing', string='nursing evaluation')
    behaviour=fields.One2many('behaviour.assessment', 'exa_behaviour', string='nursing evaluation')
    physic = fields.One2many('physical.therapy', 'exa_physical', string='Physical Therapy')
    physician_con = fields.One2many('physician.consultation', 'exa_physician_cons', string='Physician Consultation')
    exerci=fields.One2many('exercise.exercise', 'examin', string='Exercise')
    refer=fields.One2many('referal.form', 'examination_ref', string='Referal')
    # product_tem=fields.One2many(comodel_name='product.calculate', inverse_name='pro_pro', string='Exercise')
    # product_tem=fields.One2many(comodel_name='product.calculate', inverse_name='pro_pro', string='Exercise')
    # field_name_ids = fields.One2many('comodel_name', 'inverse_field_name', string='field_name')



    
    status_app = fields.Selection(related='appo.status', string='Status')
    ttu_1=fields.Text(string="")
    ttu=fields.Html(string="",palceholder="Functional Age")
    total = fields.Float(string='Total Price', compute='_compute_price')
    # patient =  fields.Many2one('droga.physio', string='Patient')
    mrn = fields.Many2one(
        comodel_name="droga.physio",
        string="MRN",
        ondelete="cascade",

    )
    patient_name =fields.Char(related="mrn.full_name",string="Patient Name", tracking=True)
    case_e =fields.Many2many(related="mrn.tags_s",string="Case", tracking=True)
    catagori = fields.Many2many(related="mrn.tags_cata",string="Catagories", tracking=True)
    serv = fields.Many2many(related="mrn.tags_services",string="Services", tracking=True)
    sub_service = fields.Html(string="Sub Services", tracking=True)
    mede_k = fields.One2many('medek.tag','medek_e',string="Medek", tracking=True)
    clinician_information = fields.Text(string="Clinician Information", compute="_compute_clinician_information")
    chiled_age = fields.Integer(related="mrn.age_in_months",string="Chiled Age in Month", tracking=True)
    chiled_age_year = fields.Integer(related="mrn.age",string="Chiled Age in Year", tracking=True)
    date = fields.Date(related="mrn.register_date" ,string="Date", tracking=True)  
    clinician1=fields.Many2one(comodel_name="hr.employee",string="Clincian")  
    cc = fields.Text(string = "C/C", tracking=True)
    hpi = fields.Text(string= "HPI", help = "HPI(pain location, types, radiate, severity, timing,weight change,sleep disturbance)", tracking=True)
    rpmh = fields.Text(string="RPMH", tracking=True)
    dignostics_imaging_finding = fields.Text(string="Diagnostics and Imaging Finding ", tracking=True)
    observation = fields.Text(string="Observation", tracking=True)
    palpation = fields.Text(string="Palpation", tracking=True)
    rom=fields.Text(string="ROM/Flexibility", tracking=True)
    lld=fields.Text(string="LLD", tracking=True)
    mmt=fields.Text(string="MMT", tracking=True)
    reflex=fields.Text(string="Reflex", tracking=True)
    sensory=fields.Text(string="Sensory", tracking=True)
    special_test=fields.Text(string="Special Test", tracking=True)
    function=fields.Text(string="Function Activities Limitation", tracking=True)
    pt=fields.Text(string="PT Dx", tracking=True)
    treatment=fields.Text(string="Treatment Plan", tracking=True)
    medical_diagnosis = fields.Html(string="Medical Diagnosis", tracking=True)
    record = fields.Html(string="Record", tracking=True)
    prenatals = fields.Html(string="Prenatal", tracking=True)
    postnatals = fields.Html(string="Postnatal", tracking=True)
    muscletone = fields.Html(string="Muscle Tone", tracking=True)
    reflexes = fields.Html(string="Reflexes", tracking=True)
    skeletal_condition = fields.Html(string="Skeletal Condition", tracking=True)
    initial_cme_program = fields.Html(string="Initial CME Program", tracking=True)
    pre_session = fields.One2many('note.preclass' ,'prej', string='Notebook', tracking=True)
    impre_clicni = fields.One2many('clinician.impressionelbow','rom_impression' , string='clinician impression', tracking=True)
    muscl_flex = fields.One2many('muscle.flexiability','rom_muscle' , string='muscle flexability', tracking=True)
    structu = fields.One2many('structural.hand','rom_struct' , string='structure', tracking=True)
    exam_rom = fields.One2many('rom.hand' ,'rom_exam', string='Exa Rom', tracking=True)
    exam_strength = fields.One2many('strength.hand' ,'strength_exam', string='Exa strength', tracking=True)
    exam_strength_lumbar = fields.One2many('lumbar.strength' ,'lumbar_strength_exam', string='Exa strength', tracking=True)
    exam_protect_lumbar = fields.One2many('lumbar.protective' ,'lumbar_protect_exam', string='Exa Protect lumbar', tracking=True)
    exam_rom_lumbar = fields.One2many('lumbar.rom' ,'lumbar_rom_exam', string='Exa Rom lumbar', tracking=True)
    exam_bio_lumbar = fields.One2many('lumbar.bio' ,'lumbar_bio_exam', string='Exa Rom lumbar', tracking=True)
    exam_exterm_lumbar = fields.One2many('lumbar.exterimity' ,'lumbar_exterm_exam', string='Exa Extermity lumbar', tracking=True)
    exam_impression_lumbar = fields.One2many('clinician.impressionlumbar' ,'lumbar_impression', string='Exa impression lumbar', tracking=True)
    exam_recommendation_lumbar = fields.One2many('clinician.recommendationlumbar' ,'lumbar_recommendation', string='Exa recommendation lumbar', tracking=True)
    exam_ankel = fields.One2many('ankel.strength' ,'ankel_strength_exam', string='Exa recommendation Ankel', tracking=True)
    exam_ankel_rom = fields.One2many('ankle.rom' ,'ankle_rom_exam', string='Exa Rom Ankel', tracking=True)
    exam_ankel_bio = fields.One2many('ankle.biomechanical' ,'ankle_bio_exam', string='Exa Bio Ankel', tracking=True)
    exam_ankel_muscle = fields.One2many('ankle.muscleflexibility' ,'ankle_muscleflexi_exam', string='Exa muscle Ankel', tracking=True)
    exam_ankel_paplation = fields.One2many('ankle.palpation' ,'ankle_palpation_exam', string='Exa muscle Ankel', tracking=True)
    exam_ankel_impression = fields.One2many('clinician.impressionankle' ,'ankle_impression', string='Exa Impression Ankel', tracking=True)
    exam_ankel_recommendation = fields.One2many('clinician.recommendationankle' ,'ankle_recommendation', string='Exa Impression Ankel', tracking=True)
    exam_cervical = fields.One2many('cervical.strength' ,'cervical_strength_exam', string='Exa cervical', tracking=True)
    exam_cervical_rom = fields.One2many('cervical.rom' ,'cervical_rom_exam', string='Exa cervical rom', tracking=True)
    exam_cervical_bio = fields.One2many('cervical.biomechanical' ,'cervical_bio_exam', string='Exa cervical rom', tracking=True)
    exam_cervical_test = fields.One2many('cervical.test' ,'cervical_test_exam', string='Exa cervical rom', tracking=True)
    exam_cervical_muscle = fields.One2many('cervical.muscleflexibility' ,'cervical_muscleflexi_exam', string='Exa cervical Muscle', tracking=True)
    exam_cervical_palpation = fields.One2many('cervical.palpation' ,'cervical_palpation_exam', string='Exa cervical palpation', tracking=True)
    exam_cervical_immpression = fields.One2many('clinician.impressioncervical' ,'cervical_impression', string='Exa cervical immpresion', tracking=True)
    exam_cervical_recommendation = fields.One2many('clinician.recommendationcervical' ,'cervical_recommendation', string='Exa cervical recommendation', tracking=True)
    exam_shoulder = fields.One2many('shoulder.rom' ,'shoulder_rom_exam', string='Exa Shoulder ', tracking=True)
    exam_shoulder_accessory = fields.One2many('shoulder.accessory' ,'shoulder_accessory_exam', string='Exa Shoulder accessory', tracking=True)
    exam_shoulder_mmt = fields.One2many('shoulder.mmt' ,'shoulder_mmt_exam', string='Exa Shoulder MMT', tracking=True)
    exam_shoulder_palpation = fields.One2many('shoulder.palpation' ,'shoulder_palpation_exam', string='Exa Shoulder palpation', tracking=True)
    exam_shoulder_isometric = fields.One2many('shoulder.isometric' ,'shoulder_isometric_exam', string='Exa Shoulder Isometric', tracking=True)
    exam_shoulder_impression = fields.One2many('shoulder.impressions' ,'shoulder_impression_exam', string='Exa Shoulder Impression', tracking=True)
    exam_shoulder_recommendation = fields.One2many('shoulder.recommendation' ,'shoulder_recommednation_exam', string='Exa Shoulder Impression', tracking=True)
    exam_knee_strength = fields.One2many('knee.strength' ,'knee_strength_exam', string='Exa Knee strength', tracking=True)
    exam_knee_rom = fields.One2many('knee.rom' ,'knee_rom_exam', string='Exa Knee strength', tracking=True)
    exam_knee_biomech = fields.One2many('knee.biomechanical' ,'knee_biomechanical_exam', string='Exa Knee Biomechanical', tracking=True)
    exam_knee_specialtest = fields.One2many('knee.specialtest' ,'knee_specialtest_exam', string='Exa Knee Special Test', tracking=True)
    exam_knee_girth = fields.One2many('knee.girth' ,'knee_girth_exam', string='Exa Knee Girth', tracking=True)
    exam_knee_impression = fields.One2many('knee.impressions' ,'knee_impressions_exam', string='Exa Knee Impression', tracking=True)
    exam_knee_recommendation = fields.One2many('knee.recommendation' ,'knee_recommednation_exam', string='Exa Knee Impression', tracking=True)
    exam_knee_incision = fields.One2many('knee.incision' ,'knee_incision_exam', string='Exa Knee Impression', tracking=True)
    exam_thoracic = fields.One2many('thoracic.strength' ,'thoracic_strength_exam', string='Exa thoracic strength', tracking=True)
    exam_thoracic_rom = fields.One2many('thoracic.rom' ,'thoracic_rom_exam', string='Exa thoracic strength', tracking=True)
    exam_thoracic_biomechanical = fields.One2many('thoracic.biomechanical' ,'thoracic_biomechanical_exam', string='Exa thoracic biomechanical', tracking=True)
    exam_thoracic_lumbar = fields.One2many('thoracic.lumbar' ,'thoracic_lumbar_exam', string='Exa thoracic lumbar', tracking=True)
    exam_thoracic_tho = fields.One2many('thoracic.tho' ,'thoracic_tho_exam', string='Exa thoracic tho', tracking=True)
    exam_thoracic_palpation = fields.One2many('thoracic.palpation' ,'thoracic_palpation_exam', string='Exa thoracic palpation', tracking=True)
    exam_thoracic_impressions = fields.One2many('thoracic.impressions' ,'thoracic_impressions_exam', string='Exa thoracic impression', tracking=True)
    exam_thoracic_recommendation = fields.One2many('thoracic.recommendation' ,'thoracic_recommednation_exam', string='Exa thoracic recommendation', tracking=True)
    exam_nuropt_muscletone = fields.One2many('nuropt.muscletone' ,'nuropt_muscletone_exam', string='Exa nuropt muscletone', tracking=True)
    exam_nuropt_sensation = fields.One2many('nuropt.sensation' ,'nuropt_sensation_exam', string='Exa nuropt sensation', tracking=True)
    exam_nuropt_consciousness = fields.One2many('nuropt.consciousness' ,'nuropt_consciousness_exam', string='Exa nuropt consciousness', tracking=True)
    exam_nuropt_motor = fields.One2many('nuropt.motor' ,'nuropt_motor_exam', string='Exa nuropt motor', tracking=True)
    exam_nuropt_listoffunction = fields.One2many('nuropt.listoffunction' ,'nuropt_listoffunction_exam', string='Exa nuropt listoffunction', tracking=True)
    exam_nuropt_balance = fields.One2many('nuropt.balance' ,'nuropt_balance_exam', string='Exa nuropt balance', tracking=True)
    exam_nuropt_musclepow = fields.One2many('nuropt.musclepow' ,'nuropt_musclepow_exam', string='Exa nuropt musclepow', tracking=True)
    exam_nuropt_reflex = fields.One2many('nuropt.reflex' ,'nuropt_reflex_exam', string='Exa nuropt reflex', tracking=True)
    exam_nuropt_asia = fields.One2many('nuropt.asia' ,'nuropt_asia_exam', string='Exa nuropt asia', tracking=True)
    exam_nuropt_immpression = fields.One2many('nuropt.immpression' ,'nuropt_immpression_exam', string='Exa nuropt immpression', tracking=True)
    exam_nuropt_recommendation = fields.One2many('nuropt.recommendation' ,'nuropt_recommendation_exam', string='Exa nuropt recommendation', tracking=True)





    exam_immpression = fields.One2many('clinician.recommendation' ,'rom_recommendation', string='Exa recommendation', tracking=True)



    pre_session_product = fields.One2many('product.calculate.product' ,'pro_pro', string='Product cal', tracking=True)
    sex=fields.Selection(related='mrn.sex',string="Gender", tracking=True)
    age=fields.Integer(related='mrn.age',string='Age', tracking=True)
    weight=fields.Integer(string='Weight', tracking=True)
    Diagnosis=fields.Char(string='Diagnosis', tracking=True)
    invetiget=fields.One2many('investigation.form','mrn',string='Investigation')
    certeficate=fields.One2many('droga.medicalcertifcates','examination_form',string='Medical Certifcates')

    note_nuro_doc = fields.Text(string='Note', tracking=True)
    sergical_nuro_doc = fields.Text(string='Past Medical and Surgical Illness', tracking=True)
    physical_nuro_doc = fields.Text(string='Physical Examination', tracking=True)
    heent_nuro_doc = fields.Text(string='HEENT', tracking=True)
    egs_nuro_doc = fields.Text(string='EGS', tracking=True)
    chest_nuro_doc = fields.Text(string='Chest', tracking=True)
    cvs_nuro_doc = fields.Text(string='CVS', tracking=True)
    abdomen_nuro_doc = fields.Text(string='Abdomen', tracking=True)
    gus_nuro_doc = fields.Text(striing='GUS', tracking=True)
    mss_nuro_doc = fields.Text(string='MSS',tracking=True)
    intergumentary_nuro_doc = fields.Text(string='Intergumentary',tracking=True)
    # nurology_nuro_doc = fields.Text(string='Nurology',tracking=True)
    consciousness_nurology_nuro_doc = fields.Text(string='Consciousness' ,tracking=True)
    cranial_nerve_nurology_nuro_doc = fields.Text(string='Caranial Nerve', tracking=True)
    motor_nurology_nuro_doc = fields.Text(string='Motor', tracking=True)
    sensory_nurology_nuro_doc = fields.Text(string='Sensory' , tracking=True)
    cordination_nurology_nuro_doc = fields.Text(string='Cordination' , tracking=True)
    gaut_nurology_nuro_doc = fields.Text(string='Gaut', tracking=True)
    other_nurology_nuro_doc = fields.Text(string='Other' ,tracking=True)
    assessment_nuro_doc = fields.Text(string='Assessment' ,tracking=True)
    treatment_nuro_doc = fields.Text(string='Treatment',tracking=True)
    plan_nuro_doc = fields.Text(string='Plan',tracking=True)
    nurological_defect = fields.Boolean(string='No Nurological Defect', default=False, tracking=True)
    nurological_remark = fields.Text(string='Remark', tracking=True)
    functional_age_total=fields.Float(string="Fuctional Age", compute="_compute_functional_age")
    chronical_age = fields.Char(string='Chronical Age of Months', tracking=True)
    functional_gap = fields.Char(string='Functional Gap of Months', tracking=True)
    services_case = fields.Selection([('cp','Cerebral Palsy'),('gdd','Gross Developmental Delay'),('ap','Apraxia'),('bpi','Brachial Plexus Injury'),('aa','Ataxia'),('bi','Brain Injury'),('ep','Epilepsies'),('sb','Spinal Bifidal'),('ds','Down Syndrome'),('cf','Club Foot'),('pmd','Pediatric Movement Disorder'),('td','Tone Disorders'),('sld','Speech and Language Disorder'),('bd','Behavioral Disorders')],string='Services', tracking=True)

    show_nurological_defect_details = fields.Boolean(string='Show nurological defect Details', compute='_compute_show_nurological_defect_details', store=False, tracking=True)

    # company_id = fields.Many2one('res.company', required=True , default=lambda  self: self.env.user.company_id)
    company_id = fields.Many2one('res.company', required=True , default=lambda  self: self.env.user.company_id)
    

    @api.model
    def _search(self, args, offset=0, limit=None, order=None, count=False, access_rights_uid=None):
        user = self.env['res.users'].browse(self.env.uid)
        if self.env.context.get('user_company_id'):
            user_company_id = user.company_id.id
            args += ['|', ('company_id', '=', False), ('company_id', 'child_of', user_company_id)]
        return super(examinationForm, self)._search(args, offset=offset, limit=limit, order=order, count=count, access_rights_uid=access_rights_uid)
    # def action_notify(self):
    #     for rec in self:
    #         if rec.clinician1.user_id:
    #             partner = rec.clinician1.user_id.partner_id
    #             if partner:

    #                 rec.message_post(body="You have new Appointment")
    
    def compute_create_medk(self):
        medek= self.env['medek.tag.config'].search([('name', '!=', '')])
        for record in medek:
            check_medek=self.env['medek.tag'].search([('medek_name','=',record.name),('medek_e','=',self.id)])
            if not check_medek :
                detail_nurs_activies=self.env['medek.tag'].create({'medek_name':record.name,
                'medek_e':self.id,
                })

    def link_medek_tags(self, medek_control_values, medek_asses_values):
        # Assume medek_control_values and medek_asses_values are dictionaries mapping medek.tag IDs to values
        for medek_tag_id, control_value in medek_control_values.items():
            for asses_value in medek_asses_values.get(medek_tag_id, []):
                # Store the mapping somewhere, e.g., in a separate model or a dictionary
                self.linked_medek_tags[medek_tag_id] = {'control': control_value, 'asses': asses_value}
    
    @api.depends('mede_k.medek_asses')
    def _compute_functional_age(self):
        for record in self:
            total_score = sum(int(tag.medek_asses) for tag in record.mede_k if tag.medek_asses)
            if total_score:
                record.functional_age_total = total_score / 7.6
            else:
                record.functional_age_total = 0.0

    @api.depends('mede_k')
    def _compute_clinician_information(self):
        for record in self:
            medek_names = ', '.join(record.mede_k.mapped('medek_name'))
            record.clinician_information = medek_names

    def action_notify(self):
        for rec in self:
            rec.clinician1.user_id.notify_info(message="Doc Notify - You have new Appointment")
            
            if rec.clinician1.user_id:
                partner = rec.clinician1.user_id.partner_id
                if partner:

                    rec.message_post(body="You have new Appointment", sticky=True)
    @api.depends('nurological_defect')
    def _compute_show_nurological_defect_details(self):
        for record in self:
            record.show_nurological_defect_details = record.nurological_defect

    @api.onchange('nurological_defect')
    def _onchange_nurological_defect(self):
        if not self.nurological_defect:
            self.nurological_defect = False

    forward_bend = fields.Boolean(string='Forward Bend', default=False, tracking=True)
    forward_bend_remark = fields.Text(string='Remark', tracking=True)

    show_forward_bend_details = fields.Boolean(string='Show forward bend Details', compute='_compute_show_forward_bend_details', store=False, tracking=True)

    @api.depends('forward_bend')
    def _compute_show_forward_bend_details(self):
        for record in self:
            record.show_forward_bend_details = record.forward_bend

    @api.onchange('forward_bend')
    def _onchange_forward_bend(self):
        if not self.forward_bend:
            self.forward_bend = False

    backward_bend = fields.Boolean(string='Backward Bend', default=False, tracking=True)
    backward_bend_remark = fields.Text(string='Remark', tracking=True)

    show_backward_bend_details = fields.Boolean(string='Show Backward bend Details', compute='_compute_show_backward_bend_details', store=False, tracking=True)

    @api.depends('backward_bend')
    def _compute_show_backward_bend_details(self):
        for record in self:
            record.show_backward_bend_details = record.backward_bend

    @api.onchange('backward_bend')
    def _onchange_backward_bend(self):
        if not self.backward_bend:
            self.backward_bend = False

    appointment_count = fields.Integer(compute='_compute_appointment_count', string='Total Appointment')
    duration = fields.Float(related='appo.dur_ation',string='Duration')
    def _compute_appointment_count(self):
        for record in self:
            record.appointment_count = self.env['appointment.set'].search_count([('mrn', '=', record.mrn.id)])
    
    state = fields.Selection([ ('draft', 'Draft'), ('done', 'Done'), ('cancel', 'Cancelled')], default='draft', index=True, required=True, string="Status")

    neuro_doc_status = fields.Char(compute='_compute_neuro_doc_status', string='Neuro Doc Status')

    def action_appointment_count(self):
        return
    @api.depends('case_e')
    def _compute_neuro_doc_status(self):
        for record in self:
            record.neuro_doc_status = 'present' if any(tag.name == "Neuro doc" for tag in record.case_e) else 'absent'

    elbow_restand_status = fields.Char(compute='_compute_elbow_restand_status', string='Elbow Restand Status')

    @api.depends('case_e')
    def _compute_elbow_restand_status(self):
        for record in self:
            record.elbow_restand_status = 'present' if any(tag.name == "Elbow Restand" for tag in record.case_e) else 'absent'

    lumbar_status = fields.Char(compute='_compute_lumbar_status', string='Lumbar Status')

    @api.depends('case_e')
    def _compute_lumbar_status(self):
        for record in self:
            record.lumbar_status = 'present' if any(tag.name == "Lumbar" for tag in record.case_e) else 'absent'

    ankel_status = fields.Char(compute='_compute_ankel_status', string='Ankle Status')

    @api.depends('case_e')
    def _compute_ankel_status(self):
        for record in self:
            record.ankel_status = 'present' if any(tag.name == "Ankle" for tag in record.case_e) else 'absent'

    cervical_status = fields.Char(compute='_compute_cervical_status', string='cervical Status')

    @api.depends('case_e')
    def _compute_cervical_status(self):
        for record in self:
            record.cervical_status = 'present' if any(tag.name == "Cervical" for tag in record.case_e) else 'absent'

    shoulder_status = fields.Char(compute='_compute_shoulder_status', string='Shoulder Status')

    @api.depends('case_e')
    def _compute_shoulder_status(self):
        for record in self:
            record.shoulder_status = 'present' if any(tag.name == "Shoulder" for tag in record.case_e) else 'absent'

    knee_status = fields.Char(compute='_compute_knee_status', string='Knee Status')

    @api.depends('case_e')
    def _compute_knee_status(self):
        for record in self:
            record.knee_status = 'present' if any(tag.name == "Knee" for tag in record.case_e) else 'absent'

    thoracic_status = fields.Char(compute='_compute_thoracic_status', string='Thoracic Status')

    @api.depends('case_e')
    def _compute_thoracic_status(self):
        for record in self:
            record.thoracic_status = 'present' if any(tag.name == "Thoracic" for tag in record.case_e) else 'absent'

    nurology_status = fields.Char(compute='_compute_nurology_status', string='Nurology Status')

    @api.depends('case_e')
    def _compute_nurology_status(self):
        for record in self:
            record.nurology_status = 'present' if any(tag.name == "Neuro Pt" for tag in record.case_e) else 'absent'
    # state_appo = fields.Selection([ ('draft', 'Draft'), ('done', 'Done'), ('cancel', 'Cancelled')], default='draft', index=True, required=True, string="Status")
    # image_url = fields.Char(compute='_compute_image_url', string='Image URL')

    #nursing_evaluation_id = fields.Many2one(comodel_name="nursing.evaluation", string="Nursing Evaluation", ondelete="cascade")

    # def action_confirm_appo(self):
    #     self.state_appo = 'done'
    # def action_cancel_appo(self):
    #     self.state_appo = 'cancel'
    def action_confirm(self):
        self.state = 'done'
    def action_cancel(self):
        self.state = 'cancel'
    def view_nursing_evaluation(self):
        return {
            'name': 'Nursing Evaluation',
            'view_type': 'form',
            'view_mode': 'form',
            'res_model': 'nursing.evaluation',
            'res_id': self.nurse.id,
            'type': 'ir.actions.act_window',
            'context': {
            'default_appointment_nursing': self.id,
            'default_mrn': self.mrn.id,
            'default_full_name': self.patient_name,
            'default_age': self.age,	
        
            'default_clinical_name': self.clinician1.id,
            
        },
        'domain': [('appointment_nursing', '=', self.id)],
        }

    def view_chiled_behaviour(self):
        return {
            'name': 'Chiled Behaviour Assessment',
            'view_type': 'form',
            'view_mode': 'form',
            'res_model': 'behaviour.assessment',
            'res_id': self.behaviour.id,
            'type': 'ir.actions.act_window',
            'context': {
            'default_exa_behaviour': self.id,
            'default_mrn': self.mrn.id,
            'default_full_name': self.patient_name,
            'default_age': self.age,	
        
            'default_clinical_name': self.clinician1.id,
            
        },
        'domain': [('exa_behaviour', '=', self.id)],
        }

    def view_physical_thrapy(self):
        return {
            'name': 'Physical Therapy',
            'view_type': 'form',
            'view_mode': 'form',
            'res_model': 'physical.therapy',
            'res_id': self.physic.id,
            'type': 'ir.actions.act_window',
            'context': {
            'default_exa_physical': self.id,
            'default_mrn': self.mrn.id,
            'default_full_name': self.patient_name,
            'default_age': self.age,	
        
            'default_clinical_name': self.clinician1.id,
            
        },
        'domain': [('exa_physical', '=', self.id)],
        }
    def view_physician_consultation(self):
        return {
            'name': 'Physican Consultation',
            'view_type': 'form',
            'view_mode': 'form',
            'res_model': 'physician.consultation',
            'res_id': self.physician_con.id,
            'type': 'ir.actions.act_window',
            'context': {
            'default_exa_physician_cons': self.id,
            'default_mrn': self.mrn.id,
            'default_full_name': self.patient_name,
            'default_age': self.age,	
        
            'default_clinical_name': self.clinician1.id,
            
        },
        'domain': [('exa_physician_cons', '=', self.id)],
        }
    @api.depends('mrn')
    def _compute_image_url(self):
        for record in self:
            record.image_url = '/D-Physiotherapy/static/description/body.png'

    def open_investigation(self):
        view = self.env.ref('D-Physiotherapy_d.investigation_form_view_form')
        return {
        'name': 'Investigation Form',
        'view_mode': 'form',
        'res_model': 'investigation.form',
        'view_id': view.id,
        'type': 'ir.actions.act_window',
        'context': {
            'default_examination': self.id,
            'default_mrn': self.mrn.id,
            'default_full_name': self.patient_name,
            'default_age': self.age,	
        
            'default_clinical_name': self.clinician1.id,
            
        },
        'domain': [('examination', '=', self.id)],
        # 'target': 'new',
        }  

    is_clinician_or_nurse = fields.Boolean(compute='_compute_is_clinician_or_nurse')

    @api.depends()
    def _compute_is_clinician_or_nurse(self):
        for record in self:
            record.is_clinician_or_nurse = self.env.user.has_group('D-Physiotherapy_d.group_clinician') or self.env.user.has_group('D-Physiotherapy_d.group_nurse')
    @api.depends('pre_session_product','pre_session_product.total')
    def _compute_price(self):
        for record in self:
           
            total =0
            
            for records in record.pre_session_product:
             
             total+=records.total
               
    
            record.total=total
    
    def open_medical(self):
        view = self.env.ref('D-Physiotherapy_d.droga_medicalcertifcates_view_form')
        return {
        'name': 'Medical Certifcates',
        'view_mode': 'form',
        'res_model': 'droga.medicalcertifcates',
        'view_id': view.id,
        'type': 'ir.actions.act_window',
        'context': {
            'default_examination_form': self.id,
            'default_mrn': self.mrn.id,
            'default_full_name': self.patient_name,
            'default_age': self.age,	
           
            'default_clinical_name': self.clinician1.id,
                
         },
        'domain': [('examination', '=', self.id)],
        # 'target': 'new',
        }   
    def open_Exercise(self):
        return {
            'name': 'Exercise Form',
            'view_type': 'form',
            'view_mode': 'form',
            'res_model': 'exercise.exercise',
            'res_id': self.exerci.id,
            'type': 'ir.actions.act_window',
            'context': {
            'default_examin': self.id,
            'default_mrn': self.mrn.id,
            'default_full_name': self.patient_name,
            'default_age': self.age,	
        
            'default_clinical_name': self.clinician1.id,
            
        },
        'domain': [('examin', '=', self.id)],
        }
    def referal_form(self):
        
        return {
        'name': 'Referal Form',
        'view_type': 'form',
        'view_mode': 'form',
        'res_model': 'referal.form',
        'res_id': self.refer.id,

        'type': 'ir.actions.act_window',
        'context': {
            'default_examination_ref': self.id,
            'default_mrn': self.mrn.id,
            'default_full_name': self.patient_name,
            'default_age': self.age,	
         
            'default_clinical_name': self.clinician1.id,
                
         },
        'domain': [('examination_ref', '=', self.id)],
        # 'target': 'new',
        }   

    def action_cancel_appointment_wizard(self):
        # This method opens the CancelAppointmentWizard
        return {
            'type': 'ir.actions.act_window',
            'res_model': 'cancel.appointment.wizard',
            'view_mode': 'form',
            'target': 'new',
        }

    is_chiled_nurse = fields.Boolean(
        string="Is Chiled Nurse",
        compute='_compute_is_chiled_nurse',
        store=False
    )

    def _compute_is_chiled_nurse(self):
        group_partimer = self.env.ref('D-Physiotherapy_d.group_partimer')
        for record in self:
            record.is_chiled_nurse = group_partimer in self.env.user.groups_id
    


class CancelAppointmentWizard(models.TransientModel):
    _name = 'cancel.appointment.wizard'
    _description = 'Cancel Appointment Wizard'

    appointment_id = fields.Many2one('examination.form', string='MRN', required=True)
    date
    reason = fields.Text(string='Reason', required=True)

    def action_cancel(self):
        return


class investigationform(models.Model):

    _name='investigation.form'
    _rec_name='mrn'
    _inherit = ['mail.thread', 'mail.activity.mixin', 'image.mixin']
    _order = "create_date desc"


    examination=fields.Many2one(comodel_name="examination.form",string="MRN") 
    mrn=fields.Many2one(related='examination.mrn',string="MRN")

    full_name=fields.Char(related='mrn.full_name',string="Name", tracking=True)
    date = fields.Date() 
    age=fields.Integer("Age", compute="_calculate_age", tracking=True)
   
    birth_date = fields.Date(related='mrn.birth_date',string="Birth Date", tracking=True)
    sex = fields.Selection(related='mrn.sex', string='Sex', tracking=True)
    investigation_requested = fields.Text(string = "Investigation Requested", tracking=True)
    clinical_data = fields.Text(string = "Clinical Data", tracking=True)
    Clinical_dx = fields.Text(string = "Clinical Dx", tracking=True)
    clinical_name=fields.Many2one(related="examination.clinician1", string="Clinicial Name")
    sign=fields.Char(string="Sign", tracking=True)
    
    @api.depends('birth_date')
    def _calculate_age(self):
        for records in self:
            age=0
            
            birth_date=records.birth_date
            current_date=datetime.today().date()
            if birth_date:
                age=(current_date-birth_date)/timedelta(days=365)
            records.age=age
    
class pains(models.Model):

    _name='physio.complian.pains'
    name=fields.Char(string="Chief Complain")

class PhysioNeurology(models.Model):

    _name='physio.neurology'
    name=fields.Char(string="Neurology")

class MedicalHistory(models.Model):

    _name='medical.history'
    name=fields.Char(string="Medical History")

class PhysioNeurology(models.Model):

    _name='physio.neurology'
    name=fields.Char(string="Chief Complain")

# class ReceptionAppointment(models.Model):

#     _name='reception.appointment'


#     appointment=fields.Many2one(comodel_name="examination.form",string="Appointment")



#     appo=fields.One2many('appointment.set', 'appointment', string='Notebook')
#     mrn=fields.Many2one ( related='appointment.mrn',string="MRN")
#     name=fields.Char(related='mrn.full_name',string="Patients Name")
#     phone=fields.Char(related='mrn.phone',string="Phone")
    # date=fields.Datetime(related='appointment.start_date',string="Date")
    # clinician=fields.Many2one(related='appointment.clincian',string="Clincian")
    


    
   

    
