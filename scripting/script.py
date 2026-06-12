#!/usr/bin/env python3
import json
import sys


ALLOWED_ACTIONS = (
    ("no-op",),
    ("create",),
    ("update",),
)


def get_changed_attrs(before, after, path=""):
    """Recursively diff two dict/value structures, returning list of dotted paths that changed."""
    changed = []

    if isinstance(before, dict) and isinstance(after, dict):
        keys = set(before.keys()) | set(after.keys())
        for k in keys:
            b = before.get(k, "__MISSING__")
            a = after.get(k, "__MISSING__")
            new_path = f"{path}.{k}" if path else str(k)
            if b != a:
                if isinstance(b, dict) and isinstance(a, dict):
                    changed.extend(get_changed_attrs(b, a, new_path))
                else:
                    changed.append(new_path)
    else:
        if before != after:
            changed.append(path if path else "(root)")

    return changed


def evaluate_resource_change(rc):
    """
    Returns (ok: bool, reasons: list[str]) for a single resource_change entry.
    """
    address = rc.get("address", "<unknown address>")
    change = rc.get("change", {})
    actions = tuple(change.get("actions", []))

    reasons = []

    # Rule 1: action must be no-op, create, or update only.
    if actions not in ALLOWED_ACTIONS:
        reasons.append(
            f"Resource '{address}' has disallowed action(s) {list(actions)}. "
            f"Only 'create' or 'update' (and 'no-op') are permitted - "
            f"deletes/replacements are not allowed."
        )
        return False, reasons

    if actions == ("no-op",) or actions == ("create",):
        return True, []

    # actions == ("update",) -> inspect what changed
    before = change.get("before") or {}
    after = change.get("after") or {}

    changed_paths = get_changed_attrs(before, after)

    for cp in changed_paths:
        if cp.startswith("tags."):
            tag_key = cp[len("tags."):]
            if tag_key != "GitCommitHash":
                reasons.append(
                    f"Resource '{address}' modifies tag '{tag_key}', "
                    f"but only the 'GitCommitHash' tag may be modified."
                )
        elif cp == "tags":
            # whole tags map flagged as changed at top level but no sub-key diff
            # (e.g. tags added/removed entirely) - inspect more precisely
            before_tags = before.get("tags") or {}
            after_tags = after.get("tags") or {}
            tag_diffs = get_changed_attrs(before_tags, after_tags, "tags")
            for td in tag_diffs:
                tag_key = td[len("tags."):]
                if tag_key != "GitCommitHash":
                    reasons.append(
                        f"Resource '{address}' modifies tag '{tag_key}', "
                        f"but only the 'GitCommitHash' tag may be modified."
                    )
        else:
            reasons.append(
                f"Resource '{address}' modifies attribute '{cp}', "
                f"but updates are only permitted to the 'tags.GitCommitHash' attribute."
            )

    return (len(reasons) == 0), reasons


def main():
    if len(sys.argv) < 2:
        plan_path = "tfplan.json"
    else:
        plan_path = sys.argv[1]

    try:
        with open(plan_path, "r") as f:
            plan = json.load(f)
    except FileNotFoundError:
        print(f"ERROR: File not found: {plan_path}")
        sys.exit(2)
    except json.JSONDecodeError as e:
        print(f"ERROR: Failed to parse JSON from {plan_path}: {e}")
        sys.exit(2)

    resource_changes = plan.get("resource_changes", [])

    if not resource_changes:
        print("APPLY ALLOWED")
        print("No resource changes found in plan.")
        sys.exit(0)

    all_ok = True
    all_reasons = []

    for rc in resource_changes:
        ok, reasons = evaluate_resource_change(rc)
        if not ok:
            all_ok = False
            all_reasons.extend(reasons)

    if all_ok:
        print("APPLY ALLOWED")
        print("All changes are 'create' actions, or 'update' actions limited to the "
              "'tags.GitCommitHash' attribute.")
        sys.exit(0)
    else:
        print("APPLY BLOCKED")
        print("The following issue(s) must be addressed before the apply can proceed:")
        for r in all_reasons:
            print(f"  - {r}")
        sys.exit(1)


if __name__ == "__main__":
    main()
