


from django.shortcuts import render, redirect
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
from django.conf import settings
import os

def my_view(request):
    df = pd.read_csv("C:\\Users\\Deckmount\\Downloads\\DATA0637.TXT", header=None)
    
    timestamps = df.iloc[:, 0]
    breath_rate = df.iloc[:, 2]
    spo2 = df.iloc[:, 3]
    pulse = df.iloc[:, 4]
    body_position = df.iloc[:, 5]
    spo2_2 = df.iloc[:, 6]

    def filter_and_interpolate(data, min_val, max_val):
        filtered_data = data.copy().astype(float)
        filtered_data[~((data >= min_val) & (data <= max_val))] = np.nan
        return filtered_data

    def filter_and_smooth(data, min_val, max_val, window_size=15):
        filtered_data = data.copy().astype(float)
        filtered_data[~((data >= min_val) & (data <= max_val))] = np.nan
        return filtered_data.rolling(window=window_size, min_periods=1).mean()

    breath_rate_filtered = filter_and_smooth(breath_rate, 80, 100)
    spo2_filtered = filter_and_interpolate(spo2, 80, 100)
    spo2_2_filtered = filter_and_interpolate(spo2_2, 0, 200)
    pulse_filtered = filter_and_interpolate(pulse, 0, 150)
    body_position_filtered = filter_and_interpolate(body_position, 0, 4)

    window_size = 6000
    start_index = 10

    static_folder = os.path.join(settings.BASE_DIR, 'monitoring', 'static')
    if not os.path.exists(static_folder):   
        os.makedirs(static_folder)

    def save_plot(x, y, title, filename, color, start_index=0, window_size=50):
        end_index = min(start_index + window_size, len(x))
        plt.figure(figsize=(12, 4))
        plt.plot(x[start_index:end_index], y[start_index:end_index], color=color, label=title, linewidth=1)
        plt.title(title, fontsize=14)
        plt.grid(True, linestyle="--", alpha=0.8)

        nan_indices = y[start_index:end_index].isna()
        nan_timestamps = x[start_index:end_index][nan_indices]

        x_min, x_max = x.iloc[start_index], x.iloc[end_index - 1]
        visible_nan_timestamps = [t for t in nan_timestamps if x_min <= t <= x_max]

        for t in visible_nan_timestamps:
            plt.vlines(t, ymin=0, ymax=20, color='orange', alpha=0.8, linewidth=0.5)

        plt.ylim(0, 150 if y.isnull().all() else 120)
        plt.xlim(x_min, x_max)
        plt.xticks(fontsize=10, rotation=30)
        plt.yticks(fontsize=10)
        plt.legend()

        static_path = os.path.join(settings.STATICFILES_DIRS[0], f"{filename}.png")
        plt.savefig(static_path, bbox_inches="tight")
        plt.close()
    
    position_labels = {0: "S", 1: "R", 2: "P", 3: "L", 4: "U"}
    
    def save_position_plot(x, y, title, filename, color, start_index=0, window_size=50):
        end_index = min(start_index + window_size, len(x))
        plt.figure(figsize=(12, 4))
        plt.plot(x[start_index:end_index], y[start_index:end_index], color=color, label=title, linewidth=2, marker="o", markersize=6)
        plt.title(title, fontsize=14)
        plt.grid(True, linestyle="--", alpha=0.8)
        plt.yticks(ticks=list(position_labels.keys()), labels=list(position_labels.values()))
        plt.xlim(x.iloc[start_index], x.iloc[end_index - 1])
        plt.xticks(fontsize=10, rotation=30)
        plt.yticks(fontsize=12)
        plt.legend()

        static_path = os.path.join(settings.STATICFILES_DIRS[0], f"{filename}.png")
        plt.savefig(static_path, bbox_inches="tight")
        plt.close()
    
    save_plot(timestamps, breath_rate_filtered, "Breath Trend (Smoothed 80-100)", "breath_trend", "blue", start_index, window_size)
    save_plot(timestamps, spo2_filtered, "SpO2 Trend (Smoothed 80-100)", "spo2_trend", "red", start_index, window_size)
    save_plot(timestamps, spo2_2_filtered, "SpO2 Trend2 (Smoothed 80-100)", "spo2_trend2", "green", start_index, window_size)
    save_plot(timestamps, pulse_filtered, "Pulse Trend (Smoothed)", "pulse_trend", "purple", start_index, window_size)  
    save_position_plot(timestamps, body_position_filtered, "Body Position Trend (ULPRS)", "body_position_trend", "orange", start_index, window_size)

    print("Graphs saved with ULPRS labels and improved spacing!")

    return render(request, "main.html")