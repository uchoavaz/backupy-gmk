
import ipdb
import pytz
import time
import glob
from os import walk
from os import path
from os import listdir
from os import stat
from decouple import config
from os.path import isfile, join
from datetime import datetime
from datetime import timedelta
from utils import read_file
from utils import is_today_file
from utils import convert_data
from utils import ignore_bkp
from utils import check_integrity
from mailer import Mailer
from database.database import InsertData


class Executor():

    alert_msg = 'Backups with alert:\n'
    success_msg = 'Backups with sucess:\n'
    error_msg = 'Backups with error:\n'
    except_msg = 'Agent Error:\n'

    def __init__(self, log_folder):
        self.log_folder = log_folder
        self.db = InsertData()

    def check_data_integrity(self, bkp_name):

        list_old_lastmodified_files = []
        has_old_lastmodified_files = False

        if check_integrity(bkp_name):
            
            today = datetime.today()
            today_year = today.year
            today_month = today.month
            today_day = today.day

            full_path = path.join(config('DBS_FOLDER'), bkp_name)
            for filename in listdir(full_path):
                full_path_file = path.join(full_path, filename)
                lastmodified = stat(full_path_file).st_mtime

                lastmodified_datetime = datetime.fromtimestamp(lastmodified)

                if lastmodified_datetime.day != today_day \
                    or lastmodified_datetime.month != today.month \
                    or lastmodified_datetime.year != today_year:

                    list_old_lastmodified_files.append(filename)
                    has_old_lastmodified_files = True

        return has_old_lastmodified_files, list_old_lastmodified_files      

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
        error_status  = False
        email_list = []
        for bkp in file_data:
            ignore = ignore_bkp(bkp)
            if not ignore:
                has_old_lastmodified_files, list_old_lastmodified_files = self.check_data_integrity(bkp)
                for line in file_data[bkp]:
                    error_status  = False
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
                            if 'Backup failed' in log['log']:
                                log_status = 4
                                error_status = True
                            else:
                                log_status = 1
                            pk_log_row = self.db.insert(
                                'core_backuplog', {
                                    'backup_id': pk_row,
                                    'log': log['log'],
                                    'status': log_status,
                                    'log_datetime': "'{0}'".format(datetime_cnvrtd)
                                }
                        )

                        if has_old_lastmodified_files:
                            self.db.insert(
                                'core_backuplog', {
                                    'backup_id': pk_row,
                                    'log': 'Files not modified: ' + ','.join(list_old_lastmodified_files),
                                    'status': 4,
                                    'log_datetime': "'{0}'".format('now()')
                                }
                        )
                        try:
                            end_date = file_data[bkp][line]['end_date']
                            end_time = file_data[bkp][line]['end_time']
                            datetime_cnvrtd = convert_data(end_date, end_time, True)
                            status = 2
                            percents_completed = 100.0

                            if file_data[bkp][line]['logs'] or has_old_lastmodified_files:
                                status = 3
                                if error_status or has_old_lastmodified_files:
                                    status = 4
                                    percents_completed = 0.0

                            msg = '- {0} - start:{1} end:{2}\n'.format(
                                bkp, (start_date + ' ' + start_time), (end_date + ' ' + end_time))

                            if status == 2 and msg not in email_list:
                                self.success_msg = self.success_msg + msg
                                email_list.append(msg)
                            if status == 3 and msg not in email_list:
                                self.alert_msg = self.alert_msg + msg
                                email_list.append(msg)
                            if status == 4 and msg not in email_list:
                                self.error_msg = self.error_msg + msg
                                email_list.append(msg)

                            self.db.update(
                                'core_backup', {
                                    'id': pk_row,
                                    'status': status,
                                    'percents_completed': percents_completed,
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
            elif 'Backup failed' in dic_file['lines'][line]['log']:
                start_date = dic_file['lines'][line]['bkp_name'].split(' ')[0]
                start_time = dic_file['lines'][line]['bkp_name'].split(' ')[1]
                bkp_name = dic_file['lines'][line]['date']
                data[bkp_name] = {}
                data[bkp_name][count_log] = {}
                data[bkp_name][count_log]['start_date'] = start_date
                data[bkp_name][count_log]['start_time'] = start_time
                data[bkp_name][count_log]['end_date'] = start_date
                data[bkp_name][count_log]['end_time'] = start_time
                data[bkp_name][count_log]['logs'] = [{
                    'date':start_date,'time':start_time,'log':dic_file['lines'][line]['log']
                }] 
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
            self.except_msg = self.except_msg + '- ' + str(e)

        finally:
            email = Mailer()
            email.send(self.success_msg, self.alert_msg, self.error_msg, self.except_msg)

if __name__ == "__main__":
    agent = Executor(config('LOG_FOLDER'))
    agent.run()