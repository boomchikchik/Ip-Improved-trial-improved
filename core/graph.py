import matplotlib.pyplot as plt
from core.utils_cli import fetch_df
from styles import *

def plot_from_sql(sql, x_col, y_col, title="Graph", kind="bar"):
    """Fetch data from SQL and display matplotlib graph"""
    df = fetch_df(sql)
    
    if df.empty:
        print(f"{BRIGHT_RED}❌ No data found for graph.")
        return

    plt.figure(figsize=(9, 5))

    # Plot based on type
    if kind == "line":
        plt.plot(df[x_col], df[y_col], marker="o", linewidth=2)
    elif kind == "pie":
        plt.pie(df[y_col], labels=df[x_col], autopct="%.1f%%", startangle=90)
    elif kind == "barh":
        plt.barh(df[x_col], df[y_col])
    else:  # default bar
        plt.bar(df[x_col], df[y_col])

    plt.title(title, fontsize=14, fontweight='bold')
    
    # Add labels and formatting (except for pie)
    if kind != "pie":
        plt.xlabel(x_col.replace("_", " ").title())
        plt.ylabel(y_col.replace("_", " ").title())
        plt.xticks(rotation=45, ha="right")
        plt.grid(alpha=0.3, linestyle='--')

    plt.tight_layout()
    plt.show()

# def plot_from_sql(sql, x_col, y_col, title="Graph", kind="bar"):
#     """Simple plotter that directly displays graph from MySQL data."""
#     df = fetch_df(sql)
#     if df.empty:
#         print(f"{BRIGHT_RED}❌ No data found for graph.")
#         return

#     plt.figure(figsize=(9, 5))

#     if kind == "line":
#         plt.plot(df[x_col], df[y_col], marker="o", linewidth=2)
#     elif kind == "pie":
#         plt.pie(df[y_col], labels=df[x_col], autopct="1.2f%%", startangle=90)
#     else:  # bar
#         plt.bar(df[x_col], df[y_col])

#     plt.title(title)
#     if kind != "pie":
#         plt.xlabel(x_col.replace("_", " ").title()) 
#         plt.ylabel(y_col.replace("_", " ").title())
#         plt.xticks(rotation=45, ha="right") #ha stands for horizontal alignment
#         plt.grid(alpha=0.3)
#     print(x_col, y_col)
#     plt.tight_layout() #tight_layout to prevent cutoff
#     plt.show()
