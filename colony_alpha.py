import os, time, random, json, threading
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.live import Live
from rich.tree import Tree
from rich import print as rprint

console = Console()

# --- DATA: GENETIC MODULES ---
GENE_POOL = {
    'Senses': ['Eagle Eye (+Crit)', 'Sonar (Night Fight)', 'Thermal (Tracking)'],
    'Muscles': ['Myostatin Block (Str)', 'Hyper-Twitch (Spd)', 'Dense Fiber (HP)'],
    'Dermal': ['Chitin Plate (Def)', 'Photosynthetic (Regen)', 'Cloaking Skin'],
    'Organs': ['Dual Heart (Resilience)', 'Second Liver (Toxin Res)', 'Electric Sac'],
    'Neural': ['Tactical Link (Teamwork)', 'Fear Suppressant', 'Overclocked Ref']
}

BUILDING_TYPES = {
    'Bio-Vat': {'cost': 200, 'desc': 'Produces Soldiers & DNA Samples'},
    'Neural-Link': {'cost': 300, 'desc': 'Boosts Scientist Research Speed'},
    'Matter-Forge': {'cost': 500, 'desc': 'Produces Advanced Alloy'},
    'Void-Drill': {'cost': 450, 'desc': 'Extracts rare Space-Crystals'},
    'Orbital-Array': {'cost': 600, 'desc': 'Increases Scan distance/success'},
    'Shield-Generator': {'cost': 700, 'desc': 'Reduces Bombardment damage'}
}

class Soldier:
    def __init__(self, name):
        self.name = name
        self.hp = 100
        self.atk = 10
        self.genes = {cat: None for cat in GENE_POOL.keys()}
        self.tier = 1

class Planet:
    def __init__(self, name, tier):
        self.name = name
        self.tier = tier
        self.power = random.randint(100, 500) * tier
        self.resources = {'Metal': random.randint(200, 1000), 'DNA': random.randint(50, 200)}
        self.conquered = False

