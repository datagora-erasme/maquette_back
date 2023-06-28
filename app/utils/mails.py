import sys
import os
from os import environ
from app import infoLogger

from smtplib import SMTP

from email import encoders
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email.utils import formatdate


class ServerSMTP(object):
    def __init__(self, addr="", port=587, login="", pwd=""):
        if addr == "" and port == 587 and login == "" and pwd == "":
            self.addr = str(environ.get("SMTP_HOST"))
            self.port = str(environ.get("SMTP_PORT"))
            self.login = str(environ.get("SMTP_AUTH_USER"))
            self.pwd = str(environ.get("SMTP_AUTH_PWD"))
        else:
            self.addr = addr
            self.port = port
            self.login = login
            self.pwd = pwd


class MessageSMTP(object):
    def __init__(
        self,
        sender="",
        to=(),
        cc=(),
        bcc=(),
        subject="",
        corps="",
        pj=(),
        codage="UTF-8",
        typetext="plain",
    ):
        # Verify all parameters
        self.sender = sender
        if isinstance(to, str):
            to = to.split(";")
        if to == [] or to == [""]:
            raise ValueError("Error : no target to send !")
        if isinstance(cc, str):
            cc = cc.split(";")
        if isinstance(bcc, str):
            bcc = bcc.split(";")
        if isinstance(pj, str):
            pj = pj.split(";")
        if codage == None or codage == "":
            codage = "UTF-8"

        # Build the mail content

        if pj == []:
            msg = MIMEText(corps, typetext, _charset=codage)
        else:
            msg = MIMEMultipart("alternatives")

        msg["From"] = sender
        msg["To"] = ", ".join(to)
        msg["Cc"] = ", ".join(cc)
        msg["Bcc"] = ", ".join(bcc)
        msg["Date"] = formatdate(localtime=True)
        msg["Subject"] = subject
        msg["Charset"] = codage
        msg["Content-Type"] = "text/" + typetext + "; charset=" + codage

        if pj != []:
            msg.attach(MIMEText(corps, typetext, _charset=codage))

            # add PJs
            for file in pj:
                part = MIMEBase("application", "octet-stream")
                try:
                    with open(file, "rb") as f:
                        part.set_payload(f.read())
                except Exception as err:
                    raise ValueError(
                        "Error : could not read the file (" + str(err) + ")"
                    )
                encoders.encode_base64(part)
                part.add_header(
                    "Content-Disposition",
                    "attachment",
                    filename="%s" % (os.path.basename(file),),
                )
                msg.attach(part)

        # create a compact one message for the email
        self.mail = msg.as_string()

        self.targets = to
        self.targets.extend(cc)
        self.targets.extend(bcc)


def sendSMTP(msg, server):
    infoLogger.info("try to send mail to " + str(msg.targets))

    smtp = None
    try:
        smtp = SMTP(server.addr, server.port)
        smtp.ehlo()
    except Exception as err:
        if smtp != None:
            smtp.quit()
        return "Error : server not recognized ! (" + str(err) + ")"

    # for debug : show all exchanges of SMTP
    # smtp.set_debuglevel(1)

    if server.login != "":
        # try to connect with logs
        try:
            smtp.starttls()
            rep = smtp.login(server.login, server.pwd)
        except Exception as err:
            if smtp != None:
                smtp.quit()
            return "Error : login or password incorrect ! (" + str(err) + ")"

    try:
        # try to send the mail
        rep = smtp.sendmail(msg.sender, msg.targets, msg.mail)
    except Exception as err:
        if smtp != None:
            smtp.quit()
        return "Error : when sending the email ! (" + str(err) + ")"

    smtp.quit()
    # return an empty string means the email was sent sucessfuly
    return ""
