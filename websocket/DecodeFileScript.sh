Current_dir=$2;
cd $Current_dir;

rm -f ./DecodeFileScript.sh;
FilePath=.;FileList=`ls $FilePath`;ComFile=$1;
for FileName in $FileList;
do
    # cat $FileName >> $ComFile;
    base64 -d $FileName >> ../$ComFile;
    rm -f $FileName;
done
echo Done