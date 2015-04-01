#! /opt/python27/bin/python
import sys
import copy
from plasTeX.TeX import TeX

CMD_WANTED = set(['title', 'abstract', 'table'])
KNOWN_CMD = set(['caption', 'hline', 'label', '%', '\\'])
NEWLINE_CMD = set(['\\', 'hline'])

def print_table(table):
    print "".join(["\\begin{table}", table, "\\end{table}\n"])

def print_abstract(abstract):
    print "".join(["\\begin{abstract}", abstract, "\\end{abstract}\n"])

def expand(tok):
    expanded = tok
    if len(tok) > 1:
        if tok == 'active::~':
            expanded = ""
        else:
            expanded = expanded + " "
    if tok in KNOWN_CMD:
        expanded = '\\' + tok
    if tok in NEWLINE_CMD:
        expanded += '\n'
    return expanded

def clean(path):
    doc = TeX(file=path)
    it = doc.itertokens()
    within_table = False
    within_abstract = False
    inlabel = False

    word = ""
    refdict = {}
    window = []
    curref = []
    cur_curl_bracket = 0
    cur_sqr_bracket = 0
    try:
        while True:
            tok = it.next()

            if len(tok.strip()) == 0 and cur_curl_bracket == 0 and cur_sqr_bracket == 0:
                if len(word) > 0:
                    window.append(word)
                    if len(window) > 10:
                        window.pop(0)
                    newcurref = []
                    for label, counter in curref:
                        if counter == 9:
                            refdict[label] += window
                        else:
                            newcurref.append((label, counter+1))
                    curref = newcurref
                    word = ""
            elif len(tok) == 1:
                if tok == '{': cur_curl_bracket += 1
                if tok == '[': cur_sqr_bracket += 1
                if cur_curl_bracket == 0 and cur_sqr_bracket == 0:
                    word += tok
                if tok == '}': cur_curl_bracket -= 1
                if tok == ']': cur_sqr_bracket -= 1

            if tok == "ref":
                label = ""
                while tok != '}':
                    tok = it.next()
                    label += tok
                if not label in refdict:
                    refdict[label] = copy.copy(window)
                else:
                    refdict[label] += window
                curref.append((label, 0))
    except:
        pass

    refout = open(sys.argv[2], 'w')
    doc = TeX(file=path)
    it = doc.itertokens()
    try:
        while True:
            tok = it.next()
            if tok in CMD_WANTED:
                cmd = tok
                content = ""
                while tok != '}':
                    tok = it.next()
                    content += tok
                print "\\" + cmd + content
            elif tok == 'begin' or tok == 'end':
                ctl = tok
                cmd = ''
                while tok != '}':
                    tok = it.next()
                    cmd += tok
                if cmd == '{table}':
                    if not within_table:
                        table_content = ""
                        within_table = True
                    else:
                        print_table(table_content)
                        within_table = False
                elif within_table:
                    table_content += "\{0}{1}".format(ctl, cmd)
                elif cmd == '{abstract}':
                    if not within_abstract:
                        abstract_content = ""
                        within_abstract = True
                    else:
                        print_abstract(abstract_content)
                        within_abstract = False
                elif within_abstract:
                    abstract_content += "\{0}{1}".format(ctl, cmd)
            elif within_table:
                if inlabel:
                    label += tok
                    if tok == '}':
                        inlabel = False
                        refout.write("{0}:{1}\t{2}\n".format(path, label, " ".join(refdict[label])))
                        label = ""
                if tok == 'label':
                    inlabel = True
                    label = ""
                expanded = expand(tok)
                table_content += expanded
            elif within_abstract:
                expanded = expand(tok)
                abstract_content += expanded
    except:
        refout.close()

if __name__ == '__main__':
    if len(sys.argv) != 3:
        print "Usage: test.py tex_file ref_output"
        exit()
    print r"""
\documentclass{article}
\begin{document}
    """
    clean(sys.argv[1])
print r"\end{document}"