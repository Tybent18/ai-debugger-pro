import pytest

from interface.demo import SCENARIOS, scenario_by_slug


def test_demo_scenarios_have_unique_slugs_and_verified_repairs():
    assert len({scenario.slug for scenario in SCENARIOS}) == len(SCENARIOS)
    assert all(scenario.source.strip() for scenario in SCENARIOS)
    assert all(scenario.failure.strip() for scenario in SCENARIOS)
    assert all(scenario.repaired_output.strip() for scenario in SCENARIOS)
    assert all(scenario.diagnosis.has_patch for scenario in SCENARIOS)
    assert all(scenario.diagnosis.regression_test.strip() for scenario in SCENARIOS)


def test_scenario_lookup_reports_available_choices():
    assert scenario_by_slug("approval-repair").title == "Approval-gated repair"
    with pytest.raises(ValueError, match="exception-diagnosis"):
        scenario_by_slug("missing")
