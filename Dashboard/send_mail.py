#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from email import encoders
from email.header import Header
from email.mime.text import MIMEText
from email.utils import parseaddr, formataddr
import smtplib
from write_message import write_message
from datetime import datetime, timedelta


def _format_addr(s):
    name, addr = parseaddr(s)
    return formataddr((Header(name, 'utf-8').encode(), addr))

now = datetime.now()
earlier = now - timedelta(hours=12)
from_date = str(earlier.year) + '/' + str(earlier.month) + '/' + str(earlier.day) + '-' + str(earlier.hour)
to_date = str(now.year) + '/' + str(now.month) + '/' + str(now.day) + '-' + str(now.hour)
	
from_addr = 'PCT@EMCN.COM'
to_addr = ['yi.li5@hpe.com', 'yuanfan.shi@hpe.com']

smtp_server = 'smtp3.hpe.com'

WD = (0, 1, 2, 3, 4)
WH = [(0.0, 23.99)]

Target_A = 24
Target_B = 42
Target_C = 6

Table_A = write_message(Type = 1, Target = Target_A, From = 'BirthDate', To = 'WHUpdateTime', WorkingDay = WD, WorkingHour = WH)
Table_B = write_message(Type = 2, Target = Target_B, From = 'WHUpdateTime', To = 'HandoverTime', WorkingDay = WD, WorkingHour = WH)
Table_C = write_message(Type = 3, Target = Target_C, From = 'HandoverTime', To = 'PGITime', WorkingDay = WD, WorkingHour = WH)

msg = MIMEText(Table_A + Table_B + Table_C, 'html', 'utf-8')
msg['From'] = _format_addr('PCT Monitor <%s>' % from_addr)
msg['To'] = _format_addr('管理员 <%s>' % to_addr)
msg['Subject'] = Header('PCT Fail Report By Shift (%s - %s)' % (from_date, to_date), 'utf-8').encode()

server = smtplib.SMTP(smtp_server, 25)
server.set_debuglevel(1)
#server.login(from_addr, password)
server.sendmail(from_addr, to_addr, msg.as_string())
server.quit()
