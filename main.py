import requests
import os
from terminaltables import AsciiTable
from dotenv import load_dotenv


POPULAR_LANGUAGES = [
        'Python',
        'Java Script',
        'Java',
        'Ruby', 
        'PHP', 
        'C++', 
        'C#', 
        'C', 
        '1C'
]


def predict_rub_salary_hh():
    url = 'https://api.hh.ru/vacancies'
    number_of_days_in_month = 30
    moscow_id = 1
    hh_salaries = []
    for language in POPULAR_LANGUAGES:
        vacancies_salaries = []
        page_number = 0
        pages = 1
        while page_number < pages:
            params = {
                    'text' : f'Программист {language}',
                    'area' : moscow_id,
                    'period' : number_of_days_in_month,
                    'page' : page_number
            }
            response = requests.get(url, params=params)
            response.raise_for_status()
            page = response.json()
            vacancies = page['items']
            for vacancy in vacancies:
                vacancy_period_salary = vacancy['salary']
                if not vacancy_period_salary:
                    continue
                payment_from = vacancy_period_salary['from']
                payment_to = vacancy_period_salary['to']
                currency = vacancy_period_salary['currency']
                predicted_salary = predict_rub_salary(currency, payment_to, payment_from)
                if predicted_salary:
                    vacancies_salaries.append(predicted_salary)
            pages = page['pages']
            page_number+=1
        vacancies_processed = len(vacancies_salaries)
        if vacancies_processed:
            average_salary = int(sum(vacancies_salaries) / vacancies_processed)
        else:
            average_salary = 0
        languages_average_salary = {
                'language' : language,
                'vacancies_found' : page['found'],
                'vacancies_processed' : vacancies_processed,
                'average_salary' : average_salary
        }
        hh_salaries.append(languages_average_salary)
    return hh_salaries


def predict_rub_salary_for_superJob(token):
    url_super_job = 'https://api.superjob.ru/2.0/vacancies/'
    sj_salaries = []
    headers = {
         'X-Api-App-Id' : token,
         'Content-Type': 'application/x-www-form-urlencoded'
    }
    for language in POPULAR_LANGUAGES:
        average_salary = 0
        vacancies_salaries = []
        page_number = 0
        moscow_id = 4
        while True:
            params = {
                'town' : moscow_id,
                'keyword' : f'{language}',
                'page' : page_number
            }
            response = requests.get(url_super_job, headers=headers, params=params)
            response.raise_for_status()
            result = response.json()
            for vacancy in result['objects']:
                payment_from = vacancy['payment_from']
                payment_to = vacancy['payment_to']
                currency = vacancy['currency']
                predicted_salary = predict_rub_salary(currency, payment_to, payment_from)
                if predicted_salary:
                    vacancies_salaries.append(predicted_salary)
            page_number+=1
            if not result['more']:
                break
        vacancies_processed = len(vacancies_salaries)
        if vacancies_processed:
            average_salary = int(sum(vacancies_salaries) / vacancies_processed)
        languages_average_salary = {
            'language' : language,
            'vacancies_found' : result['total'],
            'vacancies_processed' : vacancies_processed,
            'average_salary' : average_salary
        }
        sj_salaries.append(languages_average_salary)
    return sj_salaries


def predict_rub_salary(currency, salary_to, salary_from):
    if not (currency == 'rub' or currency == 'RUR'):
        return None
    if salary_to and salary_from:
        return (salary_to + salary_from) / 2
    elif salary_from:
        return salary_from * 1.2
    elif salary_to:
        return salary_to * 0.8
    else:
        return
    

def make_table(languages, title):
    table_payload = [['Язык программирования', 'Вакансий найдено', 'Вакансий обработано', 'Средняя зарплата']]
    for language in languages:
        table_row = [
            language['language'],
            language['vacancies_found'],
            language['vacancies_processed'],
            language['average_salary']
        ]
        table_payload.append(table_row)
    table = AsciiTable(table_payload, title)
    return table


if '__main__' == __name__:
    load_dotenv()
    sj_token = os.environ["SJ_TOKEN"]
    hh_table = make_table(predict_rub_salary_hh(), 'hh vacancies moscow')
    sj_table = make_table(predict_rub_salary_for_superJob(sj_token), 'super job vacancies moscow')
    print(hh_table.table)
    print(sj_table.table)

