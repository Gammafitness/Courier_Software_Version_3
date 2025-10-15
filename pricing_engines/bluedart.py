import math

def quote(cfg, pincode, row, used_weight, declared_value, shared):
    """
    Pricing engine for Bluedart courier service.
    Handles zones, volumetric weight, ODA, docket, insurance, fuel, and GST.
    Compatible with app_v4_2_1_fuel_basis.py (supports fuel_basis).
    """

    # --- Extract zone and base rate ---
    zone = str(row.get("zone", "")).upper()
    perkg = cfg["rates"].get(zone)
    if not perkg:
        return {"reason": f"Rate missing for zone {zone}"}

    # --- Freight calculation ---
    freight = perkg * used_weight

    # --- Insurance handling ---
    insurance_pct = float(cfg.get("insurance_pct", 0))
    insurance_flat = float(cfg.get("insurance_flat", 0))
    insurance = (freight * (insurance_pct / 100.0)) + insurance_flat

    # --- Docket ---
    docket = float(cfg.get("docket", 0))

    # --- ODA handling ---
    oda = 0
    status = str(row.get("status", "")).upper()
    oda_type = cfg.get("oda_type", "Fixed")
    oda_fixed = float(cfg.get("oda_fixed", 0))

    if "ODA" in status:
        if oda_type == "Special":
            # Bluedart special ODA = ₹0.25/kg, minimum ₹50
            oda = max(used_weight * 0.25, 50)
        else:
            oda = oda_fixed

    # --- Determine fuel calculation basis ---
    basis = (cfg.get("fuel_basis") or "freight").lower()

    if basis == "subtotal":
        base_for_fuel = freight + docket + insurance + oda
    else:
        base_for_fuel = freight

    # --- Fuel surcharge ---
    fuel_pct = float(cfg.get("fuel_pct", 0))
    fuel = base_for_fuel * (fuel_pct / 100.0)

    # --- Subtotal + GST ---
    subtotal = freight + docket + insurance + oda + fuel
    gst_pct = float(cfg.get("gst_pct", 0))
    gst = subtotal * (gst_pct / 100.0)

    # --- Minimum charge check ---
    min_charge = float(cfg.get("min_charge", 0))
    total = subtotal + gst
    if total < min_charge:
        total = min_charge

    # --- Final structured result ---
    return {
        "freight": freight,
        "docket": docket,
        "insurance": insurance,
        "oda": oda,
        "fuel": fuel,
        "subtotal": subtotal,
        "gst": gst,
        "total": total,
        "reason": "OK",
        "fuel_basis": basis
    }
