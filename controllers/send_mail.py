# Class to send mails.

import smtplib

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

