import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import os
import sys

# Ensure UTF-8 output
if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')

# Set up matplotlib for Korean font support
plt.rcParams['font.family'] = 'Malgun Gothic'
plt.rcParams['axes.unicode_minus'] = False

# Directories
artifact_dir = r"C:\Users\user\.gemini\antigravity\brain\249a9ade-e931-4e78-a47f-45eb16e7a859"
workspace_dir = r"c:\Users\user\Desktop\test folder"
merged_csv_path = os.path.join(artifact_dir, "merged_data.csv")

# Load data
df = pd.read_csv(merged_csv_path)

# Filter sets
df_regions = df[df['region'] != '전국'].copy()
df_nation = df[df['region'] == '전국'].copy()

# Print status
print("Data loaded successfully.")

# -------------------------------------------------------------
# Chart 4: Gender comparison (Nationwide)
# -------------------------------------------------------------
print("Generating Chart 4 (Gender Comparison)...")
fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 6))

# Subplot 1: Suicide Rate by Gender
df_nation_m = df_nation[df_nation['gender'] == '남자'].sort_values('year')
df_nation_f = df_nation[df_nation['gender'] == '여자'].sort_values('year')
df_nation_t = df_nation[df_nation['gender'] == '계'].sort_values('year')

ax1.plot(df_nation_m['year'], df_nation_m['suicide_rate'], color='#1f77b4', marker='o', linewidth=2.5, label='남성 자살률')
ax1.plot(df_nation_f['year'], df_nation_f['suicide_rate'], color='#ff7f0e', marker='s', linewidth=2.5, label='여성 자살률')
ax1.plot(df_nation_t['year'], df_nation_t['suicide_rate'], color='#2ca02c', marker='^', linewidth=2, linestyle=':', label='전체 평균')
ax1.set_title('성별 자살률 추이 (전국, 2020-2024)', fontsize=12, fontweight='bold', pad=10)
ax1.set_xlabel('연도', fontsize=10)
ax1.set_ylabel('자살률 (10만 명당 명)', fontsize=10)
ax1.set_xticks(df_nation_t['year'])
ax1.grid(True, linestyle=':', alpha=0.6)
ax1.legend(frameon=True, facecolor='white', edgecolor='none')

# Subplot 2: Satisfaction Score by Gender
ax2.plot(df_nation_m['year'], df_nation_m['satisfaction_score'], color='#1f77b4', marker='o', linewidth=2.5, label='남성 만족도 점수')
ax2.plot(df_nation_f['year'], df_nation_f['satisfaction_score'], color='#ff7f0e', marker='s', linewidth=2.5, label='여성 만족도 점수')
ax2.plot(df_nation_t['year'], df_nation_t['satisfaction_score'], color='#2ca02c', marker='^', linewidth=2, linestyle=':', label='전체 평균')
ax2.set_title('성별 삶의 만족도 점수 추이 (전국, 2020-2024)', fontsize=12, fontweight='bold', pad=10)
ax2.set_xlabel('연도', fontsize=10)
ax2.set_ylabel('삶의 만족도 점수 (5점 만점)', fontsize=10)
ax2.set_xticks(df_nation_t['year'])
ax2.grid(True, linestyle=':', alpha=0.6)
ax2.legend(frameon=True, facecolor='white', edgecolor='none')

plt.suptitle('남녀 성별 자살률 및 삶의 만족도 추이 비교', fontsize=15, fontweight='bold', y=0.98)
plt.tight_layout()
gender_chart_path = "gender_comparison_trends.png"
fig.savefig(os.path.join(artifact_dir, gender_chart_path), dpi=300)
fig.savefig(os.path.join(workspace_dir, gender_chart_path), dpi=300)
plt.close()
print("Saved Chart 4.")


# -------------------------------------------------------------
# Chart 5: Correlation Heatmap
# -------------------------------------------------------------
print("Generating Chart 5 (Correlation Heatmap)...")
# Select relevant columns for correlation
corr_cols = [
    'suicide_rate', 'satisfaction_score', 'satisfaction_rate', 'dissatisfaction_rate',
    '매우 만족', '약간 만족', '보통', '약간 불만족', '매우 불만족'
]

# We compute correlation on regions data (gender='계')
df_regions_t = df_regions[df_regions['gender'] == '계']
corr_matrix = df_regions_t[corr_cols].corr(method='pearson')

# Plot Heatmap using matplotlib
fig, ax = plt.subplots(figsize=(10, 8))
im = ax.imshow(corr_matrix, cmap='coolwarm', vmin=-1, vmax=1)

# Add colorbar
cbar = ax.figure.colorbar(im, ax=ax)
cbar.ax.set_ylabel("Pearson 상관계수", rotation=-90, va="bottom")

