# Data dictionary: Spotify Extended Streaming History

One JSON object = one stream (a play of a track / podcast episode). Fields below
reflect the **actual export**.

| Field | Type | Meaning |
|-------|------|---------|
| `ts` | string (ISO 8601, UTC) | When the track **stopped** playing. |
| `platform` | string | Device/OS used (ios, android, windows, cast…). |
| `ms_played` | int | Milliseconds the stream actually played. |
| `conn_country` | string | 2-letter country code of the connection (→ travel detection). |
| `ip_addr` | string | IP address logged. **sensitive info** |
| `master_metadata_track_name` | string\|null | Track name (→ renamed `track`). |
| `master_metadata_album_artist_name` | string\|null | Artist/band/podcast (→ `artist`). |
| `master_metadata_album_album_name` | string\|null | Album name (→ `album`). |
| `spotify_track_uri` | string\|null | spotify:track:<id>, the stable track id. |
| `episode_name` | string\|null | Podcast episode name (null for music). |
| `episode_show_name` | string\|null | Podcast show name. |
| `spotify_episode_uri` | string\|null | spotify:episode:<id>. |
| `audiobook_title` / `audiobook_uri` / `audiobook_chapter_*` | string\|null | Audiobook metadata (mostly null). |
| `reason_start` | string | Why playback started: trackdone, appload, clickrow, fwdbtn, backbtn, playbtn… |
| `reason_end` | string | Why it ended: trackdone, fwdbtn, backbtn, endplay, logout… |
| `shuffle` | bool\|null | Shuffle on? |
| `skipped` | bool\|null | Did the user skip to the next track? |
| `offline` | bool\|null | Played offline? |
| `offline_timestamp` | int\|null | Unix ts of when offline mode was used. |
| `incognito_mode` | bool\|null | Played in a private session? |

## Derived columns (added by helper_scripts.load_streams)

| Column | Meaning |
|--------|---------|
| `minutes` | ms_played / 60000 |
| `year`, `date`, `hour`, `weekday` | parsed from ts |
| `is_track`, `is_podcast` | row type flags |

## Useful definitions

- **"Counts as a stream"**: ms_played >= 30000 (helper_scripts.MIN_LISTEN_MS).
- **Session**: consecutive plays with gaps < 30 min (used for the notebooks' sessionization).
