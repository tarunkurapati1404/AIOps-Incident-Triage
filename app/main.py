"""A tiny order-pricing service. It has ONE intentional bug (Step 1.3)."""


def apply_discount(price: float, discount_percent: float) -> float:
    """Return price after applying discount_percent (e.g. 10 means 10%)."""
    return round(price * (1 - discount_percent), 2)  # BUG: missing /100


def calculate_shipping(item_count: int) -> float:
    """Shipping: $5 flat fee, free for 5+ items."""
    if item_count >= 5:
        return 0.0
    return 5.0