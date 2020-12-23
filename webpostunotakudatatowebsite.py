# -*- coding: utf-8 -*-
"""WebPostUNOTakuDataToWebsite.ipynb

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/1ogcTbY0Z7ezWlC2mn34VvEHfAJClkjuM#scrollTo=orObMzBqi_xv
"""
# !pip install selenium
# !pip install chromedriver_binary
# !pip install downloaded_wheel.whl
# !pip install cutlet
# !pip install unidic-lite   

# import libicu-dev #detects languages instead... 
# import sys 
# import polyglot
# import cutlet #GitHub cutlet application; for parsing JPN to Romanji/ Hepburn
# from pprint import pprint #if needed, we can decompose as pretty_print
# from polyglot.text import Text,Word # For Tokenizing using Polyglot; if not using hepburn converter, aka cutlet.

from urllib.request import urlopen as uopen
from urllib.error import HTTPError
from urllib.error import URLError
from selenium.common.exceptions import NoSuchElementException
from selenium.common.exceptions import TimeoutException
from bs4 import BeautifulSoup as bs
from BeautifulSoup import BeautifulSoup
from selenium import webdriver as webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import Select
from selenium.webdriver.support.ui import WebDriverWait as WDWait
from selenium.webdriver.support import expected_conditions as EC
from requests_html import HTMLSession
from time import sleep
import chromedriver_binary
import csv
import pandas as pd
import numpy as np
import selenium
import re
import sys
import time
import pandas as pd
import numpy as np

# The following programs for web-scraping/ Selenium-web-based injections by 
# Tony Avellino Ianacone(picano), Kevin 'Kev' Elder, and Kevin Alan Spohn

# Replace Separator Regexes : /[' & (^'s)]/g+ 'regex1' remove apostrophes 
# not before an s... Gintama...
# Split Separators (regexes) for titles: ['regexDigitsSplit' :/\s[a-zA-Z]/+1g] 


