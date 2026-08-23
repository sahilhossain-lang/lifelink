import datetime
from typing import Tuple
from app.models.medicine import Medicine

def calculate_medicine_stock(medicine: Medicine) -> Tuple[int, int]:
    """
    Calculate remaining medicine quantity and days of supply left based on:
    Remaining = Initial Quantity - (Daily Units * Elapsed Days)
    (PDF Page 8 Specification)
    Returns: (remaining_quantity, days_left)
    """
    try:
        start_date = datetime.date.fromisoformat(medicine.start_date.split("T")[0])
    except Exception:
        # Fallback if non-iso string
        start_date = datetime.date.today() - datetime.timedelta(days=5)

    today = datetime.date.today()
    elapsed_days = max(0, (today - start_date).days)
    
    daily_units = medicine.daily_units if medicine.daily_units and medicine.daily_units > 0 else 1.0
    consumed = int(elapsed_days * daily_units)
    remaining = max(0, medicine.initial_quantity - consumed)
    
    # Calculate days of medication remaining
    days_left = int(remaining / daily_units) if daily_units > 0 else 0
    
    return remaining, days_left
