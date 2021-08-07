from bs4 import BeautifulSoup
import requests
import time
import xlsxwriter
import os

living_cpi_url = 'https://www.numbeo.com/cost-of-living/rankings_by_country.jsp'
numbeo_home_url = 'https://www.numbeo.com/cost-of-living/'


def get_costs(page):
    soup = BeautifulSoup(page, 'lxml')

    title = soup.h1.text[1:]
    

    costs = soup.find('table', class_= 'data_wide_table new_bar_table')

    costs = costs.find_all('tr')

    columns = []
    el = []
    currency = soup.find('select', id='displayCurrency')
    currency = currency.find('option', selected='selected').text
    
    columns.append('Currency')
    el.append(currency)

    for cost in costs:
        if cost.td is not None:
            tds = cost.find_all('td')
            column_title = tds[0].text
            
            column_cost = tds[1].text.replace(' ', '')
            

            columns.append(column_title)
            el.append(column_cost)
        elif cost.th.div is not None:
            column_title = 'Category'
            column_el = cost.th.div.text
            

            columns.append(column_title)
            el.append(column_el)
        


    return columns, el

def save_workbook(dir, columns, els):
    workbook = xlsxwriter.Workbook(dir)
    worksheet = workbook.add_worksheet()

    col = 0
    for column in columns:
        worksheet.write(0, col, column)
        col = col + 1
    
    col = 0
    for e in els:
        worksheet.write(1, col, e)
        col = col + 1

    workbook.close()


def scrapeCountry(countryname, dir):
    html_text = requests.get(f'https://www.numbeo.com/cost-of-living/country_result.jsp?country={countryname}').text

    try:
        os.makedirs(dir, exist_ok=True)
    except OSError as error:
        print(f'Directory {dir} cannot be created')
    
    dir = dir + f'/{countryname}.xlsx'
    print(dir)
    soup = BeautifulSoup(html_text, 'lxml')
    if "Numbeo doesn't have that country in the database" in soup.find_all('div', class_= 'innerWidth')[2].text:
        return f'Numbeo does not have {countryname} in the database'

    columns, els = get_costs(html_text)
    save_workbook(dir, columns, els)
    print(f'saved dir: {dir}')
    return f'Scraped {countryname}'

def scrapeCity(cityname, dir):
    
    try:
        os.makedirs(dir, exist_ok=True)
    except OSError as error:
        print(f'Directory {dir} cannot be created')
    
    dir = dir + f'/{cityname}.xlsx'
    print(dir)

    def iterateCityurls(cityname, case):
        #punctuations = '''\n!()-[]{};:'"\, <>./?@#$%^&*_~'''
        
        trim_city = cityname
        
        if ' ' in cityname:
            trim_city = trim_city.split(' ')

        if '(' in cityname:
            if 'str' not in str(type(trim_city)):
                for trimmed in trim_city:
                    if '(' not in trimmed:
                        continue
                    
                    index = trim_city.index(trimmed)
                    trim_city.pop(index)
                    
                    li = trimmed.split('(')
                    for l in li:
                        if l == '':
                            continue

                        trim_city.insert(index, l)
                        index = index + 1
            else:
                trim_city = trim_city.split('(')
        
        if ')' in cityname:
            if 'str' not in str(type(trim_city)):
                for trimmed in trim_city:
                    if ')' not in trimmed:
                        continue
                    
                    index = trim_city.index(trimmed)
                    trim_city.pop(index)
                    
                    li = trimmed.split(')')
                    for l in li:
                        if l == '':
                            continue

                        trim_city.insert(index, l)
                        index = index + 1
            else:
                trim_city = trim_city.split(')')
        
        if '-' in cityname:
            if 'str' not in str(type(trim_city)):
                for trimmed in trim_city:
                    if '-' not in trimmed:
                        continue
                    
                    index = trim_city.index(trimmed)
                    trim_city.pop(index)
                    
                    li = trimmed.split('-')
                    for l in li:
                        if l == '':
                            continue

                        trim_city.insert(index, l)
                        index = index + 1
            else:
                trim_city = trim_city.split('-')
        
        comma_trim = []
        if ',' in cityname:
            if 'str' not in str(type(trim_city)):
                for trimmed in trim_city:
                    if ',' not in trimmed:
                        continue
                    
                    index = trim_city.index(trimmed)
                    trim_city.pop(index)

                    li = trimmed.split(',')
                    for l in li:
                        if l == '':
                            continue

                        trim_city.insert(index, l)
                        index = index + 1
                
                comma_trim = cityname.split(',')
            else:
                trim_city = trim_city.split(',')
                comma_trim = cityname.split(',')
        
        city_search = ''
        if case == 0:
            city_search = cityname
        elif case == 1:
            if 'str' not in str(type(trim_city)):
                for trimmed in trim_city:
                    if trimmed[-1] is '.':
                        trimmed[-1] = ''
                    
                    if city_search is '':
                        city_search = trimmed 
                    else:
                        city_search = city_search + ' ' + trimmed 
            else:
                city_search = trim_city
        elif case == 2:
            if 'str' not in str(type(trim_city)):
                for trimmed in trim_city:
                    if trimmed[-1] is '.':
                        trimmed[-1] = ''
                    
                    if city_search is '':
                        city_search = trimmed 
                    else:
                        city_search = city_search + '-' + trimmed 
            else:
                city_search = trim_city
        elif case == 3:
            if 'str' not in str(type(trim_city)):
                for trimmed in trim_city:
                    if trimmed[-1] is '.':
                        trimmed[-1] = ''
                    
                    if city_search is '':
                        city_search = trimmed 
                    else:
                        city_search = city_search + '-' + trimmed
            else:
                city_search = trim_city
            city_search = city_search + '-' + str(country[0]).upper() + str(country[1:])
        elif case == 4:
            if ',' in cityname:
                if 'str' not in str(type(trim_city)):
                    city_search = comma_trim[0]
        
        return city_search, case
    
    case = 0
    city_search = cityname

    
    html_text = requests.get(f'https://www.numbeo.com/cost-of-living/in/{cityname}').text
    
    
    while case < 5:
        city_search, case = iterateCityurls(cityname, case)

        html_text = requests.get(f'https://www.numbeo.com/cost-of-living/in/{city_search}').text
        soup = BeautifulSoup(html_text, 'lxml')
        if 'Cannot find city id' not in soup.h1.text[1:]:
            break

        case = case + 1
    
    if 'Cannot find city id' in soup.h1.text[1:]:
            return f'Numbeo does not have {cityname} in the database'

    columns, els = get_costs(html_text)
    save_workbook(dir, columns, els)
    print(f'saved dir: {dir}')
    return f'Scraped {cityname}'

