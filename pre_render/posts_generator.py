"""posts_generator.py

This module uses Tkinter GUI to select options as an iput for Entrez API on Pubmed.
Articles found and aknowledged are added as a new post into './publications/posts'.
This articles will be added to the 'https://neuro-ix.github.io/publications/' after quarto rendering.

Example:
  quarto render --cache-refresh
  quarto preview publications/index.qmd

Todo:
  * If category is empty, don't add to url_search
  * Create functions for the API fetch and text treatment
  * Add check boxes to select found articles that should be added to website
  * Try when catch several articles
  * Add global variables to make the code easier to understand
"""

__author__ = "Benoît Verreman"
__license__ = "MIT"
__version__ = "1.0.1"
__maintainer__ = "Benoît Verreman"
__email__ = "benoit.verreman@etsmtl.ca"
__status__ = "Production"

import os

from tkinter import *
from tkinter import ttk

import pandas as pd #open source data analysis and manipulation tool
import requests #standard for making HTTP requests 
from bs4 import BeautifulSoup as bs #library for parsing structured data
import lxml #Help BeautifulSoup dealing with xml files
from yattag import indent #Help print xml files

from unidecode import unidecode #remove accents

if not os.getenv("QUARTO_PROJECT_RENDER_ALL"):
  exit()
  
  
###Create windows


class ArticlesFinder:

    def __init__(self, root):
        root.title("Find articles on Pubmed")
        
        # Content Frame
        mainframe = ttk.Frame(root, padding="3 3 12 12")
        mainframe.grid(column=0, row=0, sticky=(N, W, E, S))
        root.columnconfigure(0, weight=1)
        root.rowconfigure(0, weight=1)
       
        # Entry: Maximum articles to find 
        self.maxi= StringVar() 
        ttk.Label(mainframe, text="Maximum articles:").grid(column=1, row=1, sticky=W)
        maxi_entry = ttk.Entry(mainframe, width=10, textvariable=self.maxi)
        maxi_entry.grid(column=2, row=1, sticky=(W, E))
        
        # Entry: Articles PMID to find
        self.pmid = StringVar() 
        ttk.Label(mainframe, text="PMIDs:").grid(column=1, row=2, sticky=W)
        pmid_entry = ttk.Entry(mainframe, width=10, textvariable=self.pmid)
        pmid_entry.grid(column=2, row=2, sticky=(W, E))
        
        # Entry: Date before publishing
        self.date = StringVar() 
        ttk.Label(mainframe, text="Days since publishing:").grid(column=1, row=3, sticky=W)
        date_entry = ttk.Entry(mainframe, width=10, textvariable=self.date)
        date_entry.grid(column=2, row=3, sticky=(W, E))

        # Entry: Key terms
        self.terms = StringVar() 
        ttk.Label(mainframe, text="Key terms:").grid(column=1, row=4, sticky=W)
        terms_entry = ttk.Entry(mainframe, width=10, textvariable=self.terms)
        terms_entry.grid(column=2, row=4, sticky=(W, E))
        
        # Button: Search 
        ttk.Button(mainframe, text="Search", command=self.search).grid(column=2, row=5, sticky=N)
        
        # Result: Articles found
        self.results = StringVar() 
        ttk.Label(mainframe, textvariable=self.results).grid(column=1, row=6, sticky=(N, W, E, S))
        
        # Some Polish
        for child in mainframe.winfo_children(): 
            child.grid_configure(padx=10, pady=10)

        maxi_entry.focus()
        root.bind("<Return>", self.search)
        
    def search(self, *args):
        try:
            url_search="https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esearch.fcgi?db=pubmed&retmax=" + \
            self.maxi.get() + \
            "&reldate=" + \
            self.date.get() + \
            "&term=" + \
            self.terms.get() + \
            "&usehistory=y"
            #value = float(self.pmid.get())
            self.results.set("Search URL:\n" + url_search)
        except ValueError:
            pass

root = Tk()
ArticlesFinder(root)
root.mainloop()


###Search the articles of interest on PubMed using specific API Entrez

url_search="https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esearch.fcgi?db=pubmed&retmax=5&reldate=40&term=Bouix[Author]&usehistory=y"
page = requests.get(url_search)
soup = bs(page.content, "xml")

qk = soup.find("QueryKey").text
we = soup.find("WebEnv").text


###Use previous search to fetch the data

url_fetch="https://eutils.ncbi.nlm.nih.gov/entrez/eutils/efetch.fcgi?db=pubmed&usehistory=y&query_key="+qk+"&WebEnv="+we #&rettype=medline&retmode=text
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
