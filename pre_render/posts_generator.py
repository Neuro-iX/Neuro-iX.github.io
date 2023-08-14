"""posts_generator.py

This module uses Tkinter GUI to select options as an iput for Entrez API on Pubmed.
Articles found and aknowledged are added as a new post into './publications/posts'.
This articles will be added to the 'https://neuro-ix.github.io/publications/' after quarto rendering.

Example:
  quarto render --cache-refresh
  quarto preview publications/index.qmd

Todo:
  * Create functions for the API fetch and text treatment
  * Add check boxes to select found articles that should be added to website
  * Try when catch several articles
  * Add global variables to make the code easier to understand

References:
  * Example of GUI using TKinter:
    https://tkdocs.com/tutorial/firstexample.html
  * For the GUI, choose between grid, pack and place:
    https://www.pythonguis.com/faq/pack-place-and-grid-in-tkinter/
"""

__author__ = "Benoît Verreman"
__license__ = "MIT"
__version__ = "1.0.2"
__maintainer__ = "Benoît Verreman"
__email__ = "benoit.verreman@etsmtl.ca"
__status__ = "Production"

import os
 
from tkinter import * # Create GUI
#import tkinter as tk
import tkinter.ttk as ttk
from tktooltip import ToolTip

import pandas as pd # Open source data analysis and manipulation tool
import requests # Standard for making HTTP requests 
from bs4 import BeautifulSoup as bs # Library for parsing structured data
import lxml # Helps BeautifulSoup dealing with xml files
from yattag import indent # Helps print xml files

from unidecode import unidecode # For removing accents


if not os.getenv("QUARTO_PROJECT_RENDER_ALL"):
  exit()
  
  
###Create windows

