#!/usr/bin/env python3
# run_all_claims.py  --  CC0
# Entry point. Runs all five claims and writes verdicts.
# stdlib only for orchestration; individual claims may need API keys.

import argparse, importlib.util, json, sys, time
from pathlib import Path

HERE = Path(__file__).parent

CLAIMS = {
    "1": ("claim1-age-bias",            "scorer",                "run"),
    "2": ("claim2-reproductive-logic",  "utility_model",         "run"),
    "3": ("claim3-agent-model",         "abm",                   "run"),
    "4": ("claim4-narrative-compression","evaluator",            "run"),
    "5": ("claim5-cross-cultural",      "co_occurrence_analysis","run"),
}


def load_and_run(claim_id, verbose=False):
    folder, module_name, fn_name = CLAIMS[claim_id]
    module_path = HERE / folder / f"{module_name}.py"
    spec = importlib.util.spec_from_file_location(module_name, module_path)
    mod = importlib.util.module_from_spec(spec)
    # add the claim folder to sys.path so relative imports work
    sys.path.insert(0, str(HERE / folder))
    spec.loader.exec_module(mod)
    fn = getattr(mod, fn_name)
    kwargs = {"verbose": verbose} if verbose else {}
    try:
        return fn(**kwargs)
    except TypeError:
        return fn()
    finally:
        sys.path.pop(0)


def main():
    ap = argparse.ArgumentParser(description="Run elder-value claims protocol.")
    ap.add_argument("--claim", choices=list(CLAIMS.keys()),
                    help="Run only this claim (default: all)")
    ap.add_argument("--verbose", "-v", action="store_true")
    ap.add_argument("--parallel", action="store_true",
                    help="Run claims concurrently (uses threading)")
    args = ap.parse_args()

    targets = [args.claim] if args.claim else list(CLAIMS.keys())

    if args.parallel and len(targets) > 1:
        import threading
        verdicts = {}
        threads = []
        lock = threading.Lock()

        def run_one(cid):
            v = load_and_run(cid, args.verbose)
            with lock:
                verdicts[cid] = v

        for cid in targets:
            t = threading.Thread(target=run_one, args=(cid,))
            threads.append(t); t.start()
        for t in threads:
            t.join()
    else:
        verdicts = {}
        for cid in targets:
            print(f"\n{'='*60}")
            print(f"CLAIM {cid}")
            print('='*60)
            verdicts[cid] = load_and_run(cid, args.verbose)

    # summary
    print(f"\n{'='*60}")
    print("SUMMARY")
    print('='*60)
    for cid, v in sorted(verdicts.items()):
        if v:
            status = "SUPPORTED" if v.get("supported") else "FALSIFIED"
            print(f"  Claim {cid}: {status}")

    # write combined verdict
    (HERE / "results_combined.json").write_text(
        json.dumps(verdicts, indent=2, default=str))
    print("\nFull results → results_combined.json")


if __name__ == "__main__":
    main()
