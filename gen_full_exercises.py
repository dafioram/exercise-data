import glob
import json
import os
from datetime import date

SOURCE_DIR = "exercises"
OUTPUT_DIR = "static"

exercises = []
errors = []
processed = 0

os.makedirs(OUTPUT_DIR, exist_ok=True)

files = glob.glob(f"{SOURCE_DIR}/*.json")

for f in files:
    try:
        with open(f, "r") as file:
            exercises.append(json.load(file))

        processed += 1

    except Exception as e:
        errors.append({
            "file": f,
            "error": str(e)
        })


# Write exercises.json only if all files loaded successfully
if not errors:
    with open(f"{OUTPUT_DIR}/exercises.json", "w") as out:
        json.dump(exercises, out, indent=2)


    version = {
        "exercisesVersion": date.today().isoformat(),
        "exerciseCount": len(exercises),
        "generated": date.today().isoformat()
    }

    with open(f"{OUTPUT_DIR}/version.json", "w") as out:
        json.dump(version, out, indent=2)


print("--------------------------------")
print("Exercise export complete")
print("--------------------------------")
print(f"Files found:     {len(files)}")
print(f"Files processed: {processed}")
print(f"Exercises:       {len(exercises)}")

if errors:
    print()
    print("FAILED:")
    for err in errors:
        print(f"  {err['file']}: {err['error']}")

    print()
    print("No output written.")
    exit(1)

else:
    print()
    print("Status: SUCCESS")
    print(f"Version: {date.today().isoformat()}")