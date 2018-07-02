
import pytz
import ipdb
from os import getenv
from decouple import config
from datetime import datetime
from datetime import timedelta

def read_line(line):
    sub_split = line.split('      ')
    len_sub_split = len(sub_split)
    len_time = len(sub_split[0].split()) - 1
    len_date = len(sub_split[0].split()) - 2
    time = sub_split[0].split()[len_time]
    date_string = sub_split[0].split()[len_date]
    log = sub_split[(len_sub_split - 1)].strip('\n')
    bkp_name = line.replace(log, '').replace(date_string, '').replace(time, '').strip()

    return {
        'bkp_name':bkp_name, 
        'date': date_string,
        'time': time,
        'log': log
        }

def read_file(path):

    count = 0
    data_file = {}
    lines = {}

    with open(path) as file:
        for line in file:
            if count > 0:
                line_data = read_line(line)
                lines[count] = line_data
            else:
                date = line.split()[0]
                data_file['file_date'] = date

            count = count + 1

    data_file['lines'] = lines
    return data_file

def is_today_file(file):

    date = file.replace('.txt','')
    dt_obj = datetime.strptime(date, '%Y-%m-%d')
    date_today = datetime.now(pytz.timezone('America/Recife')).date()
    is_today = False

    if dt_obj.date() == date_today:
        is_today = True

    return is_today

def convert_data(date, time, correct_time):

    datetime_str = date + ' ' + time
    datetime_cnvrtd = datetime.strptime(datetime_str, '%Y-%m-%d %X')
    if correct_time:
        datetime_cnvrtd = datetime_cnvrtd + timedelta(minutes = 40)
    return datetime_cnvrtd.replace(tzinfo=pytz.timezone('America/Recife'))

def ignore_bkp(bkp_name):
    ignored_list = config('IGNORED_BKPS', default='').split(',')
    if bkp_name in ignored_list:
        return True

    return False