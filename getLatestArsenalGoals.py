from bs4 import BeautifulSoup
import requests
import csv
import re

('''
A webscraper that produces a .csv file containing direct links to videos of the latest Arsenal goals.

1. The website scraped is arsenalist.com.
2. Match headline, goal titles and goal video links are gathered from the site.
3. Page hosting the goal video link is then scraped.
4. Direct video links to the goals are then gathered from the original source.
5. Print to .csv
	''')

#1
res = requests.get('http://arsenalist.com/').text

soup = BeautifulSoup(res, 'lxml')

#2
headline = soup.find('h1').text
headline = headline.replace('Highlights', 'Goals')

#5
csv_file = open(headline + '.csv', 'w')
csv_writer = csv.writer(csv_file)
csv_writer.writerow(['title', 'direct_link'])

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

#3
for i in range(0, len(link)):
	r = requests.get(link[i]).text
	soup = BeautifulSoup(r, 'lxml')
	#print(soup)
#4
	try: 
		vid_src_orig = soup.find('iframe')['src']
		vid_id = vid_src_orig.split('/')
		direct = f'https://streamable.com/e/{vid_id[4]}'
		direct_link.append(direct)
	except Exception as e:
		direct_link.append(None)


	csv_writer.writerow([title[i], direct_link[i]])

csv_file.close()