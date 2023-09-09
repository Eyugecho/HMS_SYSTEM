from odoo import fields,models,api, _ 
from odoo.exceptions import ValidationError
from datetime import datetime, date,time,timedelta

class DrogaShareHolder(models.Model):
    _name="droga.physio"
    _rec_name="description"
    _inherit = ['mail.thread', 'mail.activity.mixin', 'image.mixin']
    
    mrn = fields.Char(string="MRN",required=True, copy=False, readonly=True,default=lambda self: _('New'))

    full_name=fields.Char("Full Name")
    sex=fields.Selection([('male','Male'),('female','Female')],"Gender")
    age=fields.Integer("Age", compute="_calculate_age")
    birth_date = fields.Date('Birth Date')
    register_date = fields.Date('Register Date')
    customer = fields.Many2one("customer.class")
    customer_grade = fields.Many2one("customer.class", string="Customer Grade")
    customer_type = fields.Many2one("customer.class", string="Customer Type")
    area = fields.Many2one("customer.class",string="Area")
    location = fields.Many2one("customer.class", string="Location")

    employee_name = fields.Char("Employee Name")
    company_name = fields.Many2one("customer.class",string="Company name" )
    employee_id = fields.Char("Employee ID")
    

    phone=fields.Char("Phone" )
    region=fields.Char("Card Number")
    
    city=fields.Char("City")
    
    subcity=fields.Selection([('ca1','CA1'),('ca2','CA2'),('ca3','CA3'),('ca4','CA4')],"Subcity")
    wereda=fields.Char("Wereda")
    office_tel=fields.Char("Office Tell")

    refered_by=fields.Many2one(comodel_name="hr.employee",string="Refered By")
    house_no=fields.Char("House No.")
    tin_no=fields.Char("Tin No.")
    company=fields.Many2one(comodel_name="customer.class",string="company") 
    contract=fields.Many2one(comodel_name="droga.contract",string="contract") 




    # sequence_no = fields.Char(string='Sequence', readonly=True)
    sequence_no = fields.Char(string='Sequence Number', readonly=True, copy=False, default=lambda self: _('New'))

    
    # description = fields.Text(string="Description")
    document = fields.Binary(string='Document')

    
    is_individual = fields.Boolean(string='Individual', default=True)
    is_company = fields.Boolean(string='Company', default=False)
    organization= fields.Many2one(comodel_name="customer.class",string="Organization")

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
    
    @api.depends('birth_date')
    def _calculate_age(self):
        for records in self:
            age=0
            
            birth_date=records.birth_date
            current_date=datetime.today().date()
            if birth_date:
                age=(current_date-birth_date)/timedelta(days=365)
            records.age=age


    
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

            a=mrn+" "+name+" "+company
            record.description = a


    
    @api.constrains('tin_no')
    def _check_tin(self):
        for records in self:
            
            if records.tin_no or not records.is_individual  :
                if not records.tin_no:
                     raise ValidationError("You should add tin number")
                tin_no= len(records.tin_no)
                if tin_no >13 or tin_no < 10:
                    raise ValidationError("The tin number sholud have digits b/n 10 up to 13")
    

class NotebookClass(models.Model):
    _name = 'notebook.class'
    droga_physio_id = fields.Many2one('droga.physio', string="droga physio")
    prescription_paitent_id = fields.Many2one('prescription.paitent', string="Main Class")
    full_name=fields.Char(related='droga_physio_id.full_name', string='Full name') 
    register_date = fields.Date(related='droga_physio_id.register_date', string='Register Date')
    phone=fields.Char(related='droga_physio_id.phone',string="Phone" )
    city=fields.Char(related='droga_physio_id.city',string="City")
    subcity=fields.Selection(related='droga_physio_id.subcity',string="Subcity")
    wereda=fields.Char(related='droga_physio_id.wereda',string="Wereda")


    office_tel=fields.Char(related='droga_physio_id.office_tel',string="Office Tell")

    refered_by=fields.Many2one(comodel_name="hr.employee",string="Refered By")
    # refered_by=fields.Char(related='droga_physio_id.refered_by',string="Refered By")
    house_no=fields.Char(related='droga_physio_id.house_no',string="House No.")
    tin_no=fields.Char(related='droga_physio_id.tin_no',string="Tin No.")
    
    customer_class_id = fields.Many2one('customer.class', string="customer class")
    print_date = fields.Date(string="Print Date")
    time=fields.Datetime("Date and Time")
    appointed_to=fields.Many2one(comodel_name="hr.employee",string="Appointed To")
    remark=fields.Selection([('arrived','Arrived'),('holiday','Holiday'),('absent','Absent'),('reschedule','Reschedule')],"Remark")
    service_type=fields.Selection([('club foot','Club Foot'),('eval','Eval'),('general physical teraphy','General Physical Teraphy'),('speech teraphy','Speech Teraphy')])
    price=fields.Char("Price")
    paid_Amount=fields.Char("Paid Amount")
    condition=fields.Selection([('ankle','Ankle'),('cervical','Cervical'),('elbow','Elbow'),('elbow wrist','Elbow Wrist'),('hand','Hand'),('knee','Knee'),('lumber','Lumber'),('neuro doc','Nuro Doc'),('neuro pt','Nuro PT'),('post strock','Post Strok'),('shoulder','Shoulder'),('thoractic','Thoractic'),('wrist','Wrist')],"Condition")

    attachment = fields.Binary(string= 'Attachment')
 
    employee_name=fields.Char("Employee Name")
    profession=fields.Char("Profession")
    employee_id=fields.Char("Employee Id")
    Service_Type = fields.Many2one('product.template', string='Serivce Type',)
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
 

