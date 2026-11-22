"""Apply manual scores (one judgment per item) to the incremental results file."""
import json
import os

RFILE = r"<REPO>\closed-qa\browsecomp-hard-10\qwen36-unsloth-results.json"

# Manual judgments against each item's `key`. Partial credit is never given.
JUDGMENTS = {
    "H01": (True, "All three parts present: Chelsea, Cole Palmer (opening two goals), Enzo Maresca."),
    "H02": (True, "All three parts present: Google Quantum AI, Qolab, John Clarke."),
    "H03": (True, "Final answer gives Josephson junction and John Clarke; correct despite an earlier confused mention of Serge Haroche."),
    "H04": (True, "Compagnoni and Tomba, Norway, 18 gold - all parts present."),
    "H05": (False, "Wrong closing venue (Oval Lingueglia instead of Verona Arena) and wrong cauldron lighters (Goggia/Pellegrino instead of Compagnoni/Tomba); only the 6-22 Feb dates are right."),
    "H06": (True, "Belem Mission to 1.5, Andre Correa do Lago, 2023/COP28 - all parts present."),
    "H07": (True, "Norway and 41 total medals present."),
    "H08": (True, "Paris Saint-Germain; Cole Palmer two goals; Joao Pedro one goal - all parts present."),
    "H09": (True, "Qolab and Maresca both present."),
    "H10": (True, "San Siro and Brian Josephson both present."),
}


def main():
    with open(RFILE, "r", encoding="utf-8") as f:
        data = json.load(f)
    for item in data["items"]:
        correct, reason = JUDGMENTS[item["id"]]
        item["correct"] = correct
        item["score_reason"] = reason
        item["score"] = 1 if correct else 0
        item["flag"] = (
            "possibly guessed / leaked intermediate"
            if item["tool_call_count"] < item["min_turns"]
            else ""
        )
    data["total_score"] = sum(i["score"] for i in data["items"])
    data["n_items"] = len(data["items"])
    tmp = RFILE + ".tmp"
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
    os.replace(tmp, RFILE)
    print("total", data["total_score"], "/", data["n_items"])
    for i in data["items"]:
        print(i["id"], "correct" if i["correct"] else "INCORRECT",
              "tools", i["tool_call_count"], "min", i["min_turns"],
              "flag", repr(i["flag"]))


if __name__ == "__main__":
    main()
