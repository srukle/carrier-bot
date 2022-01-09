import datetime
from dateutil.parser import parse
from email.mime.text import MIMEText
import feedparser
import os
import requests
import smtplib
import urllib3

def gather_feeds(location):
	feeds = []
	with open(location) as file:
		for line in file:
			feeds.append(line.rstrip())
	return feeds

def legacy_rss(url):
	"""Code from StackOverFlow."""
	"""https://stackoverflow.com/questions/38015537/python-requests-exceptions-sslerror-dh-key-too-small"""
	requests.packages.urllib3.disable_warnings()
	requests.packages.urllib3.util.ssl_.DEFAULT_CIPHERS += ':HIGH:!DH:!aNULL'
	try:
		requests.packages.urllib3.contrib.pyopenssl.util.ssl_.DEFAULT_CIPHERS += ':HIGH:!DH:!aNULL'
	except AttributeError:
		pass
	page = requests.get(url, verify=False)
	return page.content

def parse_feed(url):
	d = feedparser.parse(url)
	try:
		if d.bozo == 1:
			d = feedparser.parse(legacy_rss(url))
	except Exception as e:
		pass
	for entry in d.entries:
		if parse(entry.published).strftime('%Y-%m-%d') >= (datetime.datetime.today() - datetime.timedelta(days=1)).strftime('%Y-%m-%d'):
			write_to_directory('<p><a href=\"' + entry.link + '\">' + entry.title + '</a></p>')

def send_mail(content):
	configs = []
	with open ('dw-config.txt', 'rb') as f:
		for line in f:
			configs.append(line.rstrip().decode())
	msg = MIMEText('post-security: public\n' + content)
	sender = configs[0]
	recipient = configs[1]
	msg['Subject'] = 'The Daily Herald - ' + str(datetime.datetime.today().strftime('%Y-%m-%d'))
	msg['From'] = sender
	msg['To'] = recipient
	server = smtplib.SMTP_SSL(configs[2], configs[3])
	server.login(configs[4], configs[5])
	server.sendmail(sender, recipient, msg.as_string())
	server.quit()


def write_to_directory(content):
	directory = "journal_entry"
	if os.path.isdir(directory):
		write_to_file(content)
	else:
		os.mkdir("journal_entry")
		write_to_file(content)
		
def write_to_file(content):
	file_name = datetime.datetime.today().strftime('%Y-%m-%d') + '.entry'
	if os.path.isfile('journal_entry/' + file_name):
		with open('journal_entry/' + file_name, 'a') as f:
			f.write(content)
	else:
		with open('journal_entry/' + file_name, 'w') as f:
			f.write(content)

feeds = gather_feeds('list.txt')

for url in feeds:
	parse_feed(url)


file_name = datetime.datetime.today().strftime('%Y-%m-%d') + '.entry'
with open('journal_entry/' + file_name, 'r') as f:
    output = f.read()

send_mail(output)
