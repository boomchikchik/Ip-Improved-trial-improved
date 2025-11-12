import matplotlib.pyplot as plt
from core.utils_cli import fetch_df
from styles import *

def plot_from_sql(sql, x_col, y_col, title="Graph", kind="bar"):
    """Fetch data from SQL and display matplotlib graph"""
    df = fetch_df(sql)
    
    if df.empty:
        print(f"{B_R}❌ No data found for graph.")
        return

    # Plot based on type
    if kind == "line": # Marker "o" for points, linewidth 2 for line thickness
        df.plot(x=x_col, y=y_col, marker="o", linewidth=2,kind="line")
    elif kind == "pie": # autopct for percentage display, startangle for rotation default 0
        # WHY USED labels=df[x_col]? BECAUSE IN PIE CHART, x_col REPRESENTS CATEGORIES WHICH ARE LABELED AROUND THE PIE
        df.plot(y=y_col, labels=df[x_col], autopct="%.1f%%", startangle=90, kind="pie")
    else:  # default bar
        df.plot(x=x_col, y=y_col, kind="bar")

    plt.title(title, fontsize=14, fontweight='bold') # the unit of fontsize is
    
    # Add labels and formatting (except for pie)
    if kind != "pie":
        plt.xlabel(x_col.replace("_", " ").title())
        plt.ylabel(y_col.replace("_", " ").title())
        plt.xticks(rotation=45, ha="right") #rotate x labels for readability,ha=horizontal alignment
        plt.grid(alpha=0.3, linestyle='--') # alpha for transparency, linestyle for line style

    plt.tight_layout()  # Adjust layout to prevent clipping
    plt.show()
