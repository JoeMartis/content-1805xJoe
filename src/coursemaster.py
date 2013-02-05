#################################################
#  writexml.py  
#  python script for generating 18.05x skeleton
#  After using the script you need to move the xml files from root/src/18.05x/.
#  to root/. in the parallel directory structure

# Reference for lxml:  http://lxml.de/tutorial.html

# Revisions
# 12/30/12
#   Created JMO
#  1/27/13 JMO   
#    Gave up on revision list for now: too many small changes
#
# TO DO:
# . Add commandline
# . Allow for single pieces to be written out
#
###############################################
import sys
from lxml import etree
#To handle times
import pytz
from datetime import datetime

#########################
execfile("policy.py")

kchaptergrace = "0 day 0 hours 0 minutes 0 seconds"
kpolicyformatkey = "policyformat"
kbasepolicydict = {"showanswer": "attempted"}
kNEVER = easterntoutctimestring((2015, 1, 1, 0, 1))

gnodeswithpolicies = []

#########################
kstdout = "stdout"

kcoursedir = "18.05x"
kterm = "2013_Spring"
knweeks = 13

kcoursetag = "course"
kchaptertag = "chapter"
kurlnamekey = "url_name"
kvideosequencetag = "videosequence"
ksequentialtag = "sequential"
kverticaltag = "vertical"
kproblemtag = "problem"
khtmltag = "html"
kdisplaynamekey = "display_name"
kformatkey = "format"

kstaticpdftype = "pdf"
khtmltype = "html"

kDisplayBasic = 0
kDisplayTopLevelOnly = 1
kDisplayFull = 2

kweekformat = "Week %d (%d/%d-%d/%d)"  #week #, month/day-month/day
kclassformat = "Class %d (%s %d/%d)" #class # dayOfWeek month/day
kstudioformat = "Studio %d (%s %d/%d)" #studio #  dayOfWeek month/day
knoWritexmltags = [kproblemtag]

#####################
def main():
    #test()
    writealldepth1_xml(kcoursedir, course, kDisplayTopLevelOnly)
    pname = "%s/policies/policy.json" % (kcoursedir,)
    writepolicyfile(pname, gnodeswithpolicies)

#####################
# xml utilities
def makenode(tag, properties):
    nd = etree.Element(tag)
    for k,v in properties.iteritems():
        nd.set(k,v)
    return(nd)

def writexmlfile(fname, rootxml):
    if fname != kstdout:
        fp = open(fname,"w")
    else:
        fp = sys.stdout

    fp.write(etree.tostring(rootxml, pretty_print=True))
    if fname != kstdout:
        fp.close()

####################
def writefulldisplay_xml(basedir, root, doRecurse):
    #Root is a python class Node
    rootxml, fpath  = makexmltree(root, True, doRecurse)
    if basedir == kstdout:
        fname = kstdout
    else:
        fname = "%s/%s" % (basedir, fpath)
    writexmlfile(fname,rootxml)

def writebasic_xml(basedir, root, doRecurse):
    #Root is a python class Node
    rootxml, fpath  = makexmltree(root, False, doRecurse)
    if basedir == kstdout:
        fname = kstdout
    else:
        fname = "%s/%s" % (basedir, fpath)
    writexmlfile(fname,rootxml)

def writealldepth1_xml(basedir, root, displayLevel):
    alltrees = makealldepth1xmltrees(root, displayLevel)
    for t,f in alltrees:
        if basedir == kstdout:
            fname = kstdout
        else:
            fname = "%s/%s" % (basedir, f)
        writexmlfile(fname,t)

def test():
    writefulldisplay_xml(kstdout,course, True)
    print ""

    writebasic_xml(kstdout,course, True)
    print ""

    writebasic_xml(kstdout,week9, True)
    print ""

    writefulldisplay_xml(kstdout,course, False)
    print ""

    writefulldisplay_xml(kstdout,week9, False)
    print ""

    print "****makealldepth1xmltrees***"
    alltrees = makealldepth1xmltrees(course, kDisplayBasic)
    for t,f in alltrees:
        print f, t
        writexmlfile(kstdout, t)
    print ""

