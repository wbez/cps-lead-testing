from bs4 import BeautifulSoup
import requests, time, csv, os
import smtplib
from email.mime.text import MIMEText

LEAD_URL ='http://www.cps.edu/Pages/LeadTesting.aspx'
CPS_URL = 'http://www.cps.edu'
SCHOOLS_FILE = 'schools.csv'

hdr = {'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.11 (KHTML, like Gecko) Chrome/23.0.1271.64 Safari/537.11',
	   'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
	   'Accept-Charset': 'ISO-8859-1,utf-8;q=0.7,*;q=0.3',
	   'Accept-Encoding': 'none',
	   'Accept-Language': 'en-US,en;q=0.8',
	   'Connection': 'keep-alive'}

def scrape_cps(url):

	r = requests.get(url,headers=hdr)
	html = r.content

	soup = BeautifulSoup(html, 'html.parser')
	links = soup.find_all('a')

	schools = []

	for i, link in enumerate(links):
		link_url = '%s%s' % (CPS_URL,link.get('href'))
		school = link.text.strip()

		if link_url is not None and 'CPS' not in school:
			if link_url.endswith('.pdf'):
				schools.append({'school':school,'pdf':link_url})
				print link_url, school

	
	check_list(schools)
	make_csv(schools,SCHOOLS_FILE)				

def download_pdfs(schools):
	dir_name = 'pdfs'

	try:
		os.stat(dir_name)
	except:
		os.makedirs(dir_name)

	for school in schools:
		print "downloading %s" % school['school']
		link_url = school['pdf']

		r = requests.get(link_url,headers=hdr)

		pdf = open("%s/%s" % (dir_name, link_url.split('/')[-1]), 'wb')
		pdf.write(r.content)
		pdf.close()
		time.sleep(1)
		print "wrote file %s" % link_url.split('/')[-1]

def make_csv(schools,output_file):

	with open(output_file, "wb", buffering=0) as new_csv_file:
		csv_output_file = csv.writer(new_csv_file, delimiter=',', quoting=csv.QUOTE_ALL)

		# list to hold our csv headers
		csv_header_row = [
			"school",
			"pdf",
		]

		# writes our csv headers
		csv_output_file.writerow(csv_header_row)

		for school in schools:
			csv_data_row = [school['school'],school['pdf']]
			csv_output_file.writerow(csv_data_row)

def check_list(schools):
	with open(SCHOOLS_FILE, 'rb') as f:
		old_schools = csv.DictReader(f, delimiter=',')
		new_schools = get_new_schools(old_schools,schools)

		if new_schools is not None:
			print 'New results: %s' % new_schools

			for school in new_schools:
				send_email(school)
				# download_pdfs(new_schools)

def get_new_schools(list1, list2):
	check = set([(d['school'], d['pdf']) for d in list1])
	return [d for d in list2 if (d['school'], d['pdf']) not in check]

# send an email with info from a report dictionary
def send_email(new_school):
	sender = os.environ.get('CPS_LEAD_RESULTS_GOOGLE_EMAIL')
	pw = os.environ.get('CPS_LEAD_RESULTS_GOOGLE_PASS')
	server = smtplib.SMTP('smtp.gmail.com:587')
	server.starttls()
	server.ehlo()
	server.login(sender,pw)
	# if more than one receiver, set up as a list and then join into a string for msg
	COMMASPACE = ', '
	receivers_list = ['chagan@wbez.org']
	receivers = COMMASPACE.join(receivers_list)

	message = """
	{school}
	{pdf}
	""".format(**new_school)

	msg = MIMEText(message)
	msg['Subject'] = "New CPS lead testing results: %s" % (new_school['school'])
	msg['From'] = sender
	msg['To'] = receivers
	try:
	   server.sendmail(sender, receivers_list, msg.as_string())      
	   print "Successfully sent email"
	except smtplib.SMTPException:
	   print "Error: unable to send email"


# runs the function specified
if __name__ == "__main__":
	scrape_cps(LEAD_URL)
