import numpy as np

# Function to generate data
def python_generate_data(n):
    x = np.linspace(0, 10, n)
    y = np.sin(x)
    return x.tolist(), y.tolist()

# Check Python version
def python_version():
    import sys
    return sys.version
