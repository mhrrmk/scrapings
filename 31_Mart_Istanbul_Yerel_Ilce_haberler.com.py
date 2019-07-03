import time
import requests
from bs4 import BeautifulSoup
import csv

main_page = "https://secim.haberler.com"

def getResponseWithUTF8(url):
	response = requests.get(url)
	response.encoding = "utf-8"
	return response

def htmlToSoup(url):
	while True:
		try:
			response = getResponseWithUTF8(url)
		except :
			time.sleep(5)
			continue
		else:
			break
	return BeautifulSoup(response.text, 'html.parser')

def toProperInt(stupid_string):
	return int(str(stupid_string).replace(".",""))

#returns a dictionary
def get_ilce_data(ilce_link):
	ilce_data = {}
	ilce_soup = htmlToSoup(ilce_link)
	def vote_from_class(class_name):
		return toProperInt(ilce_soup("div", class_name)[0]("span", "yspeVote")[0].string[:-3])
	ilce_data["ilçe"] = ilce_link[56:-17]
	ilce_data["CHP"] = vote_from_class("yspeBar chp")
	ilce_data["AKP"] = vote_from_class("yspeBar akp")
	ilce_data["SP"] = vote_from_class("yspeBar sp")
	ilce_data["VP"] = vote_from_class("yspeBar vp")
	ilce_data["Diğer"] = vote_from_class("yspeBar other")
	total_vote_data_soup = ilce_soup("div", "ysTotalBox")
	for data in total_vote_data_soup[3:]:
		ilce_data[data("span", "ystbTitle")[0].string] = toProperInt(data("span", "ystbNumber")[0].string)
	return ilce_data

#takes a list of dictionaries
def dataToCsv(tumIlcelerData):
	fieldnamesSetPartiler = set()
	partilerHaric = []
	for data in tumIlcelerData:
		for key in data.keys():
			if key not in partilerHaric:
				fieldnamesSetPartiler.add(key)
	with open("31_Mart_Istanbul_Ilce.csv", "w", newline='') as csvfile:
		writer = csv.DictWriter(csvfile, fieldnames= partilerHaric + list(fieldnamesSetPartiler))
		writer.writeheader()
		writer.writerows(tumIlcelerData)

main_soup = htmlToSoup(main_page)
ilce_links_div = main_soup("div", "navMenu navCity")[0]("a")
ilce_links = []
for a in ilce_links_div:
	ilce_links.append(main_page + a["href"])

total_ilce_data = []
for ilce_link in ilce_links:
	ilce_data = get_ilce_data(ilce_link)
	print(ilce_data)
	total_ilce_data.append(ilce_data)

dataToCsv(total_ilce_data)