
from os.path import isfile, join
from decouple import config
from os import listdir
from os import path
import ipdb


class Executor():

    log_folder = None

    def __init__(self, log_folder):
        self.log_folder = log_folder

    def read_file(self, path):
        count = 0
        with open(path) as file:
            for line in file:
                if count > 0:
                    sep = line.split()


    def read_logs(self, log_folder):

        list = []
        for f in listdir(log_folder):
            full_path = join(log_folder, f)
            if isfile(full_path):
                self.read_file(full_path)
                list.append(full_path)

        return list

    def run(self):
        ipdb.set_trace()
        logs_info = self.read_logs(self.log_folder)


if __name__ == "__main__":
    agent = Executor(config('LOG_FOLDER'))
    agent.run()