####################
# We represent the course using python data structures
class Node(object):
    def __init__(self, parent, tag, url_name="", display_name="", format=""):
        self.tag = tag
        #If bwritexmlfile = False writealldepth1_xml will skip this file
        if tag in knoWritexmltags:
            self.bwritexmlfile = False
        else:
            self.bwritexmlfile = True
        self.url_name = url_name
        self.display_name = display_name
        self.format = format
        self.parent = None
        if parent:
            parent.addchild(self)
        self.children = []
        self.otherproperties = {}
        self.policy = None

    def setwritexmlfile(self, b):
        self.bwritexmlfile = b

    def addchild(self,c):
        if c.parent != None:
            raise Exception("Child already has parent")
        self.children.append(c)
        c.parent = self

    def addproperty(k,v):
        #Should really check that k is not one of the hardwired properties
        self.otherproperties[k] = v

    def addpolicy(self, dct):
        #No check for  missing keys --up to user to find these
        if self.policy == None:
            self.policy = dct
            gnodeswithpolicies.append(self)
        else:
            self.policy = {}
            for k,v in dct.iteritems():
                self.policy[k] = v
            
    def mkbasicxmlnode(self, seturl):
        n = etree.Element(self.tag)
        if seturl:
            if not self.url_name:
                raise Exception("No url_name to set")
            n.set(kurlnamekey, self.url_name)
        return(n)

    def mkfulldisplayxmlnode(self):
        n = etree.Element(self.tag)
        if self.url_name:
            n.set(kurlnamekey,self.url_name)
        if self.display_name:
            n.set(kdisplaynamekey,self.display_name)
        if self.format:
            n.set(kformatkey,self.format)
        for k,v in self.otherproperties.iteritems():
            n.set(k,v)
        return(n)

def makexmltree(root, fullDisplay, doRecurse):
    #we could do this recursively, but I'm not sure about how deep 
    #python allows recursion to go
    if (fullDisplay):
        xmlroot = root.mkfulldisplayxmlnode()
    else:
        xmlroot = root.mkbasicxmlnode(False) #Root doesn't get a url_name
    
    #the filepath (from the root directory) is tag/url_name.xml
    if not root.url_name:
        raise Exception("Can't make filepath without url_name")
    fpath = "%s/%s.xml" % (root.tag, root.url_name)

    nodelst = [(root,xmlroot)]
    while nodelst:
        par,xmlpar = nodelst[0]
        for ch in par.children:
            if (fullDisplay):
                xmlch = ch.mkfulldisplayxmlnode()
            else:
                xmlch = ch.mkbasicxmlnode(True) #children all get url_name
            xmlpar.append(xmlch)
            if doRecurse: #Build tree beyond depth 1
                nodelst.append((ch,xmlch))
        del nodelst[0]
    return(xmlroot,fpath)

def makealldepth1xmltrees(root, displayLevel):
    allxmltrees = []

    nodelst = [root]
    while nodelst:
        par = nodelst[0]
        del nodelst[0]
        #the filepath (from the root directory) is tag/url_name.xml
        if not par.url_name:
            raise Exception("Can't make filepath without url_name")
        fpath = "%s/%s.xml" % (par.tag, par.url_name)

        if displayLevel in [kDisplayFull, kDisplayTopLevelOnly]:
            xmlpar = par.mkfulldisplayxmlnode()
        else:
            xmlpar = par.mkbasicxmlnode(True) #children all get url_name
        for ch in par.children:
            if displayLevel == kDisplayFull:
                xmlch = ch.mkfulldisplayxmlnode()
            else:
                xmlch = ch.mkbasicxmlnode(True) #children all get url_name
            xmlpar.append(xmlch)
            if ch.bwritexmlfile:
                nodelst.append(ch)
        allxmltrees.append((xmlpar,fpath))
    return(allxmltrees)

