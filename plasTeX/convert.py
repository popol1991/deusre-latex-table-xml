#! /opt/python27/bin/python
import os
from metadata import Metadata
from bs4 import BeautifulSoup
from xml.etree.ElementTree import Element, tostring
from xml.dom import minidom

ALPHABET = '[a-zA-Z]'
meta = Metadata("../mapping.txt")

def prettify(elem):
    """ Return a pretty-printed XML string
    """
    rough_string = tostring(elem, "utf-8")
    reparsed = minidom.parseString(rough_string)
    return reparsed.toprettyxml(indent=" ")

def makerow(row, node, subnode, tag):
    ret = Element(node)
    elemlist = row.find_all(tag)
    for elem in elemlist:
        sub = Element(subnode)
        value = elem.get_text()
        sub.text = value.strip()
        ret.append(sub)
    return ret

def cleansplit(rowlist):
    headerlist = []
    datalist = []
    databegin = False
    for row in rowlist:
        celllist = row.find_all('td')
        empty = True
        for cell in celllist:
            if len(cell.get_text().strip()) != 0:
                empty = False
                break
        if empty:
            continue

        numerical = True
        # assume the first cell is row header
        for cell in celllist[min(2, len(celllist)):]:
            text = cell.get_text()
            abcount = 0
            nocount = 0
            for ch in text:
                if ch.isalpha():
                    abcount += 1
                elif ch.isnumeric():
                    nocount += 1
            if abcount > nocount:
                numerical = False
                break
        if numerical:
            databegin = True

        if not databegin:
            headerlist.append(row)
        else:
            datalist.append(row)
    return headerlist, datalist

def load(path):
    ref = {}
    with open(path) as fin:
        aid = fin.readline().strip()
        for line in fin:
            info = line.strip().split('\t')
            label = info[0]
            if len(info) == 2:
                sentence = info[1]
            else:
                sentence = ""
            label = ":".join(label.split(':')[1:])
            ref[label] = sentence
    return aid, ref

def convert(path):
    aid, refdict = load(path + ".ref")
    aid = "http://arxiv.org/abs/" + aid
    docmeta = meta.get_meatadata_with_external(aid)
    with open(path) as fin:
        html = "".join(fin.readlines())
    soup = BeautifulSoup(html)
    xmltable = Element('tables')

    # empty
    xmltable.append(Element("metadata"))
    xmltable.append(Element("authors"))
    xmltable.append(Element("keywords"))

    # arXiv ID
    link = Element("link")
    link.text = aid
    xmltable.append(link)

    #article-title
    xmltitle = Element('article-title')
    title = " ".join(docmeta["title"])
    xmltitle.text = title
    xmltable.append(xmltitle)
    # abstract
    xmlabstract = Element('abstract')
    abstract = " ".join(docmeta["description"])
    xmlabstract.text = abstract
    xmltable.append(xmlabstract)
    # subject
    xmlsubject = Element('subject')
    subject = " ".join(docmeta["subject"])
    xmlsubject.text = subject
    xmltable.append(xmlsubject)

    for tb_node in soup.findAll('blockquote', {'class' : 'table'}):
        table = Element('table')

        # caption
        caption = Element('caption')
        caption_node = tb_node.find('div', {'class' : 'caption'})
        if caption_node is not None:
            caption.text = caption_node.get_text().strip()
            caption_node.extract()
        table.append(caption)

        # footenote
        footnote = Element('footnote')
        ftnode = tb_node.find('ul', {'class' : 'itemize'})
        if ftnode is not None:
            footnote.text = ftnode.get_text()
        table.append(footnote)

        # context
        contexts = Element('contexts')
        label = tb_node.find('a')
        if label is not None:
            key = "{" + label["id"] + "}"
            citetext = refdict[key]
            context = Element('context')
            heading = Element('heading')
            citation = Element('citation')
            sentence = Element('sentence')
            sentence.text = citetext
            citation.append(sentence)
            context.append(heading)
            context.append(citation)
            contexts.append(context)
        table.append(contexts)

        group = Element('group')
        table.append(group)
        tabletag = tb_node.find('table')
        if tabletag is None:
            continue
        rowlist = tabletag.find_all('tr')
        # Assume textual if there are alphabet in string
        headerlist, rowlist = cleansplit(rowlist)
        # TODO: Do header recognition
        for r in headerlist:
            headers = makerow(r, 'headers', 'header', 'td')
            group.append(headers)
        for r in rowlist:
            row = makerow(r, 'row', 'value', 'td')
            group.append(row)

        xmltable.append(table)

    return prettify(xmltable)

if __name__ == '__main__':
    for root, dirs, files in os.walk(u"./data/"):
        for f in files:
            if f.endswith(".html"):
                path = os.path.join(root, f)
                fname = os.path.basename(path)
                print path
                with open(path+".xml", "w") as fout:
                    fout.write(convert(path).encode('utf-8'))
