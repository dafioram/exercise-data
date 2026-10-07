"""Validate exercises/*.json and build static/exercises.json + static/version.json.

    python gen_full_exercises.py              # validate and write output
    python gen_full_exercises.py --validate   # validate only (used by CI)

Exits non-zero and writes nothing if any exercise fails validation.
"""
import glob
import hashlib
import json
import os
import re
import sys
from datetime import date

SOURCE_DIR = "exercises"
OUTPUT_DIR = "static"
IMAGE_DIR = "images"

# Allowed values. Add to these lists when introducing a new category,
# so typos and near-duplicates ("hamstring" vs "hamstrings") get caught.
MUSCLES = {
    "back", "chest", "core", "full", "glutes", "hamstrings", "hip abductors",
    "hip adductors", "hip flexors", "legs", "lower back", "obliques", "quads",
    "shoulders", "thighs", "triceps",
}
BODY_PARTS = {"upper", "lower", "core", "full"}
TYPES = {"strength", "cardio", "plyometric", "mobility", "balance"}

# field -> (python type, required)
SCHEMA = {
    "id": (int, True),
    "name": (str, True),
    "alternate_name": (str, False),
    "description": (str, True),
    "muscle": (str, True),
    "body_part": (str, True),
    "type": (str, True),
    "equipment": (str, True),
    "variants": (str, False),
    "intensity": (int, False),
    "body_weight": (bool, True),
    "active": (bool, True),
    "ab_workout": (bool, True),
    # True when you can keep your head up and facing a screen the whole time
    # (standing, seated, on your back or side, planks held in place), without
    # turning away or travelling. Used by the app's "TV Friendly" mode.
    "tv_friendly": (bool, True),
    "image": (str, False),
    "link": (str, False),
}


def validate(path, ex):
    errs = []

    for field, (ftype, required) in SCHEMA.items():
        if field not in ex:
            if required:
                errs.append(f"missing required field '{field}'")
            continue
        # bool is a subclass of int, so check it explicitly
        if not isinstance(ex[field], ftype) or (ftype is int and isinstance(ex[field], bool)):
            errs.append(f"'{field}' must be {ftype.__name__}, got {ex[field]!r}")

    for field in ex:
        if field not in SCHEMA:
            errs.append(f"unknown field '{field}'")

    if errs:
        return errs

    if not os.path.basename(path).startswith(f"{ex['id']}_"):
        errs.append(f"filename must start with the id ('{ex['id']}_')")
    if not ex["name"].strip():
        errs.append("'name' is empty")
    if not ex["description"].strip():
        errs.append("'description' is empty")
    if ex["muscle"] not in MUSCLES:
        errs.append(f"'muscle' {ex['muscle']!r} not in {sorted(MUSCLES)}")
    if ex["body_part"] not in BODY_PARTS:
        errs.append(f"'body_part' {ex['body_part']!r} not in {sorted(BODY_PARTS)}")
    if ex["type"] not in TYPES:
        errs.append(f"'type' {ex['type']!r} not in {sorted(TYPES)}")
    if "intensity" in ex and not 1 <= ex["intensity"] <= 10:
        errs.append("'intensity' must be between 1 and 10")

    image = ex.get("image", "")
    if image:
        if not re.fullmatch(rf"{IMAGE_DIR}/[\w.-]+\.(png|jpe?g|webp|gif|svg)", image):
            errs.append(f"'image' must look like '{IMAGE_DIR}/name.png', got {image!r}")
        elif not os.path.isfile(image):
            errs.append(f"'image' file {image!r} does not exist")

    return errs


def main():
    validate_only = "--validate" in sys.argv[1:]

    files = sorted(glob.glob(f"{SOURCE_DIR}/*.json"))
    exercises = []
    errors = []

    for f in files:
        try:
            with open(f, "r", encoding="utf-8") as file:
                ex = json.load(file)
        except Exception as e:
            errors.append((f, [str(e)]))
            continue

        errs = validate(f, ex)
        if errs:
            errors.append((f, errs))
        else:
            exercises.append(ex)

    ids = {}
    for ex in exercises:
        ids.setdefault(ex["id"], []).append(ex["name"])
    for ex_id, names in ids.items():
        if len(names) > 1:
            errors.append((f"id {ex_id}", [f"duplicate id used by {names}"]))

    print("--------------------------------")
    print(f"Files found:     {len(files)}")
    print(f"Valid exercises: {len(exercises)}")

    if errors:
        print()
        print("FAILED:")
        for f, errs in errors:
            for err in errs:
                print(f"  {f}: {err}")
        print()
        print("No output written.")
        sys.exit(1)

    exercises.sort(key=lambda ex: ex["id"])
    payload = json.dumps(exercises, indent=2, ensure_ascii=False) + "\n"

    # Version is a hash of the content, so any change (even two edits on the
    # same day) produces a new version, and no change keeps the old one.
    version = hashlib.sha256(payload.encode("utf-8")).hexdigest()[:12]

    if validate_only:
        print(f"Status: VALID (version {version})")
        return

    os.makedirs(OUTPUT_DIR, exist_ok=True)
    with open(f"{OUTPUT_DIR}/exercises.json", "w", encoding="utf-8") as out:
        out.write(payload)

    with open(f"{OUTPUT_DIR}/version.json", "w", encoding="utf-8") as out:
        json.dump({
            "exercisesVersion": version,
            "exerciseCount": len(exercises),
            "generated": date.today().isoformat(),
        }, out, indent=2)
        out.write("\n")

    print(f"Status: SUCCESS (version {version})")


if __name__ == "__main__":
    main()
