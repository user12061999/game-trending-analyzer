import pytest

from app.analytics import calibration
from app.analytics.revenue_estimator import RevenueEstimator


def test_no_points_means_factor_one(temp_db):
    calibration.invalidate_cache()
    assert calibration.get_factor("mobile", "us") == 1.0
    assert RevenueEstimator.estimate_mobile_revenue(1, "us")["daily_revenue"] == 1500000


def test_country_factor_from_real_figures(temp_db):
    calibration.invalidate_cache()
    raw = RevenueEstimator.estimate_mobile_revenue(5, "vn", calibrated=False)["monthly_revenue"]
    calibration.add_point({"game_title": "A", "platform": "mobile", "country": "vn", "rank": 5,
                           "actual_monthly_revenue": raw * 2})
    calibration.add_point({"game_title": "B", "platform": "mobile", "country": "vn", "rank": 5,
                           "actual_monthly_revenue": raw * 3})
    calibration.add_point({"game_title": "C", "platform": "mobile", "country": "vn", "rank": 5,
                           "actual_monthly_revenue": raw * 100})  # outlier, median ignores it
    assert calibration.get_factor("mobile", "vn") == pytest.approx(3.0, rel=0.01)
    est = RevenueEstimator.estimate_mobile_revenue(5, "vn")
    assert est["calibration_factor"] == pytest.approx(3.0, rel=0.01)
    # other countries fall back to the platform-wide median (also 3.0 here)
    assert calibration.get_factor("mobile", "jp") == pytest.approx(3.0, rel=0.01)
    # PC unaffected
    assert calibration.get_factor("pc", "global") == 1.0


def test_factor_is_clamped_and_delete_resets(temp_db):
    calibration.invalidate_cache()
    raw = RevenueEstimator.estimate_mobile_revenue(1, "us", calibrated=False)["monthly_revenue"]
    res = calibration.add_point({"game_title": "X", "country": "us", "rank": 1, "actual_monthly_revenue": raw * 1000})
    assert calibration.get_factor("mobile", "us") == calibration.MAX_FACTOR
    calibration.delete_point(res["id"])
    assert calibration.get_factor("mobile", "us") == 1.0


def test_invalid_point_rejected(temp_db):
    with pytest.raises(ValueError):
        calibration.add_point({"game_title": "", "rank": 1, "actual_monthly_revenue": 10})
    with pytest.raises(ValueError):
        calibration.add_point({"game_title": "Y", "rank": 0, "actual_monthly_revenue": 10})


def test_report_shows_errors(temp_db):
    calibration.invalidate_cache()
    raw = RevenueEstimator.estimate_mobile_revenue(3, "kr", calibrated=False)["monthly_revenue"]
    calibration.add_point({"game_title": "K", "country": "kr", "rank": 3, "actual_monthly_revenue": raw / 2})
    rep = calibration.get_report()
    p = rep["points"][0]
    assert p["raw_error_pct"] == pytest.approx(100.0, abs=0.5)
    assert p["calibrated_error_pct"] == pytest.approx(0.0, abs=0.5)
