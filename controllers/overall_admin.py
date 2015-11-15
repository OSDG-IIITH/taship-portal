#################################################################
# These are the controllers for the overall admin of the portal.#
#################################################################

#########################################################################

# Section to handle mails

import smtplib
import gluon
import os

class NewMail(object):
    def __init__(self):
        self.settings = gluon.tools.Settings()
        self.settings.server = 'smtp.gmail.com:587'
        self.settings.use_tls = True
        self.settings.sender = ''
        self.settings.login = ""
        self.settings.lock_keys = True
    def send(self,to,subject,mesg):
            try:
                (host, port) = self.settings.server.split(':')
                server = smtplib.SMTP(host, port)
                if self.settings.login:
                    server.ehlo()
                    server.ehlo()
                    (username, password) = self.settings.login.split(':')
                mesg = "From: %s\n"%(self.settings.sender)+"To: %s\n" %(to)+"Subject: %s\n" % (subject)+"\r\n"+(mesg)+"\r\n"
                server.sendmail(self.settings.sender, to, mesg)
                server.quit()
            except Exception, e:
                print e
                return False
            return True

def sendmail(sender,reciever,subj,title):

    mail=NewMail()
    # specify server
    mail.settings.server='mail.iiit.ac.in:25'
    mail.settings.login='username:password' or None

# specify address to send as
    mail.settings.sender=sender

#   mail.settings.lock_keys=True
    mail.settings.use_tls=True
#   return mail.settings.keys()

#send the message
    print "Mail to be sent"
    return mail.send(to=reciever, subject=title, mesg=subj)

#sendmail('mohit.jain@research.iiit.ac.in','mohit.jain@research.iiit.ac.in','hello there!','test mail')

#########################################################################


def check_usertype():
    """ 
    Redirects malicious users to their homepages.
    """
    if session.login==1:
        msg = 'An unexpected error occured, please contact the WebAdmins.'
        redirect(URL('overall_admin','index?message=%s'%msg))
    elif session.login==2:
        msg = 'An unexpected error occured, please contact the WebAdmins.'
        redirect(URL('faculty','index?message=%s'%msg))
    elif session.login==3:
        msg = 'Stop trying to mess things up -_-'
        redirect(URL('default','index?message=%s'%msg))
    
    session.flash = 'An unexpected error occured :/'
    redirect(URL('default','login'))

def login_option():
    if not session.login==1:
        check_usertype()

    if request.vars:
        login_token = int(request.vars.log_token)
        if login_token==2:
            session.login=login_token
            msg = 'Now acting as a faculty member'
            redirect(URL('faculty','index?message=%s'%msg))
        else:
            msg = 'Continuing as admin user'
            redirect(URL('overall_admin','index?message=%s'%msg))
            
    else:
        response.flash = 'Select the interface you want to access.'
    
    return locals()

def index():
    '''
    Homepage for the admin.
    '''
    if not session.login==1:
        check_usertype()

    if not request.vars.message:
	message = 'Greetings '+session.name
    else:
	message =request.vars.message

    response.flash = message
    return locals()

def sem_detail():
    '''
    Add a new semester or list all semester.
    Upload CSV to autofill the database.
    '''
    if not session.login==1:
        check_usertype()

    form = SQLFORM(db.Semester)
    if form.process().accepted:
        response.flash = 'New Semester Added : '+form.vars.sem_name
    elif form.errors:
        response.flash = 'Semester Addition Failed : Form has errors!'

    createSemForm = form
    semDetail = db(db.Semester.id>0).select(db.Semester.ALL)

    csv_file = []
    form = SQLFORM(db.UploadFile)
    if form.process().accepted:
        fileDetails = db(db.UploadFile.id>0).select()
        filename = os.path.join(request.folder, 'uploads', fileDetails[-1].upfile)
        ctr = autoupdate_db(filename)
        response.flash = str(ctr[0])+' courses & '+str(ctr[1])+' faculty added.'
    elif form.errors:
        response.flash = 'Database update failed. Problem uploading '+form.vars.upfile

    updateDBForm = form

    return locals()

def autoupdate_db(filename):
    '''
    Fill the databases with the course and faculty details.
    '''
    if not session.login==1:
	check_usertype()

    csv_file = open(filename)

    ctr = [0,0]
    curr_semid = db(db.Semester.id>0).select()[-1].id
    for line in csv_file:
	line_vals = line.split(',')
        course_name = line_vals[0].strip()
        course_code = line_vals[1].strip()
        course_credit = line_vals[2].strip()
        course_type = line_vals[3].strip()
        n_faculty = int(line_vals[4].strip())

	course_id = db.Course.insert(c_code=course_code, c_name=course_name, c_credits=course_credit, sem_id=curr_semid, c_type=course_type, no_of_faculty=n_faculty)
        ctr[0]+=1

        for idx in range(5,len(line_vals)-1,2):
            fac_name = line_vals[idx].strip()
            fac_email = line_vals[idx+1].strip()
            
            fac_list = [fac.fac_emailid for fac in db(db.Faculty.id>0).select()]
            if fac_email not in fac_list:
                fac_id = db.Faculty.insert(fac_name=fac_name,fac_emailid=fac_email)
                ctr[1]+=1
            
            db.Faculty_Course.insert(fac_id=fac_id, c_id=course_id)

    return ctr       

def admin_detail():
    '''
    Create a new admin for the portal
    '''
    if not session.login==1:
        check_usertype()

    form = SQLFORM(db.Admin)
    if form.process().accepted:
        response.flash = 'New Admin Added : '+form.vars.ad_name
    elif form.errors:
        response.flash = 'Admin not created : Form has errors!'

    addAdminForm = form
    adminDetail = db(db.Admin.id>0).select(db.Admin.ALL)

    return locals()

