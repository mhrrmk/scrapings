import time
startTime = time.time()
import requests
from bs4 import BeautifulSoup
import csv

def getResponseUntilUTF8(url):
	response = requests.get(url)
	response.encoding = "utf-8"
	return response

def htmlToSoup(url):
	while True:
		try:
			response = getResponseUntilUTF8(url)
		except :
			time.sleep(5)
			continue
		else:
			break
	return BeautifulSoup(response.text, 'html.parser')

def tumIlLinks():
	illerLinks = []
	i=0
	for li in htmlToSoup("https://www.haberturk.com/secim/secim2019/yerel-secim")("li", "section rlt")[0]("li"):
		illerLinks.append("https://www.haberturk.com" + li("a")[0]["href"])
		print("tumIlLinks", i)
		i+=1
	print((time.time() - startTime, "sn"))
	return illerLinks

def ilcelerFromIl(ilURL):
    ilceLinks=[]
    for li in htmlToSoup(ilURL)("li", "section rlt", style="margin-right: 0")[0]("li"):
        ilceLinks.append("https://www.haberturk.com" + li("a")[0]["href"])
    return ilceLinks

def tumIlceLinks():
	tumIlceler=[]
	i=0
	for il in tumIlLinks():
		tumIlceler += ilcelerFromIl(il)
		print("tumIlceLinks", i)
		i+=1
	print((time.time() - startTime, "sn"))
	return tumIlceler

def toProperInt(haberturkString):
	return int(str(haberturkString).replace(".",""))

def ilceData(ilceLink):
	ilceData = {}
	ilceSoup = htmlToSoup(ilceLink)
	isimler = ilceSoup("div", "group row-fluid")[0].contents[1].contents
	ilceData["İlçe"] = isimler[7].string
	ilceData["İl"]   = isimler[5].string
	data = ilceSoup("table", "general-layout")[0].contents[1]("b")
	ilceData["Toplam Seçmen"] = toProperInt(data[3].string)
	ilceData["Kullanılan Oy"] = toProperInt(data[4].string)
	ilceData["Geçerli Oy"]    = toProperInt(data[5].string)
	for parti in ilceSoup("table", "gray red tables buyuksehir")[1].contents[3:-2:2]:
		ilceData[parti.a["title"]] = toProperInt(parti("td")[1].string)
	return ilceData

def tumIlcelerData():
	tumIlcelerData = []
	i=0
	for ilce in tumIlceLinks():
		tumIlcelerData.append(ilceData(ilce))
		print("tumIlcelerData", i)
		i+=1
	return tumIlcelerData

def dataToCsv(tumIlcelerData):
	fieldnamesSetPartiler = set()
	partilerHaric = ["İl", "İlçe", "Toplam Seçmen", "Kullanılan Oy", "Geçerli Oy"]
	for data in tumIlcelerData:
		for key in data.keys():
			if key not in partilerHaric:
				fieldnamesSetPartiler.add(key)
	with open("BelediyeMeclis.csv", "w", newline='') as csvfile:
		writer = csv.DictWriter(csvfile, fieldnames= partilerHaric + list(fieldnamesSetPartiler))
		writer.writeheader()
		writer.writerows(tumIlcelerData)

dataToCsv(tumIlcelerData())
print((time.time() - startTime)/60, "dk")