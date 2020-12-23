# -*- coding: utf-8 -*-
"""UNOTaku_Web_Injection_Scraping_Implementation Attempt.ipynb

Automatically generated by Colaboratory.

Original file is located at
   https://colab.research.google.com/drive/1XmzqwErxt5LmVD2BSa7WrrAy0RwWFbHu
"""
#Downloaded Packages successfully built

#!pip install selenium 
#!pip install datetime
#!pip install chromedriver_binary
#!pip install cutlet
#!pip install unidic-lite
#!git clone https://github.com/aboSamoor/polyglot
#!pip install polyglot==14.11
#!pip install icu
#!pip install requests_html
#!pip install bs4
#!pip install html5lib


#Failed to load/ install: 

#!git clone https://github.com/python/cpython/blob/3.9/Lib/locale.py
#!pip install locale
#!pip install libicu-dev
#!polyglot --help

# For Tokenizing using Polyglot; 
# if not using # hepburn converter, aka cutlet.
# -*- coding: utf-8 -*-

import cutlet #GitHub cutlet application; for parsing JPN to Romanji/ Hepburn
import icu
import polyglot
#import libicu-dev #detects languages instead... 
#from builtins import str as _builtin_str
#from icu import Locale
#from polyglot.text import Text,Word 

# For Tokenizing using Polyglot; 
# if not using # hepburn converter, aka cutlet.
import pdb
#import mymodule

import chromedriver_binary
import csv
import numpy as np
import pandas as pd
import encodings
import encodings.aliases
import re
import locale
import _collections_abc
import functools
import unicodedata
import sys 
import requests
import json
from pprint import pprint #if needed, we can decompose as pretty_print
from selenium import webdriver as webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import Select
from urllib.error import HTTPError
from urllib.error import URLError
from selenium.common.exceptions import TimeoutException
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.support.ui import WebDriverWait as WDWait
from selenium.webdriver.support import expected_conditions as EC
from requests_html import HTMLSession
from time import sleep
from urllib.request import urlopen as uopen
from bs4 import BeautifulSoup as bs

