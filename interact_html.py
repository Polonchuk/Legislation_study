import requests, json, time, pathlib, logging
from requests.adapters import HTTPAdapter
from datetime import date, datetime
from docx2python import docx2python
import selenium
from selenium import webdriver
# from selenium.common.exceptions import NoSuchElementException
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
        logger.warning('No connection: Ответ на запрос количества документов не получен.')
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
    else:
        logger.warning(f'Missing data: Нет информации о колличестве страниц запроса.')
        return False        


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
                print(f'Сетевая ошибка. Список документов для страницы {page} не получен.')
                logger.warning(f'No connection: Список документов для страницы {page} не получен.')
            
            if len(page_list['Data']) > 0:
                print(f'Данные для страницы {page} получены успешно')
                page_list_data = page_list['Data']

                for page_item in page_list_data:
                    docs_list.append(page_item)

        return docs_list
    else:
        return False


def save_docs_list(docs_list):
    
    if docs_list:
        today_date_str = date.today().strftime('%Y%m%d')

        name_pattern = config['HTML_INTERACTIONS']['DOCS_LIST_FILE_NAME_PATTERN']

        with open(f'{name_pattern}_{today_date_str}.json', 'w', encoding='utf-8') as a_file:
            json.dump(docs_list, a_file, ensure_ascii=False)


def upload_json(file_name):
    
    try:
        with open(file_name, 'r', encoding='utf-8') as r_file:
            upl_data = json.load(r_file)
        
        return upl_data
    except:
        print(f'Missing object: Файл {file_name} отсутствует в текущей рабочей директории.')
        logger.warning(f'Missing object: Файл {file_name} отсутствует в текущей рабочей директории.')


def read_docs_list(docs_list):

    trial_docs_amount = 20

    docs_list_len = len(docs_list)
    if docs_list_len > trial_docs_amount:
        while True:
            user_input = input(f'Список документов для загрузки содержит {docs_list_len} проект(а/ов). Полная загрузка всей информации по проектам может занять значительное время. Нажмите "y" (латиницей), а затем "Enter", если готовы продолжать. В противном случае нажмите "n", а затем "Enter".')
            if user_input.lower() == 'y':
                for doc_record in docs_list:
                    doc_ID = str(doc_record['ID']) 
                    doc_title = (doc_record['Title'])
                    
                    get_doc_inner_meta(doc_ID, doc_title)
                
                doc_files_into_text()
                break

            elif user_input.lower() == 'n':
                print('Скрипт завершает работу без скачивания подробных данных о проектах с сайта.')
                break

            else:
                print('Нажмите "y" (латиницей), а затем "Enter", если готовы продолжать. В противном случае нажмите "n", а затем "Enter".')
    else:
        for doc_record in docs_list:
            doc_ID = str(doc_record['ID']) 
            doc_title = (doc_record['Title'])
            
            get_doc_inner_meta(doc_ID, doc_title)
                
        doc_files_into_text()


def get_doc_inner_meta(doc_ID, doc_title):

    driver = webdriver.Firefox()

    today_date_str = date.today().strftime('%Y%m%d')
    doc_inner_meta = {'ID': doc_ID, 'planned_stages': [], 'current_stage': '', 'keywords': '', 'justification': '', 'linked_docs': '', 'comments': '', 'text_versions': [], 'text_version_names': [], 'procedure_result': '', 'timestamp': today_date_str}

    print(f'Получаем данные со страницы проекта  {doc_ID}: "{doc_title}"')
    
    inner_meta_url = config['HTML_INTERACTIONS']['DOC_PROJECT_INNER_META_URL']
    doc_url = inner_meta_url + doc_ID      
    try:
        driver.get(doc_url)
        # time.sleep(3)

        try:
            WebDriverWait(driver, 20).until(EC.presence_of_element_located((By.CLASS_NAME, 'h-tl-cols-wrap')))        
            doc_stage_columns = driver.find_element_by_class_name('h-tl-cols-wrap')
#_____________________Пробуем найти на странице маркер результата процедуры "Оценка регулирующего воздействия"_                   
            try:
                has_result = doc_stage_columns.find_element_by_xpath('.//i[@class="enum-ProcedureResult"]')
                doc_inner_meta['procedure_result'] = has_result.get_attribute('data-val')

            except:
                doc_inner_meta['procedure_result'] = 'no_result'
#______________________Собираем колонки с этапами утверждения проекта, как список элементов___________________
            try:
                doc_stage_columns_list = doc_stage_columns.find_elements_by_xpath('./child::*')

#______________________Анализируем каждый этап (колонку) отдельно_______________________________
                current_found = False
                column_number = 1
                for col in doc_stage_columns_list: 
