Colony Alpha

Colony Alpha is a terminal-based sci-fi colony management and strategy game built in Python using the rich library. Manage resources, evolve your colony with genetic upgrades, build infrastructure, and conquer the galaxy in real time.

Features

Real-Time Simulation

The game updates every 5 seconds (1 in-game day)
A background thread handles resource changes and colony status

Live Dashboard UI

Built with rich for a dynamic terminal interface
Displays resources, DNA stability, and progress

Colony Management

Resources include Oxygen (O2), Power, Food, Metal, Research Points (RP), and Intel
Population roles include Workers, Scientists, Soldiers, and Spies

Genetic Modification System

PHOTO reduces food consumption
OXY reduces oxygen usage
BRAIN increases research output
MUSCLE increases military strength
Each gene reduces DNA stability

Infrastructure

Space Elevator produces Metal
Terraformer produces Oxygen
Spy Bureau generates Intel

Military and Conquest

Tanks provide ground power
Assault Ships provide space power
Conquering planets increases tech level

Galaxy Map

Multiple planets with different factions and strengths
Expansion is required for progression

Save System

Game progress is saved to save_colony.json
Controls

1 - Build Infrastructure
2 - Military
3 - Galaxy Map
4 - Gene Lab
6 - Save Game
Q - Quit Game

Win / Lose Conditions

Lose Condition

Oxygen or Food reaches zero and the colony collapses

Progression

Increase tech level by conquering planets
Advance Omega phases (future expansion potential)
Installation

Requirements

Python 3.8 or higher
rich library

Install dependencies:

pip install rich

Running the Game
python main.py

Project Structure
main.py
save_colony.json (created after saving)

Gameplay Tips

Balance population and resources early
Avoid stacking too many genes due to DNA stability loss
Build infrastructure before focusing on military
Use Assault Ships to conquer planets more effectively
Future Improvements
Rebellions on conquered planets
Expanded tech tree
Random events such as disasters or raids
Multiplayer or leaderboard system
GUI or web-based version
Notes

This project is designed as a lightweight but expandable simulation game. The structure allows for adding additional systems such as diplomacy, trading, or AI behavior.
