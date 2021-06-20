import json, pathlib
from elasticsearch import Elasticsearch
import configparser


def connect_elasticsearch():
    _es = None
    _es = Elasticsearch([{'host': 'localhost', 'port': 9200}])
    if _es.ping():
        print('Успешное соединение с ElasticSearch.')
    else:
        print('ElasticSearch не отвечает.')
    return _es


def create_index(index_name):
    index_created = False

    settings = {
        'settings': {
            'number_of_shards': 1,
            'number_of_replicas': 0,
            # "analysis": {
            #     "analyzer": {
            #         "htmlStripAnalyzer": {
            #         "type": "custom",
            #         "tokenizer": "standard",
            #         "char_filter": ["html_strip"]
            #         }
            #     }
            # }
        },
        'mappings': {
            '_doc': {
                'dynamic': 'true',
                'dynamic_date_formats': ['dd.MM.yyyy HH:mm:ss'],
                'properties': {
                    #___начало отображения аттрибутов проекта, приходящих в файле с перечнем проектов ("basic meta")___
                    "npa_ID": {'type': 'long'},
                    "SortOrder": {'type': 'long'},
                    "Statistic": {
                        'type': 'nested',
                        'properties': {
                            "Views": {'type': 'long'},
                            "Rating": {'type': 'double'},
                            "Comments": {'type': 'long'}
                        }
                    },
                    "IDProject": {'type': 'keyword'},
                    "Date": {'type': 'date'},
                    "PublishDate": {'type': 'date'},
                    "Title": {'type': 'text'},
                    "CreatorDepartment": {
                        'type': 'nested',
                        'properties': {
                            "ID": {'type': 'long'},
                            "Title": {'type': 'keyword'}
                        }
                    },
                    "CreatorDepartmentReal": {
                        'type': 'nested',
                        'properties': {
                            "ID": {'type': 'long'},
                            "Title": {'type': 'keyword'}
                        }
                    },
                    "Okveds": [{
                        'type': 'nested',
                        'properties': {
                            "ID": {'type': 'long'},
                            "Title": {'type': 'keyword'}    
                        }
                    }],
                    "Stage": {'type': 'short'},
                    "Status": {'type': 'short'},
                    "Category": {
                        'type': 'nested',
                        'properties': {
                            "ID": {'type': 'long'},
                            "Title": {'type': 'keyword'}
                        }
                    },
                    "Kind": {
                        'type': 'nested',
                        'properties': {
                            "ID": {'type': 'long'},
                            "Title": {'type': 'keyword'}
                        }
                    },
                    "Published": {'type': 'boolean'},
                    "DegreeRegulatoryImpact": {'type': 'long'},
                    "StartDiscussion": {'type': 'date'},
                    "EndDiscussion": {'type': 'date'},
                    "ParallelStageStartDiscussion": {'type': 'date'},
                    "ParallelStageEndDiscussion": {'type': 'date'},
                    "DiscussionPercentage": {'type': 'double'},
                    "DiscussionDaysLeft": {'type': 'long'},
                    "RegionSignificant": {'type': 'boolean'},
                    "ControlSupervisoryActivities": {'type': 'boolean'},
                    "RegulatorScissors": {'type': 'boolean'},

                    #___аттрибуты проекта, полученные со "страницы" самого проекта ("inner meta")___
                    "planned_stages": [{'type': 'keyword'}],
                    "current_stage": {'type': 'keyword'},
                    "keywords": [{'type': 'keyword'}],
                    "justification": {'type': 'text'},
                    "linked_docs": {'type': 'text'},
                    "comments": {'type': 'text'},

                    "Text_version_1": {
                        'type': 'nested',
                        'properties': {
                            "version_stage": {'type': 'short'},
                            "version_number_on_stage": {'type': 'short'},
                            "text_version_name": {'type': 'text'},
                            "version_timestamp": {'type': 'keyword'},
                            "version_download_code": {'type': 'keyword'},
                            "version_text": {
                                'type': 'flattened',
                                # "analyzer": "htmlStripAnalyzer"
                            }
                        }
                    },
                    "Text_version_2": {
                        'type': 'nested',
                        'properties': {
                            "version_stage": {'type': 'short'},
                            "version_number_on_stage": {'type': 'short'},
                            "text_version_name": {'type': 'text'},
                            "version_timestamp": {'type': 'keyword'},
                            "version_download_code": {'type': 'keyword'},
                            "version_text": {
                                'type': 'flattened',
                                # "analyzer": "htmlStripAnalyzer"
                            }
                        }
                    },
                    "Text_version_3": {
                        'type': 'nested',
                        'properties': {
                            "version_stage": {'type': 'short'},
                            "version_number_on_stage": {'type': 'short'},
                            "text_version_name": {'type': 'text'},
                            "version_timestamp": {'type': 'keyword'},
                            "version_download_code": {'type': 'keyword'},
                            "version_text": {
                                'type': 'flattened',
                                # "analyzer": "htmlStripAnalyzer"
                            }
                        }
                    },
                    "Text_version_4": {
                        'type': 'nested',
                        'properties': {
                            "version_stage": {'type': 'short'},
                            "version_number_on_stage": {'type': 'short'},
                            "text_version_name": {'type': 'text'},
                            "version_timestamp": {'type': 'keyword'},
                            "version_download_code": {'type': 'keyword'},
                            "version_text": {
                                'type': 'flattened',
                                # "analyzer": "htmlStripAnalyzer"
                            }
                        }
                    },
                    "Text_version_5": {
                        'type': 'nested',
                        'properties': {
                            "version_stage": {'type': 'short'},
                            "version_number_on_stage": {'type': 'short'},
                            "text_version_name": {'type': 'text'},
                            "version_timestamp": {'type': 'keyword'},
                            "version_download_code": {'type': 'keyword'},
                            "version_text": {
                                'type': 'flattened',
                                # "analyzer": "htmlStripAnalyzer"
                            }
                        }
                    },
                    "ORV_1": {
                        'type': 'nested',
                        'properties': {
                            "ORV_result": {'type': 'keyword'},
                            "ORV_version_name": {'type': 'text'},
                            "ORV_text_timestamp": {'type': 'keyword'},
                            "ORV_download_code": {'type': 'keyword'},
                            "ORV_conclusion_text": {
                                'type': 'flattened',
                                # "analyzer": "htmlStripAnalyzer"
                            }
                        }
                    },
                    "ORV_2": {
                        'type': 'nested',
                        'properties': {
                            "ORV_result": {'type': 'keyword'},
                            "ORV_version_name": {'type': 'text'},
                            "ORV_text_timestamp": {'type': 'keyword'},
                            "ORV_download_code": {'type': 'keyword'},
                            "ORV_conclusion_text": {
                                'type': 'flattened',
                                # "analyzer": "htmlStripAnalyzer"
                            }
                        }
                    }
                }
            }
        }
    }

    es = connect_elasticsearch()

    try:
        if not es.indices.exists(index_name):
            # Не совсем понимаю, зачем это при наличии условия выше: Ignore 400 means to ignore "Index Already Exist" error.
            es.indices.create(index=index_name, ignore=400, body=settings)
            created = True
    except Exception as ex:
        print(str(ex))
    finally:
        return created


