import tkinter as tk
from tkinter import ttk
import ttkbootstrap as tb
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import seaborn as sns

# Load the hotel bookings dataset
file_path = 'hotel_bookings.csv'
hotel_data = pd.read_csv(file_path)

# Data Preprocessing
hotel_data['children'].fillna(0, inplace=True)
hotel_data['total_guests'] = hotel_data['adults'] + hotel_data['children'] + hotel_data['babies']
hotel_data['total_nights'] = hotel_data['stays_in_week_nights'] + hotel_data['stays_in_weekend_nights']
hotel_data['reservation_status_date'] = pd.to_datetime(hotel_data['reservation_status_date'])
hotel_data['booking_month'] = hotel_data['reservation_status_date'].dt.strftime('%B')

# Create main application window
app = tb.Window(themename='cosmo')
app.title('Hotel Bookings Dashboard')
app.state("zoomed")

# Create a frame for the filters
filter_frame = ttk.Frame(app)
filter_frame.pack(fill='x', padx=20, pady=10)

# Dropdown for hotel type
hotel_var = tk.StringVar()
hotel_choices = ['All'] + sorted(hotel_data['hotel'].unique().tolist())
hotel_var.set('All')

hotel_label = ttk.Label(filter_frame, text='Hotel Type', font=('Helvetica', 12, 'bold'))
hotel_label.grid(row=0, column=0, padx=10)

hotel_menu = ttk.Combobox(filter_frame, textvariable=hotel_var, values=hotel_choices, state='readonly', width=20)
hotel_menu.grid(row=0, column=1, padx=10)

# Dropdown for customer type
customer_var = tk.StringVar()
customer_choices = ['All'] + sorted(hotel_data['customer_type'].unique().tolist())
customer_var.set('All')

customer_label = ttk.Label(filter_frame, text='Customer Type', font=('Helvetica', 12, 'bold'))
customer_label.grid(row=0, column=2, padx=10)

customer_menu = ttk.Combobox(filter_frame, textvariable=customer_var, values=customer_choices, state='readonly', width=20)
customer_menu.grid(row=0, column=3, padx=10)

# Function to update the dashboard
def update_dashboard():
    # Filter the data based on selected values
    filtered_data = hotel_data.copy()
    if hotel_var.get() != 'All':
        filtered_data = filtered_data[filtered_data['hotel'] == hotel_var.get()]
    if customer_var.get() != 'All':
        filtered_data = filtered_data[filtered_data['customer_type'] == customer_var.get()]
    
    # Create a multi-plot figure with better spacing
    fig, axes = plt.subplots(2, 2, figsize=(20, 16), constrained_layout=True)
    sns.set_theme(style='whitegrid')

    # Plot 1: Average Daily Rate (ADR) Distribution
    sns.histplot(filtered_data['adr'], kde=True, bins=50, color='#2171b5', ax=axes[0, 0])
    axes[0, 0].set_title('Average Daily Rate (ADR) Distribution', fontsize=16, weight='bold', pad=20)
    axes[0, 0].set_ylabel('Frequency', fontsize=14)

    # Plot 2: Monthly Bookings
    sns.countplot(data=filtered_data, x='booking_month', 
                  order=pd.date_range('2023-01-01', '2023-12-01', freq='MS').strftime('%B'), 
                  ax=axes[0, 1], palette='Blues')
    axes[0, 1].set_title('Monthly Booking Trends', fontsize=16, weight='bold', pad=20)
    axes[0, 1].set_ylabel('Bookings', fontsize=14)

    # Plot 3: Lead Time Distribution
    sns.boxplot(data=filtered_data, x='hotel', y='lead_time', ax=axes[1, 0], palette='Blues')
    axes[1, 0].set_title('Lead Time by Hotel Type', fontsize=16, weight='bold', pad=20)
    axes[1, 0].set_ylabel('Lead Time (Days)', fontsize=14)

    # Plot 4: Cancellation Rate by Hotel Type
    cancel_rate = filtered_data.groupby('hotel')['is_canceled'].mean().reset_index()
    sns.barplot(data=cancel_rate, x='hotel', y='is_canceled', ax=axes[1, 1], palette='Blues')
    axes[1, 1].set_title('Cancellation Rate by Hotel Type', fontsize=16, weight='bold', pad=20)
    axes[1, 1].set_ylabel('Cancellation Rate', fontsize=14)

    # Clear previous plots and add the new one
    for widget in plot_frame.winfo_children():
        widget.destroy()
    canvas = FigureCanvasTkAgg(fig, master=plot_frame)
    canvas.draw()
    canvas.get_tk_widget().pack(fill='both', expand=True)

# Create a frame for plots
plot_frame = ttk.Frame(app)
plot_frame.pack(fill='both', expand=True, padx=20, pady=10)

# Add initial plot
update_dashboard()

# Bind the update function to the filter changes
hotel_menu.bind('<<ComboboxSelected>>', lambda e: update_dashboard())
customer_menu.bind('<<ComboboxSelected>>', lambda e: update_dashboard())

# Run the main loop
app.mainloop()
