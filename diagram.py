import pandas as pd
import matplotlib.pyplot as plt

# Create a DataFrame from the data
data = {
    "Period": [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12],
    "Number of Employees": [250, 400, 502, 502, 296, 295, 295, 398, 409, 432, 477, 516],
    "Newly Recruited Employees": [150, 150, 102, 0, 0, 0, 0, 103, 11, 23, 45, 39],
    "Laid-off Employees": [0, 0, 0, 0, 206, 1, 0, 0, 0, 0, 0, 0]
}

df = pd.DataFrame(data)

# Plot the data
plt.figure(figsize=(12, 6))
plt.plot(df["Period"], df["Number of Employees"], marker='o', label='Number of Employees', color='blue')
plt.plot(df["Period"], df["Newly Recruited Employees"], marker='^', label='Newly Recruited Employees', color='green')
plt.plot(df["Period"], df["Laid-off Employees"], marker='v', label='Laid-off Employees', color='red')
plt.legend()
plt.xlabel("Period")
plt.ylabel("Number of Employees")
plt.title("Number of Employees Over Time")
plt.grid(True)
plt.show()
