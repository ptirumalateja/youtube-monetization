// Timeline for "Why can't you tickle yourself?" (Format B). Card times are TARGETS from tickle-reel.md;
// replace them with times derived from the finished voice recording (one file per voice version).
window.TL = {
  fps: 30,
  dur: 32,
  lead: 0.35, // seconds the shadow (the brain's prediction) leads the hand
  cards: [
    { t0: 0.0,  t1: 2.4,  text: "You can't [tickle] yourself.", type: 1.6 },
    { t0: 2.4,  t1: 7.0,  text: "Your brain [knows] first" },
    { t0: 7.0,  t1: 11.0, text: "[Command] + [copy]" },
    { t0: 11.0, t1: 13.5, text: "The copy [predicts]" },
    { t0: 13.5, t1: 16.0, text: "Predicted = [dampened]" },
    { t0: 16.0, t1: 18.5, text: "Less surprise. Less [tickle]." },
    { t0: 18.5, t1: 24.0, text: "No copy. No [prediction]." },
    { t0: 24.0, t1: 28.0, text: "[Surprised] by itself?" },
    { t0: 28.0, t1: 32.0, text: "Your brain already [knows].", type: 1.4 }
  ],
  labels: [
    { t0: 0,    t1: 2.4,  a: "hand, reaching",       b: "one plate, two moments" },
    { t0: 2.4,  t1: 7.0,  a: "two tries",            b: "same move, shadow ahead" },
    { t0: 7.0,  t1: 11.0, a: "inside the arm",       b: "command and copy" },
    { t0: 11.0, t1: 16.0, a: "touch, predicted",     b: "real meets predicted" },
    { t0: 16.0, t1: 18.5, a: "hand, trying",         b: "different spots" },
    { t0: 18.5, t1: 24.2, a: "someone else's hand",  b: "no copy, no shadow" },
    { t0: 24.2, t1: 28.0, a: "hand, reaching",       b: "again" },
    { t0: 28.0, t1: 32.1, a: "hand, reaching",       b: "one plate, two moments" }
  ]
};
