import time
start_time = time.time()
import requests
from bs4 import BeautifulSoup
import csv

main_page = "https://www.yenisafak.com"
genel_page = main_page + "/yerel-secim-2019/meclis-secim-sonuclari"
total_ilce_data = []

# try_func_params={each one of the arguments of try_func as a string for keys: values to be passed as arguments for value}
def try_until_success(**kwargs):
    while True:
        try:
            try_func = kwargs["try_func"]
            try_func_params = kwargs["try_func_params"]
            return try_func(**try_func_params)
        except:
            if "except_func" in kwargs.keys():
                except_func = kwargs["except_func"]
                except_func_params = kwargs["except_func_params"]
                except_func(**except_func_params)
            continue
        else:
            break

def get_response(url):
    return requests.get(url).text

def wait(seconds):
    time.sleep(seconds)

def get_html(url):
    html_start = time.time()
    html = try_until_success(try_func=get_response, try_func_params={"url": url}, except_func=wait, except_func_params={"seconds": 5})
    print("response time:" + str(time.time() - html_start))
    return html

def html_to_soup(url):
    return BeautifulSoup(get_html(url), "html.parser")

def to_proper_int(stringified_integer):
	return int(str(stringified_integer).replace(".",""))

def data_to_csv(total_data):
	fieldnames_set = set()
	for data in total_data:
		for key in data.keys():
			fieldnames_set.add(key)
	with open("yerel_secim_2019_ilce_meclis_yenisafak.csv", "w", newline='') as csvfile:
		writer = csv.DictWriter(csvfile, fieldnames= list(fieldnames_set))
		writer.writeheader()
		writer.writerows(total_data)

def enter_ilce_soup(ilce_page, ilce_data):
    soup_start = time.time()
    ilce_soup = html_to_soup(ilce_page)
    print("url to soup time:" + str(time.time() - soup_start))
    secmen_data_region = ilce_soup("div", "result-attendance")[0]("ul", "attendance")[0]("li")[1:4]
    ilce_secmen_data = { li("span")[0].text: to_proper_int(li("span")[1].text) for li in secmen_data_region }
    ilce_data.update(ilce_secmen_data)
    ilce_partiler_columns = ilce_soup("div", "container result-content-container party-charts")[0]("div", recursive=False)[6]("div", recursive=False)[2:]
    for column in ilce_partiler_columns:
        data_region = column.div.div.table.tr("td")
        parti_isimleri =[ str(li.div.text) for li in data_region[0].ul("li") ]
        oy_sayilari = [ to_proper_int(li("div", "bars-votes")[0]("span")[0].text) for li in data_region[1]("ul", "ratio ratio-back")[0]("li") ]
        ilce_data.update(dict(zip(parti_isimleri, oy_sayilari)))
    print(ilce_data)
    return ilce_data

def enter_il_soup(il_page, il):
    ilceler_of_il_data = []
    print("getting ilceler from" + " " + il)
    ilce_rows = html_to_soup(il_page)("div", "table-data", {"data-column": "1"})[0]("ul", recursive=False)[1]("li", recursive=False)
    ilce_linkleri = { li.a("span", "key")[0].text: li.a["href"] for li in ilce_rows }
    for ilce, ilce_link in ilce_linkleri.items():
        ilce_data = {}
        ilce_data["İl"] = il
        ilce_data["İlce"] = ilce
        ilce_page = main_page + ilce_link
        ilceler_of_il_data.append(try_until_success(try_func=enter_ilce_soup, try_func_params={"ilce_page": ilce_page, "ilce_data": ilce_data}))
    return ilceler_of_il_data

il_linkleri_region = html_to_soup(genel_page)("a", "button", title="Şehirler")[0].parent("ul", "sub-menu", {"data-column": "5"})[0].contents[1:]
il_linkleri = { li.a["title"]: li.a["href"] for li in il_linkleri_region }

for il, il_link in il_linkleri.items():
    il_page = main_page + il_link
    total_ilce_data += try_until_success( try_func=enter_il_soup, try_func_params={"il_page": il_page, "il": il})

data_to_csv(total_ilce_data)

# #print(il_linkleri)
# example_il_page = main_page + il_linkleri["Adıyaman"]
# #print(example_il_page)
# #print( len( html_to_soup(example_il_page)("div", "table-data", {"data-column": "1"})[0]("ul", recursive=False)[1]("li", recursive=False) ))
# example_ilce_rows = html_to_soup(example_il_page)("div", "table-data", {"data-column": "1"})[0]("ul", recursive=False)[1]("li", recursive=False)
# # example_row = example_ilce_rows[0]
# # print( example_row.a("span", "key")[0].text )
# example_ilce_linkleri = { li.a("span", "key")[0].text: li.a["href"] for li in example_ilce_rows }
# #print(example_ilce_linkleri)

# print("ilçe linkleri done")
# print(time.time() - startTime)

# example_ilce_link = example_ilce_linkleri["Balkar"]
# example_ilce_page = main_page + example_ilce_link
# #print( len(html_to_soup(example_ilce_page)("ul", "attendance") ))
# #print( (html_to_soup(example_ilce_page)("div", "result-attendance")[0]("ul")[0]("li")[1:] ))
# ilce_soup = html_to_soup(example_ilce_page)
# example_ilce_secmen_data = { li("span")[0].text: li("span")[1].text for li in ilce_soup("div", "result-attendance")[0]("ul")[0]("li")[1:] }
# # print( example_ilce_secmen_data)
# #print( len(html_to_soup(example_ilce_page)("div", "container result-content-container party-charts")[0]("div", recursive=False)[6]("div", recursive=False)[2:] ))
# example_ilce_partiler_columns = ilce_soup("div", "container result-content-container party-charts")[0]("div", recursive=False)[6]("div", recursive=False)[2:]

# print("ilçe done")
# print(time.time() - startTime)

# ilce_oy_sayilari = {}
# ilce_oy_sayilari.update(example_ilce_secmen_data)
# for column in example_ilce_partiler_columns:
#     data_region = column.div.div.table.tr("td")
#     parti_isimleri =[ str(li.div.text) for li in data_region[0].ul("li") ]
#     oy_sayilari = [ to_proper_int(li("div", "bars-votes")[0]("span")[0].text) for li in data_region[1]("ul", "ratio ratio-back")[0]("li") ]
#     ilce_oy_sayilari.update(dict(zip(parti_isimleri, oy_sayilari)))
# print(ilce_oy_sayilari)

# example_ilce_partiler_column = example_ilce_partiler_columns[0].div.div.table.tr("td")
# #print( example_ilce_partiler_column[0].ul )
# parti_isimleri =[ str(li.div.text) for li in example_ilce_partiler_column[0].ul("li") ]
# print(parti_isimleri)
# #print( example_ilce_partiler_column[1]("ul", "ratio ratio-back")[0]("li") )
# oy_sayilari = [ to_proper_int(li("div", "bars-votes")[0]("span")[0].text) for li in example_ilce_partiler_column[1]("ul", "ratio ratio-back")[0]("li") ]
# #print(oy_sayilari)
# print( dict(zip(parti_isimleri, oy_sayilari)))

print("finish")
print(time.time() - start_time)