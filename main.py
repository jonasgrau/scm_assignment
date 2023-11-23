import gurobipy as gp
from gurobipy import GRB

# Constants
days_per_month = 22
hours_per_shift = 8
normal_hourly_rate = 15
overtime_hourly_rate = 18
max_overtime_hours = 10
max_recruitment = 150
cost_hire = 800
cost_layoff = 1000
storage_cost_per_unit = 10
storage_threshold = 6000
materials_cost_per_unit = 20
selling_price_per_unit = 75
third_party_price_per_unit = 67
initial_inventory = 3000
penalty_cost_per_unit_demand = 12

# Updated demand data (for each month)
demand = [53000, 52000, 53000, 38000, 32000, 19000, 27000, 35000, 36000, 38000, 42000, 48000]

# Create model
model = gp.Model('TechMetalCorp')

# Variables
employees = model.addVars(days_per_month, lb=0, vtype=GRB.INTEGER, name='employees')
overtime = model.addVars(days_per_month, lb=0, vtype=GRB.INTEGER, name='overtime')
inventory = model.addVars(days_per_month+1, lb=0, vtype=GRB.INTEGER, name='inventory')
hiring = model.addVars(days_per_month, lb=0, vtype=GRB.INTEGER, name='hiring')
layoff = model.addVars(days_per_month, lb=0, vtype=GRB.INTEGER, name='layoff')
produce = model.addVars(days_per_month, lb=0, vtype=GRB.INTEGER, name='produce')
third_party_produce = model.addVars(days_per_month, lb=0, vtype=GRB.INTEGER, name='third_party_produce')
demand_fulfillment = model.addVars(days_per_month, lb=0, vtype=GRB.INTEGER, name='demand_fulfillment')

# Objective function: Maximize profit
model.setObjective(
    gp.quicksum((selling_price_per_unit - materials_cost_per_unit) * produce[t] - third_party_price_per_unit * third_party_produce[t] - storage_cost_per_unit * inventory[t+1] for t in range(days_per_month)) - penalty_cost_per_unit_demand * gp.quicksum(max(0, demand[t] - demand_fulfillment[t]) for t in range(days_per_month)),
    sense=GRB.MAXIMIZE
)

# Constraints
for t in range(days_per_month):
    model.addConstr(employees[t] * hours_per_shift + overtime[t] <= 8 * (1 + max_overtime_hours))
    model.addConstr(overtime[t] <= max_overtime_hours)
    model.addConstr(hiring[t] <= max_recruitment)
    model.addConstr(employees[t+1] == employees[t] + hiring[t] - layoff[t])
    model.addConstr(produce[t] == employees[t] * hours_per_shift)
    model.addConstr(third_party_produce[t] == max(0, demand[t] - produce[t]))
    model.addConstr(inventory[t+1] == inventory[t] + produce[t] - demand_fulfillment[t])

# Initial conditions
model.addConstr(inventory[0] == initial_inventory)

# Solve model
model.optimize()

# Display results
if model.status == GRB.OPTIMAL:
    optimal_profit = model.objVal
    print(f"Optimal annual profit: ${optimal_profit:.2f}")
else:
    print("No solution found.")