def scrapeWorld(dir):
    html_text = requests.get(numbeo_home_url).text
    bs = BeautifulSoup(html_text, 'lxml')
    countries = bs.find('select', id= 'country').text.split('\n')
    
    i=0
    for country in countries:
        if (country == '') | (country == '---Select country---'):
            continue
        
        html_text = requests.get(f'https://www.numbeo.com/cost-of-living/country_result.jsp?country={country}').text
        

        soup = BeautifulSoup(html_text, 'lxml')
        cities = soup.find('select', id= 'city').text.split('\n')
        index= str(i)

        if len(index) == 1:
            index = '0'+index

        print(scrapeCountry(country, f'{dir}'))

        for city in cities:
            if (city == '') | (city == '--- Select city---'):
                continue
            
            print(scrapeCity(city, f'{dir}/{country}'))
            
        
        i = i+1
        

def scrapeCitiesinCountry(countryname, dir):
    
    html_text = requests.get(f'https://www.numbeo.com/cost-of-living/country_result.jsp?country={countryname}').text

    soup = BeautifulSoup(html_text, 'lxml')
    if "Numbeo doesn't have that country in the database" in soup.find_all('div', class_= 'innerWidth')[2].text:
        return f'Numbeo does not have {countryname} in the database'
        

    cities = soup.find('select', id= 'city').text.split('\n')

    for city in cities:
            if (city == '') | (city == '--- Select city---'):
                continue
            
            print(scrapeCity(city, f'{dir}'))

def getdirectory():
    print('Please input directory to save excel')
    dir = input('>')

    return dir

while True:
    print('What would you like to search?')
    print('''
    1- Country
    2- City
    3- World [All countries and cities]
    4- Cities in specified country
    ''')
    scrapingtarget = input('>')

    if scrapingtarget == '1':
        break
    elif scrapingtarget == '2':
        break
    elif scrapingtarget == '3':
        break
    elif scrapingtarget == '4':
        break
    else:
        print('Invalid input')

if scrapingtarget == '1':
    print('What country would you like to search?')
    country = input('>')

    dir = getdirectory()

    print(scrapeCountry(country, dir))
elif scrapingtarget == '2':
    print('What city would you like to search?')
    city = input('>')

    dir = getdirectory()

    print(scrapeCity(city, dir))
elif scrapingtarget == '3':
    while True:
        print('Running this will take some time to complete. Continue? (y/n)')
        start = input('>')

        if start == 'y':
            dir = getdirectory()

            scrapeWorld(dir)
            break
        elif start == 'n':
            break
        else:
            print('Please enter "y or "n"')
elif scrapingtarget == '4':
    print('What country would you like to search?')
    country = input('>')

    dir = getdirectory()

    print(scrapeCitiesinCountry(country, dir))
    
