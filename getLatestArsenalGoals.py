#!/usr/bin/env python3

from bs4 import BeautifulSoup
import requests
import csv
import re
import datetime
import smtplib # send mail
import configparser # .ini config
import imapclient # read mail
import pyzmail
import json # store user email addresses

('''
A webscraper program that emails subscribed users a list of direct links to videos of the latest Arsenal goals.
	''')
# Scrape arsenalist.com
res = requests.get('http://arsenalist.com/').text
soup = BeautifulSoup(res, 'lxml')

# Check if any new highlights
goals_date = soup.select('#content a')[0]['href']
goals_date = goals_date.split('/')
goals_date = '-'.join(goals_date[3:6])
today = datetime.datetime.now().strftime("%Y-%m-%d")
yesterday = datetime.datetime.now() - datetime.timedelta(days=1)
yesterday_inbox = yesterday.strftime("%d-%b-%Y")
yesterday = yesterday.strftime("%Y-%m-%d")

# Get user data
config = configparser.ConfigParser()
config.read('goals_config.ini')
with open('goals_recipients.json') as f:
	recipients = json.load(f)

if (goals_date == yesterday):
	# Get headline
	headline = soup.find('h1').text
	headline = headline.replace('Highlights', 'Goals')

	# Setup csv writer
	csv_file = open(headline + '.csv', 'w')
	csv_writer = csv.writer(csv_file)
	csv_writer.writerow(['title', 'direct_link'])

	# Get goal titles and videos
	title = []
	link = []
	direct_link = []

	for goals in soup.select('.list-group a'):
		if re.match('.*(g+o+a+l+)' ,goals.text.lower()):		
			title.append(goals.text)

			try:
				vid_src = goals['href']
				link.append(vid_src)
			except Exception as e:
				vid_src = None 

	# Scrape for direct links
	for i in range(0, len(link)):
		r = requests.get(link[i]).text
		soup = BeautifulSoup(r, 'lxml')

	# Get direct video links
		try: 
			vid_src_orig = soup.find('iframe')['src']
			vid_id = vid_src_orig.split('/')
			direct = f'https://streamable.com/e/{vid_id[4]}'
			direct_link.append(direct)
		except Exception as e:
			direct_link.append(None)

		# Write data to csv
		csv_writer.writerow([title[i], direct_link[i]])

	csv_file.close()

	# Send email notifications
	msg_content = (''.join([str(a) + '\n' + b + '\n\n' for a,b in zip(title,direct_link)]))
	msg_notes = ('''\nNote: Videos liable to copyright claims.\n\nIf your friends would like to subscribe, 
they can email josephpballantyne+goals@gmail.com with the subject 'GOALS'. To unsubscribe, use subject 'STOP'.''')
	conn = smtplib.SMTP('smtp.gmail.com', 587)
	type(conn)
	conn.ehlo()
	conn.starttls()
	conn.login(config.get('main', 'sender'), config.get('main', 'password'))
	message = 'Subject: ' + headline + '\n' + headline + '\n\n' + msg_content + msg_notes
	conn.sendmail(config.get('main', 'sender'), gr.recipients, message)
	conn.quit()

# Maintain subscription list
conn = imapclient.IMAPClient('imap.gmail.com', ssl=True)
conn.login(config.get('main', 'sender'), config.get('main', 'password'))
conn.select_folder('INBOX', readonly=True)
UIDs = conn.search(['SINCE', yesterday_inbox])
for i in UIDs:
    messages = conn.fetch(i, ['BODY[]'])
    msg = pyzmail.PyzMessage.factory(messages[i][b'BODY[]'])
    subject = msg.get_subject()
    sender = msg.get_addresses('from')
    email = [item[1] for item in sender]
    if subject == 'GOALS':
    	with open('goals_recipients.json', 'w', encoding='utf8') as f:
    		recipients.append(email[0])
    		json.dump(recipients, f)
    		print(recipients)
    if subject == 'STOP':
    	with open('goals_recipients.json', 'w', encoding='utf8') as f:
    		recipients.remove(email[0])
    		json.dump(recipients, f)
    		print(recipients)