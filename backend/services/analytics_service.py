"""
Consolidated Analytics Service for Infreight Ocean Carrier Rate Automation.

Computes global cross-account sourcing intelligence, trade lane volume distributions,
carrier extraction accuracy rankings, price spectrum (cheapest vs expensive),
and user sourcing activity leaderboards.
"""
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional
import re
from sqlalchemy import select, and_
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from models.rate_search import RateSearch, CarrierSearchResult
from models.quote import Quote


CARRIER_DISPLAY_NAMES = {
    "MAERSK": "Maersk",
    "ONE": "ONE (Ocean Network Express)",
    "CMA_CGM": "CMA CGM",
    "CMA": "CMA CGM",
    "HAPAG_LLOYD": "Hapag-Lloyd",
    "HAPAG": "Hapag-Lloyd",
    "MSC": "MSC",
    "OOCL": "OOCL",
    "GREENX": "GreenX",
    "COSCO": "COSCO Shipping",
    "EVERGREEN": "Evergreen Line",
    "HMM": "HMM (Hyundai Merchant Marine)",
}


def normalize_lane_port(name: Optional[str]) -> str:
    """Normalize port string to cleanly aggregate naming variations."""
    if not name:
        return "Unknown"
    clean = name.strip()
    
    # Check for [LOCODE]
    m_bracket = re.search(r"\[([A-Z]{5})\]", clean)
    if m_bracket:
        return m_bracket.group(1)
        
    # Check for (LOCODE)
    m_paren = re.search(r"\(([A-Z]{5})\)", clean)
    if m_paren:
        return m_paren.group(1)
        
    # Check for pure 5-letter uppercase locode
    if re.fullmatch(r"[A-Z]{5}", clean):
        return clean

    # Strip extraneous parentheticals e.g. "Hamburg (Germany)" -> "Hamburg"
    base = re.sub(r"\s*\([^)]*\)", "", clean).strip()
    
    # Take first component if comma-separated e.g. "Hamburg, Germany" -> "Hamburg"
    if "," in base:
        base = base.split(",")[0].strip()
        
    return base.title() if base else clean


def get_clean_lane_key(origin: Optional[str], dest: Optional[str]) -> tuple[str, str, str]:
    """Returns (norm_origin, norm_dest, display_lane_key)."""
    norm_orig = normalize_lane_port(origin)
    norm_dest = normalize_lane_port(dest)
    return norm_orig, norm_dest, f"{norm_orig} → {norm_dest}"


