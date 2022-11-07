import requests
from bs4 import BeautifulSoup
import re
import pandas as pd
def find_school_name (source):
    """
    Finds the school name from the soup ADT.
    @param - source - a soup
    """
    name = str(source.find("div", {"class": "general-info"}).find("h1"))
    return name[4:-5]
def find_pop(source):
    """
    Finds population of the school from the given source/school page
    @param - source - a soup
    @return - the population of the school"""
    try:
        elems = source.find("div", {"class": "basic-info"}).find_all("div", {"class": "flex-table row"})[5]
    except:
        return pd.NA
    pop = elems.find_all("div", {"class": "flex-row"})
    pop = pop[1].text
    return pop
def find_grades(source):
    """
    Finds respective academic and applied averages from the EQAO website.
    @param - source - a soup document to be examined
    @return - a list with applied in 0th position and academic in 1st position
    """
    if "Academic" not in source.text:
        return [1,1]
    all_scripts = source.find_all('script')
    fall_grades = []
    counter = 0

    for script in all_scripts:
        if 'drawBarChart([["Year Range"' in script.text:
            counter+=1
            if counter == 1 or counter  == 2:
                fall_grades.append(script.text)

    scraped_grades = []
    string_list = ""

    for grades in fall_grades:
        done = False
        for i in range(0,len(grades)):
            x = i
            if grades[i] == 'P':
                while done == False:
                    if grades[x+12] == ',':
                        scraped_grades.append((string_list))
                        string_list = ''
                        x+=1
                        continue
                    elif grades[x+12] == ']':
                        scraped_grades.append((string_list))
                        string_list = ''
                        done = True
                        continue
                    string_list+=grades[x+12]
                    x+=1
    try:
        if [scraped_grades[2], scraped_grades[5]] == [1,1] or [scraped_grades[2], scraped_grades[5]] == [0,0]:
            return [pd.NA, pd.NA]
        return [scraped_grades[2], scraped_grades[5]]
    except:
        return [pd.NA, pd.NA]
def find_postal_town (source):
    try:
        whole_address = source.find('p', {"class": "address"})
        address = source.find('p', {"class": "address"}).find('br').next_sibling
        split_up = address.split()
    except:
        return [pd.NA, pd.NA]
    if len(whole_address.find_all('br')) == 2:
        address = address.next_sibling.next_sibling
        split_up = address.split()
    elif len(whole_address.find_all('br')) == 3:
        address = address.next_sibling.next_sibling.next_sibling.next_sibling
        print(address)
        split_up = address.split()
    postal = split_up[-2] + ' ' + split_up[-1]
    if (split_up[0] == split_up[-3]):
        town = split_up[0]
    else:
        town = ''
        for item in split_up:
            if item == split_up[-3]:
                town+= ' ' +item
                break
            town+=item
    final_address = [town, postal]
    return final_address

def find_hs_index():
    """Find all hs indexes. Weeds out school boards"""

    ids = []
    names = []
    for x in range(1361,10000):
        document = requests.get("https://www.eqao.com/report/?id=" + str(x), headers = headers).content
        website = BeautifulSoup(document, "lxml")
        if ("Either the requested page" in website.text or "I Like to Write" in website.text or ""):
            continue
        else:
            ids.append(x)
            print(x)
            names.append(find_school_name(website))
            print(find_grades(website))


    return names
headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/68.0.3440.84 Safari/537.36',
    'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8',
}
def create_data ():
    large_data = []
    for x in range(1300,10000):
        document = requests.get("https://www.eqao.com/report/?id=" + str(x), headers = headers).content
        website = BeautifulSoup(document, "lxml")
        if ("Either the requested page" in website.text or "I Like to Write" in website.text):
            continue
        else:
            data = []
            print(x)
            data.append(find_school_name(website))
            data.append(find_pop(website))
            data.append(find_postal_town(website)[0])
            data.append(find_postal_town(website)[1])
            data.append(find_grades(website)[0])
            data.append(find_grades(website)[1])
            large_data.append(data)
            print(large_data)
    frame = pd.DataFrame(large_data, columns = ['School Name', 'School Size', 'Town Name', 'Postal Code', 'Applied EQAO Grades', 'Academic EQAO Grades'])
    frame.to_csv('EQAODataset.csv')

create_data()
