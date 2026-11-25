"""Video finishing shared by the Slow Light Dark reels.

NO_LETTERBOX: Facebook/Instagram flag large areas of pure black at the top or bottom of a vertical video as letterbox
"black borders" and limit reach. Our dark floors and skies hit exactly that. This ffmpeg filter lifts true black to a
deep warm charcoal (Y 16 -> 28, tapering to no change at white) and adds a fine moving grain, so no band is flat black
while the look stays dark. Checked with ffmpeg cropdetect=limit=24: no crop on every frame.
"""
NO_LETTERBOX = "lutyuv=y='val+12*(1-(val-16)/219)':u='val-1':v='val+2',noise=c0s=6:c0f=t+u"
