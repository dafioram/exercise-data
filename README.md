# exercise-data

Exercise library for [workoutapp](https://github.com/dafioram/workoutapp).
Each exercise is one JSON file in `exercises/`. On every push to `main`, GitHub
Actions validates them, builds `static/exercises.json` + `static/version.json`,
and publishes to GitHub Pages. Installed copies of the app pick up the change on
their next launch with a connection.

## Adding or editing an exercise

1. Add or edit `exercises/<id>_<short_name>.json` (the filename must start with the id).
2. Optionally run `python gen_full_exercises.py --validate` locally.
3. Push to `main` (or open a PR — the validate check runs on PRs).

To hide an exercise without deleting it, set `"active": false`.

## Fields

| Field | Required | Notes |
|---|---|---|
| `id` | yes | Unique integer, matches the filename prefix |
| `name` | yes | |
| `description` | yes | Shown on the timer screen |
| `muscle` | yes | One of `MUSCLES` in `gen_full_exercises.py` |
| `body_part` | yes | `upper`, `lower`, `core` or `full` |
| `type` | yes | `strength`, `cardio`, `plyometric`, `mobility` or `balance` |
| `equipment` | yes | `none` for pure body weight |
| `body_weight` | yes | `true`/`false` |
| `active` | yes | `false` hides it in the app |
| `ab_workout` | yes | `true` includes it in the app's "Core Only" mode |
| `alternate_name` | no | Shown in brackets after the name |
| `variants` | no | Free text |
| `intensity` | no | Integer 1–10 |
| `image` | no | Path to a file in `images/`, e.g. `images/push_ups.png` (leave `""` until the image exists) |
| `link` | no | |

To add a new muscle, body part or type, add it to the allowed lists at the top
of `gen_full_exercises.py`; the validator rejects anything else so typos and
near-duplicates don't split the app's charts.

## Images

Put image files in `images/` and set `"image": "images/<file>"`. The validator
fails if the file is missing, and the deploy publishes `images/` alongside the JSON.

## One-time setup

GitHub Pages must deploy from Actions: **Settings → Pages → Build and deployment
→ Source: GitHub Actions**. `static/` is not committed; the deploy workflow builds
it, and running `python gen_full_exercises.py` locally writes it for previewing.
