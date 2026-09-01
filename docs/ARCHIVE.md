# Archived and Inactive Work

This map prevents superseded experiments from being mistaken for the current
submission. Files remain tracked for auditability; they are not active dashboard
requirements.

## Current judge-facing path

- `app.py`
- `uc_admissions/ethnicity_analysis.py`
- `uc_admissions/admission_models.py`
- `uc_admissions/benchmark.py` and `uc_admissions/benchmark_ui.py`
- `notebooks/uc_ethnicity_outcomes_colab.ipynb`
- `CONTEXT.md`
- `docs/adr/0003-ethnicity-outcomes-dashboard.md`
- `docs/DEMO.md`

## Superseded persistent-residual work

- `archive/analysis.py`
- `tests/archive/test_analysis.py`
- `tests/archive/test_dashboard_seams.py`
- `archive/notebooks/uc_persistent_gaps_colab.ipynb`
- `docs/research/archive/persistent-gap-audit.md`
- `docs/adr/archive/0001-question-led-residual-observatory.md`

These files preserve the previous school-campus residual investigation. They do
not control the current app or presentation.

## Gemini paths

- `uc_admissions/gemini.py` and `tests/test_gemini_profile.py` are the current bounded Gemini
  explanation boundary.
- `archive/profile.py` remains historical profile-guardrail work and is not connected
  to the current judge-facing app.
- `archive/gemini_adapter.py` and `tests/archive/test_gemini_adapter.py` are residual-specific
  historical work and are not used by the current ethnicity dashboard.
- `docs/adr/archive/0002-streamlit-dashboard-with-gemini-companion.md` records the
  earlier residual design and remains historical context.

The current user-facing Gemini action is documented in `docs/DEMO.md` and must
remain optional, source-grounded, and safe without an API key.

## Archived implementation prompts

- `docs/archive/IMPLEMENTATION-PROMPTS.md`

Those prompts describe the superseded residual/Gemini ticket sequence and are
retained only to explain older GitHub issues and commits.
