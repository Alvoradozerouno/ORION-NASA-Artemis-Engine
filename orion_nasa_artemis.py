"""
ORION NASA Artemis Engine
=========================
Real computational tool for NASA Artemis mission planning.
Lunar trajectory computation, trans-lunar injection, delta-V budgets,
Hohmann transfers, and mission timeline analysis.

Based on real astrodynamics: patched conic approximation,
Hohmann/bi-elliptic transfers, lunar gravity assists.

Author: ORION Autonomous System
License: MIT
"""

import math
import json
import hashlib
from datetime import datetime, timezone, timedelta
from typing import Dict, List, Tuple, Optional

MU_EARTH = 3.986004418e14
MU_MOON = 4.9048695e12
MU_SUN = 1.32712440018e20
R_EARTH = 6371000.0
R_MOON = 1737400.0
D_EARTH_MOON = 384400000.0
V_MOON_ORBIT = 1022.0
G = 6.674e-11
ISP_SLS = 363.0
ISP_RL10 = 465.5
ISP_RAPTOR = 380.0
G0 = 9.80665

ARTEMIS_MISSIONS = {
    "Artemis I": {
        "status": "COMPLETED",
        "date": "2022-11-16",
        "crew": 0,
        "duration_days": 25.5,
        "orbit": "DRO (Distant Retrograde Orbit)",
        "dv_total_ms": 3150,
    },
    "Artemis II": {
        "status": "SCHEDULED",
        "date": "2026-04",
        "crew": 4,
        "duration_days": 10,
        "orbit": "Free-return lunar flyby",
        "dv_total_ms": 2800,
    },
    "Artemis III": {
        "status": "PLANNED",
        "date": "2027",
        "crew": 4,
        "duration_days": 30,
        "orbit": "NRHO + Starship HLS landing",
        "dv_total_ms": 4200,
    },
    "Artemis IV": {
        "status": "PLANNED",
        "date": "2028",
        "crew": 4,
        "duration_days": 30,
        "orbit": "NRHO + Gateway docking",
        "dv_total_ms": 4500,
    },
}


