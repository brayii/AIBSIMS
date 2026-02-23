# Copilot Instructions - Bunny Simulator

## Project Overview

The Bunny Simulator is a 2D grid-based agent simulation written in Python using Pygame. Autonomous bunnies follow finite state machine (FSM) rules to move, interact, age, breed, and potentially mutate. The simulation is designed for future expansion with reinforcement learning capabilities.

## Setup Instructions

### Prerequisites
- Python 3.10 or higher
- Pygame library

### Installation
```bash
# Create virtual environment
python -m venv env

# Activate virtual environment
# On Windows:
.\env\Scripts\activate
# On macOS/Linux:
source env/Scripts/activate

# Install dependencies
pip install -r requirements.txt
```

### Running the Simulation
```bash
python main.py
```

## Project Structure

```
bunny_simulator/
├── core/                      # Core simulation logic
│   ├── bunny.py              # Bunny agent class
│   ├── grid.py               # Grid/world management
│   ├── fsm_dispatcher.py      # FSM decision-making
│   ├── logger.py             # Event logging system
│   └── __init__.py
├── fsm/                       # FSM behavior diagrams
│   ├── adult_female_fsm.puml
│   ├── adult_male_fsm.puml
│   ├── juvenile_fsm.puml
│   ├── vampire_fsm.puml
│   └── fsm_index.md
├── data/
│   └── logs/                  # Simulation event logs (CSV)
├── main.py                    # Simulation entry point
├── requirements.txt           # Python dependencies
├── README.md                  # Project documentation
└── copilot-instructions.md    # This file
```

## Key Components

### core/bunny.py
- **Bunny class**: Represents an individual agent
  - Properties: `sex`, `x`, `y`, `age`, `is_mutant`, `color`, `name`
  - Methods: `is_adult()`, `max_age()`, `make_baby()`, `bunny_death()`, `update()`
  - Behavior: Age-based lifecycle, mutations (2% chance), random naming

### core/grid.py
- **Grid class**: Manages the simulation world
  - Constants: `TILE_SIZE=32`, `GRID_WIDTH=20`, `GRID_HEIGHT=15`
  - Methods: `place_bunny()`, `is_empty()`, `update()`, `render()`
  - Maintains 2D cell array and bunny list

### core/fsm_dispatcher.py
- **FSMDispatcher class**: Executes FSM logic for bunnies
  - `dispatch(bunny, grid, turn, logger)`: Main decision method
  - Handles initialization, death checks, and state transitions

### core/logger.py
- **EventLogger class**: Records simulation events to CSV
  - Log fields: `turn`, `event_type`, `bunny_name`, `sex`, `age`, `mutant`, `location`, `details`, `controller`
  - Files saved in `data/logs/` with timestamp

### main.py
- Pygame initialization and main loop
- Simulation step frequency: ~500ms per turn
- Target grid occupancy: 75%
- Frame rate: 60 FPS

## Development Guidelines

### FSM Design
1. All bunny behaviors are defined in PlantUML FSM diagrams (see `fsm/`)
2. When modifying bunny behavior, update the corresponding `.puml` file first
3. The `FSMDispatcher.dispatch()` method translates FSM states into code

### Code Conventions
- Use snake_case for variables and functions
- Use PascalCase for class names
- Include type hints where practical
- Add docstrings to complex methods
- Log significant events (birth, death, mutations) via `EventLogger`

### Adding New Features
1. **New Bunny Type**: Create new FSM diagram in `fsm/`, add type to `Bunny` class
2. **New Behavior**: Update relevant FSM diagram, then implement in `FSMDispatcher`
3. **New Logging**: Add event type and details in `EventLogger.log()` calls

### Testing
- Review simulation logs in `data/logs/` (CSV format)
- Monitor bunny count and population dynamics
- Check for expected mutation rates (~2%)
- Verify breeding and death events

## Common Tasks

### Modify Bunny Lifecycle
- Edit max_age calculations in `core/bunny.py`
- Update `FSMDispatcher.dispatch()` logic
- Test with 2-3 simulation runs

### Adjust Grid Parameters
- Change `GRID_WIDTH`, `GRID_HEIGHT`, `TILE_SIZE` in `core/grid.py`
- Recalculate target occupancy in `main.py`

### Add FSM State
1. Update PlantUML diagram in `fsm/`
2. Add corresponding logic in `FSMDispatcher.dispatch()`
3. Add logging for new event type if needed

## Dependencies
- **pygame**: Rendering and event handling
- **random**: Procedural generation and stochastic events
- **csv**: Event logging
- **datetime**: Timestamped logs

## Debugging Tips
- Check `data/logs/` for event traces
- Monitor console output for turn count and bunny population
- Use breakpoints in `FSMDispatcher.dispatch()` to trace FSM decisions
- Verify grid coordinates don't exceed `GRID_WIDTH` and `GRID_HEIGHT`

## Future Enhancements (Phase 2)
- Reinforcement learning module for adaptive bunny behavior
- Advanced visualization (heatmaps, trajectories)
- Replay system using log files
- Multi-species interactions
- Environmental factors (food, predators)

## References
- PlantUML: https://plantuml.com/
- Pygame: https://www.pygame.org/
- FSM Index: [fsm/fsm_index.md](fsm/fsm_index.md)
