import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import sys

# Ensure Python version 3.12
st.title("Python 3.12 Features in a Streamlit App")

st.subheader("Python Version")
st.write(f"Current Python version: {sys.version}")

# Example 1: Enhanced Pattern Matching
st.subheader("1. Enhanced Pattern Matching (Python 3.12)")

def handle_response(response):
    match response:
        case {"status": 200, "data": data}:
            return f"Success: {data}"
        case {"status": 404}:
            return "Not Found"
        case {"status": 500}:
            return "Server Error"
        case _:
            return "Unknown response"

response = {"status": 200, "data": "Here is some sample data!"}
st.write(f"Response: {handle_response(response)}")

# Example 2: f-string Debugging in Python 3.12
st.subheader("2. f-string Debugging in Python 3.12")
a = 10
b = 20
result = a + b
st.write(f"f-string debugging output: {a=} {b=} {result=}")

# Example 3: Exception Groups
st.subheader("3. Exception Groups in Python 3.12")
def raise_multiple_exceptions():
    try:
        raise ExceptionGroup("Errors", [ValueError("Invalid value"), TypeError("Invalid type")])
    except* ValueError as e:
        return f"Caught ValueError: {e}"
    except* TypeError as e:
        return f"Caught TypeError: {e}"

st.write(raise_multiple_exceptions())

# Pandas and Matplotlib Example
st.subheader("4. Pandas and Matplotlib Example")
data = pd.DataFrame({
    'X': np.linspace(0, 10, 100),
    'Y': np.sin(np.linspace(0, 10, 100))
})

st.line_chart(data)

# Matplotlib plot
fig, ax = plt.subplots()
ax.plot(data['X'], data['Y'], label='sin(x)')
ax.set_xlabel('X')
ax.set_ylabel('Y')
ax.set_title('Sin Wave')
ax.legend()

st.pyplot(fig)