class HTMLFileNode(Node):
    #For pointing to static pdf files
    def __init__(self, parent, ftype, url_name="", display_name="", format=""):
        #Note use of khtmltag
        super(HTMLFileNode,self).__init__(parent, khtmltag, url_name, 
                                     display_name, format)
        #writexmlfile() can't do this, we'll do it ourselves
        self.setwritexmlfile(False)
        self.ftype = ftype

        #RED_FLAG: a side effect of this call is writing the html file
        if self.ftype == kstaticpdftype:
            self.writepdfhtml()
        self.writefiletypexml()

    def writepdfhtml(self):
        basedir = kcoursedir
        ext = "html"
        fname = "%s/%s/%s.%s" % (basedir, self.tag,self.url_name, ext)
            
        sformat = """<html display_name="%(display_name)s">
<h2>%(display_name)s</h2>
<p>See <a href="/static/pdf/%(url_name)s.pdf">%(display_name)s</a></p>
</html>
"""
        dct = {"display_name":self.display_name, 
               "url_name":self.url_name}
        s = sformat % dct
        fp = open(fname, "w")
        fp.write(s)
        fp.close()

    def writefiletypexml(self):
        basedir = kcoursedir
        ext = "xml"
        fname = "%s/%s/%s.%s" % (basedir, self.tag,self.url_name, ext)
        if self.ftype in [khtmltype, kstaticpdftype]:
            assetext = "html"
        else:
            raise Exception("Unknown ftype")
        s = """<html filename="%s.%s" display_name="%s"/>
""" % (self.url_name,assetext, self.display_name)
        fp = open(fname, "w")
        fp.write(s)
        fp.close()

#####################
# Here's the entire course skeleton
course = Node(None, kcoursetag, kterm, "18.05x Spring 2013", "")

if False:
    addIkeExamples()

#Individual weeks
chaptag = kchaptertag
stag = ksequentialtag

#-----------------
overview = Node(course, chaptag, "Overview", "Information, Policies and Goals", "")
overview.addpolicy({"start":easterntoutctimestring((2013,2,4,12,1)),
                    "graceperiod":kchaptergrace,
                    "showanswer":"attempted"})
a1 = HTMLFileNode(overview, khtmltype, '1805-admin', 'Course Structure',"")
a2 = HTMLFileNode(overview, khtmltype, '1805-collaboration', 
                  'Collaboration and Academic Integrity',"")
a3 = HTMLFileNode(overview, khtmltype, '1805-clickers-and-matlab', 
                  'Clickers and Matlab',"")
a4 = HTMLFileNode(overview, khtmltype, '1805-goals', 'Goals',"")
a5 = HTMLFileNode(overview, khtmltype, '1805calendar', '18.05 Calendar',"")

#-----------------
wlab = kweekformat % (1, 2,5,2,8)
week1  = Node(course, chaptag, "week1", wlab, "")
week1.addpolicy({"start":easterntoutctimestring((2013,2,5,0,1)), 
                 "graceperiod":kchaptergrace,
                 "showanswer":"attempted"})
clab = kclassformat %(1,'T',2,5)
class1 = Node(week1, stag, "class1", clab,  
              "Introduction; counting")
class1.addpolicy({"start":easterntoutctimestring((2013,2,5,10,0))})
c1_intro = HTMLFileNode(class1, kstaticpdftype,"class1-intro", 
                       "Introduction","")
c1_count = HTMLFileNode(class1, kstaticpdftype,"class1-counting", 
                       "Counting","")

clab = kclassformat %(2,'R',2,7)
class2 = Node(week1, stag, "class2", clab,
              "Install Matlab; probability basics")
class2.addpolicy({"start":easterntoutctimestring((2013,2,5,10,0))})
#class2.addpolicy({"due":easterntoutctimestring((2013,2,7,12,30))})
c1 = HTMLFileNode(class2, khtmltype, "1805class1_reminder", 
                  "Reminder", "")
c2 = Node(class2, kverticaltag, "1805installmatlab", "Install Matlab","")
c21 = HTMLFileNode(c2, khtmltype, "1805installmatlab", "Install Matlab", "")
c22 = Node(c2, kproblemtag, "1805installmatlabquest", "", "")
c3 = HTMLFileNode(class2, kstaticpdftype, "class2-prep", 
                  "Probability basics", "")
