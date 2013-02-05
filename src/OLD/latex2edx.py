#!/usr/bin/python
#
# File:   latex2edx.py
# Date:   19-Jun-12
# Author: I. Chuang <ichuang@mit.edu>
#
# use plasTeX to convert latex document to edX problem specification language format
#
# 1. convert to XHTML + edX tags using plasTeX
# 2. conert to edX course, with course.xml and problems

import os, sys, string, re, urllib
from plasTeX.TeX import TeX
from plasTeX.Renderers import XHTML
from plasTeX.Renderers.PageTemplate import Renderer as _Renderer
from xml.sax.saxutils import escape, unescape
from lxml import etree
from lxml.html.soupparser import fromstring as fsbs
import csv
import copy

# set the zpts templates path
zptspath = os.path.abspath('render')
os.environ['XHTMLTEMPLATES'] = zptspath

# input and output files
fn = sys.argv[1]
ofn = fn[:-4]+'.xhtml'

#-----------------------------------------------------------------------------

class MyRenderer(XHTML.Renderer):
    '''
    PlasTeX class for rendering the latex document into XHTML + edX tags
    '''

    def processFileContent(self, document, s):
        s = XHTML.Renderer.processFileContent(self,document,s)

        def fix_math(m):
            x = m.group(1).strip()
            x = x.replace(u'\u2019',"'")
            # x = x.encode('utf8')
            x = x.decode('ascii','ignore')
            if len(x)==0:
                return "&nbsp;"
            if x=="\displaystyle":
                return "&nbsp;"
            
            #return '{%% math eq="%s" %%}' % urllib.quote(x,safe="")            
            x = x.replace('\n','')
            x = escape(x)
            #return '{%% math eq="%s" %%}' % x
            return '[mathjaxinline]%s[/mathjaxinline]' % x

        def fix_displaymath(m):
            x = m.group(1).strip()
            x = x.replace(u'\u2019',"'")
            x = x.decode('ascii','ignore')
            if len(x)==0:
                return "&nbsp;"
            if x=="\displaystyle":
                return "&nbsp;"
            x = x.replace('\n','')
            x = escape(x)
            return '[mathjax]%s[/mathjax]' % x

        def do_image(m):
            style = m.group(1)
            sm = re.search('width=([0-9]+)',style)
            if sm:
                width = int(sm.group(1))
            else:
                width = 400
            fn = m.group(2)
            fnsuftab = ['','.png','.pdf','.png','.jpg']
            for k in fnsuftab:
                if os.path.exists(fn+k):
                    if k=='.pdf':		# convert pdf to png
                        os.system('convert -density 400 %s.pdf -scale 400x400 %s.png' % (fn,fn))
                        continue
                    self.imfnset.append(fn+k)
                    # if file doesn't exist in tutor2 web directory, copy it there
                    wwwfn = '%s/%s' % (self.imdir,fn+k)
                    #if not os.path.exists('/home/WWW' + wwwfn):
                    if 1:
                        cmd = 'cp %s /home/WWW%s' % (fn+k,wwwfn)
                        os.system(cmd)
                        print cmd
                        os.system('chmod og+r /home/WWW%s' % wwwfn)
                    return '<img src="%s" width="%d" />' % (wwwfn,width)
                
            return '<img src=NOTFOUND-%s>' % fn

        try:
            s = s.replace(u'\u201d','"')
        except Exception, err:
            print "Error in MyRenderer.processFileContent (fix unicode): ",err

        try:
            s = s.replace(u'\u2014','-')
        except Exception, err:
            print "Error in MyRenderer.processFileContent (fix unicode): ",err

        try:
            s = s.replace(u'\u2013','-')
        except Exception, err:
            print "Error in MyRenderer.processFileContent (fix unicode): ",err

        try:
            s = s.replace('\xe2\x80\x99',"'")
        except Exception, err:
            print "Error in MyRenderer.processFileContent (fix unicode): ",err

        def stripquotes(x):
            if x.startswith('"') and x.endswith('"'):
                return x[1:-1]
            return x

        def copy_attrib(abargs,aname,xml):
            if aname in abargs:
                xml.set(aname,stripquotes(abargs[aname]))

        def do_abox(m):
            '''
            Convert generic abox ('answer box') into one of the edX response types.

            Examples:
            -----------------------------------------------------------------------------
            {% abox expect="float" options=" ","noneType","int","float" %}
            
            <optionresponse>
            <optioninput options="('noneType','int','float')"  correct="int">
            </optionresponse>
            
            -----------------------------------------------------------------------------
            {% abox expect="5.0" %}
            
            <stringresponse answer="Michigan" type="ci">
            <textline size="20" />
            </stringresponse>
            
            -----------------------------------------------------------------------------
            {% abox expect="(3 * 5) / (2 + 3)" cfn="eq" %}
            
            <customresponse cfn="test_add">
            <textline size="40" correct_answer="3"/><br/>
            </customresponse>
            
            {% abox expect="0, 1, 2, 3, 4" %}
            
            -----------------------------------------------------------------------------
            
            <numericalresponse answer="5.0">
            <responseparam type="tolerance" default="5%" name="tol" description="Numerical Tolerance" />
            <textline />
            </numericalresponse>
            
            -----------------------------------------------------------------------------
            '''
            s = m.group(1)
    
            # parse answer box arguments into dict
            xs = "<abox %s/>" % s
            xs = xs.replace(u'\u2019',"'")
            # print "xs=",xs
            aboxxml = fsbs(xs)
            abargs = aboxxml[0].attrib
            #print "aboxxml = ",etree.tostring(aboxxml)
            print "  s=%s, abargs=%s" % (s,abargs)
    
            if 'tests' in abargs:
                abtype = 'externalresponse'
            elif 'type' not in abargs and 'options' in abargs:
                abtype = 'optionresponse'
            elif 'type' in abargs and abargs['type']=='option':
                abtype = 'optionresponse'
            elif 'cfn' in abargs:
                abtype = 'customresponse'
            elif 'type' in abargs and abargs['type']=='string':
                abtype = 'stringresponse'
            else:
                abtype = 'symbolicresponse'	# default
            
            abxml = etree.Element(abtype)
            if abtype=='optionresponse':
                optstr = abargs['options']				# should be double quoted strings, comma delimited
                options = [c for c in csv.reader([optstr])][0]	# turn into list of strings
                options = [x.strip() for x in options]		# strip strings
                if "" in options: options.remove("")
                options = ','.join(["'%s'" % x for x in options])	# string of single quoted strings
                options = "(%s)" % options				# enclose in parens
                oi = etree.Element('optioninput')
                oi.set('options',options)
                oi.set('correct',stripquotes(abargs['expect']))
                abxml.append(oi)
                
            elif abtype=='stringresponse':
                tl = etree.Element('textline')
                if 'size' in abargs: tl.set('size',stripquotes(abargs['size']))
                abxml.append(tl)
                abxml.set('answer',stripquotes(abargs['expect']))
    
            elif abtype=='customresponse':
                abxml.set('cfn',stripquotes(abargs['cfn']))
                tl = etree.Element('textline')
                copy_attrib(abargs,'size',tl)
                abxml.append(tl)
                tl.set('correct_answer',stripquotes(abargs['expect']))
                
            elif abtype=='externalresponse':
                tb = etree.Element('textbox')
                copy_attrib(abargs,'rows',tb)
                copy_attrib(abargs,'cols',tb)
                copy_attrib(abargs,'tests',abxml)
                abxml.append(tb)
                # turn script to <answer> later
    
            elif abtype=='symbolicresponse':
                tl = etree.Element('textline')
                copy_attrib(abargs,'size',tl)
                tl.set('math','1')
                abxml.append(tl)
                copy_attrib(abargs,'options',abxml)
                abxml.set('answer',stripquotes(abargs['expect']))

            s = etree.tostring(abxml,pretty_print=True)
            s = re.sub('(?ms)<html>(.*)</html>','\\1',s)
            # print s
            return s
    
        try:
            #s = re.sub('<math>\$(.*?)\$</math>',lambda m: '{%% math eq="%s" %%}' % urllib.urlencode({'x':m.group(1)}),s)
            s = re.sub('(?s)<math>\$(.*?)\$</math>',fix_math,s)
            s = re.sub(r'(?s)<math>\\begin{equation}(.*?)\\end{equation}</math>',fix_displaymath,s)
            s = re.sub(r'(?s)<displaymath>\\begin{edXmath}(.*?)\\end{edXmath}</displaymath>',fix_displaymath,s)
            s = re.sub(r'(?s)<math>\\\[(.*?)\\\]</math>',fix_displaymath,s)
            s = re.sub(r'(?s)<abox>(.*?)</abox>',do_abox,s)

            # fix for expression checker link
            s = re.sub(r'href="([^"]*/tutor2/go/expcheck2?)"',
                       r'''href="{{TutorRoot}}/tutor2/go/expcheck2" target="expcheck2" onClick="wopen('{{TutorRoot}}/tutor2/go/expcheck2','expecheck2',700,150); return false;"''',
                       s)

            # s = re.sub('(?s)<abox>(.*?)</abox>',r'{% abox \1 %}\n',s)             # abox
            # s = re.sub('(?s)<solution>(.*?)</solution>',r'{% solution %}\n \1 \n{% endsolution %}\n',s)             # solution
            s = re.sub('<includegraphics style="(.*?)">(.*?)</includegraphics>',do_image,s)	# includegraphics
            # s = re.sub('<tutpar></tutpar>','\n<p/>\n\n',s)	# paragraph spacing

        except Exception, err:
            print "Error in MyRenderer.processFileContent: ",err
            raise
        #s = re.compile(r'<math>$(.*)$</math>',re.I).sub('{% math eq="\1" %}',s)

        s = s.replace('<p>','<p>\n')
        s = s.replace('<li>','\n<li>')
        s = s.replace('&nbsp;','&#160;')

        s = s[s.index('<body>')+6:s.index('</body>')]

        XML_HEADER = """<!DOCTYPE HTML PUBLIC "-//W3C//DTD HTML 4.01 Transitional//EN" "http://www.w3.org/TR/html4/loose.dtd">
<html>
<head>
<meta content="text/html; charset=utf-8" http-equiv="content-type" />
</head>
<document>
"""
        XML_TRAILER = """</document></html>"""

        return XML_HEADER + s + XML_TRAILER

    def cleanup(self, document, files, postProcess=None):
        res = _Renderer.cleanup(self, document, files, postProcess=postProcess)
        return res

