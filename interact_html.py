import requests, json, time, pathlib
from requests.adapters import HTTPAdapter
# from requests.exceptions import ConnectionError
from datetime import date, datetime
from docx2python import docx2python
# from bs4 import BeautifulSoup
import selenium
from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
# from selenium.webdriver.common.keys import Keys
import configparser


def docs_list_params_setup(page_size, page=1):

    params = {
        'sort': 'Date-desc',
        'page': page,
        'pageSize': page_size,
        'group': '',
        'filter': '',
        'npaFilter.IsNotEmpty': 'true',
        'npaFilter.StrSearch': '',
        'npaFilter.SearchType': '0',
        'npaFilter.StartDate': '2021-03-01',
        # вариант даты: 28.2.2021
        'npaFilter.EndDate': '2021-06-11',
        # 'npaFilter.StartDateDiscussion': '3.5.2021',
        # 'npaFilter.EndDateDiscussion': '30.5.2021',
        # 'npaFilter.SysFilters[0].ID': '4',
        # 'npaFilter.SysFilters[0].Title': 'Наиболее посещаемые',
        # 'npaFilter.Departments[0].ID': '9',
        # 'npaFilter.Departments[0].Title': 'Минпромторг России',
        'npaFilter.Okveds[0].ID': '6',
        'npaFilter.Okveds[0].Title': 'Производство пищевых продуктов, включая напитки, и табака',
        # 'npaFilter.Categories[0].ID': '1'
        # 'npaFilter.Categories[0].Title': 'Раскрытие информации о подготовке проектов нормативных правовых актов'
        # 'npaFilter.Categories[0].Code': '01'
        'npaFilter.Kinds[0].ID': '1',
        'npaFilter.Kinds[0].Title': 'Проект постановления Правительства Российской Федерации',
        # 'npaFilter.Stages[0].Title': 'Текст',
        # 'npaFilter.Stages[0].ID': '30',
        # 'npaFilter.Statuses[0].Title': 'Идет обсуждение',
        # 'npaFilter.Statuses[0].ID': '30',

        # 'npaFilter.Stages[0].Title': 'Текст',
        # 'npaFilter.Stages[0].ID': '20',
        # 'npaFilter.Stages[1].Title': 'Оценка',
        # 'npaFilter.Stages[1].ID': '30',
        # 'npaFilter.Stages[2].Title': 'Завершение',
        # 'npaFilter.Stages[2].ID': '40',
        # 'npaFilter.Stages[3].Title': 'Принятие',
        # 'npaFilter.Stages[3].ID': '50',
        # 'npaFilter.Statuses[0].Title': 'Идет обсуждение',
        # 'npaFilter.Statuses[0].ID': '20',
        # 'npaFilter.Statuses[1].Title': 'Обсуждение завершено',
        # 'npaFilter.Statuses[1].ID': '30',
        # 'npaFilter.Statuses[2].Title': 'Разработка завершена',
        # 'npaFilter.Statuses[2].ID': '50',
        # 'npaFilter.Statuses[3].Title': 'Отказ от продолжения разработки',
        # 'npaFilter.Statuses[3].ID': '100',

        'npaFilter.ID': '0',
        'npaFilter.Hidden': 'false',
        'npaFilter.SortOrder': '-1',
        'npaFilter.RowVersion': ''
        }
    return params


def docs_folder(folder_name):
    
    docs_path = pathlib.Path.cwd()/folder_name
    if docs_path.is_dir():
        print(f'Папка с именем {folder_name} уже существует.')
    
    else:
        docs_path.mkdir()
        print(f'Создана новая папка с именем {folder_name}.')


def get_docs_list_pages_number(url):

    reg_pub_adapter = HTTPAdapter(max_retries=3)
    session = requests.Session()
    session.mount(url, reg_pub_adapter)
    
    page_size = config.getint('HTML_INTERACTIONS', 'DOCS_LIST_PAGE_SIZE')
    params = docs_list_params_setup(page_size=page_size)
    try:
        response = session.get(url, params=params)
        # response.raise_for_status()

    except(requests.RequestException, ValueError):
        print(f'Сетевая ошибка. Ответ на запрос количества документов не получен.')
        return False
    
    if response.json():
        page_list = response.json()
        docs_number = int(page_list['Total'])
        print(f'Количество документов в текущем запросе: {docs_number}')

        if docs_number > page_size:
            pages = docs_number//page_size + 1    
        else:
            pages = 1
        
        return pages