#    maria code
class Appointment (models.Model): 
     
    _name="appointment.set" 
    start_date=fields.Datetime(" Start Date") 
    end_date= fields.Datetime("End Date") 
    clinician=fields.Char("Clinician") 
    clinician1=fields.Many2one(comodel_name="hr.employee",string="Clincian",domain="[('clinicians', '=', True)]") 
    # mrn=fields.Integer("MRN") 
    mrn=fields.Many2one(comodel_name="droga.physio",string="MRN") 

    name=fields.Char("Patients Name") 

    

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
    notebook_ids = fields.One2many('notebook.class', 'prescription_paitent_id', string="Notebook") 
    # prescription_no = fields.Integer('no') 
    prescriber = fields.Char() 
    prescriber=fields.Many2one(comodel_name="hr.employee",string="prescriber") 
    medication=fields.Char("Medication") 
    frequency=fields.Char("Frequency") 
    start_date=fields.Date("start date") 
    date_ordered=fields.Date("ordered date")  
    route= fields.Selection([('oral', 'Oral'),('iv','IV' ) , ('im','IM'), ('sq','SQ'), ('tropical','Tropical'),('perrectum','Per Rectum'),('drops','Drops'),('intranasal','Intranasal'),('intraaticular','Intra aticular'),('intraosseuous','Intraosseuous'),('sublingular','Sublingular')]) 
    stop_date=fields.Date("Stop date") 
    remark=fields.Text("Remark") 
    dose=fields.Text("Dose") 
    birth_date=fields.Date("Birth Date") 
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
    patient =  fields.Many2one('droga.physio', string='Patient')
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
    
    
    patient =  fields.Many2one('droga.physio', string='Patient')

#   patient_name = _id = fields.Many2one('',string='', )
    date = fields.Date()
    # clinicians = fields.Many2one('',string='',)
    sessions = fields.Text(string = "Sessions")
    diagnosis = fields.Text(string = "Diagnosis")
    recommendation = fields.Text(string = "Recommendation")



class drogaClinicians(models.Model):

    _inherit = 'hr.employee'
    clinicians = fields.Boolean(string = "Clinicians")

class referalForm(models.Model):

    _name = 'referal.form'

    patient =  fields.Many2one('droga.physio', string='Patient')
    date = fields.Date("Date")  
    investigation = fields.Text(string = "Investigation")
    physiotherapy_diagnosis = fields.Text(string = "Physiotherapy Diagnosis")
    medical_diagnosis = fields.Text(string="Medical Diagnosis")
    treatment_given = fields.Text(string="Treatment Given")
    reasons_for_referral = fields.Text(string="Reasons for Refferral")
    clinician1=fields.Many2one(comodel_name="hr.employee",string="Clincian") 


class examinationForm(models.Model):

    _name = 'examination.form'

    patient =  fields.Many2one('droga.physio', string='Patient')
    date = fields.Date("Date") 
    clinician1=fields.Many2one(comodel_name="hr.employee",string="Clincian")  
    cc = fields.Text(string = "C/C")
    hpi = fields.Text(string = "HPI(pain location, types, radiate, severity, timing,weight change,sleep disturbance)")
    rpmh = fields.Text(string="RPMH")
    dignostics_imaging_finding = fields.Text(string="Diagnostics and Imaging Finding ")
    observation = fields.Text(string="Observation")
    palpation = fields.Text(string="Palpation")
    rom=fields.Text(string="ROM/Flexibility")
    lld=fields.Text(string="LLD")
    mmt=fields.Text(string="MMT")
    reflex=fields.Text(string="Reflex")
    sensory=fields.Text(string="Sensory")
    special_test=fields.Text(string="Special Test")
    function=fields.Text(string="Function Activities Limitation")
    pt=fields.Text(string="PT Dx")
    treatment=fields.Text(string="Treatment Plan")

class nursingEvaluation(models.Model):

    _name='nursing.evaluation'
    pains=fields.Many2many(comodel_name="physio.complian.pains", string="Chief Complain/Pains")
    physio_neurology=fields.Many2many(comodel_name="physio.neurology" , string="Neurology")
    medical_history=fields.Many2many(comodel_name="medical.history" , string="Medical History")

    
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
