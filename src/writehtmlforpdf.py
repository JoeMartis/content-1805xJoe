#Quick hack to write html files for pdf


kxmlpath = "18.05x/html/."
kstaticpdfpath = "/static/pdf"

htmlformat = """<html display_name="%(displayname)s">
  <h2>%(displayname)s</h2>
  <p>See <a href="%(urlpath)s/%(fname)s">%(displayname)s</a></p>
</html>
"""

def writehtml(displayname, pdfbase):
    formdct = {'displayname':displayname, 'urlpath':kstaticpdfpath,
               'fname':pdfbase + '.pdf'}
    s = htmlformat % formdct
    fp = open(kxmlpath + "/" + pdfbase + '.xml', 'w')
    fp.write(s)
    fp.close()

if False:
    writehtml("Structure and Policies", "1805-admin")
    writehtml("Goals", "1805-goals")
if True:
    writehtml("Class 1 Review and Examples", "class1-post")
    print "Add more files here."

