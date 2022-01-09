import datetime
from dateutil.parser import parse
import feedparser
import os
import requests
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
		if parse(entry.published).strftime('%Y-%m-%d') >= (datetime.datetime.today() - datetime.timedelta(days=3)).strftime('%Y-%m-%d'):
			write_to_directory('<p><a href=\"' + entry.link + '\">' + entry.title + '</a></p>')

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