c4 = Node(class2, kproblemtag, "c1-rq1", "Reading questions for class 1", "")
c5 = Node(class2, kproblemtag, "c2-rq1", "Reading questions for class 2", "")

slab = kstudioformat % (1,'F',2,8)
studio1 = Node(week1, stag, "studio1", slab, 
               "Diagnostic; Matlab, simulation")
studio1.addpolicy({"start":easterntoutctimestring((2013,2,7,14,0))}) 

#-----------------
wlab = kweekformat % (2, 2,11,2,15)
week2  = Node(course, chaptag, "week2", wlab, "")
week2.addpolicy({"start":kNEVER, 
                 "graceperiod":kchaptergrace,
                 "showanswer":"attempted"})
clab = kclassformat % (3,'T',2,12)
class3 = Node(week2, stag, "class3", clab,  
              "Conditional probability, Bayes' Theorem")

clab = kclassformat % (4,'R',2,14)
class4 = Node(week2, stag, "class4", clab,  
              "Discrete random variables")

slab = kstudioformat % (2,'F',2,15)
studio2 = Node(week2, stag, "studio2", slab,  
               "Simulation; Bayes with known priors")

#-----------------
wlab = kweekformat % (3, 2,19,2,22)
week3  = Node(course, chaptag, "week3", wlab, "")
week3.addpolicy({"start":kNEVER, 
                 "graceperiod":kchaptergrace,
                 "showanswer":"attempted"})
clab = kclassformat % (5,'R',2,21)
class5 = Node(week3, stag, "class5", clab,  
              "Continuous R.V.; central limit theorem")

slab = kstudioformat % (3,'F',2,22)
studio3 = Node(week3, stag, "studio3", slab,  
               "Central limit theorem, law of large numbers")

#-----------------
wlab = kweekformat % (4, 2,25,3,1)
week4  = Node(course, chaptag, "week4", wlab, "")
week4.addpolicy({"start":kNEVER, 
                 "graceperiod":kchaptergrace,
                 "showanswer":"attempted"})
clab = kclassformat % (6,'T',2,26)
class6 = Node(week4, stag, "class6", clab,  
              "Joint variables, covariance and correlation")

clab = kclassformat % (7,'R',2,28)
class7 = Node(week4, stag, "class7", clab,  
              "Linear Regression")

slab = kstudioformat % (4,'F',3,1)
studio4 = Node(week4, stag, "studio4", slab,  
               "Correlation; linear regression")

#-----------------
wlab = kweekformat % (5, 3,4,3,8)
week5  = Node(course, chaptag, "week5", wlab, "")
week5.addpolicy({"start":kNEVER, 
                 "graceperiod":kchaptergrace,
                 "showanswer":"attempted"})
clab = kclassformat % (8,'T',3,5)
class8 = Node(week5, stag, "class8", clab,  
              "Review")

clab = kclassformat % (9,'R',3,7)
class9 = Node(week5, stag, "class9", clab,  
              "Exam 1")

clab = kclassformat % (10,'F',3,8)
class10 = Node(week5, stag, "class10", clab,  
               "Introduction to statistics")

#-----------------
wlab = kweekformat % (6, 3,11,3,15)
week6  = Node(course, chaptag, "week6", wlab, "")
week6.addpolicy({"start":kNEVER, 
                 "graceperiod":kchaptergrace,
                 "showanswer":"attempted"})
clab = kclassformat % (11,'T',3,12)
class11 = Node(week6, stag, "class11", clab,  
               "Bayesian updating: discrete priors")

clab = kclassformat % (12,'R',3,14)
class12 = Node(week6, stag, "class12", clab,  
               "Bayesian updating: continuous priors")

slab = kstudioformat % (5,'F',3,15)
studio5 = Node(week6, stag, "studio5", slab,  
               "Bayesian updating")

