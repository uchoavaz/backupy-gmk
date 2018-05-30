
import ipdb
import pytz
from os import path
from os import listdir
from decouple import config
from os.path import isfile, join
from datetime import datetime
from utils import read_file
from utils import is_today_file
from utils import convert_data
from utils import ignore_bkp
from database.database import InsertData


class Executor():

    def __init__(self, log_folder):
        self.log_folder = log_folder
        self.db = InsertData()

    def save_data(self, file_data):
        ipdb.set_trace()
        for bkp in file_data:
            ignore = ignore_bkp(bkp)
            if not ignore:
                for line in file_data[bkp]:
                    start_date = file_data[bkp][line]['start_date']
                    start_time = file_data[bkp][line]['start_time']
                    datetime_cnvrtd = convert_data(start_date, start_time)
                    table_name = 'core_backup'
                    column_value = {
                        'name': bkp,
                        'percents_completed': 0,
                        'status': 1,
                        'start_backup_datetime': "'{0}'".format(datetime_cnvrtd),
                        'finish_backup_datetime': 'NULL'
                    }
                    pk_row = self.db.insert(
                        table_name, column_value)

                    for log in file_data[bkp][line]['logs']:
                        datetime_cnvrtd = convert_data(log['date'], log['time'])
                        pk_log_row = self.db.insert(
                            'core_backuplog', {
                                'backup_id': pk_row,
                                'log': log['log'],
                                'status': 1,
                                'log_datetime': "'{0}'".format(datetime_cnvrtd)
                            }
                    )

                    try:
                        end_date = file_data[bkp][line]['end_date']
                        end_time = file_data[bkp][line]['end_time']
                        datetime_cnvrtd = convert_data(end_date, end_time)
                        status = 2
                        if file_data[bkp][line]['logs']:
                            status = 3

                        self.db.update(
                            'core_backup', {
                                'id': pk_row,
                                'status': status,
                                'percents_completed': 100.0,
                                'finish_backup_datetime': "'{0}'".format(datetime_cnvrtd)
                            }

                        )

                    except KeyError:
                        pass



    def treat_data(self, dic_file):
        data = {}
        count_log = 1
        read_logs = False
        bkp_name = ''

        for line in dic_file['lines']:

            if dic_file['lines'][line]['log'] == 'Start backup':
                start_date = dic_file['lines'][line]['date']
                start_time = dic_file['lines'][line]['time']
                bkp_name = dic_file['lines'][line]['bkp_name']
                try:
                    data[bkp_name]
                except:
                    data[bkp_name] = {}
                data[bkp_name][count_log] = {} 
                data[bkp_name][count_log]['start_date'] = start_date
                data[bkp_name][count_log]['start_time'] = start_time
                data[bkp_name][count_log]['logs'] = []
                read_logs = True

            elif dic_file['lines'][line]['log'] == 'Backup finished':
                read_logs = False
                end_date = dic_file['lines'][line]['date']
                end_time = dic_file['lines'][line]['time']
                data[bkp_name][count_log]['end_date'] = end_date
                data[bkp_name][count_log]['end_time'] = end_time
                count_log = count_log + 1

            elif read_logs:
                log_string = dic_file['lines'][line]['log']
                time = dic_file['lines'][line]['time']
                date = dic_file['lines'][line]['date']
                log_dic = {}
                log_dic['date'] = date
                log_dic['time'] = time
                log_dic['log'] = log_string
                data[bkp_name][count_log]['logs'].append(log_dic)

        return data
                
    def read_logs(self):
        dic_file = None
        for f in listdir(self.log_folder):
            full_path = join(self.log_folder, f)

            if isfile(full_path) and is_today_file(f):
                dic_file = read_file(full_path)
        return dic_file

    def run(self):
        dic_file = self.read_logs()
        file_data = self.treat_data(dic_file)
        self.save_data(file_data)


if __name__ == "__main__":
    agent = Executor(config('LOG_FOLDER'))
    agent.run()