
import ipdb
import pytz
from os import path
from os import listdir
from decouple import config
from os.path import isfile, join
from datetime import datetime
from datetime import timedelta
from utils import read_file
from utils import is_today_file
from utils import convert_data
from utils import ignore_bkp
from database.database import InsertData


class Executor():

    def __init__(self, log_folder):
        self.log_folder = log_folder
        self.db = InsertData()

    def check_existent_bkp(self, bkp_name, datetime):
        bkp_exists = False
        pk_row = None
        start_backup_year = datetime.year
        start_backup_month = datetime.month
        start_backup_day = datetime.day
        start_backup_minute = datetime.minute
        start_backup_hour = datetime.hour
        start_backup_second = datetime.second

        rows = self.db.get('core_backup')
        for row in rows:
            pk_row = row[0]
            bkp_name_db = row[1]
            datetime_db = row[2] - timedelta(minutes = 180)
            start_backup_year_db = datetime_db.year
            start_backup_month_db = datetime_db.month
            start_backup_day_db = datetime_db.day
            start_backup_minute_db = datetime_db.minute
            start_backup_hour_db = datetime_db.hour
            start_backup_second_db = datetime_db.second

            if bkp_name == bkp_name_db \
                and start_backup_year == start_backup_year_db \
                and start_backup_month == start_backup_month_db \
                and start_backup_day == start_backup_day_db \
                and start_backup_minute == start_backup_minute_db \
                and start_backup_hour == start_backup_hour_db \
                and start_backup_second == start_backup_second_db:
                bkp_exists = True

        return bkp_exists, pk_row

    def save_data(self, file_data):
        for bkp in file_data:
            ignore = ignore_bkp(bkp)
            if not ignore:
                for line in file_data[bkp]:
                    start_date = file_data[bkp][line]['start_date']
                    start_time = file_data[bkp][line]['start_time']
                    datetime_cnvrtd = convert_data(start_date, start_time, False)

                    bkp_exists, pk_row_db = self.check_existent_bkp(bkp, datetime_cnvrtd)
                    if not bkp_exists:

                        table_name = 'core_backup'
                        column_value = {
                            'name': bkp,
                            'percents_completed': 0,
                            'status': 1,
                            'start_backup_datetime': "'{0}'".format(
                                convert_data(start_date, start_time, True)),
                            'finish_backup_datetime': 'NULL'
                        }
                        pk_row = self.db.insert(
                            table_name, column_value)

                        for log in file_data[bkp][line]['logs']:
                            datetime_cnvrtd = convert_data(
                                log['date'], log['time'], True)
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
                            datetime_cnvrtd = convert_data(end_date, end_time, True)
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
        try:
            dic_file = self.read_logs()
            file_data = self.treat_data(dic_file)
            self.save_data(file_data)

        except Exception as e:
            error_msg = str(e)


        finally:
            pass

if __name__ == "__main__":
    agent = Executor(config('LOG_FOLDER'))
    agent.run()