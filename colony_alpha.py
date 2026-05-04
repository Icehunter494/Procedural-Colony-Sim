import os
import time
import random
import json
import threading
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.live import Live
from rich import print as rprint

console = Console()

# --- DATA CLASSES ---
class Planet:
    def __init__(self, name, faction, power):
        self.name = name
        self.faction = faction
        self.power = power
        self.max_power = power
        self.conquered = False
        self.rebellion_progress = 0

class ColonyAlpha:
    def __init__(self):
        # --- RESOURCES ---
        self.res = {"O2": 100.0, "Power": 100.0, "Food": 50.0, "Metal": 100, "RP": 0, "Intel": 0}
        self.pop = {"Workers": 5, "Scientists": 2, "Soldiers": 0, "Spies": 0}
        
        # --- INFRASTRUCTURE & FLEET ---
        self.structures = {"Space Elevator": False, "Terraformer": False, "Spy Bureau": False}
        self.fleet = {"Tanks": 0, "Assault Ships": 0}
        
        # --- GENETICS & TECH ---
        self.active_genes = []  # Photo, Muscle, Brain, Oxy
        self.dna_stability = 100
        self.tech_level = 1
        self.omega_phases = 0
        
        # --- GALAXY ---
        self.turn_count = 0
        self.is_running = True
        self.galaxy = [
            Planet("Mars", "Mars Syndicate", 150),
            Planet("Europa", "Europa Union", 350),
            Planet("Titan", "Independent Raiders", 80),
            Planet("Callisto", "Ice Miners", 120)
        ]

    def update_tick(self):
        """Simulation Tick - Runs in background thread every 5s"""
        self.turn_count += 1
        
        # Apply Genetic Multipliers
        o2_mod = 0.7 if "OXY" in self.active_genes else 1.0
        food_mod = 0.5 if "PHOTO" in self.active_genes else 1.0
        rp_mod = 2.0 if "BRAIN" in self.active_genes else 1.0
        
        # Production
        self.res["RP"] += (self.pop["Scientists"] * 2) * rp_mod
        if self.structures["Space Elevator"]: self.res["Metal"] += 15
        if self.structures["Terraformer"]: self.res["O2"] += 8
        if self.structures["Spy Bureau"]: self.res["Intel"] += self.pop["Spies"] * 3
        
        # Consumption
        total_pop = sum(self.pop.values())
        self.res["O2"] -= (total_pop * 0.4) * o2_mod
        self.res["Food"] -= (total_pop * 0.3) * food_mod
        
        # Military Calculation
        muscle_mod = 2.0 if "MUSCLE" in self.active_genes else 1.0
        self.ground_power = ((self.pop["Soldiers"] * 5) + (self.fleet["Tanks"] * 25)) * muscle_mod
        self.space_power = (self.fleet["Assault Ships"] * 100)

        # Stability Loss
        self.dna_stability = 100 - (len(self.active_genes) * 15)

        if self.res["O2"] <= 0 or self.res["Food"] <= 0:
            self.is_running = False

    def get_layout(self):
        """Generates the Rich Live Dashboard"""
        table = Table(title=f"[bold cyan]COLONY ALPHA[/bold cyan] | Day {self.turn_count} | Tech: {self.tech_level}")
        table.add_column("Resource", style="yellow")
        table.add_column("Value", justify="right")
        
        for k, v in self.res.items():
            color = "green" if v > 20 else "red"
            table.add_row(k, f"[{color}]{int(v)}[/{color}]")
        
        table.add_row("DNA Stability", f"[bold {'green' if self.dna_stability > 70 else 'red'}]{self.dna_stability}%[/bold]")
        
        omega_bar = "█" * self.omega_phases + "░" * (4 - self.omega_phases)
        return Panel(table, subtitle=f"[blue]Omega Progress: {omega_bar}[/blue]", border_style="bright_blue")

    def save_game(self):
        data = {k: v for k, v in self.__dict__.items() if k != 'galaxy'}
        data['galaxy'] = [vars(p) for p in self.galaxy]
        with open("save_colony.json", "w") as f:
            json.dump(data, f, indent=4)
        rprint("\n[bold green][SYSTEM] Save Complete.[/bold green]")

    def load_game(self):
        try:
            with open("save_colony.json", "r") as f:
                data = json.load(f)
            for k, v in data.items():
                if k != 'galaxy': setattr(self, k, v)
            self.galaxy = [Planet(p['name'], p['faction'], p['power']) for p in data['galaxy']]
            for i, p in enumerate(self.galaxy):
                self.galaxy[i].conquered = data['galaxy'][i]['conquered']
                self.galaxy[i].rebellion_progress = data['galaxy'][i]['rebellion_progress']
            rprint("\n[bold green][SYSTEM] Load Complete.[/bold green]")
        except: rprint("\n[bold red][ERROR] No save file found.[/bold red]")

# --- GAME ACTIONS ---
def run():
    game = ColonyAlpha()
    
    def background_clock():
        while game.is_running:
            game.update_tick()
            time.sleep(5) # One 'Day' is 5 seconds

    threading.Thread(target=background_clock, daemon=True).start()

    with Live(game.get_layout(), refresh_per_second=1) as live:
        while game.is_running:
            live.update(game.get_layout())
            
            rprint("\n[b]1.[/b] Build [b]2.[/b] Military [b]3.[/b] Map [b]4.[/b] Genes [b]5.[/b] Intel [b]6.[/b] Save [b]Q.[/b] Quit")
            cmd = console.input("[bold magenta]Command > [/bold magenta]").lower()
            
            if cmd == 'q': break
            elif cmd == '1': # Infrastructure
                rprint("[yellow]A. Elevator (500m) B. Terraformer (400rp) C. Spy Bureau (200m)[/yellow]")
                sub = console.input("> ").upper()
                if sub == 'A' and game.res["Metal"] >= 500: game.structures["Space Elevator"] = True; game.res["Metal"] -= 500
            elif cmd == '2': # Military
                rprint("[yellow]A. Soldier (20f) B. Tank (60m) C. Ship (150m)[/yellow]")
                sub = console.input("> ").upper()
                if sub == 'B' and game.res["Metal"] >= 60: game.fleet["Tanks"] += 1; game.res["Metal"] -= 60
            elif cmd == '3': # Galaxy Map
                for i, p in enumerate(game.galaxy):
                    rprint(f"{i+1}. {p.name} [{'OWNED' if p.conquered else f'Garrison: {p.power}'}]")
                idx = console.input("Target: ")
                if idx.isdigit() and int(idx) <= len(game.galaxy):
                    p = game.galaxy[int(idx)-1]
                    if game.space_power > p.power: p.conquered = True; game.tech_level += 1
            elif cmd == '4': # Gene Lab
                rprint("[green]PHOTO (150rp) | BRAIN (300rp) | OXY (250rp) | MUSCLE (200rp)[/green]")
                gene = console.input("Enter Gene ID: ").upper()
                if gene in ["PHOTO", "BRAIN", "OXY", "MUSCLE"] and gene not in game.active_genes:
                    game.active_genes.append(gene); game.res["RP"] -= 200
            elif cmd == '6': game.save_game()

    if not game.is_running:
        rprint(Panel("[bold red]COLONY COLLAPSED[/bold red]\nOxygen or Food supplies reached zero."))

if __name__ == "__main__":
    run()