def upload_docs_list(file_name):

    with open(file_name, 'r', encoding='utf-8') as r_file:
        upl_docs_list = json.load(r_file)
    
    return upl_docs_list


def upload_project_inner_meta(doc_ID):
    
    folder_name = config['DEFAULT']['DOCS_SUBDIRECTORY_NAME']
    docs_dir = pathlib.Path.cwd()/folder_name
    
    if any(docs_dir.iterdir()):
        for current_file in docs_dir.iterdir():
            if current_file.suffix == '.json':
                current_file_name = current_file.name
                current_attrs = current_file_name.split('.')[0]
                current_id = str(current_attrs.split('_')[0])
                current_file_type = str(current_attrs.split('_')[1])
                inner_meta_found = False
               
                if current_file_type == 'metadata' and current_id == doc_ID:

                    inner_meta_found = True
                    with open(f'{docs_dir}/{current_file_name}', 'r', encoding='utf-8') as meta_file:
                        project_inner_meta = json.load(meta_file)

                        if project_inner_meta['ID'] == str(doc_ID):
                            return project_inner_meta

                        else:
                            print(f'Проверьте файл с метаданными для проекта под номером {doc_ID}. Данные ошибочны.')
                            return False

        if inner_meta_found == False:
                    print(f'Для проекта под номером {doc_ID} не найден файл с метаданными.')
                    return False
    else:

        print(f'Папка {folder_name} пуста. Запустите сбор информации с сайта "regulation.gov.ru".')
        return False

