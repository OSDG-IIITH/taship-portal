# -*- coding: utf-8 -*-

#########################################################################
import ldap
#########################################################################

# Section to handle mails

import smtplib
import gluon
import datetime

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
CAS.login_url='https://login.iiit.ac.in/cas/login'
CAS.check_url='https://login.iiit.ac.in/cas/validate'
CAS.logout_url='https://login.iiit.ac.in/cas/logout'
CAS.my_url='http://taship.iiit.ac.in/taportal/default/login'
#CAS.my_url='http://localhost:8000/taportal/default/login'
#########################################################################

# To make sure everyone logins
if not session.token and not request.function=='login':
    redirect(URL(r=request, f='login'))


def login():
    """
    Method to fetch the user detials from CAS
    Redirects to respective user interface
    """
    session.login = 0
    session.token = CAS.login(request)
    user_email=session.token

    l = ldap.initialize("ldap://ldap.iiit.ac.in")
    l.protocol_version = ldap.VERSION3
    baseDN = "ou=Users,dc=iiit,dc=ac,dc=in"
    searchScope = ldap.SCOPE_SUBTREE
    searchFilter = "mail="+user_email    
    result = l.search_s(baseDN, searchScope, searchFilter)
    result = result[0][1]

    user_name = result['cn'][0]
    
    session.name = user_name
    session.email = user_email
    
    if 'uidNumber' in result:
        user_roll = result['uidNumber'][0]
    else:
        user_roll = result['uid'][0]

    # check if admin
    is_admin = db(db.Admin.ad_emailid==user_email).select(db.Admin.ALL)
    if is_admin:
        session.login = 1
        redirect(URL('overall_admin','index'))

    # check if faculty
    is_faculty = db(db.Faculty.fac_emailid==user_email).select(db.Faculty.ALL)
    if is_faculty:
        session.login = 2
        redirect(URL('faculty','index'))

    # else is student. Check if details are filled already.
    has_applied = db(db.Applicant.ap_emailid==user_email).select(db.Applicant.ALL)
    session.login = 3
    session.roll = user_roll
    if has_applied:
	session.userid = has_applied[0]['id']
        redirect(URL('default','index'))
    else:
        redirect(URL('default','fill_details'))

def logout():
    session.token = None
    session.login = 0
    CAS.logout()

def check_usertype():
    """
    Redirects malicious users to their homepages.
    """
    if session.login==1:
        msg = 'Stop trying to mess things up -_-'
        redirect(URL('overall_admin','index?message=%s'%msg))
    elif session.login==2:
        msg = 'Stop trying to mess things up -_-'
        redirect(URL('faculty','index?message=%s'%msg))
    elif session.login==3:
        msg = 'Stop trying to mess things up -_-'
        redirect(URL('default','index?message=%s'%msg))
    session.flash = 'An unexpected error occured :/'
    redirect(URL('default','login'))

def index():
    """
    Landing page for students.
    """
    if not session.login==3:
        check_usertype()
    
    if not request.vars.message:
	message='Greetings '+session.name
    else:
        message=request.vars.message

    response.flash = T(message)
    message = 'Welcome to TAship Portal!'
    return locals()

def fill_details():
    """
    Get complete details of the applicant.
    """
    if not session.login==3:
        check_usertype()
    
    db.Applicant.ap_name.default=session.name
    db.Applicant.ap_emailid.default=session.email
    db.Applicant.ap_rollno.default=session.roll
    db.Applicant.ap_name.writable=False
    db.Applicant.ap_emailid.writable=False
    db.Applicant.ap_rollno.writable=False
   
    has_applied = db(db.Applicant.ap_emailid==session.email).select(db.Applicant.ALL)
    if has_applied:
        applicantForm = SQLFORM(db.Applicant,db.Applicant(has_applied[0]['id']))
    else:
        applicantForm = SQLFORM(db.Applicant)
    if applicantForm.process().accepted:
        user_id = db(db.Applicant.ap_emailid==session.email).select(db.Applicant.ALL)[0]['id']
        session.userid = user_id
        response.flash = 'Applicant Details Updated'
        redirect(URL('default','index'))
    elif applicantForm.errors:
        response.flash = 'Form has errors!'

    return locals()

