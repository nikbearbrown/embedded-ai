## LLM Exercise — Chapter 1: When AI Meets Constrained Hardware

**Project:** TinyML Feasibility Toolkit (Python CLI)
**What you're building this chapter:** The package scaffold, the `Application` dataclass, and a CLI that loads a YAML application spec and reports the four constraint targets.
**Tool:** Claude Code

---

**The Prompt:**

```
Set up a new Python package called `tinyml-feasibility`. By chapter 14 it will take a trained ML model and a target microcontroller spec and produce a deployment-feasibility report grounded in the four-constraint framework (memory, compute, power, real-time).

Scaffold:
- pyproject.toml (PEP 621, Python 3.10+, hatchling backend)
- src/tinyml_feasibility/__init__.py exposing __version__
- src/tinyml_feasibility/cli.py — Click-based CLI
- src/tinyml_feasibility/application.py — frozen Application dataclass with fields: name (str), description (str), latency_budget_ms (int), real_time_class (Literal["soft","firm","hard"]), memory_budget (nested dataclass with flash_kb and sram_kb, both int), power_budget_mw (float), accuracy_floor_pct (float), bom_ceiling_usd (float). Type hints on every field.
- src/tinyml_feasibility/schemas/application.example.yaml — a real worked example for a wildlife acoustic sensor or comparable application
- tests/test_cli.py with three passing tests
- README.md (one paragraph: what the toolkit will do by chapter 14)
- LICENSE (MIT)

CLI commands at this stage:
- `tinyml-feasibility --version` prints the version
- `tinyml-feasibility check-app <path-to-app.yaml>` loads the YAML and prints the four constraint targets in plain English

Tests:
- test_version_prints — exit code 0, stdout matches expected
- test_check_app_loads_example — runs against schemas/application.example.yaml, asserts all four budget values appear in output
- test_check_app_rejects_invalid — feeds malformed YAML, asserts exit code != 0 with a useful error message

Use the src/ layout. Run `pip install -e .` and `pytest` after writing — both must pass before you stop.
```

---

**What this produces:** A pip-installable Python package with `tinyml-feasibility check-app <yaml>` working end-to-end, three passing tests, and a documented YAML schema.

**How to adapt this prompt:**
- *For your own project:* Edit `application.example.yaml` to describe your application. Everything downstream reads from this file.
- *For ChatGPT / Gemini:* Works as-is — both handle multi-file scaffolding well.
- *For Claude Code:* Best fit. Use `--allowed-tools edit,bash`; Claude Code installs and runs `pytest` itself.
- *For a Claude Project:* Put the four-constraint framework and the YAML schema in the system prompt so subsequent chapters don't have to re-explain.

**Connection to previous chapters:** None — chapter 1.

**Preview of next chapter:** Chapter 2 adds the `Target` dataclass (microcontroller specs from datasheets) and a `Constraints` translator that converts `Application` + `Target` into the four-constraint object the rest of the toolkit reasons over.
