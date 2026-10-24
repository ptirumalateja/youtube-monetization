# Bright stars as seen from the wreck site at about 02:20 ship's time, 15 April 1912
# (ship's time ~ GMT-2h58m -> 05:18 UT). Output: unit vectors (x east, y up, z south), mag, B-V.
import json, math
UT = (1912, 4, 15, 5, 18)
LAT, LON = 41.725, -49.947
def jd(y, m, d, h, mi):
    if m <= 2: y -= 1; m += 12
    A = y // 100; B = 2 - A + A // 4
    return int(365.25*(y+4716)) + int(30.6001*(m+1)) + d + B - 1524.5 + (h + mi/60)/24
J = jd(*UT); T = (J - 2451545.0)/36525
gmst = (280.46061837 + 360.98564736629*(J-2451545) + 0.000387933*T*T) % 360
lst = math.radians((gmst + LON) % 360)
la = math.radians(LAT)
out = []
for f in json.load(open('data/stars.6.json'))['features']:
    ra, de = f['geometry']['coordinates']; mag = f['properties']['mag']
    if mag > 6.0: continue
    ra = math.radians(ra % 360) - math.radians(1.23)*0  # precession J2000->1912 ignored (~1 deg)
    de = math.radians(de); H = lst - ra
    alt = math.asin(math.sin(de)*math.sin(la) + math.cos(de)*math.cos(la)*math.cos(H))
    az = math.atan2(-math.sin(H)*math.cos(de), math.cos(la)*math.sin(de) - math.sin(la)*math.cos(de)*math.cos(H))
    if alt < -0.02: continue
    try: bv = float(f['properties']['bv'])
    except: bv = 0.6
    x = math.cos(alt)*math.sin(az); z = -math.cos(alt)*math.cos(az); y = math.sin(alt)
    out += [round(x,4), round(y,4), round(z,4), mag, round(bv,2)]
json.dump(out, open('data/sky1912.json','w'), separators=(',',':'))
print(len(out)//5, 'stars above horizon; LST deg', round(math.degrees(lst),1))
