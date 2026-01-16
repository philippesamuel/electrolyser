# Green Hydrogen Electrolyser Simulation

A real-time simulation of a PEM (Proton Exchange Membrane) Electrolyser coupled with live wind energy data.

This project demonstrates the potential of Green Hydrogen production by integrating live weather data from OpenWeather with a chemical engineering model of a 10-cell PEM stack. It serves as a Proof of Concept (PoC) for full-stack engineering in the renewable energy domain.

## 🚀 Project Overview

The system operates in a continuous loop:
1.  **Extract:** Fetches live weather data via the OpenWeather API:
    - wind speed 
    - temperature
    - pressure 
    - humidity

2.  **Transform:** Processes the data, calculates air density and applies a wind turbine power curve.

3.  **Simulate:** Feeds the generated power into a physics-based PEM Electrolyser model to calculate:
    * Cell Voltage ($V_{cell}$)
    * Hydrogen Production Rate (kg/h)
    * Stack Efficiency & Heat Generation
4.  **Load:** Stores all metrics in a SQL database.

5.  **Visualize:** Displays real-time performance on an interactive Dash dashboard.

## 🛠 Tech Stack

* **Language:** Python 3.11+
* **Backend & ETL:** 
    - [Prefect](https://www.prefect.io/) (Orchestration) 
    - [SQLModel](https://sqlmodel.tiangolo.com/) | [SQLALchemy](https://www.sqlalchemy.org) (ORM) 
    - [Alembic](https://alembic.sqlalchemy.org/) (DB Migrations)
    - [Pydantic](https://docs.pydantic.dev/) (Validation)
    - [Pydantic-Settings](https://docs.pydantic.dev/latest/concepts/pydantic_settings/) (Settings Management)

* **Frontend:** [Dash](https://dash.plotly.com/) & [Plotly](https://plotly.com/python/) (Visualization).
* **Database:** SQLite (Dev), PostgreSQL (Planned for Prod).
* **Package Manager:** [uv](https://github.com/astral-sh/uv).

## 📂 Repository Structure

```text
.
├── backend/
│   ├── alembic/       # Database migrations
│   ├── clients/       # API Clients (OpenWeather)
│   ├── db_models/     # SQLModel Database Schemas
│   ├── models/        # Calculations for air density, wind turbine power...
│   ├── tests/         # Unit tests...
│   ├── database.py    # Database engine and prefect connector
│   ├── etl.py         # Prefect Flows & Tasks
│   ├── main.py        # Electrolyser Simulation Logic (Physics Model)
│   └── config.py      # Environment Configuration
├── frontend/
│   ├── dash_chart.py  # Dashboard Logic
│   └── main.py        # Frontend Entrypoint
└── pyproject.toml
```

## ⚙️ Installation & Setup

### Prerequisites

- Python 3.11 or higher
- uv (recommended)
- OpenWeather API Key


### 1. Clone the Repository

```console
git clone https://github.com/philippesamuel/electrolyser.git
cd electrolyser
```

Create a .env file in the root directory:

```dotenv
OPENWEATHER_API_URI=https://api.openweathermap.org/data/3.0/onecall
OPENWEATHER_API_KEY="your_api_key"
WEATHER_UPDATE_INTERVAL_MINUTES=5

APP_ROOT="path/to/current/folder"
DATABASE_NAME=database.db
DATABASE_PATH=${APP_ROOT}/backend/${DATABASE_NAME}
DATABASE_URL=sqlite+pysqlite:///${DATABASE_PATH}
```

### 2. Backend Setup

```console
cd backend
uv sync
```

Initialize the prefect server:

```console
uv run prefect server start
```

Open a new terminal window and initialize the database and the ETL pipeline:

```console
uv run database.py
uv run etl.py
```

Access the prefect UI to vizualize flow execution at [http://localhost:4200](http://localhost:4200)

### 3. Frontend Setup

```console
uv frontend
uv sync
uv run main.py
```

Access the dashboard at [http://localhost:8050](http://localhost:8050)

## 🧪 Engineering Model

The electrolyser simulation is based on standard electrochemical equations for a PEM stack operating at 80°C.

$$ V_{cell} = V_{rev} + \eta_{act} + \eta_{ohm} + \eta_{con} $$

Where:
- $V_{rev}$: Reversible voltage (Nernst equation)
- $\eta_{act}$: Activation overpotential (Tafel equation)
- $\eta_{ohm}$: Ohmic overpotential (Linear resistance)
- $\eta_{con}$: Concentration overpotential (Mass transport limitation)

## 🤖 Statement on AI Usage

This project was developed with the assistance of AI tools (LLMs).

## 🔜 Roadmap

- [ ] Containerize with Docker & Docker Compose.
- [ ] Deploy to Hetzner Cloud.
- [ ] Implement "Data Generation Time" vs "Fetch Time" tracking.
- [ ] Add 3D Wind Turbine animation.

---

Created by Philippe Costa - 2026
