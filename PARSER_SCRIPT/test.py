
import random
import time

import undetected_chromedriver as uc
from fake_useragent import UserAgent
from selenium import webdriver
from lxml import html
#from webdriver_manager.firefox import GeckoDriverManager

from ENGINE import Parser
import requests
from bs4 import BeautifulSoup
import datetime


options = uc.ChromeOptions()
options.headless=True
options.add_argument("--no-sandbox")
options.add_argument("--disable-setuid-sandbox")
driver = uc.Chrome(executable_path='/usr/local/bin/chromedriver', options=options)
print(1)
driver.get('https://google.com')
print(2)
