#! /opt/python27/bin/python
import sys
from bs4 import BeautifulSoup
from lxml import etree

def makerow(row, node, subnode, tag):
    ret = etree.Element(node)
    elemlist = row.find_all(tag)
    for elem in elemlist:
        sub = etree.Element(subnode)
        value = elem.get_text()
        sub.text = value.strip()
        ret.append(sub)
    return ret

def load(path):
    ref = {}
    with open(path) as fin:
        for line in fin:
            label, sentence = line.strip().split('\t')
            label = ":".join(label.split(':')[1:])
            ref[label] = sentence
    return ref

def convert(path):
    refdict = load(path + ".ref")
    with open(path) as fin:
        html = "".join(fin.readlines())
    soup = BeautifulSoup(html)
    xmltable = etree.Element('tables')

    # empty
    xmltable.append(etree.Element("metadata"))
    xmltable.append(etree.Element("authors"))
    xmltable.append(etree.Element("keywords"))

    #article-title
    title = soup.find("title").get_text()
    xmltitle = etree.Element('article-title')
    xmltitle.text = title
    xmltable.append(xmltitle)
    # abstract
    xmlabstract = etree.Element('abstract')
    abstract_node = soup.find('blockquote', {'class' : 'abstract'})
    if abstract_node is not None:
        abstract = abstract_node.get_text()
        xmlabstract.text = abstract
    xmltable.append(xmlabstract)

    for tb_node in soup.findAll('blockquote', {'class' : 'table'}):
        table = etree.Element('table')

        # caption
        caption = etree.Element('caption')
        caption_node = tb_node.find('div', {'class' : 'caption'})
        caption.text = caption_node.get_text().strip()
        table.append(caption)
        caption_node.extract()

        # footenote
        footnote = etree.Element('footnote')
        ftnode = tb_node.find('ul', {'class' : 'itemize'})
        if ftnode is not None:
            footnote.text = ftnode.get_text()
        table.append(footnote)

        # context
        contexts = etree.Element('contexts')
        label = tb_node.find('a')
        if label is not None:
            key = "{" + label["id"] + "}"
            citetext = refdict[key]
            context = etree.Element('context')
            heading = etree.Element('heading')
            citation = etree.Element('citation')
            sentence = etree.Element('sentence')
            sentence.text = citetext
            citation.append(sentence)
            context.append(heading)
            context.append(citation)
            contexts.append(context)
        table.append(contexts)

        group = etree.Element('group')
        table.append(group)
        tabletag = tb_node.find('table')
        rowlist = tabletag.find_all('tr')
        # Assume the first row is header row
        # TODO: Do header recognition
        headers = makerow(rowlist[0], 'headers', 'header', 'td')
        group.append(headers)
        for r in rowlist[1:]:
            row = makerow(r, 'row', 'value', 'td')
            group.append(row)

        xmltable.append(table)

    print etree.tostring(xmltable, pretty_print=True)

if __name__ == '__main__':
    convert(sys.argv[1])
