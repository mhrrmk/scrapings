import time
startTime = time.time()
import requests
from bs4 import BeautifulSoup
import csv

main_page = "https://www.sabah.com.tr"
genel_page = main_page + "/secim/31-mart-2019-yerel-secim-sonuclari/tum-sehirler/yerel-secim-sonuclari"

def get_html(url):
    while True:
        try:
            response = requests.get(url)
        except:
            time.sleep(5)
            continue
        else:
            break
    return response.text

def html_to_soup(url):
    return BeautifulSoup(get_html(url), "html.parser")

il_linkleri = {str(a.string):a["href"] for a in html_to_soup(genel_page)("a", "counties-name") }

def to_proper_int(stringified_integer):
	return int(str(stringified_integer).replace(".",""))

def get_il_meclis_data(il_url):
    il_dict = {}
    il_soup = html_to_soup(il_url)
    toplam_oylar_soup = [to_proper_int(span("strong")[0].string) for span in il_soup("div", "turkey-area-top-info")[0]("span")]
    il_dict["Toplam Seçmen"] = toplam_oylar_soup[0]
    il_dict["Kullanılan Oy"] = toplam_oylar_soup[1]
    vote_rows = il_soup("div", "tab related")[0]("div", "tab-content", recursive=False)[0]("div", "tab-content-tab", recursive=False)[1].contents[1]("div", "tab-content mB20")[0].contents[1].div("tbody")[0]("tr")
    for row in vote_rows:
        il_dict[str(row("td")[0].a.span.text)] = to_proper_int(row("td")[1].span.text)
    return il_dict

def data_to_csv(total_il_data):
	fieldnamesSetPartiler = set()
	partilerHaric = ["İl", "Toplam Seçmen", "Kullanılan Oy"]
	for data in total_il_data:
		for key in data.keys():
			if key not in partilerHaric:
				fieldnamesSetPartiler.add(key)
	with open("yerel_secim_2019_il_genel_meclisi_iller_sabah.csv", "w", newline='') as csvfile:
		writer = csv.DictWriter(csvfile, fieldnames= partilerHaric + list(fieldnamesSetPartiler))
		writer.writeheader()
		writer.writerows(total_il_data)

count = 0
total_il_data = []
for il_name, il_link in il_linkleri.items():
    il_dict = {}
    il_dict["İl"] = il_name
    il_dict.update(get_il_meclis_data(main_page + il_link))
    total_il_data.append(il_dict)
    print(il_dict)
    count += 1
print(count)

data_to_csv(total_il_data)

print(time.time() - startTime)