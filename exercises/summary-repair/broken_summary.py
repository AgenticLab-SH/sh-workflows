"""INTENTIONALLY INCORRECT synthetic debugging exercise, not a toolkit utility.

Do not use for real task results. Known defect categories are discussed in
FACILITATOR.md after the learner defines expected behavior. Verification NOT_RUN.
"""
import argparse
import csv
import json


def summarize(source, day):
    total = 0.0
    with open(source, encoding="utf-8", newline="") as handle:
        for row in csv.DictReader(handle):
            if row["date"] <= day:
                total += float(row["amount"])
    return {"day": day, "total": round(total, 2)}


def main():
    parser = argparse.ArgumentParser(description="Intentionally incorrect training fixture")
    parser.add_argument("source")
    parser.add_argument("--day", required=True)
    args = parser.parse_args()
    print(json.dumps(summarize(args.source, args.day), ensure_ascii=False))


if __name__ == "__main__":
    main()
