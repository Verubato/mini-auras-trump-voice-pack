# MiniAurasVoicePackTrump

A Trump impression voice pack for [MiniAuras](https://www.curseforge.com/wow/addons/miniauras).

MiniAuras can call out important and defensive cooldowns as they land. This addon adds one more
voice to that list, speaking the same English spell names the shipped voices do.

The clips are synthetic speech, generated with a text to speech model. They are an impression,
not a recording of anyone. Nearly every clip speaks a World of Warcraft spell name. The rest are
the three category names the alerts use, and one invented sentence that plays when the voice is
picked. Nothing spoken is a quotation of anything anyone has said. The pack is offered for
entertainment. It is not an endorsement of any person or political position, and it is not
connected to or approved by anyone it imitates.

[Discord](https://discord.gg/UruPTPHHxK)

## Install

Install MiniAuras first, then this. The voice appears in **MiniAuras → Alerts → Voice pack**
alongside the voices MiniAuras ships. It speaks English, so it is offered on every client.

## Download

Available on [CurseForge](https://www.curseforge.com/wow/addons/miniauras-trump-voice-pack).

## Regenerating the clips

The clips are baked audio, one file per announced spell name, rendered with fish.audio. The
script expects a MiniAuras checkout beside this one, because the spell lists, most of the spoken
text, and the clip file names belong to it. The exception is the preview sentence the voice speaks
when it is picked, which lives in the script here.

```
python scripts/GenerateVoicePack.py            # renders whatever is missing
python scripts/GenerateVoicePack.py --force    # re-renders everything
```

It needs `FISH_AUDIO_TOKEN` and ffmpeg on the path. It refuses to run if its clip names have
drifted from the packs MiniAuras ships, since a mismatched name is a clip that silently never
plays.

What the voice says is not always the client's name for the spell. MiniAuras cuts the long names
down to the part a player reacts to, and corrects the handful of ids whose aura carries another
ability's name. This pack speaks whatever MiniAuras' own English voices speak, so it shortens
nothing of its own.
