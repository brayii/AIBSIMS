# Bunny FSM Index

This document provides a summary of the finite state machines (FSMs) defined for each type of bunny in the simulation. Each FSM is implemented using PlantUML and stored in this directory.

## 📋 FSM Files

| Bunny Type    | Diagram File                     | Description |
|---------------|-----------------------------------|-------------|
| Adult Female  | `adult_female_fsm.puml`          | Handles breeding, defense, movement, and avoidance of vampires. |
| Adult Male    | `adult_male_fsm.puml`            | Learns fertile zones, moves toward mates, no direct breeding. |
| Vampire       | `vampire_fsm.puml`               | Infects others, seeks clusters, does not breed. |
| Juvenile      | `juvenile_fsm.puml`              | Ages into adult, can be mutated, otherwise wanders randomly. |

## 🧠 How to View FSMs

Use the [PlantUML VS Code Extension](https://marketplace.visualstudio.com/items?itemName=jebbs.plantuml) or upload `.puml` files to an online PlantUML renderer.

## 📁 Directory Usage

This `fsm/` folder is tracked in source control and serves as the definitive source of behavioral logic for AI-driven bunnies. Each file may be tied to a corresponding state implementation in `core/bunny.py`.

