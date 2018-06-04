
import smtplib
from decouple import config
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart


class Mailer():

	def __init__(self):
		fromaddr = self.from_address = config('MAIL_SENDER', default='')
		port = config('EMAIL_PORT', default='')
		host = config('EMAIL_HOST', default='')
		password = config('EMAIL_PASSWORD', default='')
		self.server = smtplib.SMTP(host, port)
		self.server.starttls()
		self.server.login(fromaddr, password)

	def treat_msg(self, success_msg, error_msg):
		msg = "Success:"
		msg = msg + "\n" + success_msg
		msg = msg + "\n\n" + "Errors:"
		msg = msg + "\n" + error_msg 
		return msg

	def send(self, success_msg, error_msg):
		msg = self.treat_msg(success_msg, error_msg)

		msg = MIMEMultipart()
		msg['From'] = fromaddr
		msg['To'] = toaddr
		msg['Subject'] = "SUBJECT OF THE MAIL"
		body = "YOUR MESSAGE HERE"
		msg.attach(MIMEText(body, 'plain'))
		text = msg.as_string()
		server.sendmail(fromaddr, toaddr, text)
		self.server.quit()