#_______________________Получаем название этапа__________________________________________________
                    try:
                        column_name = col.find_element_by_xpath('.//p[@class="text-center visible-lg card-wrap-title"]').text
                        doc_inner_meta['planned_stages'].append(column_name)
                    except:
                        print(f'На странице проекта {doc_ID} не найдены названия столбцов')
                        logger.warning(f'Parsing: На странице проекта {doc_ID} не найдены названия столбцов')
#_______________________Проверяем, является ли колонка текущей стадией проекта______________________
                    if column_name:
                        try:
                            col.find_element_by_xpath('.//i[@class="stage-status"]')
                        
                        except:
                            doc_inner_meta['current_stage'] = column_name
                            current_found = True
                            # print(f'Ура! {column_name} текущая стадия!')
#_Начинаем поиск в колонке "видимых" (присутствующих без дополнительных операций на странице) ссылок на текстовые файлы_                 
                    try:
                        file_tags = col.find_elements_by_xpath('.//a[@class="file-link"]')
#_Если ссылка присутствует, пробуем получить "код" документа для дальнейшего скачивания__________
                        tag_number = 1
                        file_tag_code = False
                        for tag in file_tags:
                            if tag.get_attribute('onclick'):
                                doc_tobe_code = tag.get_attribute('onclick')
                                doc_code = doc_tobe_code.split("'")[1] 
                                file_tag_code = True
                            else:                            
                                if tag.get_attribute('href'):
                                    doc_tobe_code = tag.get_attribute('href')
                                    doc_code = doc_tobe_code.split("=")[1]
                                    file_tag_code = True
                            
                            doc_version_name = f'stage_{column_number}_version_{tag_number}'
#___Если код получен, сохраняем сам код, порядковый номер стадии, документа в текущей стадии и текст, отображенный на ссылке___
                            if file_tag_code == True:
                                doc_site_name = tag.find_element_by_xpath('.//span[1]').text
                                doc_version_element = {doc_version_name: doc_code}                        
                                doc_inner_meta['text_versions'].append(doc_version_element)
                                doc_version_name_element = {doc_version_name: doc_site_name}
                                doc_inner_meta['text_version_names'].append(doc_version_name_element)
                            else: 
                                doc_version_element = {doc_version_name: None}                        
                                doc_inner_meta['text_versions'].append(doc_version_element)
                                logger.warning(f'Parsing: На странице проекта {doc_ID}, в колонке № {column_number} найдена ссылка (class="file-link"), но не определен код документа.')
                            tag_number += 1

                    except:
                        print(f'Непосредственно в колонке № {column_number} текста документа нет.')
                    
                    if column_name:
                        column_name_split = column_name.split(' ')
#___Собираем информацию в разделе "Паспорт проекта"________________________
                    if column_number == 1:
                        try:
                            # WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.XPATH, './/a[@class="btn btn-default"]')))
                            # col.find_element_by_xpath('.//a[@class="btn btn-default"]').click()
                            WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.PARTIAL_LINK_TEXT, 'Паспорт')))
                            col.find_element_by_partial_link_text('Паспорт').click()
                            time.sleep(2)
                            try:
                                WebDriverWait(driver, 5).until(EC.presence_of_element_located((By.CSS_SELECTOR, 'dt')))
                                window_meta_info_rows = driver.find_elements_by_css_selector('dt')
                                # dt_number = len(window_meta_info_rows)
                                # print(f'Количество найденных "dt" элементов: {dt_number}')
                                for row in window_meta_info_rows:
                                    row_name = row.text
                                    try:
                                        row_text = row.find_element_by_xpath('.//following::dd').text
                                    
                                        if row_name: 
                                            row_name_split = row_name.split(' ', 1)
                                            if row_name_split[0] == 'Ключевые':
                                                doc_inner_meta['keywords'] = row_text                                            
                                            elif row_name_split[0] == 'Основание':
                                                doc_inner_meta['justification'] = row_text
                                            elif row_name_split[0] == 'Связанные':
                                                doc_inner_meta['linked_docs'] = row_text
                                            elif row_name_split[0] == 'Комментарий':
                                                doc_inner_meta['comments'] = row_text                                        
                                        else:
                                            print(f'При выполнении сценария "Паспорт проекта" для проекта {doc_ID} не найден текст элемента "<dt>".')
                                            logger.warning(f'Parsing: При выполнении сценария "Паспорт проекта" для проекта {doc_ID} не найден текст элемента "<dt>".')
                                    except:
                                        print(f'При выполнении сценария "Паспорт проекта" для проекта {doc_ID} не найден элемент <dd>.')
                                        logger.warning(f'Parsing: При выполнении сценария "Паспорт проекта" для проекта {doc_ID} не найдены элементы "<dd>".')       
                            except:
                                print(f'При выполнении сценария "Паспорт проекта" для проекта {doc_ID} не найдены элементы "<dt>".')
                                logger.warning(f'Parsing: При выполнении сценария "Паспорт проекта" для проекта {doc_ID} не найдены элементы "<dt>".')
                            
                            try:
                                driver.find_element_by_xpath('.//a[@class="btn btn-primary closeBtn"]').click()
                                time.sleep(2)
                            except:
                                print(f'Не могу закрыть окно "Паспорт проекта" для {doc_ID}!!!')
                                logger.warning(f'Parsing: При выполнении сценария "Паспорт проекта" для проекта {doc_ID} не удается закрыть окно "Паспорт проекта" (class="btn btn-primary closeBtn").')

                        except:
                            print(f'В первой колонке для проекта {doc_ID} не найдена ссылка, содержащая слово "Паспорт".')
                            logger.warning(f'Parsing: На странице проекта {doc_ID}, в колонке № {column_number} не найдена ссылка по тексту "Паспорт".')
                
