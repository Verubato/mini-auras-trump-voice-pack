"""Renders the Trump voice pack into src/Sounds/Trump/.

The spell lists, the file naming, and the loudness normalisation all belong to MiniAuras, so this
imports its generator from the sibling checkout rather than restating any of them. Most of the
spoken text comes from there too, but the preview sentence is this pack's own and lives in
PREVIEW_VOICE_TEXT below. What else lives here is the fish.audio side: which model speaks, and the
check that the clip names still match the packs MiniAuras ships.

Run from the repo root with the FISH_AUDIO_TOKEN environment variable set:
    python scripts/GenerateVoicePack.py [--force]

Existing clips are skipped unless --force is given.
"""

import json
import pathlib
import os
import sys
import time
import urllib.error
import urllib.request

REPO = pathlib.Path(__file__).resolve().parent.parent
# MiniAuras is expected beside this repo. Nothing is copied out of it: the spell lists and the
# clip names have one owner, and a stale duplicate here would ship a pack that plays nothing.
MINIAURAS = REPO.parent / "MiniAuras"

if not MINIAURAS.is_dir():
    sys.exit(f"MiniAuras checkout not found at {MINIAURAS}")

sys.path.insert(0, str(MINIAURAS / "scripts"))

import GenerateTtsAudio as base  # noqa: E402

PACK = "Trump"
ENDPOINT = "https://api.fish.audio/v1/tts"
# The fish.audio voice model that speaks every clip.
REFERENCE_ID = "e58b0d7efca34eb38d5c4985e378abcb"
# The endpoint answers 200 to a value it does not recognise and renders with its default instead,
# so a typo here would never be reported.
BACKBONE = "s2.1-pro"
# fish.audio cannot emit Vorbis, so clips arrive as MP3 and MiniAuras' own ffmpeg step converts
# and normalises them into the OGG files the addon ships.
MP3_BITRATE = 128
ATTEMPTS = 5
# Several requests in quick succession draw transient failures, and the run is short enough that
# pacing it costs little.
PAUSE_SECONDS = 0.5
# Anything smaller than this came back as an error page or an empty body, never as speech.
MIN_CLIP_BYTES = 1024
# Spoken when the pack is picked in the dropdown. A real sentence, long enough to judge the
# voice by.
PREVIEW_VOICE_TEXT = "My voice is the best of voices folks, it's a very successful voice."

OUT_DIR = REPO / "src" / "Sounds"
# The pack every generated clip name is checked against.
REFERENCE_PACK = MINIAURAS / "src" / "Sounds" / "TTS" / "David"

# Clips that needed more than one attempt, reported at the end of the run.
retried = []


def build_texts():
    """File stem -> the English text that stem's clip speaks."""
    texts = base.build_texts(base.parse_categories())
    texts["PreviewVoice"] = PREVIEW_VOICE_TEXT

    return texts


def check_against_shipped(stems):
    """A pack whose file names drift from MiniAuras' own plays nothing for the clips that
    differ, and says so nowhere, so the mismatch is caught here instead."""
    if not REFERENCE_PACK.is_dir():
        sys.exit(f"reference pack not found at {REFERENCE_PACK}")

    shipped = {path.stem for path in REFERENCE_PACK.glob("*.ogg")}
    missing = sorted(shipped - stems)
    extra = sorted(stems - shipped)

    if missing or extra:
        sys.exit(f"clip names do not match {REFERENCE_PACK.name}: missing {missing}, extra {extra}")

    print(f"clip names match {REFERENCE_PACK.name}: {len(stems)} stems")


def request_mp3(token, text):
    """One call to fish.audio, raising on anything that is not usable audio."""
    body = json.dumps(
        {
            "text": text,
            "reference_id": REFERENCE_ID,
            "format": "mp3",
            "mp3_bitrate": MP3_BITRATE,
        }
    ).encode()
    request = urllib.request.Request(
        ENDPOINT,
        data=body,
        headers={
            "Authorization": f"Bearer {token}",
            "model": BACKBONE,
            "Content-Type": "application/json",
        },
    )

    with urllib.request.urlopen(request, timeout=120) as response:
        data = response.read()

    # Writing a body this small would ship a clip that plays nothing.
    if len(data) < MIN_CLIP_BYTES:
        raise ValueError(f"got {len(data)} bytes, which is not a clip")

    return data


def fetch_mp3(token, text, label):
    """The raw MP3 bytes fish.audio speaks for one line."""
    for attempt in range(ATTEMPTS):
        try:
            data = request_mp3(token, text)

            if attempt > 0:
                retried.append(label)

            return data
        except urllib.error.HTTPError as error:
            detail = error.read().decode(errors="replace")

            if error.code in (429, 500, 502, 503, 504) and attempt < ATTEMPTS - 1:
                time.sleep(2**attempt)
                continue

            sys.exit(f"{label}: HTTP {error.code}: {detail}")
        except (urllib.error.URLError, ValueError, TimeoutError) as error:
            if attempt < ATTEMPTS - 1:
                time.sleep(2**attempt)
                continue

            sys.exit(f"{label}: {error}")


def render(token, text, path, label):
    temp = path.parent / (path.stem + ".tmp.mp3")
    temp.write_bytes(fetch_mp3(token, text, label))
    # MiniAuras owns the loudness every pack lands at, so its converter does the ffmpeg step.
    base.convert_to_ogg(temp, path)


def main():
    token = os.environ.get("FISH_AUDIO_TOKEN")

    if not token:
        sys.exit("set FISH_AUDIO_TOKEN")

    force = "--force" in sys.argv

    texts = build_texts()

    check_against_shipped(set(texts))

    pack_dir = OUT_DIR / PACK
    pack_dir.mkdir(parents=True, exist_ok=True)

    rendered, reused = 0, 0

    for file_stem in sorted(texts):
        path = pack_dir / f"{file_stem}.ogg"

        if path.exists() and not force:
            reused += 1
            continue

        if rendered > 0:
            time.sleep(PAUSE_SECONDS)

        render(token, texts[file_stem], path, path.name)
        rendered += 1
        print(f"rendered {PACK}/{path.name}")

    print(f"{rendered} clip(s) rendered, {reused} reused")
    print(f"{len(retried)} clip(s) needed a retry" + (f": {retried}" if retried else ""))


if __name__ == "__main__":
    main()
