# -*- coding: utf-8 -*-

if not request.env.web2py_runtime_gae:
	## if NOT running on Google App Engine use SQLite or other DB
	#db = DAL('sqlite://storage.sqlite')
	db = DAL('mysql://adminta:passtowards@localhost/tashiptest', migrate=False)
else:
	db = DAL('google:datastore')
	session.connect(request, response, db = db)

response.generic_patterns = ['*'] if request.is_local else []

from gluon.tools import Auth, Crud, Service, PluginManager, prettydate
auth = Auth(db)
crud, service, plugins = Crud(db), Service(), PluginManager()
from gluon.tools import Mail

## create all tables needed by auth if not custom tables
auth.define_tables(username=False, signature=False)


## configure email

mail=Mail()                                  # mailer
mail.settings.server='mail.iiit.ac.in:25'    # your SMTP server
# mail.settings.login='username:password'      # your credentials or None


## -------------------------- Databases Defined Here ---------------------------------- ##

###############################################
# Stores all information about the applicants.#
###############################################
db.define_table(
    'Applicant',
    Field('ap_name','string',required=True, label='Full Name'),
    Field('ap_emailid','string',requires=IS_EMAIL(), label='Email-id'),
    Field('ap_rollno','integer',requires=IS_INT_IN_RANGE(minimum=200000000, maximum=300000000),required=True, label='Roll No'),
    Field('ap_cgpa','double',required=True,requires=IS_FLOAT_IN_RANGE(minimum=0,maximum=10), label='CGPA'),
    Field('ap_phoneno','string',required=True, label='Phone No'),
    Field('ap_prevexp','string',default='No Experience', label='Prev. Experience'),
    Field('ap_program','string',requires=IS_IN_SET(['UG1','UG2','UG3','UG4','PG1','PG2','MS','PhD']),default='UG3', label='Program'),
    )

#########################
# Stores list of admins.#
#########################
db.define_table(
    'Admin',
    Field('ad_name','string',required=True, label='Admin Name'),
    Field('ad_emailid','string',requires=IS_EMAIL(), label='Admin Email-id')
    )

##########################
# Stores list of faculty.#
##########################
db.define_table(
    'Faculty',
    Field('fac_name','string',required=True, label='Faculty Name'),
    Field('fac_emailid','string',requires=IS_EMAIL(), label='Faculty Email-id')
    )

#####################
# List of semesters.#
#####################
db.define_table(
    'Semester',
    Field('sem_name','string',required=True, label='Semester Name')
    )

#####################################
# List of courses and their details.#
#####################################
db.define_table(
    'Course',
    Field('c_code','string',required=True, label='Course Code'),
    Field('c_name','string',required=True, label='Course Name'),
    Field('c_credits','integer',required=True,requires=IS_INT_IN_RANGE(minimum=1,maximum=6), label='Credits'),
    Field('max_ta','integer',required=True,default=10,label='Max #TAs'),
    Field('no_of_qta','integer',default=0,required=True, label='#quarter-TAs'),
    Field('no_of_hta','integer',default=0,required=True, label='#half-TAs'),
    Field('no_of_fta','integer',default=0,required=True, label='#full-TAs'),
    Field('sem_id',db.Semester,required=True,requires=IS_IN_DB(db,'Semester.id','Semester.sem_name'), label='For semester'),
    Field('c_type','string',requires=IS_IN_SET(['Full Sem','Half Sem']),default='Full', label='Course Type'),
    Field('no_of_faculty','integer',required=True,default=1, label='#Instructors')
    )

##############################
# Links Faculties to Courses.#
##############################
db.define_table(
    'Faculty_Course',
    Field('fac_id',db.Faculty,required=True,requires=IS_IN_DB(db,'Faculty.id','Faculty.fac_name'), label='Faculty'),
    Field('c_id',db.Course,required=True,requires=IS_IN_DB(db,'Course.id','Course.c_name'), label='Course')
    )

##################################
# List of nominations by Faculty.#
##################################
db.define_table(
    'Nomination',
    Field('c_id',db.Course,required=True,requires=IS_IN_DB(db,'Course.id','Course.c_name'), label='Course'),
    Field('ap_id',db.Applicant,required=True,requires=IS_IN_DB(db,'Applicant.id','Applicant.ap_name'), label='Applicant'),
    Field('fac_pref',required=True,requires=IS_IN_SET([1,2,3,4,5,6,7,8,9,10]),default=1,label='Preference'),
    Field('type','string',required=True,requires=IS_IN_SET(['Qtr. TA','Half TA','Full TA']),default='Qtr. TA', label='TA Type'),
    )

#################################
# List of TA's finally selected.#
#################################
db.define_table(
    'Selected',
    Field('ap_id',db.Applicant,required=True,requires=IS_IN_DB(db,'Applicant.id','Applicant.ap_name'), label='Applicant'),
    Field('nom_id',db.Nomination,required=True,requires=IS_IN_DB(db,'Nomination.id','Nomination.id'), label='Nomination'),
    Field('c_id',db.Course,required=True,requires=IS_IN_DB(db,'Course.id','Course.c_name'), label='Course'),
    Field('ta_type','string',required=True,requires=IS_IN_SET(['Qtr. TA','Half TA','Full TA']),default='Qtr. TA', label='TA Type'),
    Field('time_sel','datetime',required=True,default=request.now,writable=False,readable=False, label='Selected on')
    )

##############################################
# Links Applicants to Courses they apply for.#
##############################################
db.define_table(
    'Application',
    Field('ap_id',db.Applicant,required=True,requires=IS_IN_DB(db,'Applicant.id','Applicant.ap_name'),readable=False),
    Field('c_id',db.Course,required=True,requires=IS_IN_DB(db,'Course.id','Course.c_name'),label='Course'),
    Field('grade','string',required=True,requires=IS_IN_SET(['A','A-','B','B-','C','C-','D','F','P','S','X','I','W']),default='A',label='Grade Obtained'),
    Field('applied_at','datetime',required=True,default=request.now,writable=False,readable=False),
    Field('pref','integer',requires=IS_IN_SET([1,2,3,4,5,6,7,8,9,10]),label='Preference'),
    Field('status',requires=IS_IN_SET(['Selected','Rejected','Nominated','Applied','Accepted']),default='Applied',writable=False,readable=False)
    )

#######################################
# Set the Application Period Deadline.#
#######################################
db.define_table(
    'AppDeadline',
    Field('start','datetime',required=True, label='Start Time'),
    Field('end','datetime',required=True, label='End Time')
    )

#######################################
# Set the Nomination Period Deadline.#
#######################################
db.define_table(
    'NomDeadline',
    Field('start','datetime',required=True, label='Start Time'),
    Field('end','datetime',required=True, label='End Time')
    )

#################################
# Autfill data using CSV files. #
#################################
db.define_table(
    'UploadFile',
    Field('upfile','upload',required=True, label='Upload File'),
    )

## ------------------------------ Databases Definition Ends Here ---------------------------------- ##
