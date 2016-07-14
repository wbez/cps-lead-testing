from documentcloud import DocumentCloud
import csv, re

csv.field_size_limit(1000000000)

def parse_list(list):
	results = {}

	for item in list:
		result = parse_text(item['text'])
		results.update(result)

	writer = csv.writer(open('dict.csv', 'wb'))

	writer.writerow(['location','park', 'level', 'aa'])
	
	for key, value in results.items():
		park = key.split(' #')

		if float(value) >= 15:
			lead = 'Yes'
		else:
			lead = 'No'
		writer.writerow([key, park[0], value, lead])


def parse_text(text):
	lead_regex = re.compile(r'Lead\n\n.*?(\d.*?)\n')
	lead_results = lead_regex.findall(text)

	name_regex = re.compile(r'Lab ID: .*?\n\n(.*?)\n')
	name_results = name_regex.findall(text)

	results = dict(zip(name_results, lead_results))

	return results


def retrieve_document_cloud():
	client = DocumentCloud('chagan@wbez.org','Iagwomfnm23/')

	project = client.projects.get(id=28179)

	print "Retrieving documents for %s" % project.title

	docs = []

	for doc in project.document_list:
		print doc.access
		doc.access = 'organization'
		doc.put()

	for doc in project.document_list:	
		docs.append({'title':doc.title,'text':doc.full_text})

	make_csv(docs,'documents.csv')

def make_csv(documents,output_file):

	with open(output_file, "wb", buffering=0) as new_csv_file:
		csv_output_file = csv.writer(new_csv_file, delimiter=',', quoting=csv.QUOTE_ALL)

		# list to hold our csv headers
		csv_header_row = [
			"name",
			"result",
		]

		# writes our csv headers
		csv_output_file.writerow(csv_header_row)

		for doc in documents:
			csv_data_row = [doc['title'],doc['text']]
			csv_output_file.writerow(csv_data_row)

if __name__ == "__main__":
	with open('documents.csv', 'rb') as f:
		doc_list = csv.DictReader(f, delimiter=',')
		parse_list(doc_list)
