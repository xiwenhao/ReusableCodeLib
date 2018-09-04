cd $2
FileName=$1;
rm -rf ./.$FileName;
TempFile=$FileName.base64;
mkdir .$FileName;
rm -f ./getBase64Size.sh;
base64 -w 0 $FileName >> ./.$FileName/$TempFile;
cd ./.$FileName/
cat $TempFile | wc -c
rm -f $TempFile;