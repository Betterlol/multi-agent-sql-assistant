# Multi-Agent SQL Assistant

Natural language to SQL with Planner/Generator/Verifier agents, schema-linking, and execution safety checks.

## Status
- Stage: bootstrap
- Local repo initialized: yes

## Planned Structure
- \: application source code
- \: automated tests
- \: architecture, milestones, ADRs
- \: helper scripts
- \: CI workflows

## Quick Start
\\Requirement already satisfied: pip in ./.venv/lib/python3.13/site-packages (25.2)

==================================== ERRORS ====================================
_ ERROR collecting github-local-repos/ai-accelerated-dev-lab/tests/test_smoke.py _
ImportError while importing test module '/mnt/e/Git/warehouse/Working/agent/github-local-repos/ai-accelerated-dev-lab/tests/test_smoke.py'.
Hint: make sure your test modules/packages have valid Python names.
Traceback:
/home/YOUKNOWWHO/miniconda3/lib/python3.13/importlib/__init__.py:88: in import_module
    return _bootstrap._gcd_import(name[level:], package, level)
           ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
github-local-repos/ai-accelerated-dev-lab/tests/test_smoke.py:1: in <module>
    from src.main import main
E   ModuleNotFoundError: No module named 'src'
_ ERROR collecting github-local-repos/ecommerce-react-agent/tests/test_smoke.py _
ImportError while importing test module '/mnt/e/Git/warehouse/Working/agent/github-local-repos/ecommerce-react-agent/tests/test_smoke.py'.
Hint: make sure your test modules/packages have valid Python names.
Traceback:
/home/YOUKNOWWHO/miniconda3/lib/python3.13/importlib/__init__.py:88: in import_module
    return _bootstrap._gcd_import(name[level:], package, level)
           ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
github-local-repos/ecommerce-react-agent/tests/test_smoke.py:1: in <module>
    from src.main import main
E   ModuleNotFoundError: No module named 'src'
_ ERROR collecting github-local-repos/multi-agent-sql-assistant/tests/test_smoke.py _
ImportError while importing test module '/mnt/e/Git/warehouse/Working/agent/github-local-repos/multi-agent-sql-assistant/tests/test_smoke.py'.
Hint: make sure your test modules/packages have valid Python names.
Traceback:
/home/YOUKNOWWHO/miniconda3/lib/python3.13/importlib/__init__.py:88: in import_module
    return _bootstrap._gcd_import(name[level:], package, level)
           ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
github-local-repos/multi-agent-sql-assistant/tests/test_smoke.py:1: in <module>
    from src.main import main
E   ModuleNotFoundError: No module named 'src'
_ ERROR collecting github-local-repos/promptops-eval-platform/tests/test_smoke.py _
ImportError while importing test module '/mnt/e/Git/warehouse/Working/agent/github-local-repos/promptops-eval-platform/tests/test_smoke.py'.
Hint: make sure your test modules/packages have valid Python names.
Traceback:
/home/YOUKNOWWHO/miniconda3/lib/python3.13/importlib/__init__.py:88: in import_module
    return _bootstrap._gcd_import(name[level:], package, level)
           ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
github-local-repos/promptops-eval-platform/tests/test_smoke.py:1: in <module>
    from src.main import main
E   ModuleNotFoundError: No module named 'src'
_ ERROR collecting github-local-repos/rag-reliability-bench/tests/test_smoke.py _
ImportError while importing test module '/mnt/e/Git/warehouse/Working/agent/github-local-repos/rag-reliability-bench/tests/test_smoke.py'.
Hint: make sure your test modules/packages have valid Python names.
Traceback:
/home/YOUKNOWWHO/miniconda3/lib/python3.13/importlib/__init__.py:88: in import_module
    return _bootstrap._gcd_import(name[level:], package, level)
           ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
github-local-repos/rag-reliability-bench/tests/test_smoke.py:1: in <module>
    from src.main import main
E   ModuleNotFoundError: No module named 'src'
=========================== short test summary info ============================
ERROR github-local-repos/ai-accelerated-dev-lab/tests/test_smoke.py
ERROR github-local-repos/ecommerce-react-agent/tests/test_smoke.py
ERROR github-local-repos/multi-agent-sql-assistant/tests/test_smoke.py
ERROR github-local-repos/promptops-eval-platform/tests/test_smoke.py
ERROR github-local-repos/rag-reliability-bench/tests/test_smoke.py
!!!!!!!!!!!!!!!!!!! Interrupted: 5 errors during collection !!!!!!!!!!!!!!!!!!!!
5 errors in 1.83s\

## Next Milestones
See [docs/ROADMAP.md](docs/ROADMAP.md).
