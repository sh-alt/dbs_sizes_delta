import csv
import math
import os
from datetime import date
from os import walk


file1 = '18112019.csv'
file2 = '28022020.csv'
filenames = {}

def get_files():
    #получает список файлов в директории
    for (_, _, names) in walk("."):
        for name in names:
            if '.csv' in name:
                filenames['name'] = name
                filenames['date'] = date.fromisoformat(str(name[:-4]))
        continue
    if len(filenames) != 2:
        raise Exception('Неверное количество файлов в директории')
    

def normalize_data_size(input_dict):
    #метод для нормализации размеров таблиц
    units = {"B": 1, "kB": 10**3, "MB": 10**6, "GB": 10**9, "TB": 10**12}
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
    with open(input_file, 'r') as csvfile:
        filereader = csv.DictReader(csvfile)
        db_date = str(input_file[:-4])
        for row in filereader:
            print(row['database_name'])
            result.append({'db_name': row['database_name'], db_date: row['size']})
    return result


def create_set_of_names(*args):
    #создаёт список уникальных имен баз данных
    set_of_names = set()
    for input_file in args:
        with open(input_file, 'r') as csvfile:
            filereader = csv.DictReader(csvfile)
            for row in filereader:
                print(row['database_name'])
                set_of_names.add(row['database_name'])
    list_of_names = sorted(set_of_names)
    return list_of_names


def copy_list(list1, list2):
    #копирование списка словарей list2 в list1 построчно
    result_list = list1
    for row in result_list:
        row['28022020'] = '0 kB'
    for row in list2:
        added = False
        for result_row in result_list:
            if row['db_name'] == result_row['db_name']:
                date = list(row.items())[1][0]
                size = list(row.items())[1][1]
                result_row[date] = size
                added = True
                continue
    if not added:
        result_list.append(row)
        added = True
    return result_list
   

def deltaFunc(csv_list):
    #добавление столбца delta в результирующую таблицу
    return csv_list['delta']


def create_result_csv(list1, list2):
    result_list = copy_list(list1, list2)
    total = {'18112019': 0, '28022020': 0, 'delta': 0}
    for result_row in result_list:
        delta = normalize_data_size(result_row['28022020']) - normalize_data_size(result_row['18112019'])
        result_row['delta'] = delta
        total['18112019'] += normalize_data_size(result_row['18112019'])
        total['28022020'] += normalize_data_size(result_row['28022020'])
        total['delta'] += delta
    result_list.sort(reverse=True, key=deltaFunc)
    for k, v in total.items():
        total[k] = hreadeble_size(v)
    for row in result_list:
        row['delta'] = hreadeble_size(row['delta'])
    result_list.append(total)
    return result_list


#def create_result_csv(*args, list_of_db_names):
#    result_dict = []
#    for input_file in args:
#        for name in list_of_db_names:
#            date = os.path.splitext(list_of_db_names)[0]
#            result_dict.append({'db_name': name, date: j})


def output_csv(result_list):
    #создает результирующий csv-файл
    csv_columns = ['db_name', '18112019', '28022020', 'delta']
    csv_file = 'total.csv'
    try:
        with open(csv_file, 'w') as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=csv_columns)
            writer.writeheader()
            for data in result_list:
                writer.writerow(data)
    except IOError:
        print('I/O Error')

list_of_names = create_set_of_names(file1, file2)
print(list_of_names)

#result_list = create_result_csv(dblist1, dblist2)
#output_csv(result_list)
