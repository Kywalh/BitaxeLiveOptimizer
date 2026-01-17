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

## What the Tool Does

- Polls Bitaxe miner APIs at a fixed interval
- Logs all relevant metrics to CSV files
- Supports multiple Bitaxe miners simultaneously
- Associates each miner with a human-readable name
- Produces structured logs suitable for offline backtesting
- Makes firmware smoothing effects visible (error rate, averaged stats, etc.)

---

## Requirements

- Python **3.9+**
- Network access to one or more Bitaxe miners
- No virtual environment required

**Supported platforms**
- Windows
- Linux
- macOS

---

## Repository Structure

```text
BitaxeLiveOptimizer/
├── main.py
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

Example:

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

Typical questions answered by backtesting:
- Is 500 MHz actually better than 490 MHz?
- Does increasing fan speed reduce long-term error rate?
- How long does it take before thermal saturation occurs?

---

### Why Backtesting Matters

Short-term observations can be misleading.

Backtesting reveals:
- slow thermal drift
- delayed error-rate increases
- long-term instability invisible in short tests

Optimization decisions should **never** be based on only a few minutes of data.

---

## `main.py` Explained

### High-Level Execution Flow

1. Parse command-line arguments
2. Register all miners (name + IP)
3. Initialize the CSV logger
4. Start the polling loop
5. Fetch stats from each miner
6. Normalize and format metrics
7. Append one CSV row per miner per cycle
8. Stop cleanly when duration is reached

---

### Conceptual Logic

```text
start_time = now

while now < start_time + duration:
    for miner in miners:
        fetch miner stats
        parse metrics
        write CSV row
    sleep(interval)
```

---

### Design Choices

- Deterministic timing
- No background threads
- Simple control flow
- Easy debugging
- Fully reproducible logs

---

## Interpreting Results

### Good Configuration

- Stable temperature
- Flat fan behavior
- Low and steady error percentage
- Stable hashrate plateau

### Bad Configuration

- Slowly increasing temperature
- Fan constantly ramping
- Error percentage creeping upward
- Hashrate oscillations

---

## Common Mistakes

- Judging performance on very short runs
- Ignoring smoothed firmware metrics
- Comparing logs from different ambient temperatures
- Optimizing hashrate while ignoring error rate

---

## Disclaimer

- Overclocking reduces hardware lifespan
- Voltage increases heat non-linearly
- You are fully responsible for your hardware

This tool exposes reality.  
What you do with that information is your choice.

---

## License

Choose according to your goals:
- MIT
- Apache-2.0
- GPL-3.0

MIT is usually the simplest option.
