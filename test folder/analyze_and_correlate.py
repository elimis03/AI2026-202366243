import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import os
import sys

# Ensure UTF-8 output
if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')

# Set up matplotlib for Korean font support
plt.rcParams['font.family'] = 'Malgun Gothic' # Standard Windows Korean font
plt.rcParams['axes.unicode_minus'] = False     # Don't break minus sign

folder_path = r"c:\Users\user\Desktop\test folder\자살률_삶만족도"
sat_file = os.path.join(folder_path, "삶의_만족도_시도__20260606195059.xlsx")
sui_file = os.path.join(folder_path, "인구십만명당_자살률_시도_시_군_구__20260606194913.xlsx")

# Output directory for artifacts
artifact_dir = r"C:\Users\user\.gemini\antigravity\brain\249a9ade-e931-4e78-a47f-45eb16e7a859"
os.makedirs(artifact_dir, exist_ok=True)

# Region mapping dictionary
region_map = {
    '전국': '전국',
    '서울특별시': '서울',
    '부산광역시': '부산',
    '대구광역시': '대구',
    '인천광역시': '인천',
    '광주광역시': '광주',
    '대전광역시': '대전',
    '울산광역시': '울산',
    '세종특별자치시': '세종',
    '경기도': '경기',
    '강원특별자치도': '강원',
    '충청북도': '충북',
    '충청남도': '충남',
    '전라북도': '전북',
    '전북특별자치도': '전북',
    '전라남도': '전남',
    '경상북도': '경북',
    '경상남도': '경남',
    '제주특별자치도': '제주',
    '제주도': '제주'
}

# Helper to compute Spearman correlation without scipy
def spearman_corr(s1, s2):
    return s1.rank().corr(s2.rank())

# 1. Process Life Satisfaction Data
print("Loading Life Satisfaction Data...")
df_sat_raw = pd.read_excel(sat_file)
sat_sub_headers = df_sat_raw.iloc[0]
df_sat = df_sat_raw.iloc[1:].copy()

# Forward fill for merged cells
df_sat['행정구역별(1)'] = df_sat['행정구역별(1)'].ffill()
df_sat['특성별(1)'] = df_sat['특성별(1)'].ffill()
df_sat['특성별(2)'] = df_sat['특성별(2)'].ffill()

# We only care about Overall and Gender breakdown
# For Satisfaction, 特性别(1) is '전체' or '성별'.
# In 특성별(2), '계' represents the total, '남자' and '여자' represent gender.
df_sat = df_sat[df_sat['특성별(2)'].isin(['계', '남자', '여자'])].copy()

# Melt the satisfaction data
id_cols = ['행정구역별(1)', '특성별(1)', '특성별(2)']
val_cols = [c for c in df_sat.columns if c not in id_cols]
df_sat_melt = df_sat.melt(id_vars=id_cols, value_vars=val_cols, var_name='col_name', value_name='val')

# Extract Year and Satisfaction Level
df_sat_melt['year'] = df_sat_melt['col_name'].apply(lambda x: int(float(x)))
df_sat_melt['sat_level'] = df_sat_melt['col_name'].map(sat_sub_headers)

# Clean values
df_sat_melt['val'] = pd.to_numeric(df_sat_melt['val'], errors='coerce')
df_sat_melt = df_sat_melt.dropna(subset=['val'])

# Pivot back to get satisfaction levels as columns
df_sat_pivot = df_sat_melt.pivot(index=['행정구역별(1)', '특성별(2)', 'year'], columns='sat_level', values='val').reset_index()

# Clean up columns and calculate indices
df_sat_pivot.rename(columns={'행정구역별(1)': 'region', '특성별(2)': 'gender'}, inplace=True)
df_sat_pivot['region'] = df_sat_pivot['region'].map(region_map)

