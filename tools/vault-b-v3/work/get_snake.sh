cd "$(dirname "$0")/.."
UA="SlowLightReel/1.0 (https://github.com/ptirumalateja/youtube-monetization)"
while pgrep -f "commons.py" >/dev/null; do sleep 10; done
for i in $(seq 1 30); do
  J=$(curl -sS -A "$UA" "https://commons.wikimedia.org/w/api.php?action=query&format=json&titles=File:Snake%20charmer%20in%20Jaipur,%20Rajasthan.webm&prop=imageinfo&iiprop=url")
  U=$(echo "$J" | python3 -c "import json,sys;d=json.load(sys.stdin);print(list(d['query']['pages'].values())[0]['imageinfo'][0]['url'])" 2>/dev/null) && break
  sleep $((20+i*5))
done
echo "url $U"
for i in $(seq 1 30); do
  c=$(curl -sS -A "$UA" -o footage/snake/Snake_charmer_in_Jaipur_Rajasthan.webm -w "%{http_code}" "$U"); echo "try $i $c"
  [ "$c" = 200 ] && break; sleep $((20+i*5))
done
echo SNAKEDONE
