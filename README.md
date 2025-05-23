# 🐇 Bunny Simulator

A 2D visual grid-based simulation where autonomous bunnies live, move, mutate, and breed according to defined behavioral rules. Driven by finite state machines (FSMs), this simulation is written in Python and designed for future expansion with reinforcement learning and adaptive agent behaviors.

---

## 🚀 Features

- 🧠 Rule-based finite state machines (FSM) for all bunny types
- 🐇 Four agent types: Adult Male, Adult Female, Juvenile, Vampire
- 🕹️ Grid-based movement and interactions
- 👁️ Visual simulation planned with Pygame (2D)
- 🔄 Simulation turn loop with step-based progression
- 🔜 Future ML integration for agent learning

---

## 🧠 FSM Behavior Diagrams

Behavior of each bunny type is documented using PlantUML FSM diagrams.

| Bunny Type    | Diagram File                        |
|---------------|--------------------------------------|
| Adult Female  | `fsm/adult_female_fsm.puml`         |
| Adult Male    | `fsm/adult_male_fsm.puml`           |
| Vampire       | `fsm/vampire_fsm.puml`              |
| Juvenile      | `fsm/juvenile_fsm.puml`             |
| FSM Index     | `fsm/fsm_index.md`                  |

> 🧩 Use the [PlantUML VS Code Extension](https://marketplace.visualstudio.com/items?itemName=jebbs.plantuml) to view `.puml` diagrams directly in your editor.

---

## 🗂️ File Structure

bunny_simulator/
├── core/ # Core logic and agent behavior
│ ├── bunny.py
│ ├── grid.py
│ └── fsm_dispatcher.py # (Planned)
│
├── fsm/ # FSM behavior diagrams (PlantUML)
│ ├── *.puml
│ └── fsm_index.md
│
├── data/
│ └── logs/ # Birth, death, mutation logs
│
├── main.py # Simulation launcher
├── README.md # This file
├── .gitignore # Git exclusions
└── requirements.txt # Dependencies (e.g. pygame)


---

## 📦 Requirements

- Python 3.10+
- Pygame (`pip install pygame`)
- PlantUML (for diagrams, optional)
- VS Code recommended (for live preview, Git integration)

Install dependencies:

```bash
python -m venv env
source env/Scripts/activate  # or .\env\Scripts\activate.bat on Windows
pip install -r requirements.txt

🧪 Running the Simulation

python main.py

This launches the simulation grid and processes turns (1 per ~2 seconds). Bunnies will move, age, and eventually mutate or breed based on the FSM logic.

Visual output and interaction will be added in the Pygame module (coming soon).

🎯 Development Goals
 FSMs defined and versioned

 Project structure and Git initialized

 Visual grid display (Pygame)

 Turn-based simulation loop

 FSM integration per bunny type

 Logging and replay system

 ML module (Phase 2)

🤝 Contributing
Clone this repo and help expand the ecosystem!

git clone https://github.com/yourusername/bunny_simulator.git

Use the fsm/ directory to propose behavioral changes via .puml updates. Logic changes should align with FSMs.

🧠 Credits
FSM-based AI design inspired by classic agent simulations

Diagrams built with PlantUML

Simulation designed and built in Python 3

📄 License
MIT License (add LICENSE file if applicable)


