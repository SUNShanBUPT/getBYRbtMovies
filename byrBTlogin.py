import os
from PIL import Image
from io import BytesIO
import logging
import pickle
try:
    from urllib.parse import urlparse, parse_qs
except ImportError:
    from urlparse import urlparse, parse_qs
import requests
from bs4 import BeautifulSoup
from decaptcha import DeCaptcha



class Byr(object):

    """login/logout/getpage"""
    

    def __init__(self, username, password):
        """Byr Init """
        console = logging.StreamHandler()
        console.setLevel(logging.DEBUG)
        formatter = logging.Formatter(
            '[%(filename)s:%(lineno)4s - %(funcName)10s ] %(message)s'
        )
        console.setFormatter(formatter)

        self.logger = logging.getLogger("byr")
        self.logger.addHandler(console)
        self.logger.setLevel(logging.INFO)

        self._session = requests.session()
        self._session.headers = {
            'User-Agent': 'Magic Browser'
        }
        self._root = 'https://bt.byr.cn/'
        self.list = []
        self.username = username
        self.password = password
        

    def login(self):
        """Login to bt.bry.cn"""
        login_page = self.get_url('login.php')
        image_url = login_page.find('img', alt='CAPTCHA')['src']
        image_hash = login_page.find(
            'input', attrs={'name': 'imagehash'})['value']
        self.logger.debug('Image url: ' + image_url)
        self.logger.debug('Image hash: ' + image_hash)
        req = self._session.get(self._root + image_url)
        image_file = Image.open(BytesIO(req.content))
        decaptcha = DeCaptcha()
        decaptcha.load_model('./captcha_classifier.pkl')
        captcha_text = decaptcha.decode(image_file)
        self.logger.debug('Captcha text: ' + captcha_text)

        login_data = {
            'username': self.username,
            'password': self.password,
            'imagestring': captcha_text,
            'imagehash': image_hash
        }
        main_page = self._session.post(
            self._root + 'takelogin.php', login_data)
        if main_page.url != self._root + 'index.php':
            self.logger.info('Login error')
            return
        self._save()

    def _save(self):
        """Save cookies to file"""
        self.logger.info('Save cookies')
        with open('cookie', 'wb') as f:
            pickle.dump(self._session.cookies, f)

    def _load(self):
        """Load cookies from file"""
        if os.path.exists('cookie'):
            with open('cookie', 'rb') as f:
                self.logger.info('Load cookies from file.')
                self._session.cookies = pickle.load(f)
        else:
            self.logger.info('Load cookies by login')
            self.login()
            self._save()


    def get_url(self, url):
        """Return BeautifulSoup Pages
        :url: page url
        :returns: BeautifulSoups
        """
        self.logger.debug('Get url: ' + url)
        req = self._session.get(self._root + url)
        return BeautifulSoup(req.text, 'lxml')

    def start(self):
        """Start spider"""
        self.logger.info('Start Spider')
        self._load()       
                    
        for i in range(10):
            url = 'torrents.php?inclbookmarked=0&pktype=0&incldead=0&spstate=0&cat=408&page=' + str(i)
            print('Get info from https://bt.byr.cn/' + url)
            html = self.get_url(url)
            self.download(html, i)
        
        

    def download(self, html, counter):
        """Download torrent in url"""
        
        for i in range(50):
            detail_url = html.find_all('td', class_ = 'rowfollow', width = '100%', align = 'left')[i].find_all('a')[0]['href']
            movie_name = html.find_all('td', class_ = 'rowfollow', width = '100%', align = 'left')[i].b.string
            
            number = counter * 50 + i + 1
            
            line = 'Movie ' + str(number) + ':' + '网址: https://bt.byr.cn/' + detail_url + '\n' + movie_name + '\n\n'          
            
            f = open('./movies.txt', 'a', encoding='utf-8')
            f.write(line)
            f.close()
            
      



def main():
    b = Byr('', '')  # Your username and password
    b.start()


if __name__ == "__main__":
    main()
    
