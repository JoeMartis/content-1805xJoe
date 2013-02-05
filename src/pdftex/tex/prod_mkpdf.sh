#! /bin/csh -f

########################
#Revisions
#  Feb 1, 2013
#    Copied from mkpdf.sh
#########################

set outpath = "../pdf"
set prodpath = "../../../static/pdf"

set ext = "pdf"

if ($#argv < 2) then
   echo "Same as mkpdf.sh except also copies output file to production directory."
   echo "Usage: mkpdf.sh texFileBase [q or a or qa or full or raw] [opt: ptsz]"
   echo "See mkpdf.sh help for details."
   exit 0
endif

mkpdf.sh $argv
cp $outpath/$argv[1].pdf $prodpath/.
echo "Copied $outpath/$argv[1].pdf to $prodpath/."