#_В случае с этапом "Независимая антикоррупционная экспертиза" ссылка на документ, как правило, спрятана в "скрытом" разделе "Информация по проекту". Она обнаруживается после запуска скрипта кликом на соответствующем элементе__
#_!!!___________________TODO: Уточнить условие, при котором этот сценарий должен работать___________
                    elif column_name and column_name_split[0] == 'Независимая':                        
                        try:
                            WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.XPATH, './/a[@class="btn btn-default"]')))
                            inner_element_name = col.find_element_by_xpath('.//a[@class="btn btn-default"]').text
                            # print(f'Обращаемся к скрытому разделу: {inner_element_name}')
                            col.find_element_by_xpath('.//a[@class="btn btn-default"]').click()                    
                            time.sleep(2)
                            try:
                                WebDriverWait(driver, 5).until(EC.presence_of_element_located((By.CSS_SELECTOR, 'dd')))
                                window_meta_info_rows = driver.find_elements_by_css_selector('dd')
                                # dd_number = len(window_meta_info_rows)
                                # print(f'Количество найденных "dd" элементов: {dd_number}')

#_____________Анализируем открывшуюся таблицу построчно. Ищем ссылки с кодом для скачивания текстов документов.___
                                text_number = 1
                                file_row_code = False
                                for row in window_meta_info_rows:
                                    try:
                                        a_row = row.find_element_by_xpath('.//a')
                                        if a_row.get_attribute('onclick'):
                                            doc_tobe_code = a_row.get_attribute('onclick')
                                            doc_code = doc_tobe_code.split("'")[1] 
                                            file_row_code = True
                                            # print('Нашел onclick')
                                        else:                                    
                                            if a_row.get_attribute('href'):
                                                doc_tobe_code = a_row.get_attribute('href')
                                                doc_code = doc_tobe_code.split("=")[1]
                                                file_row_code = True
                                                # print('Нашел href')
#_________Сохраняем полученные коды для скачивания документов и дополнительную информацию к ним_____                                 
                                        doc_version_name = f'stage_{column_number}_version_2{text_number}'
                                        if file_row_code == True:
                                            doc_site_name = row.find_element_by_xpath('.//preceding::dt').text
                                            full_doc_site_name = str(inner_element_name) + '-' + str(doc_site_name)
                                            doc_version_element = {doc_version_name: doc_code}                        
                                            doc_inner_meta['text_versions'].append(doc_version_element)
                                            doc_version_name_element = {doc_version_name: full_doc_site_name}
                                            doc_inner_meta['text_version_names'].append(doc_version_name_element)

                                        else:
                                            print('На странице НАЭ не нашел кода документа в ".//a"') 
                                            doc_version_element = {doc_version_name: None}                        
                                            doc_inner_meta['text_versions'].append(doc_version_element)
                                        text_number += 1
                                    except:
                                        file_row_code = False
                            except:
                                print(f'При выполнении сценария "Независимая антикор. эксп." для проекта {doc_ID} не найдены элементы "<dd>".')
                                logger.warning(f'Parsing: При выполнении сценария "Независимая антикор. эксп." для проекта {doc_ID} не найдены элементы "<dd>".')  
                            try:
                                driver.find_element_by_xpath('.//a[@class="btn btn-primary closeBtn"]').click()
                                time.sleep(2)
                            except:
                                print(f'Не могу закрыть окно "Независимая антикор. эксп." для {doc_ID}!!!')
                                logger.warning(f'Parsing: При выполнении сценария "Независимая антикор. эксп." для проекта {doc_ID} не удается закрыть окно "Независимая антикор. эксп." (class="btn btn-primary closeBtn").')
                        except:
                            print(f'В колонке "Независимая антикор. эксп." для проекта {doc_ID} не найден класс "btn btn-default".')
                            logger.warning(f'Parsing: На странице проекта {doc_ID} при выполнении сценария "Независимая антикор. эксп." не найдена ссылка по имени класса (class="btn btn-default).')
