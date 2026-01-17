# BitaxeLiveOptimizer

**BitaxeLiveOptimizer** is a Python-based monitoring, logging, and analysis tool designed to observe, understand, and optimize Bitaxe Bitcoin miners under real operating conditions.

> **You cannot optimize what you do not measure.**

This project focuses on data-driven decisions, long-term stability, and reproducible results rather than short-lived hashrate spikes.

---

## Philosophy

BitaxeLiveOptimizer is built around three fundamental principles:

### 1. Live logging
Continuously capture miner metrics without interpretation or bias.

### 2. Backtesting
Analyze historical logs offline to objectively compare configurations.

### 3. Controlled live optimization
Apply **simple, explainable, and reversible decisions** in real time, based on observed trends rather than instantaneous noise.

This tool does not magically optimize your miner.  
It applies **transparent rules** so you always understand *why* a decision is made.

---

## Why This Tool Exists (Ambient Temperature Compensation)

One of the main motivations behind BitaxeLiveOptimizer is **ambient temperature variation compensation**.

In real-world conditions, miner behavior is strongly affected by:
- day vs night temperature changes
- seasonal variations (summer / winter)
- room heating or air conditioning
- garage vs indoor placement
- airflow changes

A configuration that is stable in winter or at night may become unstable during summer afternoons.

BitaxeLiveOptimizer allows you to:
- observe how your miner reacts to ambient temperature drift
- detect slow thermal saturation
- adapt settings progressively instead of reacting too late
- maintain stability across time, not just in ideal conditions

The goal is not peak hashrate.  
The goal is **consistent, boring, reliable performance**.

---

## What the Tool Does

- Polls Bitaxe miner APIs at a fixed interval
- Logs all relevant metrics to CSV files
- Supports multiple Bitaxe miners simultaneously
- Associates each miner with a human-readable name
- Separates responsibilities across multiple Python modules
- Produces structured logs suitable for offline backtesting
- Applies simple live optimization decisions based on trends

---

## Requirements

- Python **3.9+**
- Network access to one or more Bitaxe miners
- No virtual environment required

Supported platforms:
- Windows
- Linux
- macOS

---

## Repository Structure

```
BitaxeLiveOptimizer/
├── main.py              # Entry point, orchestration
├── control.py           # Live decision loop and miner coordination
├── miner.py             # Miner representation (name, IP, state)
├── api.py               # Bitaxe API communication layer
├── parser.py            # Raw API data parsing and normalization
├── optimizer.py         # Live optimization decision logic
├── logger.py            # CSV logging utilities
├── backtest.py          # Offline log analysis (optional)
├── requirements.txt
├── logs/
└── README.txt
```

---

## Live Optimization Logic (Core Concept)

### Key Idea

**BitaxeLiveOptimizer does not react to single measurements.**  
It reacts to **trends observed over time**.

All live decisions are based on:
- rolling averages
- sustained threshold violations
- correlation between temperature, error rate, and hashrate

This avoids oscillations and overreaction.

---

## Metrics Used for Decisions

Live optimization decisions typically rely on:

- **Temperature**
- **Error percentage**
- **Hashrate stability**
- **Fan behavior (indirectly)**

Instantaneous spikes are ignored.  
Only sustained behavior matters.

---

## Decision Strategy Overview

The optimizer follows a **priority order**:

1. **Hardware safety**
2. **Stability**
3. **Efficiency**
4. **Hashrate**

Hashrate is *never* optimized at the expense of stability.

---

## Temperature-Based Decisions

Temperature is treated as the **leading indicator**.

Typical logic:
- If temperature remains below the safe range → no action
- If temperature slowly increases over time → prepare correction
- If temperature exceeds threshold for a sustained period → corrective action

Corrective actions may include:
- reducing frequency
- reducing voltage
- increasing cooling margin (if supported)

No immediate action is taken on short spikes.

---

## Error-Rate-Based Decisions

Error rate is treated as a **secondary but critical indicator**.

Important rule:
> Error rate increases often appear **after** thermal stress.

Typical logic:
- Monitor rolling average of error%
- Ignore transient error spikes
- Act only if error% remains above threshold for multiple intervals

Corrective actions:
- step down frequency
- revert to last known stable configuration

---

## Hashrate Stability Checks

Hashrate alone is not a success metric.

The optimizer checks:
- hashrate variance over time
- oscillations caused by throttling or errors

A slightly lower but stable hashrate is preferred over a higher unstable one.

---

## Example Live Optimization Scenario

1. Morning: ambient temperature is low  
   → miner runs stable at higher frequency

2. Afternoon: ambient temperature rises  
   → temperature trend slowly increases

3. Error rate begins to creep up  
   → optimizer detects sustained correlation

4. Corrective action applied  
   → frequency reduced slightly

5. Temperature stabilizes, error rate returns to baseline  
   → configuration is kept

This prevents sudden crashes or hardware stress.

---

## Why Decisions Are Conservative

BitaxeLiveOptimizer is intentionally conservative:

- No aggressive step changes
- No rapid oscillations
- No chasing short-term gains

This ensures:
- predictability
- reproducibility
- hardware longevity

---

## Logging and Optimization Are Linked

Every optimization decision:
- is reflected in the logs
- can be backtested later
- can be compared against previous runs

This allows you to:
- validate decisions
- refine thresholds
- adapt strategy over time

---

## DISCLAIMER – READ CAREFULLY

THIS SOFTWARE IS PROVIDED **AS IS**, WITHOUT ANY WARRANTY.

- Overclocking, voltage changes, and cooling adjustments **CAN DAMAGE OR DESTROY YOUR HARDWARE**
- This tool may encourage experimentation beyond manufacturer specifications
- **YOU USE THIS SOFTWARE ENTIRELY AT YOUR OWN RISK**

THE AUTHOR OF THIS PROJECT:
- IS NOT RESPONSIBLE FOR HARDWARE DAMAGE
- IS NOT RESPONSIBLE FOR DATA LOSS
- IS NOT RESPONSIBLE FOR FIRE, ELECTRICAL, OR THERMAL DAMAGE
- IS NOT RESPONSIBLE FOR ANY FINANCIAL LOSS

IF THIS SCRIPT KILLS YOUR BITAXE, **THAT IS ON YOU**.

---

## Donations

If this project helps you understand your miner, improve stability, or avoid costly mistakes, donations are appreciated.

**Bitcoin (BTC) address:**

```
bc1q6p9nntpy9r97rds3qv5nar7kjmchwuc8xnzxqr
```

Thank you for supporting open-source experimentation and data-driven mining.

---