# Calculate indices:
# Satisfaction Rate = 매우 만족 + 약간 만족
df_sat_pivot['satisfaction_rate'] = df_sat_pivot['매우 만족'] + df_sat_pivot['약간 만족']
# Dissatisfaction Rate = 약간 불만족 + 매우 불만족
df_sat_pivot['dissatisfaction_rate'] = df_sat_pivot['약간 불만족'] + df_sat_pivot['매우 불만족']
# Average Satisfaction Score (1-5 scale)
# 매우 만족=5, 약간 만족=4, 보통=3, 약간 불만족=2, 매우 불만족=1
df_sat_pivot['satisfaction_score'] = (
    df_sat_pivot['매우 만족'] * 5 +
    df_sat_pivot['약간 만족'] * 4 +
    df_sat_pivot['보통'] * 3 +
    df_sat_pivot['약간 불만족'] * 2 +
    df_sat_pivot['매우 불만족'] * 1
) / 100.0

print(f"Satisfaction data processed. Shape: {df_sat_pivot.shape}")


# 2. Process Suicide Rate Data
print("Loading Suicide Rate Data...")
df_sui_raw = pd.read_excel(sui_file)
sui_sub_headers = df_sui_raw.iloc[0]
df_sui = df_sui_raw.iloc[1:].copy()

# Melt suicide rate data
df_sui_melt = df_sui.melt(id_vars=['행정구역별(1)'], value_vars=[c for c in df_sui.columns if c != '행정구역별(1)'], var_name='col_name', value_name='suicide_rate')
df_sui_melt['year'] = df_sui_melt['col_name'].apply(lambda x: int(float(x)))
df_sui_melt['gender'] = df_sui_melt['col_name'].map(sui_sub_headers)

df_sui_melt.rename(columns={'행정구역별(1)': 'region'}, inplace=True)
df_sui_melt['region'] = df_sui_melt['region'].map(region_map)
df_sui_melt['suicide_rate'] = pd.to_numeric(df_sui_melt['suicide_rate'], errors='coerce')
df_sui_melt = df_sui_melt.dropna(subset=['suicide_rate'])

print(f"Suicide rate data processed. Shape: {df_sui_melt.shape}")


# 3. Merge Data
print("Merging data...")
merged_df = pd.merge(
    df_sat_pivot,
    df_sui_melt[['region', 'gender', 'year', 'suicide_rate']],
    on=['region', 'gender', 'year'],
    how='inner'
)
print(f"Merged Data Shape: {merged_df.shape}")

# Save merged data to CSV for record
merged_csv_path = os.path.join(artifact_dir, "merged_data.csv")
merged_df.to_csv(merged_csv_path, index=False, encoding='utf-8-sig')
print(f"Saved merged data to {merged_csv_path}")


# 4. Correlation Analysis
print("\n--- Correlation Analysis ---")

# We will analyze regional data (region != '전국') and nationwide data (region == '전국') separately.
df_regions = merged_df[merged_df['region'] != '전국'].copy()
df_nation = merged_df[merged_df['region'] == '전국'].copy()

# A. Pooled correlation (All regions, all years combined) - Overall
pooled_all = df_regions[df_regions['gender'] == '계']
corr_score_pears = pooled_all['satisfaction_score'].corr(pooled_all['suicide_rate'], method='pearson')
corr_score_spear = spearman_corr(pooled_all['satisfaction_score'], pooled_all['suicide_rate'])
corr_sat_pears = pooled_all['satisfaction_rate'].corr(pooled_all['suicide_rate'], method='pearson')
corr_dissat_pears = pooled_all['dissatisfaction_rate'].corr(pooled_all['suicide_rate'], method='pearson')

print(f"Pooled (Overall, N={len(pooled_all)}):")
print(f"  - Satisfaction Score vs Suicide Rate: Pearson={corr_score_pears:.4f}, Spearman={corr_score_spear:.4f}")
print(f"  - Satisfaction Rate (%) vs Suicide Rate: Pearson={corr_sat_pears:.4f}")
print(f"  - Dissatisfaction Rate (%) vs Suicide Rate: Pearson={corr_dissat_pears:.4f}")