async def compute_admin_analytics(
    session: AsyncSession,
    time_range: str = "all",
    user_name: Optional[str] = None,
    carrier_filter: Optional[str] = None,
) -> Dict[str, Any]:
    """
    Compute full consolidated analytics payload for the admin dashboard.
    """
    now = datetime.utcnow()
    since_date = None
    timeline_days = 14

    if time_range == "today":
        since_date = now.replace(hour=0, minute=0, second=0, microsecond=0)
        timeline_days = 1
    elif time_range == "7d":
        since_date = now - timedelta(days=7)
        timeline_days = 7
    elif time_range == "14d":
        since_date = now - timedelta(days=14)
        timeline_days = 14
    elif time_range == "30d":
        since_date = now - timedelta(days=30)
        timeline_days = 30
    elif time_range == "all":
        since_date = None
        timeline_days = 30

    # Build RateSearch query
    search_stmt = select(RateSearch).options(
        selectinload(RateSearch.carrier_results).selectinload(CarrierSearchResult.quotes)
    )

    conditions = []
    if since_date:
        conditions.append(RateSearch.created_at >= since_date)
    if user_name and user_name != "all":
        conditions.append(RateSearch.user_name.ilike(f"%{user_name.strip()}%"))

    if conditions:
        search_stmt = search_stmt.where(and_(*conditions))

    search_stmt = search_stmt.order_by(RateSearch.created_at.desc())

    res = await session.execute(search_stmt)
    searches = res.scalars().all()

    total_searches = len(searches)
    total_quotes = 0
    searches_with_quotes = 0

    # Daily buckets
    today_start = datetime(now.year, now.month, now.day)
    day_buckets: Dict[str, Dict[str, Any]] = {}
    
    # Initialize timeline days
    days_to_plot = max(timeline_days, 14) if time_range in ["14d", "all"] else (timeline_days if timeline_days > 1 else 7)
    for i in range(days_to_plot - 1, -1, -1):
        dt = today_start - timedelta(days=i)
        iso = dt.strftime("%Y-%m-%d")
        label = dt.strftime("%d %b").lstrip("0")
        day_buckets[iso] = {"iso": iso, "label": label, "searches": 0, "quotes": 0}

    # Tracking aggregates
    distinct_lanes_set = set()
    users_aggregate: Dict[str, Dict[str, Any]] = {}
    lanes_aggregate: Dict[str, Dict[str, Any]] = {}
    carrier_aggregate: Dict[str, Dict[str, Any]] = {}
    all_quotes_list: List[Dict[str, Any]] = []

    for rs in searches:
        user = (rs.user_name or "").strip() or "General Sourcing / Guest"
        norm_orig, norm_dest, lane_key = get_clean_lane_key(rs.origin, rs.destination)
        distinct_lanes_set.add(lane_key)

        created_iso = rs.created_at.strftime("%Y-%m-%d") if rs.created_at else None
        if created_iso and created_iso in day_buckets:
            day_buckets[created_iso]["searches"] += 1

        # Track user stats
        if user not in users_aggregate:
            users_aggregate[user] = {
                "user_name": user,
                "search_count": 0,
                "quotes_generated": 0,
                "distinct_lanes": set(),
                "last_active": rs.created_at.isoformat() if rs.created_at else None,
            }
        users_aggregate[user]["search_count"] += 1
        users_aggregate[user]["distinct_lanes"].add(lane_key)

        # Track lane stats
        if lane_key not in lanes_aggregate:
            lanes_aggregate[lane_key] = {
                "origin": norm_orig,
                "destination": norm_dest,
                "display_lane": lane_key,
                "raw_origin": rs.origin,
                "raw_destination": rs.destination,
                "search_count": 0,
                "quotes_count": 0,
                "successful_searches": 0,
                "prices": [],
                "quotes": [],
                "users": set(),
                "last_searched_at": rs.created_at.isoformat() if rs.created_at else None,
            }
        lanes_aggregate[lane_key]["search_count"] += 1
        lanes_aggregate[lane_key]["users"].add(user)

        search_has_quotes = False

        for csr in rs.carrier_results:
            c_code = (csr.carrier or "").upper()
            
            # Apply carrier filter if specified
            if carrier_filter and carrier_filter != "all" and c_code != carrier_filter.upper():
                continue

            if c_code not in carrier_aggregate:
                carrier_aggregate[c_code] = {
                    "carrier": c_code,
                    "carrier_name": CARRIER_DISPLAY_NAMES.get(c_code, c_code),
                    "total_queries": 0,
                    "quotes_found_count": 0,
                    "no_quotes_count": 0,
                    "failure_count": 0,
                    "connector_not_available_count": 0,
                    "port_mismatch_count": 0,
                    "total_quotes": 0,
                    "prices": [],
                }

            carrier_aggregate[c_code]["total_queries"] += 1

            if csr.has_port_mismatch:
                carrier_aggregate[c_code]["port_mismatch_count"] += 1

            quotes_len = len(csr.quotes) if csr.quotes else 0
            raw_status = (csr.status or "").upper()

            if quotes_len > 0:
                search_has_quotes = True
                total_quotes += quotes_len
                users_aggregate[user]["quotes_generated"] += quotes_len
                lanes_aggregate[lane_key]["quotes_count"] += quotes_len
                carrier_aggregate[c_code]["quotes_found_count"] += 1
                carrier_aggregate[c_code]["total_quotes"] += quotes_len

                if created_iso and created_iso in day_buckets:
                    day_buckets[created_iso]["quotes"] += quotes_len

                for q in csr.quotes:
                    val = float(q.final_freight_value or 0.0)
                    if val > 0:
                        carrier_aggregate[c_code]["prices"].append(val)
                        lanes_aggregate[lane_key]["prices"].append(val)
                        lanes_aggregate[lane_key]["quotes"].append({
                            "carrier": c_code,
                            "price": val,
                            "currency": q.currency or "USD",
                            "container_type": q.container_type or rs.container_type,
                            "etd": q.etd,
                            "eta": q.eta,
                        })
                        all_quotes_list.append({
                            "lane_key": lane_key,
                            "origin": norm_orig,
                            "destination": norm_dest,
                            "carrier": c_code,
                            "carrier_name": CARRIER_DISPLAY_NAMES.get(c_code, c_code),
                            "price": val,
                            "currency": q.currency or "USD",
                            "container_type": q.container_type or rs.container_type,
                        })

            elif raw_status in ["NO_QUOTES_AVAILABLE", "NO_QUOTES"]:
                carrier_aggregate[c_code]["no_quotes_count"] += 1
            elif raw_status == "CONNECTOR_NOT_AVAILABLE":
                carrier_aggregate[c_code]["connector_not_available_count"] += 1
            elif raw_status in ["FAILED", "LOGIN_FAILED", "TIMEOUT", "UNKNOWN_ERROR", "EXTRACTION_FAILED"]:
                carrier_aggregate[c_code]["failure_count"] += 1
            elif raw_status in ["AVAILABLE_QUOTES_FOUND", "SUCCESS", "COMPLETED"]:
                # Marked complete without quotes saved
                carrier_aggregate[c_code]["quotes_found_count"] += 1
            else:
                # Other unexpected failure
                carrier_aggregate[c_code]["failure_count"] += 1

        if search_has_quotes:
            searches_with_quotes += 1
            lanes_aggregate[lane_key]["successful_searches"] += 1

    # Format Most-Searched Lanes
    top_lanes_list = []
    for lane_key, ldata in lanes_aggregate.items():
        sc = ldata["search_count"]
        vol_pct = round((sc / total_searches) * 100, 1) if total_searches > 0 else 0
        hit_rate = round((ldata["successful_searches"] / sc) * 100, 1) if sc > 0 else 0
        prices = ldata["prices"]
        min_p = round(min(prices), 2) if prices else None
        avg_p = round(sum(prices) / len(prices), 2) if prices else None
        max_p = round(max(prices), 2) if prices else None

        # Find carrier with lowest price
        cheapest_carrier = None
        if ldata["quotes"]:
            sorted_q = sorted(ldata["quotes"], key=lambda x: x["price"])
            cheapest_carrier = sorted_q[0]["carrier"]

        top_lanes_list.append({
            "display_lane": lane_key,
            "origin": ldata["origin"],
            "destination": ldata["destination"],
            "raw_origin": ldata["raw_origin"],
            "raw_destination": ldata["raw_destination"],
            "search_count": sc,
            "volume_percentage": vol_pct,
            "quotes_count": ldata["quotes_count"],
            "hit_rate_percent": hit_rate,
            "min_price": min_p,
            "avg_price": avg_p,
            "max_price": max_p,
            "cheapest_carrier": cheapest_carrier,
            "unique_users_count": len(ldata["users"]),
            "last_searched_at": ldata["last_searched_at"],
        })

    top_lanes_list.sort(key=lambda x: x["search_count"], reverse=True)

    # Format Carrier Accuracy Ranking
    carrier_ranking_list = []
    for c_code, cdata in carrier_aggregate.items():
        tot = cdata["total_queries"]
        succ = cdata["quotes_found_count"]
        acc_pct = round((succ / tot) * 100, 1) if tot > 0 else 0.0
        no_pct = round((cdata["no_quotes_count"] / tot) * 100, 1) if tot > 0 else 0.0
        fail_pct = round((cdata["failure_count"] / tot) * 100, 1) if tot > 0 else 0.0
        not_avail_pct = round((cdata["connector_not_available_count"] / tot) * 100, 1) if tot > 0 else 0.0
        prices = cdata["prices"]
        avg_p = round(sum(prices) / len(prices), 2) if prices else None

        if acc_pct >= 60.0:
            tier = "High"
        elif acc_pct >= 25.0:
            tier = "Moderate"
        else:
            tier = "Attention Needed"

        carrier_ranking_list.append({
            "carrier": c_code,
            "carrier_name": cdata["carrier_name"],
            "total_queries": tot,
            "quotes_found_count": succ,
            "accuracy_percent": acc_pct,
            "no_quotes_count": cdata["no_quotes_count"],
            "no_quotes_percent": no_pct,
            "failure_count": cdata["failure_count"],
            "failure_percent": fail_pct,
            "connector_not_available_count": cdata["connector_not_available_count"],
            "connector_not_available_percent": not_avail_pct,
            "port_mismatch_count": cdata["port_mismatch_count"],
            "total_quotes": cdata["total_quotes"],
            "avg_price_usd": avg_p,
            "reliability_tier": tier,
        })

    # Sort carriers by active status and accuracy
    carrier_ranking_list.sort(key=lambda x: (x["quotes_found_count"] > 0, x["accuracy_percent"], x["total_queries"]), reverse=True)

    # Determine Most Accurate vs Most Inaccurate Carrier (among active carriers with >= 5 queries)
    active_carriers = [c for c in carrier_ranking_list if c["total_queries"] >= 5 and c["connector_not_available_percent"] < 80]
    if not active_carriers:
        active_carriers = [c for c in carrier_ranking_list if c["total_queries"] >= 2]

    most_accurate_carrier = active_carriers[0] if active_carriers else (carrier_ranking_list[0] if carrier_ranking_list else None)
    
    # Inaccurate is one with lowest accuracy and substantial attempts
    sorted_by_worst = sorted(active_carriers, key=lambda x: (x["accuracy_percent"], -x["failure_count"]))
    most_inaccurate_carrier = sorted_by_worst[0] if (sorted_by_worst and sorted_by_worst[0]["carrier"] != (most_accurate_carrier["carrier"] if most_accurate_carrier else "")) else (sorted_by_worst[1] if len(sorted_by_worst) > 1 else None)

    # Format User Leaderboard
    user_leaderboard_list = []
    for uname, udata in users_aggregate.items():
        cnt = udata["search_count"]
        vol_pct = round((cnt / total_searches) * 100, 1) if total_searches > 0 else 0
        user_leaderboard_list.append({
            "user_name": uname,
            "search_count": cnt,
            "volume_percentage": vol_pct,
            "quotes_generated": udata["quotes_generated"],
            "distinct_lanes": len(udata["distinct_lanes"]),
            "last_active": udata["last_active"],
        })
    user_leaderboard_list.sort(key=lambda x: x["search_count"], reverse=True)

    # Pricing Spectrum: Top Economical vs Top Premium
    lanes_with_pricing = [l for l in top_lanes_list if l["min_price"] is not None and l["min_price"] > 0]
    cheapest_lanes = sorted(lanes_with_pricing, key=lambda x: x["min_price"])[:5]
    expensive_lanes = sorted(lanes_with_pricing, key=lambda x: x["max_price"] or 0, reverse=True)[:5]

    # Timeline formatting
    per_day_list = list(day_buckets.values())
    busiest_day_val = max(1, max([d["searches"] for d in per_day_list] or [1]))

    # Summary KPI card figures
    overall_hit_rate = round((searches_with_quotes / total_searches) * 100, 1) if total_searches > 0 else 0.0
    most_active_lane = top_lanes_list[0] if top_lanes_list else None
    top_user = user_leaderboard_list[0] if user_leaderboard_list else None
    cheapest_lane = cheapest_lanes[0] if cheapest_lanes else None
    most_expensive_lane = expensive_lanes[0] if expensive_lanes else None

    return {
        "summary": {
            "total_searches": total_searches,
            "total_quotes": total_quotes,
            "hit_rate_percent": overall_hit_rate,
            "searches_with_quotes": searches_with_quotes,
            "distinct_lanes": len(distinct_lanes_set),
            "active_users_count": len(users_aggregate),
            "busiest_day": busiest_day_val,
            "most_active_lane": most_active_lane,
            "top_user": top_user,
            "most_accurate_carrier": most_accurate_carrier,
            "most_inaccurate_carrier": most_inaccurate_carrier,
            "cheapest_lane": cheapest_lane,
            "most_expensive_lane": most_expensive_lane,
        },
        "timeline": {
            "days_count": len(per_day_list),
            "busiest_day": busiest_day_val,
            "per_day": per_day_list,
        },
        "top_lanes": top_lanes_list,
        "carrier_ranking": carrier_ranking_list,
        "pricing_spectrum": {
            "cheapest_lanes": cheapest_lanes,
            "expensive_lanes": expensive_lanes,
        },
        "user_leaderboard": user_leaderboard_list,
        "all_users": sorted(list(users_aggregate.keys())),
    }
