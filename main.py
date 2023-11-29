from gurobipy import Model, GRB

# =============================
# Parameters
# =============================

# Demand per month
D = [53000, 52000, 53000, 38000, 32000, 19000, 27000, 35000, 36000, 38000, 42000, 48000]

# Selling price per unit
selling_price = 75

# Production cost per unit (material cost)
production_cost = 20

# Working hours required per unit
hours_per_unit = 2

# Normal and overtime hourly wage
normal_wage = 15
overtime_wage = 18

# Maximum overtime hours per month per employee
max_overtime = 10

# Hiring and layoff costs
hiring_cost = 800
layoff_cost = 1000

# Monthly storage cost per unit
storage_cost = 10

# Initial inventory
initial_inventory = 3000

# Storage capacity
storage_capacity = 6000

# Penalty cost per unit per month for unfulfilled demand
penalty_cost = 12

# Number of working days per month and hours per shift
working_days = 22
hours_per_shift = 8

# Current number of employees
current_employees = 100

# Maximum recruitment limit per month
max_recruitment = 150

# Third party production cost per unit
third_party_cost = 67



model = Model("TechMetal Corp Production Planning")


# =============================
# Variables
# =============================

production = model.addVars(12, vtype=GRB.INTEGER, name="production")
overtime = model.addVars(12, vtype=GRB.INTEGER, name="overtime")
hiring = model.addVars(12, vtype=GRB.INTEGER, name="hiring")
layoff = model.addVars(12, vtype=GRB.INTEGER, name="layoff")
inventory = model.addVars(12, vtype=GRB.INTEGER, name="inventory")
third_party = model.addVars(12, vtype=GRB.INTEGER, name="third_party")

# Initial inventory
inventory[0] = initial_inventory

# Objective function: Maximize profit
profit = sum((selling_price - production_cost) * production[m] -
             overtime[m] * overtime_wage -
             hiring[m] * hiring_cost -
             layoff[m] * layoff_cost -
             inventory[m] * storage_cost -
             third_party[m] * third_party_cost -
             penalty_cost * max(0, D[m] - (production[m] + inventory[m-1] + third_party[m]))
             for m in range(12))


model.setObjective(profit, GRB.MAXIMIZE)

# Constraints
for m in range(12):
    # Production capacity
    model.addConstr(production[m] <= (working_days * hours_per_shift + max_overtime) * current_employees)

    # Inventory balance
    if m > 0:
        model.addConstr(inventory[m] == inventory[m-1] + production[m] + third_party[m] - D[m])

    # Employee management
    model.addConstr(hiring[m] <= max_recruitment)
    model.addConstr(current_employees + hiring[m] - layoff[m] >= 0)

    # Overtime per employee
    model.addConstr(overtime[m] <= max_overtime * current_employees)

    # Storage capacity
    model.addConstr(inventory[m] <= storage_capacity)

# Solve the model
model.optimize()

# Print the solution
if model.status == GRB.OPTIMAL:
    print("Optimal annual profit: ${:.2f}".format(model.objVal))
    for m in range(12):
        print(f"Month {m+1}: Production = {production[m].X}, Inventory = {inventory[m].X}, Overtime = {overtime[m].X}, Hiring = {hiring[m].X}, Layoff = {layoff[m].X}, Third Party = {third_party[m].X}")
else:
    print("No optimal solution found")
