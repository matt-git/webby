"""Webby was built to quickly crawl, parse, and visualize web data"""

import os
import collections
import urllib2 as ulib
from sets import Set

try:

    from lxml import html
    #from lxml.html.clean import clean_html

except ImportError as error:
    print "Import Error: %s" % error.message

__version__ = '1.3.0'
__all__ = ['ParseQueue', 'Crawler', 'Parser', 'Visualizer']

CLEANUP = dict((ord(char), None) for char in "/\".,;:><?+'!@#$%^&*()-=|][{}`~\\\n\r")
TIDY = dict((ord(char), None) for char in "\n\r\t")

def remove_non_ascii(string):
    """Returns only ASCII string"""
    return "".join(filter(lambda x: ord(x) < 128, string))

def nodupe(lst):
    """removes duplicates!"""
    empty = set()
    return [i for i in lst if not (i in empty or empty.add(i))]

class ParseQueue(object):
    """Queue -> maintains parser feeds of source code"""
    def __init__(self):
        self.feed = []

    def __repr__(self):
        return "<ParseQueue Object: Feed Length %s>"%self.length()

    def __len__(self):
        return self.length()

    def add(self, link, source):
        """Source gets put into feed"""
        self.feed.append((link, source))
        #tuples hold hyperlink and sourcecode
        return len(self.feed)

    def length(self):
        """Return queue size"""
        return len(self.feed)

    def hyperlinks(self):
        """Returns list of hrefs in feed"""
        return [links[0] for links in self.feed]

class Crawler(object):
    """Param: root -> starting point to scrape"""
    def __init__(self, root):
        if "http" not in root:
            raise ValueError

        self.root = root
        self.directory = os.getcwd()
        self.current = ulib.urlopen(self.root)
        self.source = remove_non_ascii("".join(self.current.readlines()))
        self.soup = html.fromstring(self.source)
        self.storedlinks = Set([self.root])
        self.hrefs = self.get_hyperlinks()
        #Starts Crawling from root. Root is crucial to the whole thing

    def __repr__(self):
        """Crawler print call"""
        return '<Crawler Object: URL = %s>'%(self.get_url())

    def __call__(self):
        """Info about self object"""
        print "%s\n"%self.__repr__()
        print "Root: %s\n"%self.root
        print "Directory: %s\n"%self.directory
        print "Amount of Links Crawled: %s\n"%len(self.storedlinks)
        print "Amount of Links to Crawl: %s\n"%len(self.hrefs)
        print "- Useful Socket Information: \n"
        for i in self.info():
            print i

    def info(self):
        """Displays Socket Data"""
        return self.current.info().headers

    def get_url(self):
        """Returns current URL"""
        return self.current.geturl()

    def get_hyperlinks(self):
        """Returns list of relative links"""
        return self.soup.xpath('//a/@href')

    def get_full_links(self):
        """Returns absolute path links"""
        relist = []
        for links in self.soup.xpath('//a/@href'):
            if self.root not in links:
                relist.append("%s%s"%(self.root, links))
            else:
                relist.append(links)

        return relist

    def url_search(self, keywords, url=None):
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

    def open(self, url):
        """Opens up webpage into Crawler"""
        try:
            if ("http://" in url) or ("https://" in url):
                self.current = ulib.urlopen(url)
                self.source = self.current.read()
                self.storedlinks.add(url)
                self.soup = html.fromstring(self.source)

            else:
                raise ulib.URLError

        except ValueError as error:
            print "ValueError: %s"%error.message

        except ulib.HTTPError as error:
            print "Http Error: %s"%error.message

        except ulib.URLError as error:
            print "URL Error: %s"%error.message

    def find_path(self, keyword):
        """Returns xpath for given keyword"""
        pass

    def find(self, xpath):
        """Returns list Elements relevant to XPATH"""
        return self.soup.xpath(xpath)

    def crawl(self, length=10):
        """finds all hyperlinks and crawls and scrapes"""

        queue = ParseQueue()

        count = 0
        for links in self.hrefs:
            if links in self.storedlinks:
                continue
            if count > length:
                return queue

            else:
                self.open(links)
                self.hrefs.remove(links)
                self.hrefs.extend(self.get_hyperlinks())
                self.hrefs = list(Set(self.hrefs))
                queue.add(links, self.source)

            count += 1

        return queue

    def export(self, filename, text=None):
        """Saves source into file"""
        if text == None:
            text = self.source

        if "\\" not in filename:
            filename = "%s\\%s.txt"%(self.directory, filename)
        else:
            filename += '.txt'

        currentfile = open(filename, 'w')
        currentfile.write(remove_non_ascii(text))
        currentfile.close()

        return

