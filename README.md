# Bunny Simulator — Machine Learning Requirements

## Purpose

Build a two-dimensional bunny population simulator in Python. This is a machine-learning project: learned models must control the important adult-bunny decisions during the simulation.

An implementation that controls every bunny only with hard-coded rules or a finite-state machine does not satisfy this project.

## Required technology

- Python 3.10 or newer
- Pygame for the visual grid and simulation display
- NumPy and pandas for preparing training data
- scikit-learn for training and inference
- joblib for saving and loading trained models
- Dependencies must be listed in `requirements.txt`

## Simulation requirements

The program must:

1. Display a bounded, tile-based grid using Pygame.
2. Maintain one authoritative population of bunnies and prevent two bunnies from occupying the same tile.
3. Give every bunny a unique identifier, name, sex, age, position, color, and mutation status.
4. Begin with both male and female bunnies.
5. Advance in discrete simulation turns.
6. Age each living bunny once per turn.
7. Treat a bunny as an adult when it reaches the configured adult age.
8. Remove bunnies that exceed their allowed lifespan.
9. Allow movement only to an empty adjacent tile inside the grid.
10. Allow an adult female to reproduce only when an eligible adult male and an empty adjacent tile are available.
11. Create offspring with a sex, inherited color, and configurable chance of mutation.
12. Allow mutant bunnies to infect nearby non-mutant bunnies.
13. Control excessive population growth before the grid becomes full.
14. Show the current turn, total population, adult count, mutant count, and maximum population.

## Machine-learning requirements

Machine learning is mandatory, not an optional future enhancement.

The implementation must:

1. Record simulation events as training data, including the turn, bunny attributes, position, nearby conditions, selected action, and controller.
2. Build features from the state available at the moment a decision is made. Training must not use future information.
3. Train at least one supervised-learning model that predicts an adult bunny action.
4. Use trained models during the live simulation to control adult male and adult female decisions such as moving or attempting to breed.
5. Apply physical constraints after prediction. A model may request breeding, but the simulator must reject that action when no valid mate or empty tile exists.
6. Save trained models to disk and load them for inference without retraining on every launch.
7. Use the same feature names, order, types, and meaning during training and inference.
8. Split training and test data reproducibly and report evaluation results such as a confusion matrix and classification metrics.
9. Handle missing or invalid model files with a clear message. A temporary rule-based fallback may keep the program usable, but it must not be presented as the completed ML implementation.
10. Keep rule-based behavior limited to environmental rules, validation, initialization, and simple non-learned behaviors. Hard-coded adult decision logic must not replace the trained model.

## Data and model requirements

- Training logs belong under `data/logs/`.
- Saved models belong under `models/`.
- Generated logs and model artifacts should not be committed unless they are intentionally provided as reproducible sample assets.
- The training program must fail clearly when no usable training data exists or when the data contains too few classes to train and evaluate a classifier.
- Random operations used for training and evaluation must accept a fixed seed for reproducibility.

## Quality requirements

- Grid cells and bunny coordinates must remain synchronized after placement, movement, birth, mutation, removal, and population control.
- The simulation must not crash when no move, mate, or breeding tile is available.
- Resource files and log files must be closed cleanly.
- Core behavior must have automated tests, including movement, occupied-tile protection, aging and death, breeding constraints, model loading, and training/inference feature consistency.
- The project must start from a clean checkout after installing `requirements.txt` and either loading supplied models or following documented training steps.

## Completion criteria

The simulator is complete when it runs visually, maintains a valid population and grid, produces usable training data, trains and evaluates its models, reloads those models, and uses their predictions to make adult-bunny decisions during a live simulation.

The project is not complete if the ML code is unused, if adult behavior is entirely hard-coded, or if the simulator only demonstrates an FSM implementation.
