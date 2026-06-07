#!/usr/bin/env python3
"""Local smoke validator for the release solver.

This script intentionally uses a small synthetic smoke case. It does not read
platform interaction artifacts, hidden rows, credentials, or external datasets.
"""

from __future__ import annotations

import importlib.util
import math
import py_compile
from collections import Counter
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SOLVER_PATH = ROOT / "solver.py"

SAMPLE_INPUT = """task_id_list\tcourier_id\ttotal_score\twillingness
T0000\tC000\t12.0\t0.90
T0001\tC001\t13.0\t0.85
T0002\tC002\t14.0\t0.80
T0000,T0001\tC003\t25.0\t0.75
T0001,T0002\tC004\t26.0\t0.70
T0000\tC005\t20.0\t0.50
"""


def parse_input(input_text: str):
    taskset_strings = set()
    edges = set()
    all_tasks = set()
    for raw_line in input_text.splitlines():
        parts = raw_line.strip().split("\t")
        if len(parts) < 4:
            continue
        task_id_list, courier_id, score_text, willingness_text = [part.strip() for part in parts[:4]]
        if (
            task_id_list.lower() == "task_id_list"
            or courier_id.lower() == "courier_id"
            or score_text.lower() == "total_score"
            or willingness_text.lower() == "willingness"
        ):
            continue
        try:
            score = float(score_text)
            willingness = float(willingness_text)
        except ValueError:
            continue
        if not task_id_list or not courier_id or not math.isfinite(score) or not math.isfinite(willingness):
            continue
        task_ids = [task.strip() for task in task_id_list.split(",") if task.strip()]
        if not task_ids:
            continue
        taskset_strings.add(task_id_list)
        edges.add((task_id_list, courier_id))
        all_tasks.update(task_ids)
    return taskset_strings, edges, all_tasks


def strict_validate(input_text: str, result):
    issues = []
    taskset_strings, edges, all_tasks = parse_input(input_text)
    if not isinstance(result, list):
        return False, ["result must be list"]

    task_counter = Counter()
    courier_counter = Counter()
    for index, item in enumerate(result):
        if not isinstance(item, (list, tuple)) or len(item) != 2:
            issues.append(f"item[{index}] must be pair")
            continue
        task_id_list, courier_ids = item
        if not isinstance(task_id_list, str) or task_id_list not in taskset_strings:
            issues.append(f"item[{index}] task_id_list not found in input")
            continue
        if not isinstance(courier_ids, list) or not courier_ids:
            issues.append(f"item[{index}] courier list invalid")
            continue
        task_ids = [task.strip() for task in task_id_list.split(",") if task.strip()]
        if len(task_ids) != len(set(task_ids)):
            issues.append(f"item[{index}] duplicate task inside task_id_list")
        for task_id in task_ids:
            task_counter[task_id] += 1
        for courier_id in courier_ids:
            if not isinstance(courier_id, str):
                issues.append(f"item[{index}] courier id is not str")
                continue
            courier_counter[courier_id] += 1
            if (task_id_list, courier_id) not in edges:
                issues.append(f"item[{index}] missing exact input edge")

    duplicated_tasks = [task for task, count in task_counter.items() if count > 1]
    duplicated_couriers = [courier for courier, count in courier_counter.items() if count > 1]
    if duplicated_tasks:
        issues.append(f"duplicate tasks: {duplicated_tasks}")
    if duplicated_couriers:
        issues.append(f"duplicate couriers: {duplicated_couriers}")
    if set(task_counter) - all_tasks:
        issues.append("output contains task outside input universe")
    return not issues, issues


def load_solver():
    spec = importlib.util.spec_from_file_location("release_solver", SOLVER_PATH)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot import {SOLVER_PATH}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    if not callable(getattr(module, "solve", None)):
        raise RuntimeError("solver.py does not define callable solve")
    return module


def main() -> int:
    py_compile.compile(str(SOLVER_PATH), doraise=True)
    solver = load_solver()
    result = solver.solve(SAMPLE_INPUT)
    ok, issues = strict_validate(SAMPLE_INPUT, result)
    print("py_compile: PASS")
    print(f"solve output items: {len(result) if isinstance(result, list) else 'invalid'}")
    print("strict_validate:", "PASS" if ok else "FAIL")
    if not ok:
        for issue in issues:
            print("-", issue)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