#_______________________Переходим к следующей колонке ________
                    column_number += 1
            except:
                print(f'На странице проекта {doc_ID} не найдены столбцы ("child" для класса "h-tl-cols-wrap")')
                logger.warning(f'Parsing: На странице проекта {doc_ID} не найдены столбцы ("child" для класса "h-tl-cols-wrap")')

            if current_found == False:
                print(f'Для документа {doc_ID} не определена текущая стадия разработки!')
                logger.warning(f'Parsing: На странице проекта {doc_ID} не определена текущая стадия разработки (колонка без класса "stage-status).')
#__Сохраняем мета-данные по проекту (с кодами для скачивания текстов) в отдельном файле, общем для всего проекта_____
# _________________________________TODO: Уточнить условие, когда это имеет смысл делать______________________            
            folder_name = config['DEFAULT']['DOCS_SUBDIRECTORY_NAME']
            doc_inner_meta_file_name = f'{folder_name}/{doc_ID}_metadata_{today_date_str}.json'
            # doc_inner_meta_file_name = f'{folder_name}/{doc_ID}_metadata_test.json'

            with open(doc_inner_meta_file_name, 'w', encoding='utf-8') as d_file:
                json.dump(doc_inner_meta, d_file, ensure_ascii=False)
#__Запускаем скачивание всех текстов документов по всем кодам на скачивание, собранным со страницы проекта___
# __________________________________TODO: Уточнить условие, когда это имеет смысл делать______________________    
         
            download_doc_file(doc_inner_meta)

        except Exception as ex:
            print(f'На странице проекта {doc_ID} не найден общий класс для столбцов (класс "h-tl-cols-wrap"): {ex}')
            logger.warning(f'Parsing: На странице проекта {doc_ID} не найден общий класс для столбцов (класс "h-tl-cols-wrap"): {ex}')
    except Exception as ex:
        print(f'Ошибка при обращении браузера к странице проекта: {ex}')
        logger.warning(f'No connection: Ошибка при обращении браузера к странице проекта: {ex}')

    driver.quit()


def download_doc_file(doc_inner_meta):

    download_link = config['HTML_INTERACTIONS']['TEXT_FILES_DOWNLOAD_URL']

    doc_ID = doc_inner_meta['ID']
    text_versions_list = doc_inner_meta['text_versions']
    today_date_str = date.today().strftime('%Y%m%d')

    for version in text_versions_list:
        if [*version.values()][0] != None:
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
                    logger.warning(f'Missing data: Документ с ID {doc_ID} версии {version_attrs} при запросе по коду вернул пустой doc файл.')

            except(requests.RequestException, ValueError):
                print(f'Сетевая ошибка. Документ ID {doc_ID} версия {version_attrs} не получен.')
                logger.warning(f'No connection: Документ ID {doc_ID} версия {version_attrs} не получен.')
            
            sleep_time = config.getint('HTML_INTERACTIONS', 'TEXT_FILES_DOWNLOADING_TIMESLEEP')
            time.sleep(sleep_time)


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

                doc_ID = doc_attrs.split('_')[0]
                doc_version_stage = str(doc_attrs.split('_')[2])
                doc_version_on_stage = str(doc_attrs.split('_')[4])
                doc_download_timestamp = doc_attrs.split('_')[5]

                # doc_lenth = len(doc_content[0])
                # print(f'Первый элемент файла {doc_file_name} имеет длину {doc_lenth}.')

                # уточнить условие
                if len(doc_content[0]) > 0:

                    doc_content_list = [[{'ID': doc_ID, 'stage': doc_version_stage, 'stage_version': doc_version_on_stage, 'download_timestamp': doc_download_timestamp}]]
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
                    logger.warning(f'Missing data: doc-файл проекта с ID {doc_ID} версии {doc_attrs} не содержит текста.')
            else:
                continue
    else:
        print(f'Папка {folder_name} пуста.')
        logger.warning(f'Missing data: при попытке прочесть скачаные doc-файлы папка {folder_name} оказалась пуста.')


if __name__ == "__main__":
    
    logger = logging.getLogger('reg_logger')
    reg_handler = logging.FileHandler('reg.log')
    reg_handler.setLevel(logging.WARNING)
    reg_format = logging.Formatter('%(name)s - %(message)s')
    reg_handler.setFormatter(reg_format)
    logger.addHandler(reg_handler)

    config = configparser.ConfigParser()
    config.read('config.ini')
    folder_name = config['DEFAULT']['DOCS_SUBDIRECTORY_NAME']
    docs_folder(folder_name)
    
    docs_list = get_docs_list()

    save_docs_list(docs_list)

    # Строка ниже - это подгрузка уже имеющегося "списка документов" (get_docs_list()). Используется для отладки и тестирования.
    # docs_list = upload_json('reg_pub_test_20210615.json')

    read_docs_list(docs_list)