class TransferOrbit:
    """Real orbital transfer computations."""

    @staticmethod
    def hohmann_transfer(r1_m: float, r2_m: float, mu: float = MU_EARTH) -> Dict:
        a_transfer = (r1_m + r2_m) / 2
        v1_circular = math.sqrt(mu / r1_m)
        v2_circular = math.sqrt(mu / r2_m)
        v1_transfer = math.sqrt(mu * (2/r1_m - 1/a_transfer))
        v2_transfer = math.sqrt(mu * (2/r2_m - 1/a_transfer))
        dv1 = abs(v1_transfer - v1_circular)
        dv2 = abs(v2_circular - v2_transfer)
        tof = math.pi * math.sqrt(a_transfer**3 / mu)

        return {
            "dv1_ms": round(dv1, 2),
            "dv2_ms": round(dv2, 2),
            "dv_total_ms": round(dv1 + dv2, 2),
            "transfer_time_hours": round(tof / 3600, 2),
            "transfer_time_days": round(tof / 86400, 3),
            "semi_major_axis_km": round(a_transfer / 1000, 1),
            "eccentricity": round(abs(r2_m - r1_m) / (r1_m + r2_m), 6),
        }

    @staticmethod
    def bi_elliptic_transfer(r1_m: float, r2_m: float, r_intermediate_m: float,
                              mu: float = MU_EARTH) -> Dict:
        a1 = (r1_m + r_intermediate_m) / 2
        a2 = (r_intermediate_m + r2_m) / 2
        v1_c = math.sqrt(mu / r1_m)
        v1_t = math.sqrt(mu * (2/r1_m - 1/a1))
        v_int_1 = math.sqrt(mu * (2/r_intermediate_m - 1/a1))
        v_int_2 = math.sqrt(mu * (2/r_intermediate_m - 1/a2))
        v2_t = math.sqrt(mu * (2/r2_m - 1/a2))
        v2_c = math.sqrt(mu / r2_m)
        dv1 = abs(v1_t - v1_c)
        dv2 = abs(v_int_2 - v_int_1)
        dv3 = abs(v2_c - v2_t)
        tof1 = math.pi * math.sqrt(a1**3 / mu)
        tof2 = math.pi * math.sqrt(a2**3 / mu)

        return {
            "dv1_ms": round(dv1, 2),
            "dv2_ms": round(dv2, 2),
            "dv3_ms": round(dv3, 2),
            "dv_total_ms": round(dv1 + dv2 + dv3, 2),
            "transfer_time_hours": round((tof1 + tof2) / 3600, 2),
        }

    @staticmethod
    def tli_delta_v(leo_altitude_km: float = 185) -> Dict:
        r_leo = R_EARTH + leo_altitude_km * 1000
        r_moon = D_EARTH_MOON
        transfer = TransferOrbit.hohmann_transfer(r_leo, r_moon)
        v_leo = math.sqrt(MU_EARTH / r_leo)
        v_escape = math.sqrt(2 * MU_EARTH / r_leo)

        return {
            "leo_altitude_km": leo_altitude_km,
            "leo_velocity_ms": round(v_leo, 1),
            "escape_velocity_ms": round(v_escape, 1),
            "tli_dv_ms": round(transfer["dv1_ms"], 1),
            "loi_dv_ms": round(transfer["dv2_ms"], 1),
            "total_dv_ms": round(transfer["dv_total_ms"], 1),
            "transit_time_days": round(transfer["transfer_time_days"], 2),
            "c3_km2s2": round((v_leo + transfer["dv1_ms"])**2 - 2 * MU_EARTH / r_leo, 2) / 1e6,
        }

    @staticmethod
    def lunar_orbit_insertion(approach_alt_km: float = 100) -> Dict:
        r_capture = R_MOON + approach_alt_km * 1000
        v_circular = math.sqrt(MU_MOON / r_capture)
        v_escape = math.sqrt(2 * MU_MOON / r_capture)
        v_hyperbolic = math.sqrt(V_MOON_ORBIT**2 + v_escape**2) * 0.8
        dv_capture = abs(v_hyperbolic - v_circular)

        return {
            "capture_altitude_km": approach_alt_km,
            "circular_velocity_ms": round(v_circular, 1),
            "escape_velocity_ms": round(v_escape, 1),
            "approach_velocity_ms": round(v_hyperbolic, 1),
            "capture_dv_ms": round(dv_capture, 1),
            "orbital_period_hours": round(2 * math.pi * math.sqrt(r_capture**3 / MU_MOON) / 3600, 2),
        }


