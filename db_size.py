import csv
import math
import os
from datetime import date
from os import walk

filenames = []

def get_files():
    #получает список файлов в директории
    #сортирует их по дате по возрастанию
    for (_, _, names) in walk("."):
        for name in names:
            _file = {}
            if '.csv' in name:
                _file['name'] = name
                _file['date'] = date.fromisoformat(str(name[:-4]))
                filenames.append(_file)
        continue
    filenames.sort(key= lambda _file: _file['date'])
    if len(filenames) != 2:
        raise Exception('Неверное количество файлов в директории')
    

def normalize_data_size(input_dict):
    #метод для нормализации размеров таблиц
    #units = {"B": 1, "kB": 10**3, "MB": 10**6, "GB": 10**9, "TB": 10**12}
    units = {"B": 1, "kB": 2**10, "MB": 2**20, "GB": 2**30, "TB": 2**40}
    number, unit = [string.strip() for string in input_dict.split()]
    return int(float(number)*units[unit])


def hreadeble_size(size):
    power = 2**10
    n = 0
    power_labels = {0 : '', 1: 'kB', 2: 'MB', 3: 'GB', 4: 'TB'}
    if size < 0:
        msize = math.fabs(size)
        while msize > power:
            msize /= power
            n += 1
        return f"{format(-msize, '.2f')} {power_labels[n]}"
    else:
        while size > power:
            size /= power
            n += 1
        return f"{format(size, '.2f')} {power_labels[n]}"


def create_dict(input_file):
    #создаёт список словарей формата [{"db_name": название_бд, дата: размер_бд}]
    result = []
    with open(input_file['name'], 'r') as csvfile:
        filereader = csv.DictReader(csvfile)
        db_date = str(input_file['date'])
        for row in filereader:
            result.append({'db_name': row['database_name'], db_date: row['size']})
    return result


def create_set_of_names(*args):
    #создаёт список уникальных имен баз данных
    set_of_names = set()
    for input_file in args:
        with open(input_file, 'r') as csvfile:
            filereader = csv.DictReader(csvfile)
            for row in filereader:
                set_of_names.add(row['database_name'])
    list_of_names = sorted(set_of_names)
    return list_of_names


def copy_list(list1, list2, set_of_names):
    #копирование списка словарей list2 в list1 построчно
    result_list = []
    #заполняет нулями столбец с данными о размерах БД за последний месяц
    for item in set_of_names:
        d = {}
        d['db_name'] = item
        d[str(filenames[0]['date'])] = '0 kB'
        d[str(filenames[1]['date'])] = '0 kB'
        result_list.append(d)
    #построчно проходит по значениям столбца с ранними значениями
    #если находит имя БД 
    for row in list1:
        for result_row in result_list:
            if row['db_name'] == result_row['db_name']:
                date = list(row.items())[1][0]
                size = list(row.items())[1][1]
                result_row[date] = size
    for row in list2:
        for result_row in result_list:
            if row['db_name'] == result_row['db_name']:
                date = list(row.items())[1][0]
                size = list(row.items())[1][1]
                result_row[date] = size
    return result_list
   

def deltaFunc(csv_list):
    #добавление столбца delta в результирующую таблицу
    return csv_list['delta']


def create_result_csv(result_list):
    first_date = str(filenames[0]['date'])
    second_date = str(filenames[1]['date'])
    total = {first_date: 0, second_date: 0, 'delta': 0}
    #подставил даты в названия столбцов
    for result_row in result_list:
        delta = normalize_data_size(result_row[second_date]) - normalize_data_size(result_row[first_date])
        result_row['delta'] = delta
        total[first_date] += normalize_data_size(result_row[first_date])
        total[second_date] += normalize_data_size(result_row[second_date])
        total['delta'] += delta
    result_list.sort(reverse=True, key=deltaFunc)
    for k, v in total.items():
        total[k] = hreadeble_size(v)
    for row in result_list:
        row['delta'] = hreadeble_size(row['delta'])
    result_list.append(total)
    print(result_list)
    return result_list


def output_csv(result_list):
    #создает результирующий csv-файл
    csv_columns = ['db_name', str(filenames[0]['date']), str(filenames[1]['date']), 'delta']
    csv_file = 'total.csv'
    try:
        with open(csv_file, 'w') as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=csv_columns)
            writer.writeheader()
            for data in result_list:
                writer.writerow(data)
    except IOError:
        print('I/O Error')

if __name__ == "__main__":
    get_files()
    first_file = create_dict(filenames[0])
    second_file = create_dict(filenames[1])
    set_of_names = create_set_of_names(filenames[0]['name'], filenames[1]['name'])
    copied_list = copy_list(first_file, second_file, set_of_names)
    result_csv = create_result_csv(copied_list)
    output_csv(result_csv)
    
