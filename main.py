import gurobipy as gp
from gurobipy import GRB, Model

# Data
monthly_demand = [53000, 52000, 53000, 38000, 32000, 19000, 27000, 35000, 36000, 38000, 42000, 48000]
num_months = len(monthly_demand)
initial_inventory = 3000
prod_capacity = 100  # number of employees
max_employees = 150  # max number of employees per month
hire_cost = 800
layoff_cost = 1000
prod_rate = 2  # hours per employee to make 1 unit
monthly_hours = 22 * 8  # 22 days at 8 hours per day
inv_cost = 10  # inventory holding cost per unit per month
inv_limit = 6000  # max inventory due to space constraints
mat_cost = 20  # materials cost per unit
sell_price = 75  # selling price per unit
ot_rate = 18  # overtime pay per hour
ot_limit = 10  # max overtime hours per employee
third_party_cost = 67  # cost to outsource per unit
penalty_cost = 12  # penalty per unit backordered per month

# Create model
model = Model("TechMetal")

# Decision variables
prod = model.addVars(num_months, name="Production")  # monthly production
inv = model.addVars(num_months, name="Inventory")  # end-of-month inventory
backorder = model.addVars(num_months, name="Backorder")  # backordered demand
employees = model.addVars(num_months, vtype=GRB.INTEGER, name="Employees")  # number of employees
overtime = model.addVars(num_months, name="Overtime")  # overtime hours used
outsource = model.addVars(num_months, name="Outsource")  # units outsourced
hire = model.addVars(num_months, vtype=GRB.INTEGER, name="Hire")
layoff = model.addVars(num_months, vtype=GRB.INTEGER, name="Layoff")

# Objective - maximize profit
profit = gp.quicksum(sell_price * prod[i] for i in range(num_months))
profit -= gp.quicksum(mat_cost * prod[i] for i in range(num_months))
profit -= gp.quicksum(inv_cost * inv[i] for i in range(num_months))
profit -= gp.quicksum(hire_cost * hire[i] for i in range(num_months))
profit -= gp.quicksum(layoff_cost * layoff[i] for i in range(num_months))
profit -= gp.quicksum(third_party_cost * outsource[i] for i in range(num_months))
profit -= gp.quicksum(penalty_cost * backorder[i] for i in range(num_months))
model.setObjective(profit, GRB.MAXIMIZE)

# Constraints
for i in range(num_months):
    # inventory balance
    if i == 0:
        model.addConstr(inv[i] == initial_inventory + prod[i] - monthly_demand[i] + backorder[i])
    else:
        model.addConstr(inv[i] == inv[i - 1] + prod[i] - monthly_demand[i] + backorder[i])

    # production capacity
    model.addConstr(prod[i] <= employees[i] * monthly_hours / prod_rate + overtime[i])

    # overtime limit per employee
    model.addConstr(overtime[i] <= employees[i] * ot_limit)

    # inventory limits
    model.addConstr(inv[i] <= inv_limit)

    # backorders fulfilled
    if i == num_months - 1:
        model.addConstr(backorder[i] == 0)

    # workforce dynamics
    if i > 0:
        model.addConstr(employees[i] == employees[i - 1] + hire[i] - layoff[i])

    # hiring limits
    model.addConstr(hire[i] <= max_employees)

model.optimize()

print('Maximum annual profit: $' + str(model.objVal))