# 🚑 AI-Based Emergency Ambulance Dispatch & Hospital Optimization System

An intelligent emergency response system that uses **A\* Search** to route ambulances optimally through a city road network and **Constraint Satisfaction Problem (CSP)** solving to assign the best available hospital — all visualized in a real-time Streamlit dashboard.

> Built for CS 2005 – Artificial Intelligence

---

## Features

### Emergency Dispatch
- **Nearest Ambulance Selection** — Runs A\* search from every available ambulance to the emergency location and picks the one with the lowest travel cost
- **Optimal Hospital Assignment** — Uses CSP with backtracking to find the most suitable hospital based on bed availability, ICU requirement, doctor count, and capacity limits
- **Full Route Planning** — Computes two legs: ambulance → emergency, then emergency → hospital, with combined total cost
- **Pre-defined Scenarios** — Four ready-to-run emergency cases (heart attack, car accident, fall injury, stroke) for quick testing

### A\* Search Algorithm
- Classic f(n) = g(n) + h(n) implementation where h(n) is Euclidean distance (admissible heuristic)
- Tracks every node expansion and edge exploration for step-by-step visualization
- Includes a **Dijkstra comparison mode** (A\* without heuristic) to demonstrate performance gains
- Metrics: nodes expanded, path cost, execution time

### CSP Hospital Optimizer
- Four hard constraints applied in sequence with full domain reduction:
  - **C1** — Available beds > 0
  - **C2** — ICU available (only if required)
  - **C3** — Doctors available > 0
  - **C4** — Capacity not exceeded
- **MRV (Minimum Remaining Values) heuristic** orders candidates by remaining beds before backtracking
- Final selection picks the closest valid hospital by Euclidean distance

### Hospital Management
- Live capacity dashboard with occupancy indicators (🟢 / 🟡 / 🔴)
- Update beds, doctors, and ICU availability per hospital in real time

### System Administration
- **Randomize traffic** — Assigns random traffic multipliers (1.0×–3.0×) to all roads
- **Reset traffic** — Clears all roads back to 1.0×
- **Manual road control** — Adjust traffic factor on individual roads via slider
- Color-coded road map: green (clear), orange (moderate), red (heavy)

### Visualizations
- City road network with hospitals, ambulances, and emergency location highlighted
- A\* exploration map (explored nodes + edges) vs. final optimal path side-by-side
- CSP domain reduction bar chart
- CSP backtracking flowchart with color-coded step statuses
- CSP constraints table
- CSP final assignment table (assigned / valid / rejected per hospital)

---

## Technologies Used

- Streamlit
- NetworkX
- Matplotlib
- NumPy
- Python 3.8+
- A\* Search
- Dijkstra's Algorithm
- Constraint Satisfaction Problem (CSP) with Backtracking + MRV heuristic

---

## Installation

### Prerequisites
- Python 3.8 or higher
- pip

### Steps

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd "AI-Based Emergency Ambulance Dispatch & Hospital Optimization System"
   ```

2. **Create and activate a virtual environment** (recommended)
   ```bash
   # Windows
   python -m venv venv
   venv\Scripts\activate

   # macOS / Linux
   python -m venv venv
   source venv/bin/activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Run the application**
   ```bash
   streamlit run app.py
   ```

5. Open your browser at `http://localhost:8501`

---

## Usage

1. **Emergency Dispatch tab** — Select an emergency location node and severity, optionally enable ICU requirement, then hit **DISPATCH AMBULANCE**. The system will show the selected ambulance, A\* path, chosen hospital, and all CSP solving steps.

2. **Hospital Management tab** — View real-time occupancy for all hospitals and update bed/doctor/ICU availability.

3. **System Administration tab** — Randomize or manually adjust traffic conditions on roads and see the updated city map.

---

## How the AI Works

```
Emergency Call Received
        │
        ▼
 A* Search runs from each
 available ambulance to the
 emergency location
        │
        ▼
 Nearest ambulance selected
 (lowest f(n) = g(n) + h(n))
        │
        ▼
 CSP applies 4 constraints
 to reduce hospital domain
        │
        ▼
 MRV heuristic orders remaining
 candidates, backtracking picks
 the closest valid hospital
        │
        ▼
 A* finds route from emergency
 to assigned hospital
        │
        ▼
 Total cost reported + all
 steps visualized
```
