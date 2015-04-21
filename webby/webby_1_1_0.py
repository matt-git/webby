#Folksonomy: A user-generated system of classifying and organizing online content 
#            into different categories by the use of metadata such as electronic tags

import os
import sys
import time
import collections
import difflib
import re
import urllib2 as ulib
import urllib
from sets import Set

try:

	from bs4 import BeautifulSoup, SoupStrainer
	from lxml import html
	from lxml.html.clean import clean_html
	
except ImportError as ie:
	print "Import Error: %s" % ie.message




__version__ = '1.1.0'
__all__ = ['Crawler', 'Parser', 'Feed']

HTML = 0
	
ID = 'id'
XPATH = 'xpath'
LINK_TEXT = 'link text'
PARTIAL_LINK_TEXT = 'partial link text'
NAME = 'name'
TAG_NAME = 'tag name'
CLASS_NAME = 'class name'
CSS_SELECTOR = 'css selector'
CLEANUP = dict((ord(char), None) for char in "/\".,;:><?+'!@#$%^&*()-=|][{}`~\\\n\r")
TIDY = dict((ord(char), None) for char in "\n\r\t")
BADTAGS = map(lambda x: x.upper(), Set(['all', 'just', 'being', 'over', 'both', 'through', 'yourselves', 'its', 'before', 'herself', 'had', 'should', 
'to', 'only', 'under', 'ours', 'has', 'do', 'them', 'his', 'very', 'they', 'not', 'during', 'now', 'him', 'nor', 'did', 'this', 
'she', 'each', 'further', 'where', 'few', 'because', 'doing', 'some', 'are', 'our', 'ourselves', 'out', 'what', 'for', 'while', 
'does', 'above', 'between', 't', 'be', 'we', 'who', 'were', 'here', 'hers', 'by', 'on', 'about', 'of', 'against', 's', 'or', 'own',
'into', 'yourself', 'down', 'your', 'from', 'her', 'their', 'there', 'been', 'whom', 'too', 'themselves', 'was', 'until', 'more', 'himself', 
'that', 'but', 'don', 'with', 'than', 'those', 'he', 'me', 'myself', 'these', 'up', 'will', 'below', 'can', 'theirs', 'my', 'and', 'then', 'is',
'am', 'it', 'an', 'as', 'itself', 'at', 'have', 'in', 'any', 'if', 'again', 'no', 'when', 'same', 'how', 'other', 'which', 'you', 'after', 'most',
 'such', 'why', 'a', 'off', 'i', 'yours', 'so', 'the', 'having', 'once', 'li', 'b', 'c', 'd', 'e', 'h1', 'h2', 'h3', 'h4', 'h5', 'h6', 'body',
 'div', 'span', 'header', 'font', 'menu', 'f', 'g', 'h', 'j', 'k', 'l', 'm', 'n', 'o', 'p', 'q', 'r', 's', 't', 'http', 'www', 'function', 'goto', 'else', 'do',
 'while', 'var', 'with', 'for', 'true', 'false', 'amp', 'also', 'this', 'was', 'is', 'more', 're']))

GOOGLE = 'http://www.google.com'
AMAZON = 'http://www.amazon.com'
FACEBOOK = 'http://www.facebook.com'
LINKEDIN = 'http://www.linkedin.com'