# B. Yearly Cross-Sectional Correlation (across 17 regions, for each year)
print("\nYearly Cross-Sectional Correlation (N=17 regions per year, Gender='계'):")
yearly_corrs = []
for y in sorted(df_regions['year'].unique()):
    df_y = df_regions[(df_regions['year'] == y) & (df_regions['gender'] == '계')]
    p_corr_score = df_y['satisfaction_score'].corr(df_y['suicide_rate'], method='pearson')
    p_corr_sat = df_y['satisfaction_rate'].corr(df_y['suicide_rate'], method='pearson')
    p_corr_dissat = df_y['dissatisfaction_rate'].corr(df_y['suicide_rate'], method='pearson')
    print(f"  Year {y}:")
    print(f"    Satisfaction Score vs Suicide Rate: Pearson={p_corr_score:.4f}")
    print(f"    Satisfaction Rate vs Suicide Rate: Pearson={p_corr_sat:.4f}")
    print(f"    Dissatisfaction Rate vs Suicide Rate: Pearson={p_corr_dissat:.4f}")
    yearly_corrs.append({'year': y, 'p_corr_score': p_corr_score, 'p_corr_sat': p_corr_sat, 'p_corr_dissat': p_corr_dissat})
df_yearly_corrs = pd.DataFrame(yearly_corrs)

# C. Gender-specific Pooled Correlation
print("\nGender-specific Pooled Correlation (Regions only):")
for g in ['남자', '여자']:
    df_g = df_regions[df_regions['gender'] == g]
    p_corr = df_g['satisfaction_score'].corr(df_g['suicide_rate'], method='pearson')
    p_corr_sat = df_g['satisfaction_rate'].corr(df_g['suicide_rate'], method='pearson')
    p_corr_dissat = df_g['dissatisfaction_rate'].corr(df_g['suicide_rate'], method='pearson')
    print(f"  Gender: {g} (N={len(df_g)}):")
    print(f"    Satisfaction Score vs Suicide Rate: Pearson={p_corr:.4f}")
    print(f"    Satisfaction Rate vs Suicide Rate: Pearson={p_corr_sat:.4f}")
    print(f"    Dissatisfaction Rate vs Suicide Rate: Pearson={p_corr_dissat:.4f}")

# D. Nationwide Trend Correlation (N=5 years, '전국', '계')
print("\nNationwide Trend Correlation over 5 years (N=5):")
nation_total = df_nation[df_nation['gender'] == '계']
nation_corr = nation_total['satisfaction_score'].corr(nation_total['suicide_rate'], method='pearson')
print(f"  Nationwide Trend (2020-2024): Pearson={nation_corr:.4f}")
print("  Nationwide Data:")
print(nation_total[['year', 'satisfaction_score', 'satisfaction_rate', 'dissatisfaction_rate', 'suicide_rate']])


# 5. Visualizations
print("\nGenerating charts...")

# Chart 1: Scatter Plot of Satisfaction Score vs Suicide Rate (Pooled, 17 regions * 5 years = 85 points)
plt.figure(figsize=(10, 7))
colors = {2020: '#1f77b4', 2021: '#ff7f0e', 2022: '#2ca02c', 2023: '#d62728', 2024: '#9467bd'}
for y in sorted(df_regions['year'].unique()):
    df_y = df_regions[(df_regions['year'] == y) & (df_regions['gender'] == '계')]
    plt.scatter(df_y['satisfaction_score'], df_y['suicide_rate'], label=f'{y}년', color=colors[y], alpha=0.8, edgecolors='none', s=80)

# Add regression line for pooled data
x = pooled_all['satisfaction_score']
y = pooled_all['suicide_rate']
m, b = np.polyfit(x, y, 1)
plt.plot(x, m*x + b, color='#333333', linestyle='--', linewidth=1.5, label='선형 추세선')

# Annotate regions for 2024 to make it readable
df_2024 = df_regions[(df_regions['year'] == 2024) & (df_regions['gender'] == '계')]
for idx, row in df_2024.iterrows():
    plt.annotate(row['region'], (row['satisfaction_score'], row['suicide_rate']), textcoords="offset points", xytext=(0,5), ha='center', fontsize=9, alpha=0.8)

plt.title('삶의 만족도 점수와 자살률의 상관관계 (17개 시도, 2020-2024년)', fontsize=14, fontweight='bold', pad=15)
plt.xlabel('삶의 만족도 평균 점수 (5점 만점)', fontsize=12, labelpad=10)
plt.ylabel('인구 10만 명당 자살률 (명)', fontsize=12, labelpad=10)
plt.legend(frameon=True, facecolor='white', edgecolor='none')
plt.grid(True, linestyle=':', alpha=0.6)

