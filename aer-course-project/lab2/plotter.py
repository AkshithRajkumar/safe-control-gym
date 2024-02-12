import pandas as pd
import matplotlib.pyplot as plt

# Read CSV file into a DataFrame
df = pd.read_csv('AcPos.csv')

fig, ax = plt.subplots()
# Plot first four columns in one graph
# plt.figure(figsize=(10, 5))
for column in df.columns[:4]:
    ax.plot(df[column], label=column)
ax.legend()
ax.set_title('Error v/s Time')
ax.set_xlabel('Time')
ax.set_ylabel('Error')
ax.grid(True)
# y_min = df.iloc[:, :4].values.min()
# y_max = df.iloc[:, :4].values.max()
# ax.set_ylim(0, 1)
plt.show()

# Plot rest four columns in another graph
# plt.figure(figsize=(10, 5))
# for column in df.columns[4:]:
#     plt.plot(df[column], label=column)
plt.plot(df[df.columns[4]], label=df.columns[4])
plt.plot(df[df.columns[8]], label=df.columns[8])
plt.legend()
plt.title('Current v/s Desired X')
plt.xlabel('Value')
plt.ylabel('Time')
plt.grid(True)
plt.show()

# plt.figure(figsize=(10, 5))
# for column in df.columns[4:]:
#     plt.plot(df[column], label=column)
plt.plot(df[df.columns[5]], label=df.columns[5])
plt.plot(df[df.columns[9]], label=df.columns[9])
plt.legend()
plt.title('Current v/s Desired Y')
plt.xlabel('Value')
plt.ylabel('Time')
plt.grid(True)
plt.show()

# plt.figure(figsize=(10, 5))
# for column in df.columns[4:]:
#     plt.plot(df[column], label=column)
plt.plot(df[df.columns[6]], label=df.columns[6])
plt.plot(df[df.columns[10]], label=df.columns[10])
plt.legend()
plt.title('Current v/s Desired Z')
plt.xlabel('Value')
plt.ylabel('Time')
plt.grid(True)
plt.show()

# plt.figure(figsize=(10, 5))
# for column in df.columns[4:]:
#     plt.plot(df[column], label=column)
plt.plot(df[df.columns[7]], label=df.columns[7])
plt.plot(df[df.columns[11]], label=df.columns[11])
plt.legend()
plt.title('Current v/s Desired Yaw')
plt.xlabel('Value')
plt.ylabel('Time')
plt.grid(True)
plt.show()