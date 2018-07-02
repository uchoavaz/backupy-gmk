
import ipdb
import time
import smtplib
from os import getenv
from decouple import config
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart


class Mailer():

	def __init__(self):
		self.fromaddr = config('MAIL_SENDER', default='')
		self.toaddr = config('SEND_TO', default='')
		port = config('EMAIL_PORT', default='')
		host = config('EMAIL_HOST', default='')
		password = config('EMAIL_PASSWORD', default='')
		self.server = smtplib.SMTP(host, port)
		self.server.starttls()
		self.server.login(self.fromaddr, password)

	def treat_msg(self, success_msg, alert_msg, error_msg, except_error):
		msg = success_msg + '\n' + alert_msg + '\n' + error_msg + '\n' + except_error
		return msg

	def dispatch(self, treated_msg):

		emails = self.toaddr.split(',')
		for email in emails:
			msg = MIMEMultipart()
			msg['From'] = self.fromaddr
			msg['To'] = email
			msg['Subject'] = "{0}'backup' at {1}".format(
				config('AGENT_SERVER', default=''), time.strftime('%d-%m-%Y:%H:%M'))
			body = treated_msg
			msg.attach(MIMEText(body, 'plain'))
			text = msg.as_string()
			self.server.sendmail(self.fromaddr, self.toaddr, text)

	def send(self, success_msg, alert_msg, error_msg, except_error):
		treated_msg = self.treat_msg(success_msg, alert_msg, error_msg, except_error)

		self.dispatch(treated_msg)
		self.server.quit()