class ArticlesFinder:
    """
    A class used to represent a GUI to search for articles on Pubmed

    ...

    Attributes
    ----------
    maxi : str
        Maximum number of articles to search for
    pmid : str
        List of PMID of articles on Pubmed
    days : str
        Maximum number of days since publishing date
    terms : str
        Key terms (for example: Bouix[Author])
    results : str
        List of the title, date, first author and DOI of all the articles found
        
    Methods
    -------
    search(self, *args) -> (str) we, (str) qk
        Creates the command for Entrez API and gets WebEnv and query_key
    fetch(self, *args) -> (str) results
        Creates the command for Entrez API and gets searching data results
    """
    
    # Modules
    def __init__(self, root):
        """Initialize a root window with every buttons and entries
      
        Parameters
        ----------
        root : tkinter
            Tkinter GUI for searching parameters and creating posts
      
        """
        
        # Statics
        n_widget = 0
        n_frame = 0
        
        # Constants
        WIDTH_ENTRY = 100
        
        # Root config
        root.title("Articles finder")
        root.columnconfigure(0, weight = 1)
        root.rowconfigure(0, weight = 1)      
        
        # Creating Frames
        mainframe = ttk.Frame(root, padding = "3 3 12 12")
        mainframe.grid(column = 0, row = n_frame, sticky = (N, W, E, S))
        n_frame += 1
        
        resultframe = ttk.Frame(root, padding = "3 3 12 12")
        resultframe.grid(column = 0, row = n_frame, sticky = (N, W, E, S))
        n_frame += 1

        # Entry: Maximum articles to find 
        self.maxi = StringVar() 
        n_widget += 1
        maxi_b = Button(mainframe, text = "Maximum articles", disabledforeground = "black")
        maxi_b["state"]="disable"
        maxi_b.grid(column = 1, row = n_widget, sticky = (W, E))
        ToolTip(maxi_b, msg="Maximum number of articles to search for")
        maxi_entry = ttk.Entry(mainframe, width = WIDTH_ENTRY, textvariable=self.maxi)
        maxi_entry.grid(column = 2, row = n_widget, sticky = (W, E))
        
        # Entry: Articles PMID to find
        self.pmid = StringVar() 
        n_widget += 1
        maxi_b = Button(mainframe, text = "PMIDs", disabledforeground = "black")
        maxi_b["state"]="disable"
        maxi_b.grid(column = 1, row = n_widget, sticky = (W, E))
        ToolTip(maxi_b, msg = "List of article PMIDs on Pubmed")
        pmid_entry = ttk.Entry(mainframe, width = WIDTH_ENTRY, textvariable = self.pmid)
        pmid_entry.grid(column = 2, row = n_widget, sticky = (W, E))
        
        # Entry: Date before publishing
        self.date = StringVar() 
        n_widget += 1
        maxi_b = Button(mainframe, text = "Days", disabledforeground = "black")
        maxi_b["state"]="disable"
        maxi_b.grid(column = 1, row = n_widget, sticky = (W, E))
        ToolTip(maxi_b, msg = "Maximum number of days since publishing date")
        date_entry = ttk.Entry(mainframe, width = WIDTH_ENTRY, textvariable = self.date)
        date_entry.grid(column = 2, row = n_widget, sticky = (W, E))

        # Entry: Key terms
        self.terms = StringVar() 
        n_widget += 1
        maxi_b = Button(mainframe, text = "Terms", disabledforeground = "black")
        maxi_b["state"]="disable"
        maxi_b.grid(column = 1, row = n_widget, sticky = (W, E))
        ToolTip(maxi_b, msg = "Special terms like Bouix[Author]")
        terms_entry = ttk.Entry(mainframe, width = WIDTH_ENTRY, textvariable = self.terms)
        terms_entry.grid(column = 2, row = n_widget, sticky = (W, E))
        
        # Button: Search 
        n_widget += 1
        ttk.Button(mainframe, text = "Search", command = self.toSearch).grid(column = 2, row = n_widget, sticky = N)
        root.bind("<Return>", self.toSearch)
        
        # Some Polish
        for child in mainframe.winfo_children(): 
            child.grid_configure(padx = 10, pady = 10)
        
        # Default widget selection
        maxi_entry.focus()
        
        # Search URL: Use esearch command frome API Entrez
        self.searched_url = StringVar() 
        n_widget += 1
        ttk.Label(resultframe, textvariable = self.searched_url).grid(column = 1, row = n_widget, sticky = (N, W, E, S))
        
        """
        n_widget += 1
        searched_url_label = ttk.Entry(resultframe, width = WIDTH_ENTRY, textvariable = self.searched_url)
        
        new_state = "disabled" if searched_url_label.get() == "" else "normal"
        searched_url_label.configure(state=new_state)
        
        searched_url_label["state"] = "readonly"
        searched_url_label.grid(column = 1, row = n_widget, sticky = (N, W, E, S))
        """
        
        # Fetch URL: Use efetch command frome API Entrez
        self.fetched_url = StringVar() 
        n_widget += 1
        ttk.Label(resultframe, textvariable = self.fetched_url).grid(column = 1, row = n_widget, sticky = (N, W, E, S))
        
        # Results: Found articles 
        self.resulting_text = StringVar() 
        n_widget += 1
        ttk.Label(resultframe, textvariable = self.resulting_text).grid(column = 1, row = n_widget, sticky = (N, W, E, S))
        
        self.qk = str() 
        self.we = str() 
        
    def toSearch(self, *args):            
        url_search = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esearch.fcgi?db=pubmed"
        if self.maxi.get() :
          url_search += "&retmax=" + self.maxi.get()
        if self.date.get() :
          url_search += "&reldate=" + self.date.get()
        if self.terms.get() :
          url_search += "&term=" + self.terms.get()
        url_search += "&usehistory=y"
        
        self.searched_url.set("Search URL:\n"+url_search)
      
        page = requests.get(url_search)
        
        if page:
            soup = bs(page.content, "xml")
            
            self.qk = soup.find("QueryKey").text
            self.we = soup.find("WebEnv").text
                
            self.toFetch()
        else:
            self.fetched_url.set("No article found")
        
    def toFetch(self, *args):
        url_fetch = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/efetch.fcgi?db=pubmed&usehistory=y&query_key="+self.qk+"&WebEnv="+self.we #&rettype=medline&retmode=text
        page = requests.get(url_fetch) 
        soup = bs(page.content, "xml")
        
        self.fetched_url.set("Fetch URL:\n" + url_fetch)
        
        self.soup = soup
        self.toPresent()

    
    def toPresent(self, *args):
        try:
            title = self.soup.find('ArticleTitle').text
            if title.endswith('.'):
                title = title[:-1]
                
            self.resulting_text.set("Articles found:\n" + title)
        except:
            self.resulting_text.set("No article found")
            pass
          
          
root = Tk()
ArticlesFinder(root)
root.mainloop()


###Search the articles of interest on PubMed using specific API Entrez

url_search = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esearch.fcgi?db=pubmed&retmax=5&reldate=40&term=Bouix[Author]&usehistory=y"
page = requests.get(url_search)
soup = bs(page.content, "xml")

qk = soup.find("QueryKey").text
we = soup.find("WebEnv").text


###Use previous search to fetch the data