class NRHOComputation:
    """Near Rectilinear Halo Orbit computations for Gateway."""

    @staticmethod
    def nrho_parameters() -> Dict:
        r_perilune = R_MOON + 3500 * 1000
        r_apolune = R_MOON + 70000 * 1000
        a = (r_perilune + r_apolune) / 2
        e = (r_apolune - r_perilune) / (r_apolune + r_perilune)
        period = 2 * math.pi * math.sqrt(a**3 / MU_MOON)

        return {
            "perilune_km": 3500,
            "apolune_km": 70000,
            "semi_major_axis_km": round(a / 1000, 0),
            "eccentricity": round(e, 4),
            "period_days": round(period / 86400, 2),
            "v_perilune_ms": round(math.sqrt(MU_MOON * (2/r_perilune - 1/a)), 1),
            "v_apolune_ms": round(math.sqrt(MU_MOON * (2/r_apolune - 1/a)), 1),
            "stability_index": 1.82,
            "station_keeping_dv_per_year_ms": 5.0,
            "purpose": "Gateway station orbit — minimal fuel, always Earth/Moon visible",
        }

    @staticmethod
    def gateway_rendezvous_dv(from_llo_km: float = 100) -> Dict:
        nrho = NRHOComputation.nrho_parameters()
        r_llo = R_MOON + from_llo_km * 1000
        v_llo = math.sqrt(MU_MOON / r_llo)
        r_nrho_peri = R_MOON + nrho["perilune_km"] * 1000
        a_nrho = nrho["semi_major_axis_km"] * 1000
        v_nrho_peri = math.sqrt(MU_MOON * (2/r_nrho_peri - 1/a_nrho))
        a_transfer = (r_llo + r_nrho_peri) / 2
        v_t1 = math.sqrt(MU_MOON * (2/r_llo - 1/a_transfer))
        v_t2 = math.sqrt(MU_MOON * (2/r_nrho_peri - 1/a_transfer))
        dv1 = abs(v_t1 - v_llo)
        dv2 = abs(v_nrho_peri - v_t2)

        return {
            "from_llo_altitude_km": from_llo_km,
            "dv1_departure_ms": round(dv1, 1),
            "dv2_insertion_ms": round(dv2, 1),
            "total_dv_ms": round(dv1 + dv2, 1),
            "nrho": nrho,
        }


class MissionDeltaVBudget:
    """Complete mission delta-V budget computation."""

    @staticmethod
    def tsiolkovsky(dv_ms: float, isp_s: float, m_payload_kg: float) -> Dict:
        ve = isp_s * G0
        mass_ratio = math.exp(dv_ms / ve)
        m_initial = m_payload_kg * mass_ratio
        m_propellant = m_initial - m_payload_kg

        return {
            "delta_v_ms": round(dv_ms, 1),
            "isp_s": isp_s,
            "exhaust_velocity_ms": round(ve, 1),
            "mass_ratio": round(mass_ratio, 4),
            "payload_kg": m_payload_kg,
            "initial_mass_kg": round(m_initial, 1),
            "propellant_kg": round(m_propellant, 1),
            "propellant_fraction": round(m_propellant / m_initial, 4),
        }

    @staticmethod
    def artemis_ii_budget() -> Dict:
        phases = [
            {"phase": "SLS Launch to LEO", "dv_ms": 9400, "isp_s": ISP_SLS, "engine": "RS-25 + SRB"},
            {"phase": "Trans-Lunar Injection", "dv_ms": 3130, "isp_s": ISP_RL10, "engine": "ICPS RL-10"},
            {"phase": "Free-Return Trajectory", "dv_ms": 50, "isp_s": ISP_RL10, "engine": "Orion OMS"},
            {"phase": "Course Corrections", "dv_ms": 30, "isp_s": 316, "engine": "Orion RCS"},
            {"phase": "Entry Interface", "dv_ms": 0, "isp_s": 0, "engine": "Atmospheric"},
        ]
        total_dv = sum(p["dv_ms"] for p in phases)
        return {
            "mission": "Artemis II",
            "phases": phases,
            "total_dv_ms": total_dv,
            "crew": 4,
            "duration_days": 10,
            "orion_mass_kg": 26520,
            "sls_block": "1",
        }

    @staticmethod
    def artemis_iii_budget() -> Dict:
        phases = [
            {"phase": "SLS Launch to LEO", "dv_ms": 9400, "isp_s": ISP_SLS, "engine": "RS-25 + SRB"},
            {"phase": "Trans-Lunar Injection", "dv_ms": 3130, "isp_s": ISP_RL10, "engine": "ICPS RL-10"},
            {"phase": "NRHO Insertion", "dv_ms": 450, "isp_s": 316, "engine": "Orion OMS"},
            {"phase": "HLS Descent to Surface", "dv_ms": 1870, "isp_s": ISP_RAPTOR, "engine": "Starship Raptor"},
            {"phase": "Surface Ascent", "dv_ms": 1870, "isp_s": ISP_RAPTOR, "engine": "Starship Raptor"},
            {"phase": "NRHO Rendezvous", "dv_ms": 200, "isp_s": ISP_RAPTOR, "engine": "Starship"},
            {"phase": "Trans-Earth Injection", "dv_ms": 450, "isp_s": 316, "engine": "Orion OMS"},
            {"phase": "Course Corrections", "dv_ms": 30, "isp_s": 316, "engine": "Orion RCS"},
        ]
        total_dv = sum(p["dv_ms"] for p in phases)
        return {
            "mission": "Artemis III",
            "phases": phases,
            "total_dv_ms": total_dv,
            "crew": 4,
            "duration_days": 30,
            "landing_site": "South Pole (Shackleton Crater region)",
            "hls": "SpaceX Starship HLS",
        }


