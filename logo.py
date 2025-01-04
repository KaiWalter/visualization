import matplotlib.pyplot as plt
import numpy as np

# Create a black background
fig, ax = plt.subplots(figsize=(5, 5), dpi=100)
ax.set_facecolor('black')

# Draw a circular section of space
circle = plt.Circle((0.5, 0.5), 0.4, color='white', ec='None', alpha=0.1)
ax.add_artist(circle)

# Function to add stars
def draw_star(ax, x, y):
    ax.plot(x, y, 'o', color='yellow', markersize=np.random.rand()*10)

# Randomly place stars
np.random.seed(0)
for _ in range(50):
    x, y = np.random.rand(2)
    draw_star(ax, x, y)

# Add the letters DIP
stars_x = np.random.rand(3)
stars_y = np.random.rand(3)
for (x, y, letter) in zip(stars_x, stars_y, 'DIP'):
    ax.text(x, y, letter, fontsize=30, color='white', ha='center', va='center')

# Add a banner
ax.text(0.5, 0.1, 'Digital Integration Platforms', fontsize=15, color='white', ha='center', va='center', bbox=dict(facecolor='black', alpha=0.5))

# Set limits and hide axes
ax.set_xlim(0, 1)
ax.set_ylim(0, 1)
ax.axis('off')

# Save the image
plt.savefig('logo.png', format='png')
plt.close()