#-----------------
wlab = kweekformat % (7, 3,18,3,22)
week7  = Node(course, chaptag, "week7", wlab, "")
week7.addpolicy({"start":kNEVER, 
                 "graceperiod":kchaptergrace,
                 "showanswer":"attempted"})
clab = kclassformat % (13,'T',3,19)
class13 = Node(week7, stag, "class13", clab,  
               "Choosing priors; credible intervals")

clab = kclassformat % (14,'R',3,21)
class14 = Node(week7, stag, "class14", clab,  
               "Finish Bayes")

slab = kstudioformat % (6,'F',3,22)
studio6 = Node(week7, stag, "studio6", "Studio 6",  
               "Bayesian inference")

#-----------------
wlab = kweekformat % (8, 4,2,4,5)
week8  = Node(course, chaptag, "week8", wlab, "")
week8.addpolicy({"start":kNEVER, 
                 "graceperiod":kchaptergrace,
                 "showanswer":"attempted"})
clab = kclassformat % (15,'T',4,2)
class15 = Node(week8, stag, "class15", clab,  
               "Confidence intervals")

clab = kclassformat % (16,'R',4,4)
class16 = Node(week8, stag, "class16", clab,  
               "Confidence intervals continued")

slab = kstudioformat % (7,'F',4,5)
studio7 = Node(week8, stag, "studio7", slab,  
               "Confidence intervals")

#-----------------
wlab = kweekformat % (9, 4,9,4,12)
week9  = Node(course, chaptag, "week9", wlab, "")
week9.addpolicy({"start":kNEVER, 
                 "graceperiod":kchaptergrace,
                 "showanswer":"attempted"})
clab = kclassformat % (17,'T',4,9)
class17 = Node(week9, stag, "class17", clab,  
               "Bayesian vs. frequentist methods")

clab = kclassformat % (18,'R',4,11)
class18 = Node(week9, stag, "class18", clab,  
               "Bootstrapping")

slab = kstudioformat % (8,'F',4,12)
studio8 = Node(week9, stag, "studio8", slab,  
               "Bootstrapping")

#-----------------
wlab = kweekformat % (10, 4,16,4,19)
week10 = Node(course, chaptag, "week10", wlab, "")
week10.addpolicy({"start":kNEVER, 
                  "graceperiod":kchaptergrace,
                  "showanswer":"attempted"})
clab = kclassformat % (19,'R',4,18)
class19 = Node(week10, stag, "class19", clab,  
               "Review")

clab = kclassformat % (20,'F',4,19)
class20 = Node(week10, stag, "class20", clab,  
               "Exam 2")

#-----------------
wlab = kweekformat % (11, 4,23,4,26)
week11 = Node(course, chaptag, "week11", wlab, "")
week11.addpolicy({"start":kNEVER, 
                  "graceperiod":kchaptergrace,
                  "showanswer":"attempted"})
clab = kclassformat % (21,'T',4,23)
class21 = Node(week11, stag, "class21", clab,  
               "Significance testing")

clab = kclassformat % (21,'R',4,25)
class22 = Node(week11, stag, "class22", clab,  
               "t and chi-square tests")

slab = kstudioformat % (8,'F',4,26)
studio9 = Node(week11, stag, "studio9", slab,  
               "Significance testing")

#-----------------
wlab = kweekformat % (12, 4,29,5,3)
week12 = Node(course, chaptag, "week12", wlab, "")
week12.addpolicy({"start":kNEVER, 
                  "graceperiod":kchaptergrace,
                  "showanswer":"attempted"})
clab = kclassformat % (23,'T',4,30)
class23 = Node(week12, stag, "class23", clab,  
               "Distributes related to normal")

clab = kclassformat % (24,'R',5,2)
class24 = Node(week12, stag, "class24", clab,  
               "What NHST does and does not mean")

slab = kstudioformat % (10,'F',5,3)
studio10 = Node(week12, stag, "studio10", slab,  
                "NHST and Bayes")

#-----------------
wlab = kweekformat % (13, 5,7,5,10)
week13 = Node(course, chaptag, "week13", wlab, "")
week13.addpolicy({"start":kNEVER, 
                  "graceperiod":kchaptergrace,
                  "showanswer":"attempted"})
