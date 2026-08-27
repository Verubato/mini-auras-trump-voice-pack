# MiniAurasVoicePackTrump - bot reference

Version 1.0.1. Interface version 120100. No saved variables, no options UI,
no slash commands.

## What it does

Adds one voice, **Trump**, to the voice pack dropdown in MiniAuras' Alerts
settings. It covers the same announcements the shipped English voices do:
important cooldowns, defensive cooldowns, and enemy debuffs.

The clips are synthetic speech generated with a text to speech model.
Nearly every one speaks a spell name. The rest are the three category names
and one invented preview sentence, and nothing spoken is a quotation. They
are an impression rather than a recording, and the pack carries no
endorsement or political meaning.

The addon is audio plus one registration call. It draws nothing, stores
nothing, and does not change how or when MiniAuras announces.

## How it works

- Ships one OGG per announced spell name under `Sounds\Trump\`, using the
  same file names as MiniAuras' own packs.
- Hands the folder to MiniAuras through
  `MiniAurasApi.v1:RegisterVoicePack`, with no locale tag, so the pack is
  offered on every client.
- MiniAuras is an optional dependency, so it normally loads first. If it has
  not, the addon waits on ADDON_LOADED and registers as soon as the API
  appears.

## Settings

None of its own. The voice is picked in MiniAuras under **Alerts → Voice
pack**, and the choice is saved by MiniAuras.

## Troubleshooting

**"The voice is not in the dropdown."** Check MiniAuras itself is installed
and enabled, and is recent enough to have the voice pack API (5.2.0 and
later). Unlike the translated packs, this one is not hidden on any client,
so a missing entry is never the client locale.

**"The announcement is not what my client calls the spell."** Deliberate for
about fifty names, and identical to what the shipped English voices say.
MiniAuras cuts long names down to the part players react to, and a few ids
are announced on the aura rather than the cast, so the client's name for
them belongs to a different ability.
