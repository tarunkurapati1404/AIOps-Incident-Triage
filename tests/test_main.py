from app.main import apply_discount, calculate_shipping


def test_apply_discount_ten_percent():
    assert apply_discount(200.0, 10) == 180.0  # 10% off $200 = $180


def test_calculate_shipping_free_for_bulk():
    assert calculate_shipping(6) == 0.0