class VoyagerPrime:
    def __init__(self):
        # --- RESOURCES ---
        self.res = {'Metal': 500, 'RP': 0, 'Credits': 1000, 'O2': 100, 'Food': 100, 'Crystals': 0, 'DNA': 50}
        self.pop = {'Workers': 10, 'Scientists': 5, 'Spies': 2}
        self.barracks = [] 
        self.fleet = {'Tanks': 0}
        self.buildings = {} 
        self.turn = 1
        self.is_running = True
        self.msg_log = ["System Initialized. Welcome, Commander."]
        
        # --- GALAXY ---
        self.galaxy = [Planet(f"Sector-{i}", random.randint(1, 3)) for i in range(10)]
        self.orbiting = self.galaxy[0]

    def add_log(self, msg):
        self.msg_log.append(f"Day {self.turn}: {msg}")
        if len(self.msg_log) > 6: self.msg_log.pop(0)

    def update_tick(self):
        """Background heartbeat of the ship"""
        self.turn += 1
        # Production
        self.res['RP'] += self.pop['Scientists'] * (2 + self.buildings.get('Neural-Link', 0))
        self.res['Metal'] += self.pop['Workers'] * (1 + self.buildings.get('Matter-Forge', 0))
        if self.buildings.get('Void-Drill', 0) > 0: self.res['Crystals'] += self.buildings['Void-Drill'] * 5
        
        # Consumption
        total_pop = sum(self.pop.values()) + len(self.barracks)
        self.res['O2'] -= total_pop * 0.2
        self.res['Food'] -= total_pop * 0.1
        
        if self.res['O2'] <= 0: 
            self.add_log("[RED]OXYGEN DEPLETED. CRITICAL FAILURE.[/RED]")
            self.is_running = False

    def draw_dashboard(self):
        os.system('cls' if os.name == 'nt' else 'clear')
        
        # 1. Resource Table
        table = Table(title=f"VOYAGER PRIME | System: {self.orbiting.name}", title_style="bold green")
        table.add_column("Resource", style="cyan")
        table.add_column("Value", style="magenta")
        for k, v in self.res.items():
            color = "green" if v > 20 else "red"
            table.add_row(k, f"[{color}]{int(v)}[/{color}]")
        
        # 2. Army Composition
        army_tree = Tree("[bold yellow]Active Barracks")
        for s in self.barracks[:5]:
            active = sum(1 for g in s.genes.values() if g)
            army_tree.add(f"{s.name} (T{s.tier}) | HP: {s.hp} | DNA: {active}/5")
        if len(self.barracks) > 5: army_tree.add(f"... and {len(self.barracks)-5} more units")

        # Layout Split
        layout = Table.grid(expand=True)
        layout.add_column(ratio=1)
        layout.add_column(ratio=1)
        layout.add_row(Panel(table, border_style="green"), Panel(army_tree, border_style="yellow"))
        
        console.print(layout)
        console.print(Panel("\n".join(self.msg_log), title="Bridge Comms", border_style="white"))
        rprint("\n[b m]1.[/b m] Build [b m]2.[/b m] Bio-Lab [b m]3.[/b m] Foundry [b m]4.[/b m] Galaxy Map [b r]Q.[/b r] Quit")

    def bio_lab(self):
        """Genetic Engineering Menu"""
        os.system('cls' if os.name == 'nt' else 'clear')
        rprint(Panel("[bold green]DNA SPLICING CHAMBER[/bold green]"))
        if not self.barracks:
            rprint("[red]No units in stasis. Recruit at Foundry first.[/red]"); time.sleep(2); return
        
        rprint(f"DNA Samples: {self.res['DNA']}")
        for i, s in enumerate(self.barracks[:10]): print(f"{i+1}. {s.name}")
        
        choice = input("\nSelect unit index: ")
        if choice.isdigit() and int(choice) <= len(self.barracks):
            s = self.barracks[int(choice)-1]
            cats = list(GENE_POOL.keys())
            for i, cat in enumerate(cats): print(f"{i+1}. {cat}: {s.genes[cat] or 'Empty'}")
            
            cat_choice = input("\nSelect Category: ")
            if cat_choice.isdigit() and int(cat_choice) <= len(cats):
                cat_name = cats[int(cat_choice)-1]
                for i, gene in enumerate(GENE_POOL[cat_name]): print(f"{i+1}. {gene}")
                
                gene_idx = input("\nSelect Gene (Cost: 50 DNA): ")
                if gene_idx.isdigit() and int(gene_idx) <= 3 and self.res['DNA'] >= 50:
                    self.res['DNA'] -= 50
                    s.genes[cat_name] = GENE_POOL[cat_name][int(gene_idx)-1]
                    s.hp += 25
                    self.add_log(f"Spliced {s.genes[cat_name]} into {s.name}.")
        time.sleep(1)

def run():
    game = VoyagerPrime()
    # Live Ticker
    def clock():
        while game.is_running:
            game.update_tick()
            time.sleep(5)
    threading.Thread(target=clock, daemon=True).start()

    while game.is_running:
        game.draw_dashboard()
        cmd = console.input("\n[bold cyan]COMMAND > [/bold cyan]").lower()
        
        if cmd == 'q': break
        elif cmd == '1': # Infrastructure
            os.system('cls' if os.name == 'nt' else 'clear')
            rprint("[bold blue]ENGINEERING BAY[/bold blue]")
            for b, d in BUILDING_TYPES.items():
                lvl = game.buildings.get(b, 0)
                print(f"- {b} (Lv {lvl}) | Cost: {d['cost']*(lvl+1)} Metal")
            
            target = input("\nEnter Name to Upgrade: ").title()
            if target in BUILDING_TYPES:
                cost = BUILDING_TYPES[target]['cost'] * (game.buildings.get(target, 0)+1)
                if game.res['Metal'] >= cost:
                    game.res['Metal'] -= cost
                    game.buildings[target] = game.buildings.get(target, 0) + 1
                    game.add_log(f"Upgrade Complete: {target} Lv {game.buildings[target]}")
        elif cmd == '2': game.bio_lab()
        elif cmd == '3': # Foundry
            os.system('cls' if os.name == 'nt' else 'clear')
            print("1. Recruit Soldier (50 Food)\n2. Build Tank (150 Metal)")
            sub = input("> ")
            if sub == '1' and game.res['Food'] >= 50:
                game.res['Food'] -= 50
                game.barracks.append(Soldier(f"Unit-{len(game.barracks)+1}"))
                game.add_log("Soldier spawned in Bio-Vat.")
            time.sleep(1)

if __name__ == "__main__":
    run()