def faculty_detail():
    '''
    Add a new faculty member or list all members or allot course to faculty.
    '''
    if not session.login==1:
        check_usertype()

    form = SQLFORM(db.Faculty)
    if form.process().accepted:
        response.flash = 'New Faculty Added'+form.vars.fac_name
    elif form.errors:
        response.flash = 'Faculty not added : Form has errors!'

    addFacultyForm = form
    facultyDetail = db(db.Faculty.id>0).select(db.Faculty.ALL)
   
    form = SQLFORM(db.Faculty_Course)
    if form.process().accepted:
        response.flash = 'Course alloted to Faculty'
    elif form.errors:
        response.flash = 'Course not alloted : Form has errors!'

    facultyCourseForm = form

    return locals()

def course_detail():
    '''
    Add a new Course or list all course details.
    '''
    if not session.login==1:
        check_usertype()

    form = SQLFORM(db.Course)
    if form.process().accepted:
        response.flash = 'New Course Added : '+form.vars.c_name
    elif form.errors:
        response.flash = 'Course not added : Form has errors!'

    addCourseForm = form
    courseDetail = db(db.Course.id>0).select(db.Course.ALL)

    return locals()

def set_deadline():
    '''
    Set the deadline for application and nomination.
    '''
    if not session.login==1:
        check_usertype()

    form = SQLFORM(db.AppDeadline)
    if form.process().accepted:
        response.flash = 'Application Period Set : '+str(form.vars.start)+' to '+str(form.vars.end)
    elif form.errors:
        response.flash = 'Application Period not Set : Form has errors!'

    appDeadlineForm = form
    try:
        appDetail = db(db.AppDeadline.id>0).select(db.AppDeadline.ALL)[-1]
    except:
        appDetail = ''
    
    form = SQLFORM(db.NomDeadline)
    if form.process().accepted:
        response.flash = 'Nomination Period Set : '+str(form.vars.start)+' to '+str(form.vars.end)
    elif form.errors:
        response.flash = 'Nomination Period not Set : Form has errors!'

    nomDeadlineForm = form
    try:
        nomDetail = db(db.NomDeadline.id>0).select(db.NomDeadline.ALL)[-1]
    except:
        nomDetail = ''

    return locals()

def application_detail():
    '''
    View the status of all applications and select nominated candidates.
    '''
    if not session.login==1:
        check_usertype()

    course_list = db(db.Course.id>0).select()

    courseid = ''
    if request.vars.sel_courseid and request.vars.sel_courseid!='all':
        courseid = int(request.vars.sel_courseid)    
        appDetail = db((db.Application.id>0) & (db.Applicant.id==db.Application.ap_id) & (db.Course.id==db.Application.c_id) & (db.Application.c_id==courseid)).select(db.Application.ALL, db.Applicant.ALL, db.Course.ALL, orderby=db.Course.id)
    elif request.vars.sel_courseid=='all':
        appDetail = db((db.Application.id>0) & (db.Applicant.id==db.Application.ap_id) & (db.Course.id==db.Application.c_id)).select(db.Application.ALL, db.Applicant.ALL, db.Course.ALL, orderby=db.Course.id)
    else:
        appDetail = ''
    
    return locals()

def accept_application():
    '''
    Changes the status from nominated -> accepted.
    '''
    if not session.login==1:
        check_usertype()

    indices = request.vars.check
    if indices:
        if isinstance(indices, list):
            for idx in indices:
                idx = int(idx)
                db(db.Application.id==idx).update(status='Selected')
                applicant_id = db(db.Application.id==idx).select()[0]['ap_id']
                course_id = db(db.Application.id==idx).select()[0]['c_id']
                #db.Selected.insert(c_id=course_id, ap_id=idx, type=
	        admin_email = db(db.Admin.id>0).select(db.Admin.ALL)[0]['ad_emailid']
	        details = db((db.Application.id==idx) & (db.Applicant.id==db.Application.ap_id) & (db.Application.c_id==db.Course.id)).select(db.Applicant.ALL, db.Course.ALL)[0]
                stud_name = details['Applicant']['ap_name']
                stud_email = details['Applicant']['ap_emailid']
                stud_course = details['Course']['c_name']
	        sendmail(admin_email,stud_email,'Congratulations '+stud_name+'! You have been selected as a TA for the '+stud_course+' course. Please accept this position on the TAship portal within the next 24hours to confirm your selection.','[TA-Portal] Selected as TA for '+stud_course+' [NO REPLY]')
        else:
            idx = int(indices)
            db(db.Application.id==idx).update(status='Selected')
            applicant_id = db(db.Application.id==idx).select()[0]['ap_id']
            course_id = db(db.Application.id==idx).select()[0]['c_id']
            #db.Selected.insert(c_id=course_id, ap_id=idx, type=
	    admin_email = db(db.Admin.id>0).select(db.Admin.ALL)[0]['ad_emailid']
	    details = db((db.Application.id==idx) & (db.Applicant.id==db.Application.ap_id) & (db.Application.c_id==db.Course.id)).select(db.Applicant.ALL, db.Course.ALL)[0]
            stud_name = details['Applicant']['ap_name']
            stud_email = details['Applicant']['ap_emailid']
            stud_course = details['Course']['c_name']
	    sendmail(admin_email,stud_email,'Congratulations '+stud_name+'! You have been selected as a TA for the '+stud_course+' course. Please accept this position on the TAship portal within the next 24hours to confirm your selection.','[TA-Portal] Selected as TA for '+stud_course+' [NO REPLY]')
    else:
        pass

    redirect(URL('overall_admin','application_detail'))

    return locals()