class Parser(object):
    """Give the crawler source-code or a ParseQueue object"""
    def __init__(self, text, directory=os.getcwd()):
        self._rawtext = text
        self.directory = directory
        self.data = collections.defaultdict(dict)
        self.code = hash(self._rawtext)
        self._max = 0
        self.titles = Set([])
        self.soup = html.fromstring(self._rawtext, 'html.parser')

    def __repr__(self):
        """Parser print call"""
        return "<Parser Object: Code = %s>"%self.code

    def __len__(self):
        """Returns Len of rawtext"""
        return len(self._rawtext)

    def __dict__(self):
        """Returns Data Dict"""
        return self.data

    def _text(self):
        """Returns a long string of pulled html text"""

        scripts = self.soup.xpath('//script')
        for elements in scripts:
            parent = elements.getparent()
            parent.remove(elements)
        contentpath = self.soup.xpath("//p")
        contentpath = filter(lambda x: x is not None, [words.text for words in contentpath])
        return " ".join(contentpath)

    def wordcloud(self, amount=20):
        """Displays most common words"""
        pass

    def add(self, key, subkey=None, value=None):
        """Adds data to default dict"""

        if subkey is None:
            if isinstance(key, list):
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
        """Checks if key is within data dict"""
        if subkey is None:
            return key in self.data
        else:
            return subkey in self.data[key]

    def lookup(self, key, subkey=None):
        """Looks up data by hash code"""

        try:
            if subkey is None:
                return self.data[key]
            else:
                return self.data[key][subkey]

        except KeyError:
            return None

    def search(self, keyword):
        """finds hash code of given data"""
        for key, value in self.data.iteritems():
            for item in value.viewvalues():
                if keyword in item:
                    return key

    def set_text(self, text):
        """Sets source to new source"""
        self._rawtext = text
        self.soup = html.fromstring(self._rawtext)
        self.code = hash(self._rawtext)

    def tags(self):
        """Discovers shape of current text data"""
        #Availible tags on webpage
        tagset = Set([])

        for tags in self.soup.find_all(True):
            tagset.add(tags.name)

        return tagset

    def scrape_directory(self, xpath, directory, name=None):
        """Pulls data from all files in a directory"""
        if name is None:
            name = hash(xpath)

        filelist = [name for name in os.listdir(directory)]
        amount = len(filelist)

        print "Preparing to scrape directory: %s"%directory
        print "Discovered %s files"%amount

        for files in filelist:
            self.load("%s\\%s"%(directory, files))
            self.scrape(xpath, name)

    def scrape(self, xpath, name=None, element=False):
        """Pulls and stores HTML Elements by XPATH"""
        if name is None:
            name = hash(xpath)

        pathlist = self.soup.xpath(xpath)
        if len(pathlist) == 1:
            result = unicode(pathlist[0].text).translate(TIDY).strip()
            self.add(self.code, subkey=name, value=result)
        else:

            for elements in pathlist:
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
        """Finds all instances of scrape"""
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
            headfont.height = 13 * 20
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
                """Helper output function for writing out to excel files"""
                for i in range(0, len(lst)):
                    worksheet.write(row+1, i, lst[i], datastyle)

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
        for itervalue in self.data.itervalues():
            row = ""

            for ids, values in itervalue.iteritems():
                if ids not in headers:
                    headers.append(ids)

                row = "%s, %s"%(row, values)

            returnstring = "%s%s\n"%(returnstring, row)

        currentfile = open(filename, 'w')
        currentfile.write(remove_non_ascii(returnstring))
        currentfile.close()

        print "CVS file exported to %s"%filename

    def blockscrape(self, xpath, name, attr=None, condition=lambda x: x, linetag=None):
        """Great for scraping tables or multi-valued xpaths"""

        workinglist = self.soup.xpath(xpath)
        self.titles.add(name)

        self._max = len(workinglist)

        while len(workinglist) < self._max:
            workinglist.append("None")
        if attr is not None:
            for units in range(0, len(workinglist)):
                try:
                    self.add(self.code+units, subkey=name, value=workinglist[units].attrib[attr])
                    if linetag is not None:
                        self.add(hash(self.code+units), subkey=hash(name), value=linetag)
                except AttributeError:
                    continue
        else:

            try:
                workinglist = filter(condition, [i.text for i in workinglist if i.text is not None])
                self._max = len(workinglist)
                for units in range(0, len(workinglist)):

                    self.add(hash(self.code+units), subkey=name, value=workinglist[units])

                    if linetag is not None:
                        self.add(hash(self.code+units), subkey=hash(name), value=linetag)

            except AttributeError:
                print "Attribute 'text' non-existant for pulled data"

    def pulltable(self):
        """Extracts HTML Tables"""
        tableheaders = [header.text for header in self.soup.xpath("//th")]
        print tableheaders

    def datawand(self):
        """Discovers and saves useful web data"""
        pass
        #links = filter(lambda x: "%s%s"%x, self.soup.xpath("//a/@href"))
        #tabletitles = [i for i in self.soup.xpath("//th")]
        #tablerows = [i for i in self.soup.xpath("//td")]
        #[self.add(hash(self.code+units),
        #   subkey="Links", value=links[units]) for units in range(0, len(links))]
        #[self.add(hash(self.code+units),
        #   subkey="Titles", value=tabletitles[units]) for units in range(0, len(tabletitles))]
        #[self.add(hash(self.code+units),
        #   subkey="Rows", value=tablerows[units]) for units in range(0, len(tablerows))]

    def load(self, filename):
        """From current directory or given"""
        try:
            currentfile = open("%s\\%s"%(self.directory, filename), 'r')
            self.set_text(currentfile.read())
            self.soup = html.fromstring(self._rawtext, 'html.parser')
            self.code = hash(self._rawtext)
            currentfile.close()
        except IOError:
            try:
                currentfile = open(filename, 'r')
                self.set_text(currentfile.read())
                self.soup = html.fromstring(self._rawtext)
                self.code = hash(self._rawtext)
                currentfile.close()
            except IOError:
                print "IOError: Directory not found at %s"%filename

class Visualizer(object):
    """Generates HTML code and CSS of result tables"""
    def __init__(self, parser):
        self.dataset = parser.data
        self.html = ['<!DOCTYPE html>\n<html>\n<body>\n<table border="10" style="width:50%">\n']
        self.htmlstring = ""
        self.titles = parser.titles
        #This should describe where the html and css files will be stored

    def table(self):
        """Returns html string with dataset printed"""
        self.html.append("<tr>")

        for titles in self.titles:
            self.html.append("<th>%s</th>\n"%titles)

        self.html.append("</tr>")
        for itervalues in self.dataset.itervalues():

            self.html.append("<tr>\n")

            for values in itervalues.values():
                self.html.append('<td>%s</td>\n'%values)

            self.html.append("</tr>\n")

        self.html.append('</table>\n</body>\n</html>')
        self.htmlstring = "".join(self.html)
        return True

    def export_html(self, directory):
        """Saves HTML file to directory"""
        try:
            directory = "%s.html"%directory

            currentfile = open(directory, 'w+')
            currentfile.write(self.htmlstring)
            currentfile.close()
            print "File written out to %s"%directory

        except IOError as error:
            print error.message

    def style_table(self):
        """CSS code to style table"""
