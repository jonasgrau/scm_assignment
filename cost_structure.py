import matplotlib.pyplot as plt

# Data for the cycle diagram
labels = [
    'Wages for Employees', 'Wages for Overtime', 'Costs of Hiring',
    'Layoff Costs', 'Storage Costs', 'Material Costs',
    'Third-Party Production Costs', 'Penalty Costs'
]
sizes = [12598080, 301536, 498400, 207000, 10600, 8566240, 2793096, 145536]

# Plotting
plt.figure(figsize=(8, 8))
plt.pie(sizes, labels=labels, autopct='%1.1f%%', startangle=140)
plt.axis('equal')  # Equal aspect ratio ensures that pie is drawn as a circle.

plt.title('Cost Distribution in a Cycle Diagram')
plt.show()
