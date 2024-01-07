import threading
import os, shutil
import time
import datetime
from abc import ABC, abstractclassmethod

class EventStaggerer:
    def __init__(self, wait_time: float):
        self.wait_time = wait_time
        self.last_event_time = datetime.datetime.now()
        self.checking_time = threading.Semaphore(1)

    def block_until_event(self, message: str = 'event'):
        while True:
            self.checking_time.acquire()
            t = datetime.datetime.now()
            if (t - self.last_event_time).total_seconds() > self.wait_time:
                self.last_event_time = t
                break
            time.sleep(0.1)
            self.checking_time.release()
        print(f'{message} at {self.last_event_time}!')
        self.checking_time.release()

class MassDownloader(ABC):
    def __init__(
        self,
        n_threads: int = 20,
        dl_wait_time: float = 600,
        rm_dls: bool = False,
        dl_folder: str = '/home/prashant/sdler/dls',
        event_wait_time: float = 0.01
    ):
        self.rm_dls = rm_dls
        self.dl_folder = dl_folder
        self.n_threads = n_threads
        self.dl_wait_time = dl_wait_time
        self.event_staggerer = EventStaggerer(wait_time=self.event_wait_time)
        self.spots_left = threading.Semaphore(n_threads)

    def clean_dls(self):
        if self.rm_dls:
            for filename in os.listdir(self.dl_folder):
                file_path = os.path.join(self.dl_folder, filename)
                try:
                    if os.path.isfile(file_path) or os.path.islink(file_path):
                        os.unlink(file_path)
                    elif os.path.isdir(file_path):
                        shutil.rmtree(file_path)
                except Exception as e:
                    print(f'Failed to delete {file_path}. Reason: {e}')

    def load_urls(self, urls: str):
        self.targets = (url for url in urls.split('\n') if len(url) > 0)

    @abstractclassmethod
    def dl_target(self, link: str):
        pass

    def execute(self):
        self.clean_dls()
        threads = []
        for target in self.targets:
            tr = threading.Thread(target=self.dl_target, args=(target,))
            tr.start()
            threads.append(tr)

        for tr in threads:
            tr.join()