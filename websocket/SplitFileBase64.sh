cd $2
FileName=$1;
echo $FileName;
rm -rf ./.$FileName;
TempFile=$FileName.base64;
mkdir .$FileName;
rm -f ./SplitFileBase64.sh;
base64 -w 0 $FileName >> ./.$FileName/$TempFile;
cd ./.$FileName/
split -b 64k $TempFile -d -a 5 $FileName;
cat $TempFile | wc -c
# rm -f $TempFile;
ls | wc -l;