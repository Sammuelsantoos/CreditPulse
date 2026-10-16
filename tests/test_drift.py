from src.drift_monitor import build_current, build_reference, generate_report


def test_reference_and_current_have_same_columns():
    ref = build_reference(n=100)
    cur = build_current(n=100)
    assert list(ref.columns) == list(cur.columns)
    assert len(ref) == 100
    assert len(cur) == 100


def test_report_is_generated(tmp_path):
    path = generate_report(out_dir=tmp_path)
    assert path.exists()
    assert path.suffix == ".html"
    assert path.stat().st_size > 1000