def get_docs_list():

    url = config['HTML_INTERACTIONS']['DOCS_LIST_RETRIEVAL_URL']

    reg_pub_adapter = HTTPAdapter(max_retries=3)
    session = requests.Session()
    session.mount(url, reg_pub_adapter)
    
    pages = get_docs_list_pages_number(url)
    
    if pages:
        docs_list = []

        for page in range(1, pages+1):
            page_size = config.getint('HTML_INTERACTIONS', 'DOCS_LIST_PAGE_SIZE')
            params = docs_list_params_setup(page_size=page_size)
            params['page'] = page
            try:
                # print(f'Получаю данные для страницы {page}')
                response = session.get(url, params=params)
                # response.raise_for_status()
                page_list = response.json()

            except(requests.RequestException, ValueError):
                print(f'Сетевая ошибка. Список документов для страницы {pages} не получен.')
            
            if len(page_list['Data']) > 0:
                print(f'Данные для страницы {page} получены успешно')
                page_list_data = page_list['Data']

                for page_item in page_list_data:
                    docs_list.append(page_item)

        return docs_list
    else:
        return False


def save_docs_list(docs_list):
    
    today_date_str = date.today().strftime('%Y%m%d')

    name_pattern = config['HTML_INTERACTIONS']['DOCS_LIST_FILE_NAME_PATTERN']

    with open(f'{name_pattern}_{today_date_str}.json', 'w', encoding='utf-8') as a_file:
        json.dump(docs_list, a_file, ensure_ascii=False)


def upload_json(file_name):

    with open(file_name, 'r', encoding='utf-8') as r_file:
        upl_data = json.load(r_file)
    
    return upl_data


def download_doc_file(doc_inner_meta):

    download_link = config['HTML_INTERACTIONS']['TEXT_FILES_DOWNLOAD_URL']

    doc_ID = doc_inner_meta['ID']
    text_versions_list = doc_inner_meta['text_versions']
    today_date_str = date.today().strftime('%Y%m%d')

    for version in text_versions_list:
        
        version_attrs = [*version][0]
        version_code = [*version.values()][0]
        
        # print(f'ID: {doc_ID}; version: {version_attrs}; code: {version_code}')
        params = {'fileid': version_code}
        
        folder_name = config['DEFAULT']['DOCS_SUBDIRECTORY_NAME']
        doc_path = pathlib.Path.cwd()/folder_name/f'{doc_ID}_{version_attrs}_{today_date_str}.docx'

        try:
            response = requests.get(download_link, params=params, allow_redirects=True)
            # response.raise_for_status()    
            if response.content:
                with open(doc_path, 'wb') as b_file:
                    b_file.write(response.content)  
                
                    print(f'{doc_ID}_{version_attrs}_{today_date_str}.docx сохранен успешно.')
            
            else:
                print(f'Документ с ID {doc_ID} версии {version_attrs} при запросе по коду вернул пустой doc файл.')

        except(requests.RequestException, ValueError):
            print(f'Сетевая ошибка. Документ ID {doc_ID} версия {version_attrs} не получен.')
        
        sleep_time = config.getint('HTML_INTERACTIONS', 'TEXT_FILES_DOWNLOADING_TIMESLEEP')
        time.sleep(sleep_time)


