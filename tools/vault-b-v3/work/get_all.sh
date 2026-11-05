cd "$(dirname "$0")/.."
python3 -u -I work/fetch.py footage/temple "File:Sree Padmanabhaswamy Temple 2.jpg" "File:Sree Padmanabhaswamy Temple 3.jpg" "File:Sree Padmanabhaswamy Temple,.jpg" "File:Sree Padmanabhaswamy Temple at night.jpg" "File:Sree Padmanabhaswamy Temple night.jpg" "File:Sree Padmanabhswamy Temple at night, with Padmatheertha Pond in the foreground.jpg" "File:Sree Padmanabhaswamy Temple Lakshadeepam.jpg" "File:Padmanabhaswamy Temple temple tank 03.jpg" "File:TVM Padmanabhaswamy Temple.jpg" "File:Anantha Padmanabha swamy temple.jpg" "File:Sree Padmanabhaswamy Temple 2014 (6).jpg" "File:TVM aps temple.jpg"
python3 -u -I work/fetch.py footage/snake "File:Snake charmer in Jaipur, Rajasthan.webm" "File:Cobra video 2017.webm"

python3 -u -I work/commons.py "Naja naja hood" "spectacled cobra" "Nagaraja Kerala" "naga stone sculpture" "Sarpa Kavu" "gold coins hoard" "pile of gold coins" "gold chain jewellery Kerala" "gold crown jewels" "diamond jewellery antique" "golden idol statue" "riveted iron door" "old iron door texture" "oil lamp flame filetype:video" "diya flame filetype:video" "Nilavilakku" "temple bell Kerala" > work/search2.txt
echo SEARCHDONE
echo ALLDONE
