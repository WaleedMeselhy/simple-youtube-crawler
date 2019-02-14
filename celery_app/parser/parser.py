from parsel import Selector
from time import sleep, time
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
import re
from database_core.repositories import JobRepository, VideoRepository
from database_core.factories import Video, Job as JobModel
from database_core.database.gateway import DBGateway
from utils import download
job_repository = JobRepository()
video_repository = VideoRepository()


class YoutubeParser(object):
    """docstring for YoutubeParser."""

    def __init__(self, url, browser):
        super(YoutubeParser, self).__init__()
        self.url = url
        self.browser = browser

    def open_url(self, url):
        self.browser.get(url)

    def parse(self, job_id):
        # job = job_repository.get(DBGateway, url=self.url)
        self.open_url(self.url)
        for a_tag in self.a_tags():
            href = 'https://www.youtube.com' + a_tag
            video_id = self.get_video_id(href)
            self.open_url(href)
            if not self.wait_with_xpath(
                    '//div[@id="count"]/yt-view-count-renderer'):
                print('link skipped')
                continue
            title = self.parse_title()
            duration = self.parse_duration()
            views = self.parse_views()
            thumbnail_image = (
                'https://img.youtube.com/vi/{}/default.jpg'.format(video_id))
            original_full_sized_image = (
                'https://img.youtube.com/vi/{}/maxresdefault.jpg'.format(
                    video_id))
            local_thumbnail_image = (
                '/downloads/{video_id}_thumbnail.jpg'.format(
                    video_id=video_id))
            local_original_full_sized_image = (
                '/downloads/{video_id}_original_full_sized.jpg'.format(
                    video_id=video_id))

            download(thumbnail_image, local_thumbnail_image)
            download(original_full_sized_image,
                     local_original_full_sized_image)
            video = Video({
                'job_id':
                job_id,
                'video_url':
                href,
                'title':
                title,
                'duration':
                duration,
                'views':
                str(views),
                'thumbnail_image':
                thumbnail_image,
                'original_full_sized_image':
                original_full_sized_image,
                'local_thumbnail_image':
                local_thumbnail_image,
                'local_original_full_sized_image':
                local_original_full_sized_image
            })
            video.validate()
            _, created = video_repository.create_or_update(
                DBGateway,
                video_url=href,
                job_id=job_id,
                title=title,
                duration=duration,
                views=str(views),
                thumbnail_image=thumbnail_image,
                original_full_sized_image=original_full_sized_image,
                local_thumbnail_image=local_thumbnail_image,
                local_original_full_sized_image=local_original_full_sized_image
            )
            # print('href', href, 'video_id', video_id, 'title', title,
            #       'duration', duration, 'views', views)
            # print('created', created)
            # break

    def wait_with_xpath(self, xpath):
        return self.browser.wait_with_xpath(xpath)

    def get_video_id(self, href):
        pattern = re.compile('v=[^&]*')
        result = pattern.search(href)
        return result.group().replace('v=', '')

    def extract_tag_by_xpath(self, source, xpath):
        return source.xpath(xpath)

    def extract_first(self, source, xpath):
        return self.extract_tag_by_xpath(source, xpath).extract_first()

    def extract_all(self, source, xpath):
        return self.extract_tag_by_xpath(source, xpath).extract()

    def a_tags(self):
        pass

    def parse_title(self):
        sel = Selector(text=self.browser.get_source())
        return self.extract_first(
            sel, ('//ytd-video-primary-info-renderer/div[@id="container"]'
                  '/h1/yt-formatted-string/text()'))

    def parse_views(self):

        sel = Selector(text=self.browser.get_source())
        views = self.extract_first(
            sel, '//div[@id="count"]/yt-view-count-renderer//span[1]/text()')
        pattern = re.compile('\\d+')
        return ''.join([str(n) for n in pattern.findall(views)])

    def parse_duration(self):
        sel = Selector(text=self.browser.get_source())
        return self.extract_first(sel,
                                  '//span[@class="ytp-time-duration"]/text()')


class ChannelYoutubeParser(YoutubeParser):
    """docstring for ChannelYoutubeParser."""
    channel_pattern = re.compile('https://www.youtube.com/user/.*/videos')

    def __init__(self, url, browser):
        super(ChannelYoutubeParser, self).__init__(url, browser)

    def a_tags(self):
        while True:
            old_height = self.browser.execute_script(
                "return document.documentElement.scrollHeight")
            self.browser.execute_script(
                "window.scrollTo(0, {height});".format(height=old_height))
            sleep(1)
            new_height = self.browser.execute_script(
                "return document.documentElement.scrollHeight")
            if new_height == old_height:
                break

        sel = Selector(text=self.browser.get_source())
        return self.extract_all(
            sel, '//ytd-grid-video-renderer/div/ytd-thumbnail/a/@href')


class PlaylistYoutubeParser(YoutubeParser):
    """docstring for ChannelYoutubeParser."""
    playlist_pattern_1 = re.compile('https://www.youtube.com/watch.*')
    playlist_pattern_2 = re.compile('https://www.youtube.com/playlist.*')

    def __init__(self, url, browser):
        super(PlaylistYoutubeParser, self).__init__(url, browser)

        if PlaylistYoutubeParser.playlist_pattern_1.match(url):
            pattern = re.compile('list=[^&]*')
            self.url = 'https://www.youtube.com/playlist?{lst}'.format(
                lst=pattern.search(url).group())

    def a_tags(self):
        sel = Selector(text=self.browser.get_source())
        return self.extract_all(
            sel,
            ('//ytd-playlist-video-list-renderer'
             '/div/ytd-playlist-video-renderer/div[@id="content"]/a/@href'))


class ParserFactory():
    def create_parser(self, url):
        return (
            ChannelYoutubeParser
            if ChannelYoutubeParser.channel_pattern.match(url) else
            PlaylistYoutubeParser if
            (PlaylistYoutubeParser.playlist_pattern_1.match(url)
             or PlaylistYoutubeParser.playlist_pattern_2.match(url)) else None)


class Browser():
    def __init__(self, *options):
        self.chrome_options = Options()
        for option in options:
            self.chrome_options.add_argument(option)

    def __enter__(self):
        self.driver = webdriver.Chrome(chrome_options=self.chrome_options)
        return self

    def __exit__(self, *args):
        # pass
        self.driver.quit()

    def get(self, url):
        self.driver.get(url)

    def execute_script(self, script):
        return self.driver.execute_script(script)

    def get_source(self):
        return self.driver.page_source

    def wait_with_xpath(self, xpath):
        try:
            WebDriverWait(self.driver, 3).until(
                EC.presence_of_element_located((By.XPATH, xpath)))
        except Exception as e:
            print(e, type(e))
            return False
        return True


def parse_url(url, job_id):
    # with Browser('--disable-gpu') as browser:
    start_time = time()
    with Browser('--headless', '--disable-gpu', '--no-sandbox') as browser:
        # url = 'https://www.youtube.com/user/AsapSCIENCE/videos'
        # url = 'https://www.youtube.com/playlist?list=PLvFsG9gYFxY_2tiOKgs7b2lSjMwR89ECb'
        # url = 'https://www.youtube.com/watch?v=ztiHRiFXtoc&list=PLvFsG9gYFxY_2tiOKgs7b2lSjMwR89ECb'
        parser_factory = ParserFactory()
        youtube_parser = parser_factory.create_parser(url)(url, browser)
        youtube_parser.parse(job_id)
    print('duration ', time() - start_time)


# parse_url('https://www.youtube.com/user/AsapSCIENCE/videos')
