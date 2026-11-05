cd "$(dirname "$0")/.."
while pgrep -f get_snake.sh >/dev/null; do sleep 10; done
python3 -u -I work/fetch.py footage/cobra "File:Indian Cobra Naja naja by Dr Raju Kasambe DSCN4991 (16).jpg" "File:Indian Cobra Naja naja by Dr Raju Kasambe DSCN4991 (2).jpg" "File:Indian Cobra Naja naja by Dr Raju Kasambe DSCN4991 (9).jpg" "File:Indian Cobra Naja naja by Dr Raju Kasambe DSCN4991 (12).jpg" "File:Naja-naja-kobra-kopf.jpg" "File:Naja naja - Wilhelma 01.jpg" "File:Naja deity stone sculpture ayBhuvanagiri Fort.jpg" "File:Naga deity stone sculpture ayBhuvanagiri Fort.jpg" "File:Thuravoor temple nagaraja.JPG" "File:Naga prathimas in tirumala .jpg" "File:Sarpa Kavu By Manojk.JPG"
echo COBRADONE
