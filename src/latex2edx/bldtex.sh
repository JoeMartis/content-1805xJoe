#! /bin/csh -ef

########################
#Revisions
#  Jan. 1, 2013 JMO
#    Created
#########################

set pdfoutpath = "../18.05x/pdf"
set myrenderoutpath = "../18.05x/myrender"
set imdir = "../18.05x/static/html"
set imurl = "../18.05x/html"
set nogitproboutpath = "../18.05x/problem"
set nogithtmloutpath = "../18.05x/html"
set gitproboutpath = "../../problem"
set githtmloutpath = "../../html"

if ($#argv < 3) then
    echo "Usage: bldtex.sh texFileBase outtype git_or_nogit"
    echo "  texFileBase has no extension (.tex)"
    echo "  outtyp is one of:"
    echo "    xml: calls python mylatex2edx.py "
    echo "        (A thinly processed html file is put in $myrenderoutpath."
    echo "        (The output xhtml file is deleted.)"
    echo "    pdf: calls pdflatex and puts the result in $pdfoutpath/."
    echo "  git_or_nogit is one of:"
    echo "    nogit: put output in non-git tracked directory "
    echo "         xml output goes in one of $nogitproboutpath, $nogithtmloutpath"
    echo "         (The crude html file goes in $myrenderoutpath.)"    
    echo "    git: put output (except crude html) in git tracked directorie"
    echo "         Directories are $gitproboutpath, $githtmloutpath"
    echo "    git_or_nogit has no effect for output type pdf"
    echo "  pdf files go in $pdfoutpath"
    exit 0
endif

set basename = $argv[1]

if ($argv[2] == xml) then
    if ($argv[3] == git) then
       set outprob = $gitproboutpath
       set outhtml = $githtmloutpath
    else if ($argv[3] == nogit) then
       set outprob = $nogitproboutpath
       set outhtml = $nogithtmloutpath
    else
       echo "Unknown choice for git_or_nogit: " $argv[3]
       exit 1
    endif
    set outcrude = $myrenderoutpath
    set myargs = "--problemdir=$outprob --htmldir=$outhtml --crudehtmldir=$outcrude --imdir=$imdir --imurl=$imurl"
    
    python mylatex2edx.py $myargs $basename.tex
    #python latex2edx.py $myargs $basename.tex
    rm $basename.xhtml 
else if ($argv[2] == pdf) then
    pdflatex $basename.tex
    mv $basename.pdf $pdfoutpath/.
    rm $basename.aux
    rm $basename.log
    echo "Made $pdfoutpath/$basename.pdf"
else
  echo "Unknown choice for buildtype: " $argv[2]
  exit 1
endif