#-----------------------------------------------------------------------------
# main

if 1:
    # get the input latex file
    latex_str = open(fn).read()
    
    # Instantiate a TeX processor and parse the input text
    tex = TeX()
    tex.ownerDocument.config['files']['split-level'] = -100
    tex.ownerDocument.config['files']['filename'] = ofn
    tex.ownerDocument.config['general']['theme'] = 'plain'
    
    tex.input(latex_str)
    document = tex.parse()
    
    renderer = MyRenderer()
    renderer.imdir = '/tutorexport/8.371'
    renderer.imfnset = []
    
    renderer.render(document)
    
    print "\n======================================== IMAGE FILES"
    print renderer.imfnset
    print "========================================"
    
#--------------------
# read XHTML file in and extract course + problems

xml = etree.parse(ofn)

course = xml.find('//course')	# top-level entry for edX course - should only be one

cnumber = course.get('number')	# course number, like 18.06x
print "Course number: %s" % cnumber
cdir = cnumber
pdir = '%s/problems' % cdir
if not os.path.exists(cdir):
    os.mkdir(cdir)
    if not os.path.exists(pdir):
        os.mkdir(pdir)

# extract problems and put those in separate files
for problem in course.findall('.//problem'):
    pfn = problem.get('name')
    print "  problem %s" % pfn
    pfn = pfn.replace(' ','_').replace('/','').replace(':','_').replace('(','').replace(')','')
    nprob = etree.Element('problem')
    for a in problem.attrib:
        nprob.set(a,problem.get(a))
        problem.attrib.pop(a)
    #open('%s/%s.xml' % (pdir,pfn),'w').write(etree.tostring(problem,pretty_print=True))
    os.popen('xmllint -format -o %s/%s.xml -' % (pdir,pfn),'w').write(etree.tostring(problem,pretty_print=True))
    nprob.set('filename',pfn)
    nprob.set('type','lecture')
    nprob.set('showanswer','attempted')
    nprob.set('rerandomize','never')
    parent = problem.getparent()
    parent.insert(parent.index(problem),nprob)
    parent.remove(problem)

# clean up course tree so it has nothing but allowed tags

psltags = ['course', 'chapter', 'section', 'sequential', 'vertical', 'problem', 'html']
def walk_tree(tree):
    nchildren = [walk_tree(x) for x in tree]
    while None in nchildren: nchildren.remove(None)
    if tree.tag not in psltags:
        # print "    Dropping %s (%s)" % (tree.tag,etree.tostring(tree))
        if len(tree)==0: return None
        for nc in nchildren:
            tree.addprevious(nc)
            # print "      moving up %s" % nc
        tree.getparent().remove(tree)
    return tree

walk_tree(course)

# write out course.xml
#open('%s/course.xml' % cdir,'w').write(etree.tostring(course,pretty_print=True))
os.popen('xmllint -format -o %s/course.xml -' % cdir,'w').write(etree.tostring(course,pretty_print=True))

