
from datetime import datetime
import pytz
import ipdb

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