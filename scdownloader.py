import asyncio
from playwright.async_api import async_playwright, Playwright, Browser, BrowserContext
import time
from massdownloader import ChromiumDownloader

def rem_sc(link: str):
    return link[len('https://soundcloud.com/'):]

class SCDownloader(ChromiumDownloader): 
    async def dl_target(self, driver: BrowserContext, link: str):
        while True:
            try:
                await self.spots_left.acquire()
                page = await driver.new_page()

                async def click_fast(
                    xpath: str, 
                    message: str, 
                    return_element: bool = False, 
                    click: bool = True
                ):
                    await self.event_staggerer.block_until_event(message = message)
                    button = page.locator(f'xpath={xpath}')
                    await button.hover(timeout=self.button_wait_time)
                    await asyncio.sleep(self.click_wait_time)
                    await button.click(timeout=self.button_wait_time)
                    if return_element:
                        return button

                await page.goto("https://soundcloudmp3.org/")

                input_xpath = '/html/body/div[2]/div[3]/div/div/div[1]/form/div/input[2]'
                input_box = await click_fast(input_xpath, return_element=True, message = f'typing url in {rem_sc(link)}')
                await input_box.fill(link)

                dl_xpath = '/html/body/div[2]/div[3]/div/div/div[1]/form/div/span/button'
                await click_fast(dl_xpath, message = f'clicking get dl for {rem_sc(link)}')

                dl_xpath = '/html/body/div[2]/div[3]/div/div/div[1]/div[2]/div[5]/a'
                async with page.expect_download() as download_info:
                    print(f'DOWNLOADING {rem_sc(link)}')
                    await click_fast(dl_xpath, message = f'clicking dl for {rem_sc(link)}')
                download = await download_info.value
                await download.save_as(self.dl_folder + download.suggested_filename)
                print(f'{rem_sc(link)} downloaded')
                return

            except Exception as e:
                print(f'{rem_sc(link)} died because {e}')
                await asyncio.sleep(3)
            finally:
                self.spots_left.release()