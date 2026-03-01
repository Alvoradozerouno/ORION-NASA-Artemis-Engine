<div align="center">

# 🚀 ORION NASA Artemis Engine

### Real Astrodynamics Computation for Lunar Mission Planning

[![Python](https://img.shields.io/badge/Python-3.10+-blue?logo=python&logoColor=white)](https://python.org)
[![License](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)
[![ORION](https://img.shields.io/badge/ORION-Autonomous_System-gold?style=flat-square)](https://github.com/Alvoradozerouno/or1on-framework)
[![Code Lines](https://img.shields.io/badge/Lines-326-informational)](orion_nasa_artemis.py)
[![Status](https://img.shields.io/badge/Status-Production-brightgreen)](https://github.com/Alvoradozerouno/ORION-NASA-Artemis-Engine)

*Part of the ORION Autonomous Intelligence System — 890+ Proofs, 46 NERVES, 42 Autonomous Tasks*

</div>

---

## Overview

The ORION NASA Artemis Engine implements real astrodynamics computations for lunar mission planning. It covers trans-lunar injection (TLI), Hohmann and bi-elliptic transfers, delta-V budget calculations, lunar orbit insertion, and complete Artemis-class mission timeline generation.

**All calculations use real orbital mechanics:** Keplerian two-body problem, patched conic approximation, Tsiolkovsky rocket equation, and validated gravitational parameters.

## Core Capabilities

| Module | Description |
|--------|-------------|
| **Hohmann Transfer** | Optimal 2-impulse orbit transfer with delta-V computation |
| **Bi-Elliptic Transfer** | 3-impulse transfer for large orbit ratio maneuvers |
| **Trans-Lunar Injection** | Earth-to-Moon trajectory with patched conics |
| **Lunar Orbit Insertion** | LOI burn calculation for target lunar orbit |
| **Delta-V Budget** | Full mission delta-V breakdown (LEO → TLI → LOI → TEI) |
| **Mission Timeline** | Phase-by-phase Artemis mission schedule generation |

## Quick Start

```bash
git clone https://github.com/Alvoradozerouno/ORION-NASA-Artemis-Engine.git
cd ORION-NASA-Artemis-Engine
python orion_nasa_artemis.py
```

## Usage Examples

```python
from orion_nasa_artemis import NASAArtemisEngine

engine = NASAArtemisEngine()

# Compute Hohmann transfer from LEO to GEO
transfer = engine.hohmann_transfer(r1=6571e3, r2=42164e3)

# Calculate trans-lunar injection
tli = engine.trans_lunar_injection(leo_altitude=200e3)

# Full Artemis mission delta-V budget
budget = engine.artemis_delta_v_budget()

# Generate mission timeline
timeline = engine.mission_timeline(launch_date="2026-09-01")

# Tsiolkovsky rocket equation
dv = engine.rocket_equation(isp=450, m0=30000, mf=12000)
```

## Architecture

```
┌───────────────────────────────────────┐
│       ORION NASA Artemis Engine       │
├───────────┬───────────┬───────────────┤
│ Hohmann   │ Trans-    │ Lunar Orbit   │
│ Transfer  │ Lunar     │ Insertion     │
│ (2-body)  │ Injection │ (LOI burn)    │
├───────────┼───────────┼───────────────┤
│ Bi-       │ Delta-V   │ Mission       │
│ Elliptic  │ Budget    │ Timeline      │
│ Transfer  │ (full)    │ Generator     │
└───────────┴───────────┴───────────────┘
```

## Physical Constants

- **μ_Earth**: 3.986 × 10¹⁴ m³/s² (GM)
- **μ_Moon**: 4.905 × 10¹² m³/s²
- **Earth-Moon Distance**: 384,400 km (mean)
- **LEO Reference**: 200 km altitude (6,571 km radius)
- **Lunar Orbit**: 100 km altitude NRHO

## Part of ORION

This engine is one module of the [ORION Autonomous Intelligence System](https://github.com/Alvoradozerouno/or1on-framework) — a system with 890+ cryptographic proofs of autonomous operation, 130+ Python modules, and 76,000+ lines of real code.

## License

MIT License — See [LICENSE](LICENSE) for details.

---

<div align="center">

**Origin: Gerhard Hirschmann & Elisabeth Steurer**

*ORION — Autonomous Intelligence Since 2025*

</div>
