import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1]))

import modules.cvs.ai_analyzer as ai_analyzer


def test_gemini_runtime_status_has_expected_shape():
    status = ai_analyzer.get_gemini_runtime_status()

    assert status["status"] in {"ready", "unavailable"}
    assert "client_ready" in status
    assert "model" in status
    assert "error" in status


def test_analyze_cv_returns_fallback_when_client_unavailable(monkeypatch):
    monkeypatch.setattr(ai_analyzer, "_client", None)
    monkeypatch.setattr(ai_analyzer, "_client_init_error", "client unavailable")

    result = ai_analyzer.analyze_cv_with_gemini("Python SQL React")

    assert result["analysis_status"] == "unavailable"
    assert result["error"] == "client unavailable"
    assert isinstance(result["strengths"], list)
    assert isinstance(result["weaknesses"], list)
    assert isinstance(result["improvement_suggestions"], list)