url_fetch = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/efetch.fcgi?db=pubmed&usehistory=y&query_key="+qk+"&WebEnv="+we #&rettype=medline&retmode=text
page = requests.get(url_fetch) 
soup = bs(page.content, "xml")


xml_text = indent(str(soup))
print(xml_text)
print("--------------------\n\n")

###Process the data to create the blog

##Get Title
title = soup.find('ArticleTitle').text
if title.endswith('.'):
    title = title[:-1]

##Get Abstract
raw_abstract = soup.find('Abstract')
raw_abstract_children=raw_abstract.find_all('AbstractText')

if raw_abstract_children==[]: #Test if there are 'AbstractText'
  abstract=raw_abstract.text
else:
  abstract_list=[] #Contain the different paragraphs of the abstract with the labels
  for i in raw_abstract_children:
    abstract_list.append(i["Label"]+': '+i.text)
  abstract='\n\n'.join(abstract_list)
  
abstract_print='# Abstract:\n\n'+abstract

##Get Authors
raw_authors= soup.find_all('Author')
lastname=[]
forename=[]
affiliations=[]
list_affiliations=[]

for i in raw_authors:
  lastname.append(i.find('LastName').text)
  forename.append(i.find('ForeName').text)
  l1=i.find_all('Affiliation') #all affiliations
  l2=[] #indexes of affiliations
  for j in l1:
    j_text=j.text
    if not(j_text in list_affiliations):
      list_affiliations.append(j_text)
    l2.append(list_affiliations.index(j_text))
  affiliations.append(l2)

dict={'lastname':lastname,'forename':forename,'affiliations':affiliations}  
authors_df = pd.DataFrame(dict)

authors_list=[a+' '+b for a,b in zip(forename,lastname)]

authors_print=["  - name: "+a+'\n' for a in authors_list]
authors_print=''.join(authors_print)
authors_print=authors_print.replace("?", "e")

affiliations_print=' | '.join(list_affiliations)

##Get Journal and Date
raw_journal= soup.find('Journal')

journal=raw_journal.find('Title').text

def mtn(x):
    months = {
        'jan': "{:02d}".format(1),
        'feb': "{:02d}".format(2),
        'mar': "{:02d}".format(3),
        'apr': "{:02d}".format(4),
         'may': "{:02d}".format(5),
         'jun': "{:02d}".format(6),
         'jul': "{:02d}".format(7),
         'aug': "{:02d}".format(8),
         'sep': "{:02d}".format(9),
         'oct': "{:02d}".format(10),
         'nov': "{:02d}".format(11),
         'dec': "{:02d}".format(12)
        }
    a = x.strip()[:3].lower()
    try:
        return months[a]
    except:
        raise ValueError('Not a month')
raw_date=raw_journal.find('PubDate')
date=[raw_date.find('Year').text,mtn(raw_date.find('Month').text),"{:02d}".format(int(raw_date.find('Day').text))]

date_print=date[0]+'-'+date[1]+'-'+date[2]

##Get Publication Type
publication_type=soup.find('PublicationType').text

##Get Keyword List
raw_kw=soup.find_all('Keyword')
kw=[]
for i in raw_kw:
    kw.append(i.text)

kw_print="["+', '.join(kw)+"]"

##Get DOI
doi= soup.find('ELocationID',{"EIdType" : "doi"}).text

##Get PMID
pmid=soup.find('PMID').text


###Use previous search to get links and citation

##Get Citation
# url_link="https://eutils.ncbi.nlm.nih.gov/entrez/eutils/elink.fcgi?db=pubmed&cmd=prlinks&retmode=ref&query_key="+qk+"&WebEnv="+we
# page = requests.get(url_link) 
# soup0 = bs(page.content, "xml")
# 
# xml_text = indent(str(soup0))
# print(xml_text)
# print("--------------------\n\n")


###Create post in 'posts' directory
# print('pwd= ',os.getcwd())
title_part='_'.join(title.split()[:6])
post_name=date[0]+'_'+date[1]+'_'+date[2]+'_'+title_part

path = './publications/posts/'+post_name
if not os.path.exists(path):
    os.makedirs(path)

new_post="""---
title: {title}
#description: {description}
author:
{authors}
date: {date}
categories: {categories}
#image: map.jpg
format:
  html:
    toc: false #No table of content
engine: knitr
---

{abstract}
""".format(title='"'+unidecode(title)+'"', description='"'+unidecode(affiliations_print)+'"', authors=unidecode(authors_print), date='"'+unidecode(date_print)+'"', categories=kw_print, abstract=unidecode(abstract_print))

with open(path+"/index.qmd", 'w') as f:
  f.write(new_post)
