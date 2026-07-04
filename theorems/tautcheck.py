# SPDX-License-Identifier: Apache-2.0
"""Exhaustive propositional tautology checker — a decision procedure.

For propositional logic, checking a formula under ALL 2^n assignments IS a
proof of tautologyhood (the method is a complete decision procedure), so a
formula verified here earns `machine_checked` honestly for its full scope.

Formulas are JSON values: atoms are strings; connectives are
["not", A], ["and", A, B], ["or", A, B], ["->", A, B], ["iff", A, B].
Fail-closed: an unknown connective raises rather than defaulting.
"""
from __future__ import annotations

from itertools import product


class FormulaError(ValueError):
    """Malformed formula. Fail closed: no verdict is produced."""


def atoms_of(formula) -> list[str]:
    if isinstance(formula, str):
        return [formula]
    if isinstance(formula, list) and formula:
        seen: list[str] = []
        for sub in formula[1:]:
            for a in atoms_of(sub):
                if a not in seen:
                    seen.append(a)
        return seen
    raise FormulaError(f"malformed formula: {formula!r}")


def evaluate(formula, env: dict[str, bool]) -> bool:
    if isinstance(formula, str):
        try:
            return env[formula]
        except KeyError as exc:
            raise FormulaError(f"unbound atom {formula!r}") from exc
    if not isinstance(formula, list) or not formula:
        raise FormulaError(f"malformed formula: {formula!r}")
    op, args = formula[0], formula[1:]
    if op == "not" and len(args) == 1:
        return not evaluate(args[0], env)
    if op == "and" and len(args) == 2:
        return evaluate(args[0], env) and evaluate(args[1], env)
    if op == "or" and len(args) == 2:
        return evaluate(args[0], env) or evaluate(args[1], env)
    if op == "->" and len(args) == 2:
        return (not evaluate(args[0], env)) or evaluate(args[1], env)
    if op == "iff" and len(args) == 2:
        return evaluate(args[0], env) == evaluate(args[1], env)
    raise FormulaError(f"unknown connective/arity: {formula!r}")


def check_tautology(formula) -> dict:
    """Verify under every assignment. Returns a full report; never guesses."""
    names = atoms_of(formula)
    n_checked = 0
    for values in product((False, True), repeat=len(names)):
        env = dict(zip(names, values))
        if not evaluate(formula, env):
            return {"tautology": False, "n_atoms": len(names),
                    "n_assignments_checked": n_checked,
                    "countermodel": env}
        n_checked += 1
    return {"tautology": True, "n_atoms": len(names),
            "n_assignments_checked": n_checked, "countermodel": None}
