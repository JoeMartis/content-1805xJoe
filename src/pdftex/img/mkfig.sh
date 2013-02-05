#! /bin/csh -ef

set outext = "pdf"
set outpath = "."

if ($#argv < 1) then
   echo "Usage: $0 basename"
   echo "  basename is a tex file (leave out the .tex extension)"
   exit 0
endif

set basename = $argv[1]
set headfname = "fighead"

set cmds = "\input{$headfname.tex}\input{$basename.tex}\input{figfoot.tex}"
set myoutput = $outpath/$basename.$outext
pdflatex "$cmds"


mv $headfname.pdf $myoutput
echo ""
echo Output placed in $myoutput

rm $headfname.aux
rm $headfname.log
