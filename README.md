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

### 3. Manual optimization
No blind auto-tuning. You decide what matters: stability, temperature, error rate, noise, or hashrate.

This tool does not magically optimize your miner.  
It provides facts so you can optimize intelligently.

---

## Why This Tool Exists (Ambient Temperature Compensation)

One of the main motivations behind BitaxeLiveOptimizer is **ambient temperature variation compensation**.

In real-world conditions, miner behavior is strongly affected by:
- day vs night temperature changes
- seasonal variations (summer / winter)
- room heating or air conditioning
- garage vs indoor placement
- airflow changes

A configuration that is perfectly stable at night or in winter may become:
- unstable during the day
- error-prone in summer
- thermally saturated after several hours

BitaxeLiveOptimizer allows you to:
- **observe how your miner reacts to ambient temperature drift**
- **compare logs across different conditions**
- **adjust frequency, voltage, or cooling strategy accordingly**
- **build configurations that remain stable across time, not just in ideal conditions**

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
- Makes firmware smoothing effects visible (error rate, averaged stats, etc.)

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
├── control.py           # Core control loop and miner coordination
├── miner.py             # Miner representation (name, IP, state)
├── api.py               # Bitaxe API communication layer
├── parser.py            # Raw API data parsing and normalization
├── logger.py            # CSV logging utilities
├── backtest.py          # Offline log analysis (optional)
├── requirements.txt
├── logs/
└── README.txt
```

---

## Installation

Clone the repository:

```bash
git clone https://github.com/<your-user>/BitaxeLiveOptimizer.git
cd BitaxeLiveOptimizer
```

Install dependencies:

```bash
pip install -r requirements.txt
```

---

## Miner Definition (IP and Name)

Each Bitaxe miner is defined by:
- an **IP address or hostname**
- a **logical, human-readable name**

Using names is essential to keep logs readable and comparable.

### Miner syntax

```text
<miner_name>=<ip_or_hostname>
```

Example:

```text
bitaxe_garage=192.168.1.50
```

---

## Command-Line Parameters

### `--miner`

Defines a Bitaxe miner.  
This option can be used multiple times.

```text
--miner bitaxe_garage=192.168.1.50
--miner bitaxe_lab=192.168.1.51
```

---

### `--interval`

Polling interval in seconds.

```text
--interval 10
```

Typical values:
- `5`   → very granular, higher load
- `10`  → recommended default
- `30+` → long-term monitoring

---

### `--duration`

Total logging duration in minutes.

```text
--duration 6
```

Notes:
- ~6 minutes corresponds to one internal Bitaxe stats update window
- 20–30 minutes recommended for thermal stability analysis

---

### `--output`

CSV output file path.

```text
--output logs/test_run.csv
```

If omitted, a timestamped file is created automatically.

---

## Full Example Command

```bash
python main.py   --miner bitaxe_garage=192.168.1.50   --miner bitaxe_lab=192.168.1.51   --interval 10   --duration 6   --output logs/oc_490mhz.csv
```

---

## Logging Explained

### Why Logging Is Necessary

Some Bitaxe firmware metrics (especially **error percentage**) are smoothed and updated only every ~300–360 seconds.  
The web interface alone can therefore be misleading.

Continuous logging allows you to:
- correlate temperature with error rate
- observe delayed instability
- objectively compare multiple configurations
- understand behavior changes caused by ambient temperature variation

---

### Logged Data

Each CSV row represents one polling cycle for one miner.

Typical logged fields:
- Timestamp
- Miner name
- Miner IP
- Hashrate
- Temperature
- Fan speed
- Voltage (if exposed)
- Frequency (if exposed)
- Error percentage
- Accepted / rejected shares (if exposed)

Example CSV:

```csv
timestamp,miner,ip,hashrate,temp,error_percent,fan_rpm,voltage,freq
2026-01-17T16:10:00,bitaxe_garage,192.168.1.50,552,63.1,0.18,4800,1.15,490
```

---

## Backtesting Explained

Backtesting consists of:
- loading previously generated CSV logs
- analyzing them offline
- comparing different miner configurations objectively

Backtesting is especially useful to compare:
- day vs night behavior
- summer vs winter conditions
- identical settings under different ambient temperatures

---

## Architecture Explained

### main.py
- Parses command-line arguments
- Initializes configuration
- Starts and stops the monitoring session

### control.py
- Implements the main polling loop
- Coordinates all registered miners

### miner.py
- Represents a single Bitaxe miner
- Stores name, IP, and runtime state

### api.py
- Handles HTTP communication with the Bitaxe API
- Fetches raw JSON statistics

### parser.py
- Converts raw API responses into normalized metrics

### logger.py
- Manages CSV file creation and structured writes

### backtest.py
- Performs offline log analysis and comparisons

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

## License

Choose according to your goals:
- MIT
- Apache-2.0
- GPL-3.0

MIT is usually the simplest option.