clab = kclassformat % (25,'T',5,7)
class25 = Node(week13, stag, "class25", clab,  
               "TBD")

clab = kclassformat % (26,'R',5,9)
class26 = Node(week13, stag, "class26", clab,  
               "TBD")

slab = kstudioformat % (11,'F',5,10)
studio11 = Node(week13, stag, "studio11", slab,  
                "TBD")

#-----------------
wlab = kweekformat % (14, 5,13,5,16)
week14 = Node(course, chaptag, "week14", wlab, "")
week14.addpolicy({"start":kNEVER, 
                  "graceperiod":kchaptergrace,
                  "showanswer":"attempted"})
clab = kclassformat % (27,'T',5,14)
class27 = Node(week14, stag, "class27", clab,  
               "Review")

clab = kclassformat % (28,'R',5,16)
class28 = Node(week14, stag, "class28", clab,  
               "Review")

#-----------------
def addIkeExamples():
    #For now we keep the sample assets Ike included
    #The start date is set to Jan 1, 2015.
    p = course
    t = kchaptertag
    sampvidseq = Node(p,t, "sample_videoseq", "Sample Video Sequence", "")
    sampvidseq.addpolicy({"start":kNEVER, 
                          "graceperiod":kchaptergrace,
                          "showanswer":"attempted"})
    samplessonseq = Node(p,t, "sample_lessonseq", "Sample Lesson Sequence", "")
    samplessonseq.addpolicy({"start":kNEVER, 
                             "graceperiod":kchaptergrace,
                             "showanswer":"attempted"})
    samphtml = Node(p,t, "sample_htmllessons", "Sample HTML Lessons", "")
    samphtml.addpolicy({"start":kNEVER, 
                        "graceperiod":kchaptergrace,
                        "showanswer":"attempted"})
    sampapplets = Node(p,t, "sample_applets", "Sample Applets", "")
    sampapplets.addpolicy({"start":kNEVER, 
                           "graceperiod":kchaptergrace,
                           "showanswer":"attempted"})
    sampproblemgallery = Node(p,t, "sample_problemgallery", 
                              "Sample Problem Gallery", "")
    sampproblemgallery.addpolicy({"start":kNEVER, 
                                  "graceperiod":kchaptergrace,
                                  "showanswer":"attempted"})
    ikeexamples = Node(p,t, "Ike_examples", "Ike Examples", "")
    ikeexamples.addpolicy({"start":kNEVER, 
                           "graceperiod":kchaptergrace,
                           "showanswer":"attempted"})


    #Don't write the xml for the sequences since those are in Ike's examples
    #Note: the url_names for the sequences are Ike's original names
    t = kvideosequencetag
    p = sampvidseq
    vs1 = Node(p,t, "example_vseq1"); vs1.setwritexmlfile(False)
    p = samplessonseq 
    mt1 = Node(p,t, "Midterm_1"); mt1.setwritexmlfile(False)
    p = samphtml
    lec1 = Node(p,t, "Lecture_1"); lec1.setwritexmlfile(False)
    lec2 = Node(p,t, "Lecture_2"); lec2.setwritexmlfile(False)
    lec3 = Node(p,t, "Lecture_3"); lec3.setwritexmlfile(False)
    p = sampapplets
    t2d = Node(p,t, "tools_2d"); t2d.setwritexmlfile(False)
    t3d = Node(p,t, "tools_3d"); t3d.setwritexmlfile(False)
    t = ksequentialtag
    p = sampproblemgallery
    probtemp = Node(p,t, "Problem_Templates"); probtemp.setwritexmlfile(False)
    testseq = Node(p,t,"Test_Sequence"); testseq.setwritexmlfile(False)
    
    #We write these example xml files because we generated them
    t = kvideosequencetag
    p = ikeexamples
    lec1Q2 = Node(p,t, "1806example0")
    l1 = Node(lec1Q2,kproblemtag, "lec1Q2")

######################
if __name__=="__main__":
    main()

######################