try: 
    # For subsequent runs, change 3 elements to make it generlized... 
    # 1. change the writing privilege of the csv file reader ('a+', 
    # ONLY IF myanimelist has changed stock titles and there exists titles that 
    # don't exist in dB on UNOTaku; then 'w+')
    # 2. the topAnimeListURL array, to the starting page ?= {50*idx} where left off...
    # 3,4: indices of iteration... Set up the dominoes... 

    # from stackOverflow JPN detection for non-unicode string...
    
    def make_unicode(input):
        if type(input) != unicode:
           input = input.decode('utf-8')
        return input

    def textExtractionFromBS(bsObject):
        #Derived from StackOverflow User Hugh Bothwell...
        # URL: https://stackoverflow.com/questions/22799990/beatifulsoup4-get-text-still-has-javascript 
        # kill all script and style elements
        for script in bsObject(["script", "style"]):
            script.decompose()    # rip it out
        # get text
        text = bsObject.get_text()
        # break into lines and remove leading and trailing space on each
        lines = (line.strip() for line in text.splitlines())
        # break multi-headlines into a line each
        chunks = (phrase.strip() for line in lines for phrase in line.split("  "))
        # drop blank lines
        text = '\n'.join(chunk for chunk in chunks if chunk)
        text = text.encode('utf-8')
      # print(f"Raw Text from bsObject: {text}.\n") 
        return text
    
    # animeTitleURL Extraction from "https:/myAnimeList.net/anime/[toolTipID/ 
    # AnimeTitleURLName]"
    
    def getAnimeURLTitles(url):
        #print(f"url: {url}\n")
        page = requests.get(url)
        #print(f"page: {page}\n")
        bsCurr = bs(page.content, 'html.parser')
        #print(f"bsCurr: {bsCurr}\n")     
        animeTitles = []
        hrefURLs = []
        title = ""
        tTID = 0
        toolTipRegexForm = re.compile("^/\d+/")
        animeTitleRegexForm = re.compile("^/([a-zA-Z0-9_])\w+/")
        # Element containing href, and text for title
        # all h3 elems, class="hoverinfo_trigger fl-l fs14 fw-b anime_ranking_h3"
        # then get all a classes where .find("a", attrs =  {"href": re.compile("^https://myanimelist.net/anime/") )  
        hrefSoup = bsCurr.find_all("h3", attrs = { "class": 
        "hoverinfo_trigger fl-l fs14 fw-b anime_ranking_h3"})
        
        hrefSoup = hrefSoup.find_all("h3 > a", attrs = {"href": re.compile(
        "^https://myanimelist.net/anime/{0}/{1}".format(
        toolTipRegexForm, animeTitleRegexForm) ) }, href=True, text=True)

        for a in hrefSoup: 
            hrefURLs.append(str (a["href"]) )  
        
        print(f"hrefURLs:\n")
        for el in hrefURLs: 
            print(f"{el}\n")  
        for tLIdx,a in hrefSoup:
            title = str (a["href"])
            if title is not None: 
               tTID = int (title.strip().replace(
               "https://myanimelist.net/anime/", "").split("/")[0]) 
               title = str (title.strip().replace(
               "https://myanimelist.net/anime/", "").split("/")[1]) 
            #  print(f"tTID: {tTID}, title: {title}.\n")
            else:
               title = ""
               tTID = 0
               print(f"Trace Point Beta...\n")
               pdb.set_trace()
            animeTitles.append({"href": hrefURLs[tLIdx], "title": title, 
                                "toolTipID": tTID })    
        return animeTitles

    #CONSTANTS: ...
    sources = ["KissAnime", "Anime-Planet", "Internet", "WCOStream"]
    lastEpisode = "0"
    titleColumns = ["noTitle", "ENG Title", "JPN Title", "Sources", "Synopsis", 
                    "Last Episode", "ALT Titles", "Genres"]
    animeGenresFiltered = ["Hentai"] 

    # Dropping all from the html where the Genre  
    # Tags contain forbidden genres...

    # VARIABLES NEEDED:
    properTitles = [] # all titles on top of each [...]/anime/%d/%s webpage...
    engTitle = [] # list of all collected ENG Anime Titles that fulfill all 
    # criteria
    jpnTitle = [] # ...                   JPN ...
    altTitles = []# ...                 Subsequent Alternative Titles Affiliated 
    # with anime title ...
    genres = [] # list of all genres with anime titles, 
    animeURLTitles = [] # /* list of all titles extracted from url's 
    # affiliated with index j; # j=0; j < 50; j+=1.*/  
    synopsisText = [] 
    toolTipID = []
    currAnimeListURL = [] # All title URL's of specific webpage of the above form
    topAnimeListURL = ["https://myanimelist.net/topanime.php?limit=0"] 
    # all URL's of 'https://myanimelist.net/topanime.php?limit={0 = (50*idx)}'
    rows = [] # /* Manually writes the mutated formula for anime php query... */

    idx = 0
    endIdx = 100 #Modify this value to allow for multiple pages of the 
    # below url form by iterating i = [0, endIdx-1] :
    
    while (idx < endIdx): 
      topAnimeListURL.append(
      "https://myanimelist.net/topanime.php?limit={0}".format((50*idx + 50)) )
      idx += 1
    print(f"topAnimeListURL: {topAnimeListURL}\n")

    splitRegexList = [".", "Season", "Series", "'", "I", "II", "III"] 
    divSpanTagAnimeDesired = ["English:", "Japanese:","Synonyms:"]

  # localeList = ["utf-8", "ja_JP.UTF-8", "en-US.UTF-8", "en_US"]
    # check if locale for generic utf-8 is either ja_JP.UTF-8, en-US.UTF-8
  # locale.setLocale("utf-8")
    idx = 0
    print("I'm Mr.Meeseeks!!! Look at MEEE!!!\n")
    
    while(idx < len(topAnimeListURL)): 
      url = topAnimeListURL[idx]
      print(f"url: {url}\n")
      page = requests.get(url)
      #print(f"page: {page}.\n")
      bsCurr = bs(page.content, 'html.parser')
      #print(f"bsCurr: {bsCurr}\n") 
      
      # Anime title html href dictionary object...
      # Collect the following:
      # i. extracted titleName from URL in animeURLTitles,
      # ii. toolTipID value in toolTipID, and, 
      # iii. animeURLTitles into currAnimeListURL
      dictionaryArr = getAnimeURLTitles(url)

      #pprint(f"dictionaryArr: {json.loads(dictionaryArr)}.\n")
      for el in dictionaryArr: 
          titleDictEl = json.loads(el) 
          if  (titleDictEl["title"] is None) or (
              titleDictEl["tTID"] is None) or (
              titleDictEl["href"] is None): 
              
              print("Trace Point Alpha...\n")
              pdb.set_trace()
          else:
              animeURLTitles.append(str (titleDictEl["title"]))
              toolTipID.append(int (titleDictEl["tTID"]))   
              currAnimeListURL.append(str (titleDictEl["href"]) )
              url = str (titleDictEl["href"])          
              
              print(f"toolTipID: {toolTipID},\n" + 
                    f"currAnimeListURL: {currAnimeListURL},\n" + 
                    f"animeURLTitles:{animeURLTitles}.\n")
          
         #print(f"url: {url}\n")
         page = requests.get(url)
         #print(f"page: {page}\n")
         bsCurr = bs(page.content, 'html.parser')
         #print(f"bsCurr: {bsCurr}\n")     
         
         # curr. anime title 
          for span in bsCurr.find_all("span", attrs={"itemprop": "genre", 
              "style":"display: none"},text = True) and (span is not None):
              print(f"span: {str (span.text)}\n")
              
              if (animeGenresFiltered[0] not in span.text): 
                 genres.append(str (span.text) )
              else:
                 print(f"Trace Point Gamma...\n")
                 pdb.set_trace() 
                 break # collects all genre types; #2
              print(f"genres: {genres}\n")
              
              # get from each anime title URL the following info if the genres 
              # don't contain the forbidden genre(s): 

              # main anime title title:  # body/div x 7/(title:h1 > strong, subTitle: p)
              titleElem = bsCurr.find_all("body > div > div > div > div > div > div > div > h1 > strong", text = True)  
              if titleElem is not None:
                 properTitles.append(str (el.text) for el in titleElem)
              else: 
                 print(f"Trace Point Delta...\n")
                 pdb.set_trace() 
              # secondTitle anime 
              subTitleElem = bsCurr.find_all("body > div > div > div > div > div > div > div > p", text = True)
              if subTitleElem is not None:
                 properTitles.append(str (el.text) for el in subTitleElem)
              else: 
                 print(f"Trace Point Epsilon...\n")
                 pdb.set_trace() 

              print(f"properTitles: {properTitles}\n") #1a
              # Span body/div/div/div/table/tbody/tr/td/div/div/span/strong
              for el in properTitles:
                  
                  print(f"el: {el}\n") 
                  altTitles.append(el) #1
              print(f"altTitles: {altTitles}\n")  
                  
                  # append properTitles elements to 
                  # altTitles ... 
              for k,div in bsCurr.find_all("div", {"class": "spaceit_pad"}, text = True):          
                  properTitles = []
                  divText = str (div.text )
                  print(f"divText: {divText}.\n")
                  if divSpanTagAnimeDesired[k] in divText:
                     for el in div.find("span", {"class": "dark_text"}, text=True):    
                         
                         spanText = str (el.text) 
                         
                         if (spanText is not None): 
                            spanText.strip() 
                         else: 
                            spanText = ""
                            print(f"spanText: {spanText}\n")
                         
                         filteredTitleStr = ""

                         if "English:" in spanText and (spanText != "") and (
                            divText != ""):
                        
                            filteredTitleStr = str (str (divText).replace(
                            "English:", "").split(", ")[0])    
                        
                            print(f"filteredTitleStr:{filteredTitleStr}\n")
                        
                            properTitles = str (divText).replace(
                            "English:", "").split(", ")[1::-1]
                        
                            print(f"properTitles: {properTitles}\n")
                        
                            engTit = ""
                        
                            for regex in splitRegexList:
                                filteredTitleStr = filteredTitleStr.replace(
                                regex,"")     
                                print(f"filteredTitleStr:{filteredTitleStr}\n")
                        
                            for el in properTitles: #properTitles1
                                for regex in splitRegexList:
                                    el = str (el).replace(regex,"") 
                                  # print(f"el:{el}\n")
                                    altTitles.append(el)
                            engTit += filteredTitleStr
                            print(f"engTitle Before Split: {engTit}\n")

                            # remove unwanted tokenizers... 
                            # Cannot Remove digits from text though, 
                            # because some titles contain them... grab 
                            # the first title. Assume all in ENG...
                        
                            engTit = str (engTit.split(", ")[0]) 
                            print(f"engTitle After Split: {engTit}\n")
                            engTitle.append(engTit)
                        
                            print(f"engTitle Array: {engTitle}\n")
                            # only ENG Title, in theory
                            # Change properTitles to do splits for span tag
                            # titles; properTitles2
                            
                            if "Japanese:" in str (spanText) and (spanText 
                            is not None) and (str (divText) != ""):
                        
                               filteredTitleListStr = str (str (divText).replace(
                               "Japanese:", "").split(", ")[0])
                        
                               print(f"filteredTitleListStr: " +
                                     f"{filteredTitleListStr}\n")
                        
                               properTitles = str (divText).strip().replace(
                               "Japanese:", "").split(", ")[1::-1]
                        
                               print(f"properTitles: {properTitles}\n")
                               altTitle = "" # JPN Title Name, main/alt ...
                        
                               # string.decode(locale)                        
                               jpnTitle.append(filteredTitleStr)
                               print(f"jpnTitle After:{jpnTitle}\n")

                               for el in altTitles and (str (el) != 
                                   filteredTitleStr) and (el != ""):
                            
                                   altTitle = ""
                                   altTitle += str (el).strip()
                               print(f"altTitle: {altTitle}\n")
                            
                               altTitles.append(altTitle)                         
                               print(f"altTitles: {altTitles}\n")                                                                                  

                         if "Synonyms:" in spanText and (spanText != "") and (
                             str (divText) !=""):          
                        
                             properTitles = str (divText).replace(
                             "Synonymns:", "").split(", ")
                        
                             print("properTitles: {properTitles}\n")
                        
                             altTitle = ""
                             for el in properTitles and (
                                 str (el)!= filteredTitleStr):
                                 altTitle = ""
                                 print(f"el: {el}\n")
                            
                                 altTitle += str (el).strip()
                                 print(f"altTitle: {altTitle}\n")
                            
                                 altTitles.append(altTitle) 
                             print(f"altTitles:{altTitles}\n")              
                 
                             synopsisDelRegexList = ["[Written by MAL Rewrite]",
                             "(Source: Wikipedia)", "(Source: otakumode)"] 

                             synopsis = ""

                             pDescrArr= bs.find_all("p",{"itemprop":"description"}, 
                                                    text= True)
                     
                             synopsis += [str (
                                 el.text).strip() for el in pDescrArr]

                             print(f"Synopsis Before Replace:{synopsis}\n")
                             synopsis = synopsis.replace("<br>", "")
                             for regex in synopsisDelRegexList:
                                 synopsis.replace(regex, "") 

                             print(f"Synopsis After Replace:{synopsis}\n")            
                             synopsisText.append(synopsis) 
                             # get Synopsis Text here

          rows.append(int (50*idx + j + 1), engTitle[0], jpnTitle[0], sources, 
                      synopsisText, lastEpisode, altTitles, genres) 
          # Append all extracted data elems. to multidimensional rows array.
         
          print(f"properTitles: {properTitles}\nengTitle:{engTitle}\n"+ 
                f"jpnTitle:{jpnTitle}\naltTitles: {altTitles}\n" + 
                f"genres:{genres}\nsynopsisText: {synopsisText}\n")
          
          print(f"Before deleting the unneeded arrays, their contents are as" + 
                f" follows:\ntoolTipID : {toolTipID}\ncurrAnimeListURL: " +
                f"{currAnimeListURL}\ntopAnimeListURL: {topAnimeListURL}\n")
          
          toolTipID = [] #If the list, rows, is mutable, then these 
          currAnimeListURL = [] # are irrelevant variables. Delete them.
          topAnimeListURL  = [] # Let garbage collection do its job...      
          properTitles = [] # Reset all extracted arrays, bc they
          engTitle = [] # should be in rows, and the co-vectors
          jpnTitle = [] # still have a job to do, so they are overridden...
          altTitles = []
          genres = []
          synopsisText = []
          
          idx += 1 
    
  # print(f"Rows at the end of whole looping Struct: {rows}\n") 
    for row,i in range(len(rows)):
        for col,j in range(len(rows[i])):
            rows[i][j] = f"{rows[i][j]}    "
        rows[i][len(row[i]) - 1] += "\n"
    print(f"Rows: {rows}\n")

    fileName = "web_Scraper_UNOTaku_Anime_Club_Edit_Anime_List_1.csv"
    with open(fileName, encoding='utf-8',mode='w+') as csvfile:
         csvwriter = csv.writer(csvfile)
         print("Writer successfully created...\n")
         csvwriter.writerow(titleColumns)
         print("Writing column names to file...\n")
         csvwriter.writerows(rows)
         print("Writing rows to file...\n")
         
         for i,row in len(rows): 
             print(f"printing row {i+1}: {row}.\n")
         print(f"All Done!!!\n...Poof...\n")

except URLError: 
         print(f"Cannot Open Web Reader for extraction by BeautifulSoup,"+ 
         f"or there is a problem with the webpage (Error 404, webpage down, "+ 
         f"etc...).\n")
except HTTPError:
         print("Webpage had an internal error fail to load the webpage," + 
              " or misc. reasons,\n and/or because of this, the webpage "+ 
              " cannot be scraped. Sorry...\n")
except NoSuchElementException:
         print("Element does not exist, or cannot be parsed properly by "+ 
               "webpage...\n")
except IOError:       
         print("The *.csv file requested to be opened and written upon cannot"+
              " be accomplished, for some reason.\nPlease check your settings,"
              +" and try again...\n")
except TimeoutException: 
         print("Session has timed out. Please try again.\n")  
except Exception:
         print("Miscellaneous Exception type... Something went terribly"+ 
               " wrong, dude.\nCheck the compiler for more...\n")
except Error:
         print("Miscellaneous Error type... Something went horribly "+ 
               "wrong, dude.\nCheck the compiler for more...\n") 