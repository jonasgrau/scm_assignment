from gurobipy import Model, GRB

# =============================
# Parameters
# =============================

# Demand per month
D = [53000, 52000, 53000, 38000, 32000, 19000, 27000, 35000, 36000, 38000, 42000, 48000]

# Months
months = ["January", "February", "March", "April", "May", "June", "July", "August", "September", "October", "November", "December"]

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

# Number of units produced each month
production = model.addVars(12, lb=0, vtype=GRB.INTEGER, name="production")

# Total overtime hours worked by all employees each month
overtime = model.addVars(12, lb=0, vtype=GRB.INTEGER, name="overtime")

# Number of new employees hired each month
hiring = model.addVars(12, lb=0, ub=150, vtype=GRB.INTEGER, name="hiring")

# Number of employees laid off each month
layoff = model.addVars(12, lb=0, vtype=GRB.INTEGER, name="layoff")

# Number of units in inventory at the end of each month
inventory = model.addVars(12, lb=0, vtype=GRB.INTEGER, name="inventory")

# Number of units purchased from third-party suppliers each month
third_party = model.addVars(12, lb=0, vtype=GRB.INTEGER, name="third_party")

# Quantity of demand that is not met each month
unfulfilled_demand = model.addVars(12, lb=0, vtype=GRB.INTEGER, name="unfulfilled_demand")


# Update the model to integrate new variables
model.update()

# Objective function
profit = sum((selling_price - production_cost) * production[m] -
             overtime[m] * overtime_wage -
             hiring[m] * hiring_cost -
             layoff[m] * layoff_cost -
             inventory[m] * storage_cost -
             third_party[m] * third_party_cost -
             penalty_cost * unfulfilled_demand[m]
             for m in range(12))

model.setObjective(profit, GRB.MAXIMIZE)

# =============================
# Constraints
# =============================

for m in range(12):
    # Production capacity
    model.addConstr(production[m] <= (working_days * hours_per_shift + max_overtime) * (current_employees + sum(hiring[i] - layoff[i] for i in range(m+1))))

    # Inventory balance and initial inventory handling
    if m == 0:
        model.addConstr(inventory[m] == initial_inventory + production[m] + third_party[m] - D[m])
    else:
        model.addConstr(inventory[m] == inventory[m-1] + production[m] + third_party[m] - D[m])

    # Unfulfilled demand calculation
    model.addConstr(unfulfilled_demand[m] >= D[m] - (production[m] + inventory[m] + third_party[m]))

    # Employee management
    model.addConstr(hiring[m] <= max_recruitment)
    model.addConstr(current_employees + sum(hiring[i] - layoff[i] for i in range(m+1)) >= 0)

    # Overtime per employee
    model.addConstr(overtime[m] <= max_overtime * (current_employees + sum(hiring[i] - layoff[i] for i in range(m+1))))

    # Storage capacity
    model.addConstr(inventory[m] <= storage_capacity)

# Solve the model
model.optimize()

# Print the solution
if model.status == GRB.OPTIMAL:
    print("Optimal annual profit: ${:.2f}".format(model.objVal))
    for m in range(12):
        print(f"{months[m]} : Production = {production[m].X}, Inventory = {inventory[m].X}, Overtime = {overtime[m].X}, Hiring = {hiring[m].X}, Layoff = {layoff[m].X}, Third Party = {third_party[m].X}, Unfulfilled Demand = {unfulfilled_demand[m].X}")
else:
    print("No optimal solution found")