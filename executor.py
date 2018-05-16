
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

    def read_logs(self):
        list = []
        for f in listdir(self.log_folder):
            full_path = join(self.log_folder, f)

            if isfile(full_path) and is_today_file(f):
                dic_file = read_file(full_path)

        return list

    def run(self):
        logs_info = self.read_logs()


if __name__ == "__main__":
    agent = Executor(config('LOG_FOLDER'))
    agent.run()