def apply():
    """
    Method shows form for applying as TA.
    Options to move preference up/down or remove application.
    """
    if not session.login==3:
        check_usertype()
   
    AppTime = db(db.AppDeadline.id>0).select(db.AppDeadline.ALL)[-1]
    startTime = AppTime['start']
    endTime = AppTime['end']

    st_delta = request.now - startTime
    end_delta = request.now - endTime

    if st_delta < datetime.timedelta(seconds=1):
	msg = 'Application Period starts on '+str(startTime)
        redirect(URL('default','index?message=%s'%msg))
    if end_delta > datetime.timedelta(seconds=1):
	msg = 'Application Period has ended on '+str(endTime)+' now time : '+str(request.now)
        redirect(URL('default','index?message=%s'%msg))
 
    filledApps = db((db.Application.ap_id==session.userid) & (db.Application.c_id==db.Course.id) &(db.Application.ap_id==db.Applicant.id)).select(db.Application.ALL, db.Applicant.ALL, db.Course.ALL, orderby=db.Application.pref)
   
    cur_pref = 1
    if filledApps: 
        cur_pref = filledApps[-1]['Application']['pref']+1
    
    db.Application.ap_id.default = session.userid
    db.Application.ap_id.writable = False
    db.Application.pref.default = cur_pref
    db.Application.pref.writable = False
    applicationForm = SQLFORM(db.Application)
    if applicationForm.process().accepted:
        response.flash = 'Application Successfully Submitted!'
        redirect(URL('default','apply'))
    elif applicationForm.errors:
        response.flash = 'Form has errors!'

    return locals()

def update_pref():
    """
    Updates the preference of applications moving requested application one step up.
    """
    if not session.login==3:
        check_usertype()
    
    if request.vars.pref_val:
        source_pref = int(request.vars.pref_val)
        target_pref = source_pref-1
        if source_pref==1:
            session.flash = 'Stop trying to mess things up -_-'
            redirect(URL('default','apply'))
    
        source_app = db((db.Application.ap_id==session.userid) & (db.Application.pref==source_pref)).select(db.Application.ALL)
        target_app = db((db.Application.ap_id==session.userid) & (db.Application.pref==target_pref)).select(db.Application.ALL)

        if source_app and target_app:
            db(db.Application.id==source_app[0]['id']).update(pref=target_pref)
            db(db.Application.id==target_app[0]['id']).update(pref=source_pref)
            redirect(URL('default','apply'))
        else:
            session.flash = 'Stop trying to mess things up -_-'
            redirect(URL('default','apply'))
    elif request.vars.app_id:
        del_app_id = int(request.vars.app_id)
        del_app_pref = db((db.Application.ap_id==session.userid) & (db.Application.id==del_app_id)).select(db.Application.ALL)
        if not del_app_pref:
            session.flash = 'Stop trying to mess things up -_-'
            redirect(URL('default','apply'))
        
        del_app_pref = del_app_pref[0]['pref']
        len_prefs = len(db(db.Application.ap_id==session.userid).select(db.Application.ALL))
        for ap_pref in range(del_app_pref+1,len_prefs+1):
            db((db.Application.ap_id==session.userid) & (db.Application.pref==ap_pref)).update(pref=ap_pref-1)
        db(db.Application.id==del_app_id).delete()
        redirect(URL('default','apply'))
    else:
        session.response = 'Invalid Request'
        redirect(URL('default','apply'))

def course_detail():
    '''
    Display the list of Courses with the faculty.
    '''
    if not session.login==3:
        check_usertype()
   
    courseDetail = db(db.Course.id>0).select()
    
    return locals()

def admin_page():
    """
    Display the list of Admins.
    """
    adminList = db(db.Admin.id>0).select(db.Admin.ALL)
    
    return locals()

def user():
    """
    exposes:
    http://..../[app]/default/user/login
    http://..../[app]/default/user/logout
    http://..../[app]/default/user/register
    http://..../[app]/default/user/profile
    http://..../[app]/default/user/retrieve_password
    http://..../[app]/default/user/change_password
    http://..../[app]/default/user/manage_users (requires membership in
    use @auth.requires_login()
        @auth.requires_membership('group name')
        @auth.requires_permission('read','table name',record_id)
    to decorate functions that need access control
    """
    return dict(form=auth())


@cache.action()
def download():
    """
    allows downloading of uploaded files
    http://..../[app]/default/download/[filename]
    """
    return response.download(request, db)


def call():
    """
    exposes services. for example:
    http://..../[app]/default/call/jsonrpc
    decorate with @services.jsonrpc the functions to expose
    supports xml, json, xmlrpc, jsonrpc, amfrpc, rss, csv
    """
    return service()