def upload_doc_version_text(version_file_name):
    
    folder_name = config['DEFAULT']['DOCS_SUBDIRECTORY_NAME']
    doc_path = pathlib.Path.cwd()/folder_name/f'{version_file_name}'

    try:
        with open(doc_path, 'r', encoding='utf-8') as v_file:
            version_text = json.load(v_file)
            return version_text
    except:
        print(f'Файл {version_file_name} не загружен в папку {folder_name} или не приведен к json формату.')
        return False

def compose_upload_data_to_es(docs_list, index_name):
    docs_list_lenth = len(docs_list)
    docs_upl = 0
    for doc_basic_meta in docs_list:
        doc_ID = str(doc_basic_meta['ID'])
        
        doc_dataset = {
            "npa_ID": int(doc_basic_meta['ID']),
            "SortOrder": int(doc_basic_meta['SortOrder']),
            "Statistic": {
                "Views": int(doc_basic_meta['Statistic']['Views']),
                "Rating": float(doc_basic_meta['Statistic']['Rating']),
                "Comments": int(doc_basic_meta['Statistic']['Comments'])
            },
            "IDProject": doc_basic_meta['IDProject'],
            "Date": doc_basic_meta['Date'],
            "PublishDate": doc_basic_meta['PublishDate'],
            "Title": doc_basic_meta['Title'],
            "CreatorDepartment": {
                "ID": int(doc_basic_meta['CreatorDepartment']['ID']),
                "Title": doc_basic_meta['CreatorDepartment']['Title']
            },
            "CreatorDepartmentReal": {
                "ID": int(doc_basic_meta['CreatorDepartmentReal']['ID']),
                "Title": doc_basic_meta['CreatorDepartmentReal']['Title']
            },

            "Okveds": [],
            "Stage": int(doc_basic_meta['Stage']),
            "Status": int(doc_basic_meta['Status']),
            "Category": {
                "ID": int(doc_basic_meta['Category']['ID']),
                "Title": doc_basic_meta['Category']['Title']
            },
            "Kind": {
                "ID": int(doc_basic_meta['Kind']['ID']),
                "Title": doc_basic_meta['Kind']['Title']
            },
            "Published": doc_basic_meta['Published'],
            "DegreeRegulatoryImpact": int(doc_basic_meta['DegreeRegulatoryImpact']),
            "StartDiscussion": doc_basic_meta['StartDiscussion'],
            "EndDiscussion": doc_basic_meta['EndDiscussion'],
            "ParallelStageStartDiscussion": doc_basic_meta['ParallelStageStartDiscussion'],
            "ParallelStageEndDiscussion": doc_basic_meta['ParallelStageEndDiscussion'],
            "DiscussionPercentage": (doc_basic_meta['DiscussionPercentage']),
            "DiscussionDaysLeft": (doc_basic_meta['DiscussionDaysLeft']),
            "RegionSignificant": doc_basic_meta['RegionSignificant'],
            "ControlSupervisoryActivities": doc_basic_meta['ControlSupervisoryActivities'],
            "RegulatorScissors": doc_basic_meta['RegulatorScissors'],
        }
        okveds_count = 0
        for area in doc_basic_meta['Okveds']:
            okved = {"ID": int(doc_basic_meta['Okveds'][okveds_count]['ID']), "Title": doc_basic_meta['Okveds'][okveds_count]['Title']}
            doc_dataset['Okveds'].append(okved)
            okveds_count += 1

        if upload_project_inner_meta(doc_ID):
            doc_inner_meta = upload_project_inner_meta(doc_ID)
            doc_dataset["planned_stages"] = doc_inner_meta['planned_stages']
            doc_dataset["current_stage"] = doc_inner_meta['current_stage']

            doc_dataset["justification"] = doc_inner_meta['justification']
            doc_dataset["linked_docs"] = doc_inner_meta['linked_docs']
            doc_dataset["comments"] = doc_inner_meta['comments']
            doc_dataset["keywords"] = []

            doc_keywords = doc_inner_meta['keywords']
            doc_keywords_del = doc_keywords.replace(';', ',')
            doc_keywords_split = doc_keywords_del.split(',')
            if type(doc_keywords_split) == list:
                for keyword in doc_keywords_split:
                    keyword_strip = keyword.strip()
                    doc_dataset["keywords"].append(keyword_strip)
            else:
                keyword_strip = doc_keywords_split.strip()
                doc_dataset["keywords"].append(keyword_strip)

            text_versions_list = doc_inner_meta['text_versions']
            # today_date_str = date.today().strftime('%Y%m%d')
            version_download_timestamp = doc_inner_meta['timestamp']
            text_v_num = 1
            orv_v_num = 1
            if len(text_versions_list) > 0:
                for version in text_versions_list:                    
                    version_code = [*version.values()][0]
                    version_attrs = [*version][0]
                    version_file_name = f'{doc_ID}_{version_attrs}_{version_download_timestamp}.json'

                    if upload_doc_version_text(version_file_name):
                        doc_version_text = upload_doc_version_text(version_file_name)
                        version_stage = int(doc_version_text[0][0]["stage"])
                        # print(f'{version_file_name} version_stage: {version_stage}')
                        version_stage_name = doc_inner_meta["planned_stages"][version_stage - 1]
                        # print(f'{version_file_name} version_stage_name: {version_stage_name}')

                        version_site_names = doc_inner_meta["text_version_names"]
                        for site_name in version_site_names:
                            if [*site_name][0] == version_attrs:
                                site_name_text = [*site_name.values()][0]

                        version_stage_name_split = version_stage_name.split(' ')
                        if 'ОРВ' in version_stage_name_split:
                            orv_map_name = "ORV_" + str(orv_v_num)
                            doc_dataset[orv_map_name] = {
                                "ORV_stage": version_stage,
                                "ORV_result": doc_inner_meta["procedure_result"],
                                "ORV_version_name": site_name_text,
                                "ORV_text_timestamp": doc_inner_meta["timestamp"],
                                "ORV_download_code": version_code,
                                "ORV_conclusion_text": str(doc_version_text)
                            }
                            orv_v_num += 1

                            print(f'{version_file_name} - текст на стадии "ОРВ".')

                        else:
                            text_map_name = "Text_version_" + str(text_v_num)
                            doc_dataset[text_map_name] = {
                                "version_stage": version_stage,
                                "version_number_on_stage": int(doc_version_text[0][0]["stage_version"]),
                                "text_version_name": site_name_text,
                                "version_timestamp": doc_inner_meta["timestamp"],
                                "version_download_code": version_code,
                                "version_text": str(doc_version_text)
                            }
                            text_v_num += 1
                            
                            print(f'{version_file_name} - текст на стадии {version_stage_name}')

                    else:
                        raise Exception(f'Файл {doc_ID}_{version_attrs}_{version_download_timestamp}.json не загружен или не приведен к json-формату.')

        # print(doc_dataset)

        es = connect_elasticsearch()

        # is_stored = True
        try:
            outcome = es.index(index=index_name, body=doc_dataset)

            docs_upl += 1
            
        except Exception as ex:
            print('Ошибка при загрузке данных в базу.')
            print(str(ex))
            # is_stored = False

    print(f'Из {docs_list_lenth} документов в списке сохранено в базу: {docs_upl} документов')


def index_deletion(index_name):
    
    es = connect_elasticsearch()
    try:
        es.indices.delete(index=index_name)
    except Exception as ex:
        print('Ошибка при удалении индекса из базы.')
        print(str(ex))


if __name__ == "__main__":
    
    config = configparser.ConfigParser()
    config.read('config.ini')
    index_name = config['ELASTICSEARCH']['ES_INDEX_NAME']

    ci = create_index(index_name)
    print(f'Индекс для {index_name} создан: {ci}')

    docs_list = upload_docs_list('reg_pub_test_20210615.json')
    # l = len(docs_list)
    # print(f'Длина полученного списка документов: {l}')

    compose_upload_data_to_es(docs_list, index_name)
    
    # Ниже расположен вызов функции, удаляющей созданный индекс со всеми данными. Будьте осторожны!!!
    # index_deletion(index_name)

