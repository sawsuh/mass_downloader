import asyncio
from playwright.async_api import async_playwright, BrowserContext
import os, shutil
import datetime
from abc import ABC, abstractmethod


class EventStaggerer:
    def __init__(self, wait_time: float):
        self.wait_time = wait_time

        self.next_event_time = datetime.datetime.now()
        self.checking_time = asyncio.Lock()

    async def block_until_event(self, message: str = "event"):
        # while True:
        async with self.checking_time:
            t = datetime.datetime.now()
            time_until_next_ev = (self.next_event_time - t).total_seconds()
            self.next_event_time = max(t, self.next_event_time) + datetime.timedelta(
                seconds=self.wait_time
            )
        await asyncio.sleep(time_until_next_ev)
        print(f"{message} at {datetime.datetime.now()}!")


class MassDownloader(ABC):
    def __init__(
        self,
        n_threads: int = 20,
        dl_wait_time: float = 600,
        rm_dls: bool = False,
        dl_folder: str = "../dls/",
        event_wait_time: float = 0.01,
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
            print(f"cleaning downloads")
            for filename in os.listdir(self.dl_folder):
                file_path = os.path.join(self.dl_folder, filename)
                try:
                    if os.path.isfile(file_path) or os.path.islink(file_path):
                        os.unlink(file_path)
                    elif os.path.isdir(file_path):
                        shutil.rmtree(file_path)
                except Exception as e:
                    print(f"Failed to delete {file_path}. Reason: {e}")

    def load_urls(self, urls: str):
        self.targets = (url for url in urls.split("\n") if len(url) > 0)

    @abstractmethod
    async def dl_target(self, driver: BrowserContext, link: str):
        pass

    @abstractmethod
    def execute(self):
        pass


def rem_sc(link: str):
    return link[len("https://soundcloud.com/") :]


def rem_spot(link: str):
    return link


class ChromiumDownloader(MassDownloader):
    def __init__(
        self,
        *args,
        adblocker_file: str = r"../adblocker/",
        button_wait_time: float = 20 * 10**3,
        click_wait_time: float = 0.01,
        **kwargs,
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
                    "/tmp/test_data_dir",
                    headless=False,
                    args=[
                        f"--disable-extensions-except={self.adblocker_file}",
                        f"--load-extension={self.adblocker_file}",
                    ],
                )
                await asyncio.gather(
                    *[
                        asyncio.create_task(self.dl_target(driver, target))
                        for target in self.targets
                    ]
                )

        asyncio.run(main())

    async def dl_target(self, driver: BrowserContext, link: str):
        if "soundcloud" in link:
            await self.dl_target_soundcloud(driver, link)
        elif "spotify" in link:
            await self.dl_target_spotify(driver, link)

    async def click_button(self, button):
        await button.hover(timeout=self.button_wait_time)
        await button.click(timeout=self.button_wait_time)
        await asyncio.sleep(self.click_wait_time)

    async def get_button(
        self,
        page,
        xpath: str,
        message: str,
    ):
        await self.event_staggerer.block_until_event(message=message)
        return page.locator(f"xpath={xpath}")

    async def dl_target_spotify(self, driver: BrowserContext, link: str):
        while True:
            try:
                await self.spots_left.acquire()
                page = await driver.new_page()

                async def get_button(xpath, message):
                    return await self.get_button(page, xpath, message)

                await page.goto("https://spotifymate.com/en")

                input_xpath = '//*[@id="url"]'
                input_box = await get_button(
                    input_xpath, message=f"typing url in {rem_spot(link)}"
                )
                await self.click_button(input_box)
                await input_box.fill(link)

                dl_xpath = "/html/body/main/div[1]/div/div/div/div/form/button/span"
                await self.click_button(
                    await get_button(
                        dl_xpath, message=f"clicking get dl for {rem_spot(link)}"
                    )
                )

                file_xpath = "/html/body/main/div[2]/div/div/div/div/div/div[1]/div[3]/div[1]/a/span/span"
                async with page.expect_download() as download_info:
                    print(f"DOWNLOADING {rem_spot(link)}")
                    await self.click_button(
                        await get_button(
                            file_xpath,
                            message=f"clicking download for {rem_spot(link)}",
                        )
                    )
                download = await download_info.value
                await download.save_as(
                    self.dl_folder
                    + download.suggested_filename[len("SpotifyMate.com - ") :]
                )
                print(f"{rem_spot(link)} downloaded")
                return

            except Exception as e:
                print(f"{rem_sc(link)} died because {e}")
                await asyncio.sleep(3)
            finally:
                self.spots_left.release()

    async def dl_target_soundcloud(self, driver: BrowserContext, link: str):
        while True:
            try:
                await self.spots_left.acquire()
                page = await driver.new_page()

                async def get_button(xpath, message):
                    return await self.get_button(page, xpath, message)

                await page.goto("https://soundcloudmp3.org/")

                input_xpath = (
                    "/html/body/div[2]/div[3]/div/div/div[1]/form/div/input[2]"
                )
                input_box = await get_button(
                    input_xpath, message=f"typing url in {rem_sc(link)}"
                )
                await self.click_button(input_box)
                await input_box.fill(link)

                dl_xpath = (
                    "/html/body/div[2]/div[3]/div/div/div[1]/form/div/span/button"
                )
                await self.click_button(
                    await get_button(
                        dl_xpath, message=f"clicking get dl for {rem_sc(link)}"
                    )
                )

                dl_xpath = "/html/body/div[2]/div[3]/div/div/div[1]/div[2]/div[5]/a"
                async with page.expect_download() as download_info:
                    print(f"DOWNLOADING {rem_sc(link)}")
                    await self.click_button(
                        await get_button(
                            dl_xpath, message=f"clicking dl for {rem_sc(link)}"
                        )
                    )
                download = await download_info.value
                await download.save_as(self.dl_folder + download.suggested_filename)
                print(f"{rem_sc(link)} downloaded")
                return

            except Exception as e:
                print(f"{rem_sc(link)} died because {e}")
                await asyncio.sleep(3)
            finally:
                self.spots_left.release()