class Crawler(object):
	def __init__(self, root=GOOGLE):
		self.root = root
		self.directory = os.getcwd()
		self.current = ulib.urlopen(self.root)
		self.source = "".join(self.current.readlines())
		self.soup = html.fromstring(self.source)
		self.storedlinks=Set([self.root])
		#self.proxy = ulib.ProxyHandler({'http': '5.153.101.255'})
		#opener = ulib.build_opener(self.proxy)
		#ulib.install_opener(opener)
		
		self.__active = False
		self.__structured = False
		self.__log = {}

		self.hrefs = self.get_hyperlinks()
		#Starts Crawling from root. Root is crucial to the whole thing
		
	def __repr__(self):
		return '<Crawler Object: URL = %s>'%(self.get_url())
		
	def __call__(self):
		print "%s\n"%self.__repr__()
		print "Root: %s\n"%self.root
		print "Directory: %s\n"%self.directory
		print "Amount of Links Crawled: %s\n"%len(self.storedlinks)
		print "Amount of Links to Crawl: %s\n"%len(self.hrefs)
		print "- Useful Socket Information: \n"
		for i in self.info():
			print i
		
		
		
	def _remove_non_ascii(self, string):
		returnstring = "".join(filter(lambda x: ord(x)<128, string))
		if string != returnstring:
			return returnstring
		else: return returnstring
		
	def info(self):
		return self.current.info().headers
		
	def get_url(self):
		return self.current.geturl()

	def get_hyperlinks(self):
		return self.soup.xpath('//a/@href')
	
	def get_full_links(self):
		relist = []
		for links in self.soup.xpath('//a/@href'):
			if self.root not in links:
				relist.append("%s%s"%(self.root, links))
			else:
				relist.append(links)
			
		return relist
		
	def search(self, keywords, url=None):
		"""Uses root website's search functionality"""
		if url is None:
			url = self.root
			
		searchword = ""
		if isinstance(keywords, list):
			for words in keywords:
				searchword += str(words)+"+"
				
			self.open(url+searchword)
		if isinstance(keywords, str):
			self.open(url+(keywords.replace(" ", "+")))
		
	
		
	def open(self, url=None):
	
		try:
			if url is not None:
				if url in self.storedlinks: return -1
				
				else:
						if ("http://" in url) or ("https://" in url):
							self.current = ulib.urlopen(url)
							self.source = self.current.read()
							self.storedlinks.add(url)
							self.soup = html.fromstring(self.source)
							return 1
						else:
							return None

			else:
				self.current = ulib.urlopen(self.root)
				self.source = "".join(self.current.readlines())
				self.soup = html.fromstring(self.source)
				return 1
				
				
		except ValueError as ve:
			print ve.message
			return None
			
		except ulib.HTTPError as ht:
			print ht.message
			return None
			
		except ulib.URLError as u:
			print "Could not connect to given URL"
			return None
		
		
	def crawl(self, length=10, directory=None):
		"""finds all hyperlinks and crawls and scrapes"""
		#Surely this can be cleaned up a bit more. not sure, it may be efficient
		count = 0
		for links in self.hrefs:
			if links in self.storedlinks: continue
			if count > length: 
				return
			
			else:
				self.open(links)
				self.hrefs.remove(links)
				self.hrefs.extend(self.get_hyperlinks())
				self.hrefs = list(Set(self.hrefs))
				
			count += 1
		
			if not directory:
			
				if not self.soup.title: continue
				
				else:
					title = self.soup.title.text.translate(CLEANUP)

					self.export(self._remove_non_ascii("%s\\%s"%(self.directory, title)))
					
			else:
				if not self.soup.title:
					continue
				else:
					title = self.soup.title.text.translate(CLEANUP)

					self.export(self._remove_non_ascii("%s\\%s"%(directory, title)))
	
	def ship(self):
		"""Returns feed"""
				
	def html(self):
		print self.soup.prettify()
		return

	def export(self, filename, text=None):
		"""Saves source into file"""
		if text == None: text = self.source
		if "\\" not in filename: filename = "%s\\%s.txt"%(self.directory, filename)
		else: filename += '.txt'
		
		f = open(filename, 'w')
		f.write(self._remove_non_ascii(text))
		f.close()
		
		return 
		
	def exit(self):
		"""exits module cleanly"""
		sys.exit(1)
		
		
class Feed(object):
	def __init__(self, sourcecode):
		self.sourcelist = [sourcecode]
		self.source = sourcecode
		
	def eat(self, sourcecode):
		self.sourcelist.append(sourcecode)
		return None
		
	def get(self):
		return self.sourcelist
		

