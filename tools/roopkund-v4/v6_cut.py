"""V6 picture: same beats/times as V5 (tight-VO seconds), weak stock shots swapped for Teja's 6 Nov uploads:
real Roopkund photos + DNA-paper figures (Harney et al. 2019, CC BY 4.0), Raj Jat + Homkund temple photos, and Flow clips
(skull in ice, cracked skull, travellers, hail/pilgrims/lab/melt montage). Used by build4 with V6=1."""
C6 = {
 'skull_ice':  'v6/skull_ice.jpg',   'travellers': 'v6/travellers.jpg', 'temple': 'v6/temple.jpg',
 'bones_field':'v6/bones_field.jpg', 'lake_pano':  'v6/lake_pano.jpg',  'rajjat': 'v6/rajjat.jpg',
 'pca_greek':  'v6/pca_greek.jpg',   'dates_800':  'v6/dates_800.jpg',  'dates_1800': 'v6/dates_1800.jpg', 'dates_full': 'v6/dates_full.jpg',
 'cracked':    'v6/researcher_skull.mp4',   # 0-4 s crack on the dome, 6-8 s hand on top
 'storm':      'v6/pilgrims_storm.mp4',     # 0-2 hail falls, 2-4 pilgrims + lightning (~3.0), 4-6 lab drill, 6-8 melt reveals skeleton
 'hail':       'v6/hail_lab_melt.mp4',      # 0-3.3 hailstones smash on rocks (lightning ~1.0)
}
FLOW6 = {'skull_ice', 'travellers', 'cracked', 'storm', 'hail'}
CUT = [
 ('skull_ice', 0.00, 1.35, 1.00, 1.22, .50, 1.0, 'PF'),    # hook: skull melting out of the ice
 ('ice',       1.20, 2.62, 1.00, 1.10, .50, 1.0, 'BS'),
 ('rise',      0.00, 3.85, 1.12, 1.00, .50, 1.0, 'B'),
 ('heap',      0.00, 5.30, 1.06, 1.22, .47, 1.0, 'FS'),    # gives back its dead
 ('lake_pano', 0.00, 6.40, 1.00, 1.10, .50, 1.0, 'B'),     # Roopkund (real photo)
 ('peaks',     1.00, 8.15, 1.00, 1.10, .55, 1.0, 'P'),
 ('face',      1.00, 9.20, 1.00, 1.08, .36, 1.0, 'B'),
 ('bones_field',0.00, 11.10, 1.00, 1.14, .50, 1.0, 'FS'),  # hundreds of skeletons (real photo)
 ('shore',     0.20, 13.30, 1.08, 1.00, .50, 0.8, 'B'),
 ('drone',     6.50, 14.50, 1.00, 1.06, .55, 1.0, 'D'),
 ('valley',    4.00, 16.55, 1.00, 1.08, .50, 0.7, 'NLK'),
 ('ice',       5.00, 18.00, 1.10, 1.22, .50, 1.0, 'PFS'),   # they didn't
 ('storm',     4.10, 19.60, 1.00, 1.10, .50, 1.0, 'G'),     # DNA: tooth drilled in the lab
 ('helixB',    5.30, 22.45, 1.00, 1.12, .50, 1.0, 'GF'),    # 800 AD (Teja: keep the DNA clips, no charts)
 ('helixR',    4.00, 25.10, 1.12, 1.00, .50, 1.0, 'MS'),    # 1800
 ('drone',     10.0, 26.80, 1.00, 1.08, .55, 1.0, 'B'),     # a thousand years apart
 ('rise',      4.20, 28.90, 1.00, 1.10, .50, 1.0, 'D'),     # same frozen lake
 ('travellers',0.00, 30.40, 1.00, 1.12, .50, 1.0, 'GS'),    # and the second group?
 ('valley',    8.00, 31.90, 1.00, 1.10, .50, 1.0, 'BD'),    # closest match
 ('map',       0.00, 34.85, 1.00, 1.00, .50, 1.0, 'G'),
 ('cracked',   0.20, 37.20, 1.00, 1.15, .50, 1.0, 'P'),     # skulls cracked
 ('cracked',   6.00, 38.40, 1.08, 1.00, .50, 1.0, 'B'),     # from above
 ('rajjat',    0.00, 40.50, 1.00, 1.10, .50, 1.0, 'B'),     # villagers' song (Raj Jat)
 ('temple',    0.00, 41.60, 1.05, 1.15, .50, 1.0, 'PL'),    # a goddess (Nanda temple, Homkund)
 ('storm',     2.00, 43.10, 1.00, 1.08, .50, 1.0, 'S'),     # hail hits the pilgrims, lightning
 ('hail',      0.20, 44.20, 1.00, 1.12, .50, 1.0, 'PFS'),   # iron
 ('ice',       0.00, 46.30, 1.00, 1.18, .50, 0.7, 'X'),
 ('storm',     6.00, 48.45, 1.00, 1.12, .50, 0.8, 'X'),     # ice gives back a little more: melt reveals bones
 ('skull_ice', 0.00, 50.30, 1.22, 1.00, .50, 1.0, ''),      # loop back to the hook
]
