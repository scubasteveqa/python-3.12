import numpy as np
import pandas as pd
from bokeh.layouts import column
from bokeh.models import Slider
from bokeh.plotting import figure, curdoc
import sys

# Ensure we're using Python 3.12
print(f"Running on Python: {sys.version}")

# Create a function to generate sine wave data
def generate_data(frequency):
    x = np.linspace(0, 4 * np.pi, 200)
    y = np.sin(frequency * x)
    return x, y

# Initialize Bokeh plot with sample data
x, y = generate_data(1)
plot = figure(title="Interactive Sine Wave", x_axis_label="X", y_axis_label="Y")
line = plot.line(x, y, line_width=2)

# Example 1: Python 3.12 f-string debugging in action
a, b = 10, 20
print(f"f-string debugging output: {a=} {b=} {result=a + b}")

# Example 2: Python 3.12 Exception Groups
def raise_exceptions():
    try:
        raise ExceptionGroup("Multiple Errors", [ValueError("Invalid value"), TypeError("Wrong type")])
    except* ValueError as e:
        print(f"Caught ValueError: {e}")
    except* TypeError as e:
        print(f"Caught TypeError: {e}")

raise_exceptions()

# Add a slider to adjust the frequency of the sine wave
slider = Slider(start=1, end=10, value=1, step=0.1, title="Frequency")

# Update the sine wave based on the slider's value
def update_data(attr, old, new):
    frequency = slider.value
    x, y = generate_data(frequency)
    line.data_source.data = {'x': x, 'y': y}

slider.on_change('value', update_data)

# Layout and add to document
layout = column(slider, plot)
curdoc().add_root(layout)
curdoc().title = "Bokeh App with Python 3.12"
