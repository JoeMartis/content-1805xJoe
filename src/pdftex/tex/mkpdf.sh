#! /bin/csh -f

########################
#Revisions
#  Feb 11, 2012
#    Total revamp to use header.tex and commandline control rather
#    that whichclass.tex etc.
#  Feb 5, 2012
#    Copied from sdm prob
#########################

set outpath = "../pdf"
set ext = "pdf"

if ($#argv < 2) then
   echo "Usage: mkpdf texFileBase [q or a or qa or full or raw] [opt: ptsz]"
   echo "  texFileBase is a tex file (do not include the .tex extension)"
   echo "    q: use myquest sections, skip mysol sections"
   echo "    a: use mysol sections, skip myquest sections"
   echo "    qa: use both myquest and mysol sections"
   echo "    full: use myquest and arg2 from myhide"
   echo "    raw: just run pdflatex and put output in "$outpath"/texFileBase.pdf"
   echo "  Example: $0 ps1 q"
   echo "     This takes ps1.tex and produces "$outpath"/ps1."$ext 
   echo "     This  shows myquest and arg1 in myhide macro and skips the mysol macro."
   echo "  Example: $0.sh ps1 a"
   echo "     This takes ps1.tex and produces "$outpath"/ps1-solutions."$ext 
   echo "     This  shows mysol and arg1 in myhide macro and skips the myquest macro."
   echo "  Example: $0.sh ps1 qa"
   echo "     This takes ps1.tex and produces "$outpath"/ps1-QA."$ext 
   echo "     This  shows mysol and arg1 in myhide macro and skips the myquest macro."
   echo "    $0.sh lec1 full"
   echo "  produces "$outpath"/lec1-full.pdf, which shows arg2 in the myhide macro (and shows myquest, hides mysol)."
   echo ""
   echo "The default font size is 12. You can change it by setting the ptsz argument to 10, 11 or 12. Typical pset size is 11."
   exit 0
endif

set basename = $argv[1]
set outbase = $outpath/$basename
set ptsz = "12pt"
if ($#argv >= 3) then
    if ($argv[3] == "10") then
       set ptsz = "10pt"
    else if ($argv[3] == "11") then
       set ptsz = "11pt"
    else if ($argv[3] == "12") then
       set ptsz = "12pt"
    else
       echo "Unknown point size $argv[3]"
       exit (0)
    endif
endif

if ($argv[2] == "q") then
    set defsI = "\def\myquest{\myquestA} \def\mysol{\mynull} \def\myhide{\myhidehide}"
    set outx = ""
else if ($argv[2] == "a") then
    set defsI = "\def\myquest{\mynull} \def\mysol{\mysolA} \def\myhide{\myhidehide}"
    set outx = "-solutions"
else if ($argv[2] == "qa") then
    set defsI = "\def\myquest{\myquestA} \def\mysol{\mysolA} \def\myhide{\myhidehide}"
    set outx = "-QA"
else if ($argv[2] == "full") then
    set defsI = "\def\myquest{\myquestA} \def\mysol{\mynull} \def\myhide{\myhideshow}"
    set outx = "-full"
else if ($argv[2] == "raw") then
    set outx = ""
else
    echo "Unknown option: $argv[2]"
    exit(0)
endif

set myoutput = $outbase$outx.pdf

if ($argv[2] == "raw") then
    echo ""
    echo "********* Processing of $basename ($argv[2]) **************"
    echo ""
    pdflatex $basename.tex
    mv $basename.pdf $myoutput
    echo "" 
    echo "********* Output placed in $myoutput **************"
    #rm $basename.aux leave so can use \label \ref
    rm $basename.log
else
    set cmds = "\def\ptsz{$ptsz} \input{header.tex} $defsI \input{$basename.tex} \input{footer.tex}"
    echo ""
    echo "********* Processing of $basename ($argv[2]) **************"
    echo ""
    pdflatex "$cmds"
    mv header.pdf $myoutput
    echo "" 
    echo "********* Output placed in $myoutput **************"
    
    #rm header.aux leave so can use \label \ref
    rm header.log
endif

echo ""
echo "*** If you are using labels and refs then you need to run this twice on the file. ***"
