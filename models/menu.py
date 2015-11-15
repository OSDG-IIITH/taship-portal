# -*- coding: utf-8 -*-
# this file is released under public domain and you can use without limitations

#########################################################################
## Customize your APP title, subtitle and menus here
#########################################################################

response.logo = A(B(SPAN('IIIT-H')),XML('&trade;&nbsp;'),
                  _class="navbar-brand",_href=URL('default','login'))
response.title = 'TA Portal'

## read more at http://dev.w3.org/html5/markup/meta.name.html
response.meta.author = 'Mohit Jain <mohit.jain@research.iiit.ac.in>'
response.meta.description = 'TAship Portal for IIIT-H'
response.meta.keywords = 'web2py, python, framework'
response.meta.generator = 'Web2py Web Framework'

## your http://google.com/analytics id
response.google_analytics_id = None

#########################################################################
## this is the main application menu add/remove items as required
#########################################################################

if session.login==1:
    controler = 'overall_admin'
elif session.login==2:
    controler = 'faculty'
elif session.login==3:
    controler = 'default'
else:
    controler = 'login'

response.menu = [    
    (T('Home'), False, URL(controler, 'index'), []),
]

if session.login==1:
    response.menu+=[
    (T('Faculty Interface'), True, URL('overall_admin', 'login_option'), []),
    (T('Admin Options'), True, URL('overall_admin', 'index'), [ 
		(T('Applications'), True, URL('overall_admin','application_detail'), []),
		(T('Admin Details'), True, URL('overall_admin','admin_detail'), []),
		(T('Set Deadline'), True, URL('overall_admin','set_deadline'), []),
		(T('Semester Details'), True, URL('overall_admin','sem_detail'), []),
		(T('Faculty Details'), True, URL('overall_admin','faculty_detail'), []),
		(T('Course Details'), True, URL('overall_admin','course_detail'), []),
	]),
    (T('Log Out'), True, URL('default', 'logout'), []),
]
else:
    response.menu+=[
    (T('Admins'), False, URL('default', 'admin_page'), []),
    (T('Log Out'), True, URL('default', 'logout'), []),
]


DEVELOPMENT_MENU = False