# Show all ticks and label them with the respective list entries
labels = ['자살률', '만족도 점수', '만족 비율', '불만족 비율', '매우 만족', '약간 만족', '보통', '약간 불만족', '매우 불만족']
ax.set_xticks(np.arange(len(labels)))
ax.set_yticks(np.arange(len(labels)))
ax.set_xticklabels(labels, rotation=45, ha="right", rotation_mode="anchor")
ax.set_yticklabels(labels)

# Loop over data dimensions and create text annotations.
for i in range(len(labels)):
    for j in range(len(labels)):
        val = corr_matrix.iloc[i, j]
        text = ax.text(j, i, f"{val:.2f}",
                       ha="center", va="center", 
                       color="white" if abs(val) > 0.4 else "black",
                       fontweight='bold' if i == 0 or j == 0 else 'normal')

ax.set_title("삶의 만족도 세부 항목과 자살률 상관관계 히트맵 (시도별 데이터 통합)", fontsize=14, fontweight='bold', pad=15)
plt.tight_layout()
heatmap_chart_path = "correlation_heatmap.png"
fig.savefig(os.path.join(artifact_dir, heatmap_chart_path), dpi=300)
fig.savefig(os.path.join(workspace_dir, heatmap_chart_path), dpi=300)
plt.close()
print("Saved Chart 5.")


# -------------------------------------------------------------
# Chart 6: Change Correlation (2020 vs 2024)
# -------------------------------------------------------------
print("Generating Chart 6 (Change Correlation)...")
# Calculate changes from 2020 to 2024 for each region
df_2020 = df_regions_t[df_regions_t['year'] == 2020].set_index('region')
df_2024 = df_regions_t[df_regions_t['year'] == 2024].set_index('region')

# Shared regions
regions_shared = df_2020.index.intersection(df_2024.index)

df_change = pd.DataFrame(index=regions_shared)
df_change['sui_change'] = df_2024.loc[regions_shared, 'suicide_rate'] - df_2020.loc[regions_shared, 'suicide_rate']
df_change['sat_change'] = df_2024.loc[regions_shared, 'satisfaction_score'] - df_2020.loc[regions_shared, 'satisfaction_score']
df_change['sat_rate_change'] = df_2024.loc[regions_shared, 'satisfaction_rate'] - df_2020.loc[regions_shared, 'satisfaction_rate']

# Calculate correlation of changes
corr_changes = df_change['sat_change'].corr(df_change['sui_change'])
corr_rate_changes = df_change['sat_rate_change'].corr(df_change['sui_change'])

print(f"Correlation between satisfaction score change and suicide rate change: {corr_changes:.4f}")
print(f"Correlation between satisfaction rate (%) change and suicide rate change: {corr_rate_changes:.4f}")

fig, ax = plt.subplots(figsize=(10, 7))
ax.scatter(df_change['sat_change'], df_change['sui_change'], color='#e377c2', s=100, alpha=0.8, edgecolors='none', label='지역별 변화량')

# Annotate regions
for region, row in df_change.iterrows():
    ax.annotate(region, (row['sat_change'], row['sui_change']), textcoords="offset points", xytext=(0,5), ha='center', fontsize=9)

# Trend line
m, b = np.polyfit(df_change['sat_change'], df_change['sui_change'], 1)
x_vals = np.linspace(df_change['sat_change'].min() - 0.05, df_change['sat_change'].max() + 0.05, 100)
ax.plot(x_vals, m*x_vals + b, color='#333333', linestyle='--', linewidth=1.5, label='변화량 추세선')

ax.set_title("2020년 대비 2024년 삶의 만족도 변화량 vs 자살률 변화량", fontsize=14, fontweight='bold', pad=15)
ax.set_xlabel("삶의 만족도 점수 변화 (2024년 점수 - 2020년 점수)", fontsize=11, labelpad=10)
ax.set_ylabel("자살률 변화 (2024년 자살률 - 2020년 자살률)", fontsize=11, labelpad=10)
ax.grid(True, linestyle=':', alpha=0.6)
ax.legend(frameon=True, facecolor='white', edgecolor='none')

# Text box
textstr = '\n'.join((
    f'변화량 상관계수: {corr_changes:.3f}',
    f'추세선 식: Δy = {m:.2f} * Δx + {b:.2f}'
))
props = dict(boxstyle='round', facecolor='wheat', alpha=0.3, edgecolor='none')
ax.text(0.05, 0.95, textstr, transform=ax.transAxes, fontsize=10, verticalalignment='top', bbox=props)

plt.tight_layout()
change_chart_path = "satisfaction_suicide_change_scatter.png"
fig.savefig(os.path.join(artifact_dir, change_chart_path), dpi=300)
fig.savefig(os.path.join(workspace_dir, change_chart_path), dpi=300)
plt.close()
print("Saved Chart 6.")

print("All new charts generated successfully!")
