## ------ Controllers for the Faculty ------ ##

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
    '''
    Homepage for faculty.
    '''
    if not session.login==2:
        check_usertype()

    if not request.vars.message:
	message = 'Greetings '+session.name
    else:
	message = request.vars.message

    response.flash = message
    return locals()

def application_detail():
    '''
    List of applications for the courses taken by the faculty.
    '''
    if not session.login==2:
        check_usertype()

    course_list = db((db.Course.id>0) & (db.Faculty_Course.c_id==db.Course.id) & (db.Faculty_Course.fac_id==db.Faculty.id) & (db.Faculty.fac_emailid==session.email)).select(db.Course.ALL)

    courseid = ''
    if request.vars.sel_courseid and request.vars.sel_courseid!='all':
        courseid = int(request.vars.sel_courseid)
        appDetail = db((db.Application.id>0) & (db.Application.c_id==db.Faculty_Course.c_id) & (db.Faculty_Course.fac_id==db.Faculty.id) & (db.Faculty.fac_emailid == session.email) & (db.Course.id==db.Application.c_id) & (db.Application.ap_id==db.Applicant.id) & (db.Application.c_id==courseid)).select(db.Application.ALL, db.Course.ALL, db.Applicant.ALL, orderby=db.Course.id)
    else:
        appDetail = db((db.Application.id>0) & (db.Application.c_id==db.Faculty_Course.c_id) & (db.Faculty_Course.fac_id==db.Faculty.id) & (db.Faculty.fac_emailid == session.email) & (db.Course.id==db.Application.c_id) & (db.Application.ap_id==db.Applicant.id)).select(db.Application.ALL, db.Course.ALL, db.Applicant.ALL, orderby=db.Course.id)

    return locals()

def nominate_application():
    '''
    Changes the status of selected applications from Applied->Nominated.
    '''
    if not session.login==2:
        check_usertype()

    nomTime = db(db.NomDeadline.id>0).select(db.NomDeadline.ALL)[-1]
    nomStart = nomTime['start']
    nomEnd = nomTime['end']

    st_delta = request.now - nomStart
    end_delta = request.now - nomEnd

    if st_delta < datetime.timedelta(seconds=1):
	msg = 'Nomination Period starts on '+str(nomStart)
	redirect(URL('faculty','index?message=%s'%msg))
    if end_delta > datetime.timedelta(seconds=1):
	msg = 'Nomination Perod ended on '+str(nomEnd)+' : Contact Admins for help'
	redirect(URL('faculty','index?message=%s'%msg))

    indices = request.vars.check
    if indices:
        if isinstance(indices, list):
            for idx in indices:
                idx = int(idx)
                db(db.Application.id==idx).update(status='Nominated')
                applicant_id = db(db.Application.id==idx).select()[0]['ap_id']
                course_id = db(db.Application.id==idx).select()[0]['c_id']
                #db.Nomination.insert(c_id=course_id, ap_id=idx, type=
	        for admin_email in db(db.Admin.id>0).select(db.Admin.ALL):
	   	    admin_email = admin_email['ad_emailid']
    	            sendmail(session.email,admin_email,'I have nominated the students as TAs for my course on TAship Portal. Please accept them as TAs as soon as you can. --'+session.name,'[TA-Portal] Nominations from '+session.name)
        else:
            idx = int(indices)
            db(db.Application.id==idx).update(status='Nominated')
            applicant_id = db(db.Application.id==idx).select()[0]['ap_id']
            course_id = db(db.Application.id==idx).select()[0]['c_id']
            #db.Nomination.insert(c_id=course_id, ap_id=idx, type=
            for admin_email in db(db.Admin.id>0).select(db.Admin.ALL):            
                admin_email = admin_email['ad_emailid']
                sendmail(session.email,admin_email,'I have nominated the students as TAs for my course on TAship Portal. Please accept them as TAs as soon as you can. --'+session.name,'[TA-Portal] Nominations from '+session.name)	   
    else:
        pass

    redirect(URL('faculty','application_detail'))
    return locals()
