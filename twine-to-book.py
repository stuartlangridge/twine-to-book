import sys, random, re, codecs
import html5lib # apt-get install python-html5lib

def die(msg):
    print ("This is only a stupid demo. It can't deal with complex "
        "Twine files, for some very low-level definition of the word "
        "'complex'. Soz. What it complained about specifically is this:")
    print msg
    sys.exit(2)

def parseText(text, everything):
    def lookup(m):
        linkname = m.group()[2:-2]
        idx = everything[linkname]["index"]
        return "%s (turn to %s)" % (linkname, idx+1)

    return re.sub(r"\[\[[^]]+\]\]", lookup, text)

if __name__ == "__main__":
    try:
        inp = sys.argv[1]
        outp = sys.argv[2]
    except:
        print "Syntax: %s <input> <output>" % sys.argv[0]
        sys.exit(1)

    with open(inp, "rb") as f:
        dom = html5lib.parse(f, treebuilder="dom")
        twstorydata = dom.getElementsByTagName("tw-storydata")
        if len(twstorydata) != 1:
            die("Couldn't find a tw-storydata element.")
        storydata = twstorydata[0]
        passages_by_name = {}
        startpassage = None
        startname = None
        for p in storydata.getElementsByTagName("tw-passagedata"):
            name = p.getAttribute("name")
            pdata = {"text": ''.join([x.nodeValue for x in p.childNodes])}
            if p.getAttribute("pid") == storydata.getAttribute("startnode"):
                startpassage = pdata
                startname = name
            else:
                passages_by_name[name] = pdata
        # shuffle the passages into some random order
        lst = passages_by_name.items()
        random.shuffle(lst)
        lst.insert(0, (startname, startpassage))
        for i in range(len(lst)):
            lst[i][1]["index"] = i
        passages = dict(lst)
        for name in passages:
            passages[name]["text"] = parseText(passages[name]["text"], passages)
        
        fp = codecs.open(outp, "w", encoding="utf8")
        fp.write("<!doctype html><html><head><meta charset=utf8>")
        fp.write("<title>%s</title></head><body>\n" % storydata.getAttribute("name"))
        fp.write("<!doctype html><html><head><meta charset=utf8><title>%s</title></head><body>")
        lst = passages.items()
        lst.sort(cmp=lambda a,b: cmp(a[1]["index"], b[1]["index"]))
        for name, data in lst:
            fp.write("<h1>%s</h1>\n<p>%s</p>\n" % (data["index"]+1, data["text"]))
        fp.write("</body></html>")
        fp.close()



