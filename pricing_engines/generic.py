import math

def quote(cfg, pincode, row, used_weight, declared_value, shared):
    """
    Pricing engine for standard couriers.
    Applies Fuel Surcharge according to fuel_basis:
    - 'freight' → only on basic freight
    - 'subtotal' → on (freight + docket + insurance + oda)
    """

    perkg = cfg["rates"].get(str(row.get("zone", "")).upper())
    if not perkg:
        return {"reason": f"Rate missing for zone {row.get('zone')}"}

    freight = perkg * used_weight
    docket = cfg.get("docket", 0)
    insurance = (freight * (cfg.get("insurance_pct", 0) / 100.0)) + cfg.get("insurance_flat", 0)

    oda = 0
    if "ODA" in str(row.get("status", "")).upper():
        oda = cfg.get("oda_fixed", 0)

    basis = (cfg.get("fuel_basis") or "freight").lower()
    if basis == "subtotal":
        base_for_fuel = freight + docket + insurance + oda
    else:
        base_for_fuel = freight

    fuel = base_for_fuel * (cfg.get("fuel_pct", 0) / 100.0)
    subtotal = freight + docket + insurance + oda + fuel
    gst = subtotal * (cfg.get("gst_pct", 0) / 100.0)
    total = max(subtotal + gst, cfg.get("min_charge", 0))

    return {
        "freight": freight,
        "docket": docket,
        "insurance": insurance,
        "oda": oda,
        "fuel": fuel,
        "subtotal": subtotal,
        "gst": gst,
        "total": total,
        "reason": "OK"
    }
