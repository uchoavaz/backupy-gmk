
from os.path import isfile, join
from decouple import config
from file_manager import read_file
from file_manager import is_today_file
from os import listdir
from os import path
import ipdb


class Executor():

    def __init__(self, log_folder):
        self.log_folder = log_folder

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

        ipdb.set_trace()
                
    def read_logs(self):
        dic_file = None
        for f in listdir(self.log_folder):
            full_path = join(self.log_folder, f)

            if isfile(full_path) and is_today_file(f):
                dic_file = read_file(full_path)
        return dic_file

    def run(self):
        dic_file = self.read_logs()
        self.treat_data(dic_file)


if __name__ == "__main__":
    agent = Executor(config('LOG_FOLDER'))
    agent.run()