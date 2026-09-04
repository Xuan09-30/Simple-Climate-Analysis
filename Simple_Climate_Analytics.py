import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import requests

sns.set_theme(style="white", palette="muted")

url = (
    "https://archive-api.open-meteo.com/v1/archive?"
    "latitude=3.1390&longitude=101.6869&"
    "start_date=2023-01-01&end_date=2023-12-31&"
    "daily=temperature_2m_mean,precipitation_sum&"
    "timezone=Asia%2FSingapore"
)

print("Fetching real historical weather data for Kuala Lumpur...")
response = requests.get(url).json()

daily_data = pd.DataFrame(response['daily'])
daily_data['time'] = pd.to_datetime(daily_data['time'])
daily_data['Month_Num'] = daily_data['time'].dt.month
daily_data['Month'] = daily_data['time'].dt.strftime('%b')

df_weather = daily_data.groupby(['Month_Num', 'Month']).agg({
    'precipitation_sum': 'sum',
    'temperature_2m_mean': 'mean'
}).reset_index()

df_weather.rename(columns={
    'precipitation_sum': 'Total_Rainfall_mm',
    'temperature_2m_mean': 'Avg_Temperature_C'
}, inplace=True)

correlation = df_weather['Total_Rainfall_mm'].corr(df_weather['Avg_Temperature_C'])
print(f"Pearson Correlation (Rainfall vs. Temperature): {correlation:.4f}\n")

def identify_monsoon_phase(month_num):
    if month_num in [11, 12, 1, 2, 3]:
        return "Northeast Monsoon"
    elif month_num in [5, 6, 7, 8, 9]:
        return "Southwest Monsoon"
    else:
        return "Inter-Monsoon"

df_weather['Monsoon_Phase'] = df_weather['Month_Num'].apply(identify_monsoon_phase)
avg_rainfall_per_monsoon = df_weather.groupby('Monsoon_Phase')['Total_Rainfall_mm'].mean().reset_index()

print("Average Rainfall per Monsoon Phase:")
print(avg_rainfall_per_monsoon)
print("\nGenerating chart...")

fig, ax_rain = plt.subplots(figsize=(11, 5.5))

bars = ax_rain.bar(
    df_weather['Month'], 
    df_weather['Total_Rainfall_mm'], 
    color='#2B5B84', alpha=0.85, width=0.5, label='Total Rainfall (mm)'
)
ax_rain.set_ylabel('Total Rainfall (mm)', color='#1A365D', fontsize=11, fontweight='bold', labelpad=10)
ax_rain.tick_params(axis='y', labelcolor='#1A365D')
ax_rain.set_xlabel('Month', fontsize=11, fontweight='bold', labelpad=10)

max_rain = df_weather['Total_Rainfall_mm'].max()
ax_rain.set_ylim(0, max_rain * 1.25)
ax_rain.grid(axis='y', linestyle=':', alpha=0.6)

ax_temp = ax_rain.twinx()
ax_temp.plot(
    df_weather['Month'], df_weather['Avg_Temperature_C'], 
    color='#D9381E', marker='o', markersize=6, linewidth=2, label='Average Temp (°C)'
)
ax_temp.set_ylabel('Average Temperature (°C)', color='#8B2110', fontsize=11, fontweight='bold', labelpad=10)
ax_temp.tick_params(axis='y', labelcolor='#8B2110')

min_temp = df_weather['Avg_Temperature_C'].min()
max_temp = df_weather['Avg_Temperature_C'].max()
ax_temp.set_ylim(min_temp - 0.8, max_temp + 1.2)

peak_idx = df_weather['Total_Rainfall_mm'].idxmax()
peak_rain_val = df_weather.loc[peak_idx, 'Total_Rainfall_mm']

ax_rain.annotate(
    'Peak Flood Risk',
    xy=(peak_idx, peak_rain_val),
    xytext=(peak_idx - 1.2, peak_rain_val + (max_rain * 0.08)),
    arrowprops=dict(facecolor='#1A365D', shrink=0.08, width=1.2, headwidth=6),
    fontsize=10, fontweight='bold', color='#1A365D'
)

plt.title('Kuala Lumpur Climate: Precipitation vs. Temperature (2023)', fontsize=13, fontweight='bold', pad=15)

lines_1, labels_1 = ax_rain.get_legend_handles_labels()
lines_2, labels_2 = ax_temp.get_legend_handles_labels()
ax_rain.legend(lines_1 + lines_2, labels_1 + labels_2, loc='upper left', framealpha=0.9)

sns.despine(ax=ax_rain, top=True)
sns.despine(ax=ax_temp, top=True, right=False)
plt.tight_layout()

plt.savefig('kl_climate_dual_axis.png', dpi=300, bbox_inches='tight')
plt.show()