import asyncio
from playwright.async_api import async_playwright, Playwright, Browser, BrowserContext
import os, shutil
import time
import datetime
from abc import ABC, abstractclassmethod

class EventStaggerer:
    def __init__(self, wait_time: float):
        self.wait_time = wait_time

        self.next_event_time = datetime.datetime.now()
        self.checking_time = asyncio.Lock()

    async def block_until_event(self, message: str = 'event'):
        #while True:
        async with self.checking_time:
            t = datetime.datetime.now() 
            time_until_next_ev = (self.next_event_time - t).total_seconds()
            self.next_event_time = max(t, self.next_event_time) + datetime.timedelta(seconds=self.wait_time)
        await asyncio.sleep(time_until_next_ev)
        print(f'{message} at {datetime.datetime.now()}!')

class MassDownloader(ABC):
    def __init__(
        self,
        n_threads: int = 20,
        dl_wait_time: float = 600,
        rm_dls: bool = False,
        dl_folder: str = '/home/prashant/sdler/dls/',
        event_wait_time: float = 5
    ):
        self.rm_dls = rm_dls
        self.dl_folder = dl_folder
        self.n_threads = n_threads
        self.dl_wait_time = dl_wait_time
        self.event_wait_time = event_wait_time
        self.event_staggerer = EventStaggerer(wait_time=self.event_wait_time)
        self.spots_left = asyncio.Semaphore(n_threads)

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
    async def dl_target(self, link: str):
        pass

    @abstractclassmethod
    def execute(self):
        pass

class ChromiumDownloader(MassDownloader):
    def __init__(
        self, 
        *args, 
        adblocker_file: str = '/home/prashant/sdler/adblocker/', 
        button_wait_time: float = 20*10**3,
        click_wait_time: float = 0.01,
        **kwargs
    ):
        super().__init__(*args, **kwargs)
        self.button_wait_time = button_wait_time
        self.click_wait_time = click_wait_time
        self.adblocker_file = adblocker_file

    def execute(self):
        self.clean_dls()
        async def main():
            async with async_playwright() as p:
                driver = await p.chromium.launch_persistent_context(
                    '/tmp/test_data_dir',
                    headless=False,
                    args=[
                        f"--disable-extensions-except={self.adblocker_file}",
                        f"--load-extension={self.adblocker_file}",
                    ],
                )
                await asyncio.gather(
                    *[asyncio.create_task(self.dl_target(driver, target)) for target in self.targets]
                )
        asyncio.run(main())