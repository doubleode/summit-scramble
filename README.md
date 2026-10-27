# Summit Scramble

A 6-player pixel platformer race: stomp rivals, team up when you must. Plays on phones and computers. Online play works with no account: the host gets a room code and an invite link.

**Play:** https://doubleode.github.io/summit-scramble/

## Stage editor

STAGE EDITOR on the title screen: pick a biome, paint tiles from the palette (left click paints, right click erases, wheel scrolls), then TEST PLAY. Saved stages appear in the lobby's WORLD option and work online; the host's stage is sent to everyone. SHARE CODE / LOAD CODE trade stages as text.

## Files

- `index.html` is the game GitHub Pages serves. It's built from the files in `source/`, so don't edit it by hand.
- `source/summit-scramble.html` is the main game, the version that also runs as a Claude artifact.
- `source/make_web.py` turns the Claude version into `index.html`. It swaps Claude's room connection for direct phone-to-phone connections (PeerJS / WebRTC), and adds the invite link, the full-screen button and the Home Screen icon.
- `source/peerjs.min.js` is the PeerJS 1.5.4 library (MIT license), built into `index.html`.

## Rebuild after a change

```
python3 source/make_web.py
```

## Full screen on iPhone

Open the game in Safari, tap Share, then **Add to Home Screen**, and launch it from the new icon.