# Text box with correlation coefficients
textstr = '\n'.join((
    f'전체 상관계수 (Pearson): {corr_score_pears:.3f}',
    f'전체 상관계수 (Spearman): {corr_score_spear:.3f}',
    f'추세선 식: y = {m:.2f}x + {b:.2f}'
))
props = dict(boxstyle='round', facecolor='wheat', alpha=0.3, edgecolor='none')
plt.gca().text(0.05, 0.05, textstr, transform=plt.gca().transAxes, fontsize=10, verticalalignment='bottom', bbox=props)

scatter_path = os.path.join(artifact_dir, "satisfaction_suicide_scatter.png")
plt.tight_layout()
plt.savefig(scatter_path, dpi=300)
plt.close()
print(f"Saved scatter plot to {scatter_path}")


# Chart 2: Nationwide Trend line chart comparing Satisfaction Score and Suicide Rate (Dual Axis)
fig, ax1 = plt.subplots(figsize=(10, 6))

color = '#1f77b4'
ax1.set_xlabel('연도', fontsize=12, labelpad=10)
ax1.set_ylabel('삶의 만족도 점수', color=color, fontsize=12, labelpad=10)
line1 = ax1.plot(nation_total['year'], nation_total['satisfaction_score'], color=color, marker='o', linewidth=2.5, label='삶의 만족도 점수 (좌축)')
ax1.tick_params(axis='y', labelcolor=color)
ax1.set_xticks(nation_total['year'])
ax1.grid(True, linestyle=':', alpha=0.5)

ax2 = ax1.twinx()  
color = '#d62728'
ax2.set_ylabel('자살률 (10만 명당 명)', color=color, fontsize=12, labelpad=10)
line2 = ax2.plot(nation_total['year'], nation_total['suicide_rate'], color=color, marker='s', linewidth=2.5, linestyle='--', label='자살률 (우축)')
ax2.tick_params(axis='y', labelcolor=color)

# Combine legends
lines = line1 + line2
labels = [l.get_label() for l in lines]
ax1.legend(lines, labels, loc='upper left', frameon=True, facecolor='white', edgecolor='none')

plt.title('전국 삶의 만족도 및 자살률 연도별 추이 (2020-2024년)', fontsize=14, fontweight='bold', pad=15)
trend_path = os.path.join(artifact_dir, "nationwide_trend.png")
plt.tight_layout()
plt.savefig(trend_path, dpi=300)
plt.close()
print(f"Saved trend plot to {trend_path}")


# Chart 3: Regional comparison for the latest year (2024)
df_regions_2024 = df_regions[(df_regions['year'] == 2024) & (df_regions['gender'] == '계')].sort_values(by='suicide_rate', ascending=True)

fig, ax1 = plt.subplots(figsize=(12, 6))

# Plot suicide rate as bars
color = '#e377c2'
bars = ax1.bar(df_regions_2024['region'], df_regions_2024['suicide_rate'], color=color, alpha=0.7, label='자살률 (좌축)', width=0.5)
ax1.set_ylabel('자살률 (10만 명당 명)', color=color, fontsize=12)
ax1.tick_params(axis='y', labelcolor=color)
ax1.set_xticks(range(len(df_regions_2024['region'])))
ax1.set_xticklabels(df_regions_2024['region'], rotation=45)

# Plot satisfaction score as line
ax2 = ax1.twinx()
color = '#1f77b4'
line = ax2.plot(df_regions_2024['region'], df_regions_2024['satisfaction_score'], color=color, marker='o', linewidth=2, label='삶의 만족도 (우축)')
ax2.set_ylabel('삶의 만족도 점수 (5점 만점)', color=color, fontsize=12)
ax2.tick_params(axis='y', labelcolor=color)

# Combine legends
plt.title('2024년 17개 시도별 자살률 및 삶의 만족도 비교', fontsize=14, fontweight='bold', pad=15)
fig.legend(loc="upper right", bbox_to_anchor=(1,1), bbox_transform=ax1.transAxes)

region_compare_path = os.path.join(artifact_dir, "regional_comparison_2024.png")
plt.tight_layout()
plt.savefig(region_compare_path, dpi=300)
plt.close()
print(f"Saved regional comparison plot to {region_compare_path}")

print("Analysis and charts generation complete!")
