from gurobipy import *
from itertools import combinations
# =============================
# Parameters
# =============================

# Planning period and time periods
T = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12]

# Demand per period
D = [53000, 52000, 53000, 38000, 32000, 19000, 27000, 35000, 36000, 38000, 42000, 48000]


# Selling price per piece
E = 75

# Working hours per piece
u = 2

# Number of regular working hours
h = 176 # 22*8

# Maximum number of overtime hours
o_max = 10

# Labor costs monthly
c_W = 2640  #15*176

# Recruitment costs
c_H = 800

# Lay-off costs
c_L = 1000

# Cost of materials
c_P = 20

# Warehousing costs
c_I =  10

# Shortage costs
c_S = 12

# Third-party procurement costs
c_C = 67

# Overtime costs
c_O = 18

# initializatioj
max_profit = -float('inf')
best_promo_count = None
best_promo_months = None
original_D = D.copy()

# consider 2 or 3 promotion months combinations
for promo_count in [2, 3]:
    for promo_months in combinations(T, promo_count):
        # reset demand
        D = original_D.copy()

        # adjust the demand accordingly
        for month in promo_months:
            D[month - 1] *= 1.40  # increase 40%
            if month < 12:
                D[month] *= 0.85  # decrease 15% for next month

model = Model()
model.setParam("MIPGap", 1e-10)

# =============================
# Variables
# =============================

# Number of workers in period t, (t = 0 -> initial period)
W = model.addVars([0] + T, name="W", vtype=GRB.INTEGER)

# Number of workers hired at period t
H = model.addVars(T, name="H", vtype=GRB.INTEGER)

# Number of workers laid off at period t
L = model.addVars(T, name="L", vtype=GRB.INTEGER)

# Production quantity in period t
P = model.addVars(T, name="P", vtype=GRB.INTEGER)

# Stock in period t, (or at the end of period t)
I = model.addVars([0] + T, name="I", vtype=GRB.INTEGER)

# Shortage in period t
S = model.addVars([0] + T, name="S", vtype=GRB.INTEGER)

# External procurement in period t
C = model.addVars(T, name="C", vtype=GRB.INTEGER)

# Overtime in period t
O = model.addVars(T, name="O", vtype=GRB.INTEGER)

# =============================
# Constraints
# =============================

# Set initial number of workers to 100
model.addConstr(W[0] == 100)

# Set the initial stock to 3000
model.addConstr(I[0] == 3000)

# Set the inventory in the last period to at least 500 units
#model.addConstr(I[6] >= 500)

# Set missing quantities to 0
model.addConstr(S[0] == 0)

# No shortages at the end of the planning period, meet all demand
model.addConstr(S[12] == 0)



# Number of workers
model.addConstrs(
    W[t] == W[t - 1] + H[t] - L[t] for t in T)

# Number of recruitment not exceed 150 per period
model.addConstrs(
    H[t] <= 150 for t in T
)

# Production capacity
model.addConstrs(
    P[t] <= (h/u) * W[t] + O[t]/u for t in T)

# Overtime is limited
model.addConstrs(
    O[t] <= o_max * W[t] for t in T)

# Warehousing 
model.addConstrs(
    I[t - 1] + P[t] + C[t] == D[t - 1] + S[t - 1] + I[t] - S[t] for t in T)

# Warehousing capacity of 6000 units
model.addConstrs(
    I[t] <= 6000 for t in T 
)


# t = 1 -> I[0]+P[1]+C[1] == D[0]+S[0]+I[1]-S[1]
# t = 6 -> I[5]+P[6]+C[6] == D[5]+S[5]+I[6]-S[6]


# Objective function: maximization of profit
model.setObjective(
            sum(E * D[t - 1] if t not in promo_months else E * 0.95 * D[t - 1] for t in T)
            - sum(c_W * W[t] + c_O * O[t] + c_H * H[t] + c_L * L[t]
                  + c_I * I[t] + c_S * S[t] + c_P * P[t] + c_C * C[t]
                  for t in T),
            GRB.MAXIMIZE)


model.optimize()

current_profit = model.objVal

# check if the current combi has the largest profit
if current_profit > max_profit:
    max_profit = current_profit
    best_promo_count = promo_count
    best_promo_months = promo_months

print("The optimal number of months with promotion is：", best_promo_count, "，best promotion months are：", best_promo_months, "，expected profit：", max_profit)

model.printAttr("X")

print("TechMetal, the optimal production plan,"
      "profit of {} monetary units".format(model.objVal))

for t in T:
    print("The number of employees in the period is {} {}.".format(t, W[t].X))
    if H[t].X != 0:
        print("The number of newly recruited"
              " Employees in period {} {}.".format(t, H[t].X))
    if L[t].X != 0:
        print("The number of laid-off"
              " Employees in period {} {}.".format(t, L[t].X))

print("The costs for employee salaries amount to more than the planning"
      " period to {} monetary units.".format(sum(c_W * W[t].X for t in T)))
print("The costs for overtime amount to more than the planning"
      " period to {} monetary units.".format(sum(c_O * O[t].X for t in T)))
print("The costs for new hires amount to over the planning"
      " period to {} monetary units.".format(sum(c_H * H[t].X for t in T)))
print("The costs for redundancies amount to more than the planning"
      " period to {} monetary units.".format(sum(c_L * L[t].X for t in T)))
print("The costs for warehousing amount to more than the planning"
      " period to {} monetary units.".format(sum(c_I * I[t].X for t in T)))
print("The costs for shortfalls amount to more than the planning"
      " period to {} monetary units.".format(sum(c_S * S[t].X for t in T)))
print("The costs for production material amount to more than the planning"
      " period to {} monetary units.".format(sum(c_P * P[t].X for t in T)))
print("The costs for external procurement amount to over the planning"
      " period to {} monetary units.".format(sum(c_C * C[t].X for t in T)))



for t in T:
  
    monthly_cost = c_W * W[t].X + c_O * O[t].X + c_H * H[t].X + c_L * L[t].X + c_I * I[t].X + c_S * S[t].X + c_P * P[t].X
    monthly_production = P[t].X
    if monthly_production > 0:
        unit_cost = monthly_cost / monthly_production
    else:
        unit_cost = 0

    print("The  month {} average cost per unit is {:.2f} ".format(t, unit_cost))
    print ("the procurement in month", t, "is", C[t].X)