class Parser(object):
	def __init__(self, text=None):
		self._rawtext = text
		self._blockset = Set([])
		self._structured = False
		self.directory = os.getcwd()
		self.data = collections.defaultdict(dict)
		if text is None: self.soup = html.Element("html")
		else: self.soup = html.fromstring(self._rawtext, 'html.parser')
		self.code = hash(self._rawtext)
		self._max = 0
			
	def __nodupe(self, lst):
		"""removes duplicates!"""
		empty = set()
		return [ i for i in lst if not (i in empty or empty.add(i))]
		
	def __repr__(self):
		return "<Parser Object: Code = %s>"%self.code
		
	def __len__(self):
		return len(self._rawtext)
		
	def __dict__(self):
		return self.data
		
	def _text(self):
		"""Returns a long string of pulled html text"""
		
		scripts = self.soup.xpath('//script')
		for s in scripts:
			p = s.getparent()
			p.remove(s)
		c = self.soup.xpath("//p")
		c = filter(lambda x: x is not None, [words.text for words in c])
		return " ".join(c)
		
	def _remove_non_ascii(self, string):
		returnstring = "".join(filter(lambda x: ord(x)<128, string))
		if string != returnstring:
			return returnstring
		else: return returnstring
		
	def wordcloud(self, amount=20):
		#Get rid of small and annoying words, leave in meaty goodness
		allwords = re.findall(r'\w+', self._text())
		allwords = filter(lambda x: x.upper() not in BADTAGS, allwords)
		wordcount = collections.Counter([word.upper() for word in allwords])

		#percent = int(len(wordcount) * 0.25)
		try:
			return wordcount.most_common()[:amount]
		except IndexError:
			return wordcount.most_common()
		
	def add(self, key, subkey=None, value=None):
		
		
		if subkey is None:
			if instance(key, list):
				for i in key:
					self.add(i, value="None")
					
			else:
				self.data[key] = "None"
		else:
			if isinstance(subkey, list):
				for i in subkey:
					self.add(key, i, value)
					
			else:	
				self.data[key][subkey] = value
			
	def contains(self, key, subkey=None):
		if subkey is None: 
			return key in self.data
		else: 
			return subkey in self.data[key]
		
	def find_all(self, tag, attribute=None, regex=False):
		"""finds all info by tag"""
		if not regex: 
			if isinstance(attribute, dict):
				return self.soup.findAll(tag, attrs=attribute)
			else:
				return self.soup.findAll(tag)
				
		else: 
			if isinstance(attribute, dict):
				return self.soup.findAll(re.compile(tag), attrs=attribute)
			else:
				return self.soup.find_all(tag)
		
	def find(self, tag, attribute=None, regex=False):
		"""finds first info by tag"""
		if not regex: 
			if isinstance(attribute, dict):
				return self.soup.find(tag, attribute)
			else:
				return self.soup.find(tag)
				
		else: 
			if isinstance(attribute, dict):
				return self.soup.find(re.compile(tag), attribute)
			else:
				return self.soup.find(re.compile(tag))
		
	def lookup(self, key, subkey=None):
	
		try:
			if subkey is None:
				return self.data[key]
			else:
				return self.data[key][subkey]
		
		except KeyError:
			return None
		
	def search(self, keyword):
		for key, value in self.data.iteritems():
			for item in value.viewvalues():
				if keyword in item:
					return key
		
	def set_text(self, text):
		self._rawtext = text
		self.soup = html.fromstring(self._rawtext)
		self.code = hash(self._rawtext)
	
	def tags(self):
		"""Discovers shape of current text data"""
		#Availible tags on webpage
		ls = Set([])
		for tags in self.soup.find_all(True): ls.add(tags.name)
		return ls

	def scrape_directory(self, xpath, directory, name=None):
		if name is None:
			name = hash(xpath)
			
		self.filelist = [name for name in os.listdir(directory)]
		self.amount = len(self.filelist)
		
		print "Preparing to scrape directory: %s"%directory
		print "Discovered %s files"%self.amount
		
		for files in self.filelist:
			self.curfile = files
			self.load("%s\\%s"%(directory, files))
			self.scrape(xpath, name)
		
		
	def scrape(self, xpath, name=None, element=False):
		if name is None:
			name = hash(xpath)
			
		
		x = self.soup.xpath(xpath)
		if len(x) == 1:
			result = unicode(x[0].text).translate(TIDY).strip()
			self.add(self.code, subkey=name, value=result)
		else:
		
			
			for elements in x:
				if element:
					self.add(self.code, subkey=hash(elements), value=elements)

				try:
				
					if elements.text is None:
						continue
					else:
						result = unicode(elements.text).translate(TIDY).strip()
						self.add(self.code, subkey=hash(elements), value=result)
	
				except AttributeError:
					continue
				
		
	def scrape_all(self, tag, attribute=None, reg=False, filename=None):
		if not isinstance(tag, list):
			raise TypeError
			
		else:
			for items in tag:
				self.scrape(items, attribute, reg, filename)
		
	def export_excel(self, filename):
		"""Export to excel, csv, or access database"""
		#will put it in current directory unless given in filename
		extension = ".xls"
		if 'C:' not in filename:
			filename = "%s\\%s%s"%(self.directory, filename, extension)
			
		else:
			filename = "%s%s"%(filename, extension)
		try:
			import xlwt as x
			
			#Set up the fonts and such to prepare for excel exportation
			
			
			headfont = x.Font()
			headfont.name = 'Arial Narrow'
			headfont.colour_index = 0
			headfont.underline = x.Font.UNDERLINE_SINGLE
			
			headfontsize = 13
			headfont.height = headfontsize * 20
			#We go by Twips remember (1/20th of a pixel)
			datafont = x.Font()
			datafont.name = 'Calibri'
			
			headstyle = x.XFStyle()
			headstyle.font = headfont
			
			datastyle = x.XFStyle()
			datastyle.font = datafont
			
			workbook = x.Workbook(encoding='ascii')
			worksheet = workbook.add_sheet('Parser Output')
			
			#Now that the workbook is all ready to go, we can organize our data and write out
			
			def output(lst, row):
				#Helper output function for writing out to excel files
				for i in range(0, len(lst)):
				#	try:
					worksheet.write(row+1, i, lst[i], datastyle)
				#	except UnicodeError:
				#		worksheet.write(row+1, i, "Corrupt Data", datastyle)
					
			
			
			headers = []
			table = []
			
			
		
			#Begin the Export Loop
			#Quick Fill and see all unique title names
			for value in self.data.viewvalues():
				for ids in value.viewkeys():
					if ids not in headers:
						headers.append(ids)
					#add one cell to the row for each value in the dict

			
			for codes in self.data.viewkeys():
				row = []
				for subkeys in headers:
					row.append(self.lookup(codes, subkeys))
					
				table.append(row)
						
				
				#table.append(row)
				
				
			for heads in range(0, len(headers)):
				worksheet.write(0, heads, label=headers[heads], style=headstyle)
			for rowsplace in range(0, len(table)):
				output(table[rowsplace], rowsplace)
				
			workbook.save(filename)
			print "File Exported to -> %s" % filename
			
		

		except AttributeError:
			print "Please install xlwt to use this function"
			
	def export_csv(self, filename):
		"""Outputs comma seperated file"""
		extension = ".csv"
		filename = "%s%s"%(filename, extension)
		headers = []
		returnstring = ""
		for key, value in self.data.iteritems():
			row = ""
			
			for ids, v in value.iteritems():
				if ids not in headers:
					headers.append(ids)
					
				row = "%s, %s"%(row, v)
				
			returnstring = "%s%s\n"%(returnstring, row)
			
		f = open(filename, 'w')
		f.write(self._remove_non_ascii(returnstring))
		f.close()
		
		print "CVS file exported to %s"%filename
				
			
	def blockscrape(self, xpath, name, attr=None):
		
		workinglist = self.soup.xpath(xpath)
	
			
		self._max = len(workinglist)

		
		while len(workinglist) < self._max:
			workinglist.append("None")

			
		
			
		if attr is not None:
			for units in range(0, len(workinglist)):
				try:
					self.add(self.code+units, subkey=name, value=workinglist[units].attrib[attr])
				except AttributeError:
					continue
		else:
		
			for units in range(0, len(workinglist)):
			
				
			
				if isinstance(workinglist[units], str):
					self.add(hash(self.code+units), subkey=name, value=workinglist[units])
				else:
					self.add(hash(self.code+units), subkey=name, value=workinglist[units].text)

				
	def blockscrape2(self, xpath, attributes, columnname, nextpath=None):
		"""Path to Product, attr to pull, name for export"""
		#Nextpath is used to do another xpath within each result element.
		results = self.soup.xpath(xpath)
		amount = len(results)
		
		workingcode = self.code
		
		for ute in attributes:
			for i in map(lambda x: x.attrib[ute], results):
				
				self.add(workingcode, columnname, i)
				workingcode += 1
				
			workingcode = self.code
			if nextpath is not None:
				for i in map(lambda x: x.xpath(nextpath)[self.code-workingcode].text, results):
					#THIS IS SO WRONG....
					self.add(workingcode, nextpath, i)
					workingcode += 1
				
			
			
			#self.add(self.code+hash(ute), subkey=columnname, filter(lambda x: x.attrib[ute])
			
		
		
	def load(self, filename):
		"""From current directory or given"""
		try:
			f = open("%s\\%s"%(self.directory, filename), 'r')
			self.set_text(f.read())
			self.soup = html.fromstring(self._rawtext, 'html.parser')
			self.code = hash(self._rawtext)
			f.close()
		except IOError as ie:
			try:
				f = open(filename, 'r')
				self.set_text(f.read())
				self.soup = html.fromstring(self._rawtext)
				self.code = hash(self._rawtext)
				f.close()
			except IOError as ie:
				print "IOError: Directory not found at %s"%filename