def get_doc_inner_meta(docs_list):

    for doc_record in docs_list:
        driver = webdriver.Firefox()

        doc_ID = str(doc_record['ID']) 
        doc_title = (doc_record['Title'])

        today_date_str = date.today().strftime('%Y%m%d')

        doc_inner_meta = {'ID': doc_ID, 'planned_stages': [], 'current_stage': '', 'text_versions': [], 'procedure_result': '', 'timestamp': today_date_str}
        # Не могу найти способ (interact_html_6.py) получить со страницы проекта 'likes': '', 'dislikes': ''
        print(f'Получаем данные со страницы проекта  {doc_ID}: "{doc_title}"')
        
        inner_meta_url = config['HTML_INTERACTIONS']['DOC_PROJECT_INNER_META_URL']
        doc_url = inner_meta_url + doc_ID      
        try:
            driver.get(doc_url)
            time.sleep(3)

            try:
                columns_presence = EC.presence_of_element_located((By.CLASS_NAME, 'h-tl-cols-wrap'))
                WebDriverWait(driver, 3).until(columns_presence)
            except Exception as ex:
                print(f'Ошибка парсинга: {ex}')
            
            doc_stage_columns = driver.find_element_by_class_name('h-tl-cols-wrap')
                    
            try:
                has_result = doc_stage_columns.find_element_by_xpath('.//i[@class="enum-ProcedureResult"]')
                doc_inner_meta['procedure_result'] = has_result.get_attribute('data-val')

            except:
                doc_inner_meta['procedure_result'] = 'no_result'

            
            doc_stage_columns_list = doc_stage_columns.find_elements_by_xpath('./child::*')
            current_found = False
            
            column_number = 1
            for col in doc_stage_columns_list:            
                column_name = col.find_element_by_xpath('.//p[@class="text-center visible-lg card-wrap-title"]').text
                doc_inner_meta['planned_stages'].append(column_name)
                
                try:
                    is_current = col.find_element_by_xpath('.//i[@class="stage-status"]')
                
                except:
                    doc_inner_meta['current_stage'] = column_name
                    current_found = True
                    # print(f'Ура! {column_name} текущая стадия!')
                
                try:
                    file_tags = col.find_elements_by_xpath('.//a[@class="file-link"]')

                    tag_number = 1
                    file_tag_link = False
                    file_tag_code = False
                    for tag in file_tags:

                        try:
                            doc_code_raw = tag.get_attribute('onclick')
                            doc_code = doc_code_raw.split("'")[1] 
                            file_tag_code = True
                        except:
                            
                            try:
                                doc_tobe_code = tag.get_attribute('href')
                                doc_code = doc_tobe_code.split("=")[1]
                                file_tag_link = True
                            except:
                                print('"file-link" - no code')

                        if file_tag_link == True or file_tag_code == True:
                            doc_version_name = f'stage_{column_number}_version_{tag_number}'
                            doc_version_element = {doc_version_name: doc_code}                        
                            doc_inner_meta['text_versions'].append(doc_version_element)
                            tag_number += 1
                        else:
                            doc_inner_meta['text_versions'].append(f'"file-link" found but text code not defined')

                except(selenium.common.exceptions.NoSuchElementException):
                    doc_inner_meta['text_versions'].append(f'no_text')
                
                column_number += 1

            if current_found == False:
                print(f'Для документа {doc_ID} не определена текущая стадия разработки!')
            
            folder_name = config['DEFAULT']['DOCS_SUBDIRECTORY_NAME']
            doc_inner_meta_file_name = f'{folder_name}/{doc_ID}_metadata_{today_date_str}.json'
            with open(doc_inner_meta_file_name, 'w', encoding='utf-8') as d_file:
                json.dump(doc_inner_meta, d_file, ensure_ascii=False)
        
        except Exception as ex:
            print(f'Сетевая ошибка: {ex}')
            return False
        
        download_doc_file(doc_inner_meta)

        driver.quit()


def doc_files_into_text():
    
    folder_name = config['DEFAULT']['DOCS_SUBDIRECTORY_NAME']
    doc_dir = pathlib.Path.cwd()/folder_name

    if any(doc_dir.iterdir()):

        for doc_file in doc_dir.iterdir():
            if doc_file.suffix == '.docx':
                document = docx2python(doc_file)
                doc_content = document.body
                doc_file_name = doc_file.name
                doc_attrs = doc_file_name.split('.')[0]

                doc_id = doc_attrs.split('_')[0]
                doc_version_stage = str(doc_attrs.split('_')[2])
                doc_version_on_stage = str(doc_attrs.split('_')[4])
                doc_download_timestamp = doc_attrs.split('_')[5]

                # doc_lenth = len(doc_content[0])
                # print(f'Первый элемент файла {doc_file_name} имеет длину {doc_lenth}.')

                # уточнить условие
                if len(doc_content[0]) > 0:

                    doc_content_list = [[{'ID': doc_id, 'stage': doc_version_stage, 'stage_version': doc_version_on_stage, 'download_timestamp': doc_download_timestamp}]]
                    for table in doc_content:
                        table_content = []
                        for row in table:
                            row_content = []
                            for cell in row:
                                cell_content = []
                                for par in cell:
                                    cell_content.append(par)
                                row_content.append(cell_content)
                            table_content.append(row_content)
                        doc_content_list.append(table_content)

                    with open(f'{doc_dir}/{doc_attrs}.json', 'w', encoding='utf-8') as a_file:
                        json.dump(doc_content_list, a_file, ensure_ascii=False)
                    
                else:
                    print(f'Пустой файл {doc_file}')
            else:
                continue
    else:
        print(f'Папка {folder_name} пуста.')


if __name__ == "__main__":
    
    config = configparser.ConfigParser()
    config.read('config.ini')
    folder_name = config['DEFAULT']['DOCS_SUBDIRECTORY_NAME']

    docs_folder(folder_name)
    
    docs_list = get_docs_list()
    # print(docs_list)

    save_docs_list(docs_list)

    # docs_list = upload_json('reg_pub_20210610_may_week.json')

    doc_inner_meta = get_doc_inner_meta(docs_list)

    doc_files_into_text()