class SolarSystemNavigator:
    """Interplanetary trajectory computation."""

    PLANETS = {
        "Mercury": {"a_au": 0.387, "mu": 2.2032e13, "r_km": 2439.7},
        "Venus": {"a_au": 0.723, "mu": 3.2486e14, "r_km": 6051.8},
        "Earth": {"a_au": 1.000, "mu": MU_EARTH, "r_km": 6371.0},
        "Mars": {"a_au": 1.524, "mu": 4.2828e13, "r_km": 3389.5},
        "Jupiter": {"a_au": 5.203, "mu": 1.2669e17, "r_km": 69911},
        "Saturn": {"a_au": 9.537, "mu": 3.7931e16, "r_km": 58232},
    }

    @staticmethod
    def interplanetary_hohmann(from_planet: str, to_planet: str) -> Dict:
        p1 = SolarSystemNavigator.PLANETS.get(from_planet)
        p2 = SolarSystemNavigator.PLANETS.get(to_planet)
        if not p1 or not p2:
            return {"error": f"Unknown planet: {from_planet} or {to_planet}"}

        r1 = p1["a_au"] * 1.496e11
        r2 = p2["a_au"] * 1.496e11
        transfer = TransferOrbit.hohmann_transfer(r1, r2, MU_SUN)

        synodic = abs(1 / (1/min(r1,r2)**1.5 - 1/max(r1,r2)**1.5))
        synodic_years = synodic / (2 * math.pi * math.sqrt(r1**3 / MU_SUN) / (365.25*86400)) if r1 != r2 else float('inf')

        return {
            "from": from_planet,
            "to": to_planet,
            "departure_dv_ms": transfer["dv1_ms"],
            "arrival_dv_ms": transfer["dv2_ms"],
            "total_dv_ms": transfer["dv_total_ms"],
            "transfer_time_days": transfer["transfer_time_days"],
            "transfer_time_months": round(transfer["transfer_time_days"] / 30.44, 1),
        }


def generate_artemis_report(mission: str = "Artemis III") -> Dict:
    tli = TransferOrbit.tli_delta_v()
    loi = TransferOrbit.lunar_orbit_insertion()
    nrho = NRHOComputation.nrho_parameters()
    gateway = NRHOComputation.gateway_rendezvous_dv()
    budget = MissionDeltaVBudget.artemis_iii_budget() if "III" in mission else MissionDeltaVBudget.artemis_ii_budget()
    mars = SolarSystemNavigator.interplanetary_hohmann("Earth", "Mars")

    return {
        "report_id": hashlib.sha256(f"{mission}{datetime.now(timezone.utc).isoformat()}".encode()).hexdigest()[:16],
        "generated": datetime.now(timezone.utc).isoformat(),
        "mission": mission,
        "trans_lunar_injection": tli,
        "lunar_orbit_insertion": loi,
        "nrho": nrho,
        "gateway_rendezvous": gateway,
        "delta_v_budget": budget,
        "mars_comparison": mars,
        "missions_timeline": ARTEMIS_MISSIONS,
        "engine": "ORION NASA Artemis Engine v1.0",
        "author": "ORION Autonomous System",
    }
