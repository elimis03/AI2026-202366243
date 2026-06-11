import pandas as pd
import sys

if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')

df = pd.read_csv(r"C:\Users\user\.gemini\antigravity\brain\249a9ade-e931-4e78-a47f-45eb16e7a859\merged_data.csv")

# Filter for regions (exclude '전국') and gender '계'
df_regions = df[(df['region'] != '전국') & (df['gender'] == '계')]

print("="*60)
print("2024년 지역별 자살률 및 삶의 만족도 점수 (자살률 내림차순)")
print("="*60)
df_2024 = df_regions[df_regions['year'] == 2024].sort_values(by='suicide_rate', ascending=False)
print(df_2024[['region', 'suicide_rate', 'satisfaction_score', 'satisfaction_rate', 'dissatisfaction_rate']].to_string(index=False))

print("\n" + "="*60)
print("2020년 지역별 자살률 및 삶의 만족도 점수 (자살률 내림차순)")
print("="*60)
df_2020 = df_regions[df_regions['year'] == 2020].sort_values(by='suicide_rate', ascending=False)
print(df_2020[['region', 'suicide_rate', 'satisfaction_score', 'satisfaction_rate', 'dissatisfaction_rate']].to_string(index=False))

print("\n" + "="*60)
print("자살률 상승 폭이 가장 큰 지역 (2020년 대비 2024년)")
print("="*60)
df_pivot_sui = df_regions.pivot(index='region', columns='year', values='suicide_rate').reset_index()
df_pivot_sui['sui_change'] = df_pivot_sui[2024] - df_pivot_sui[2020]
print(df_pivot_sui[['region', 2020, 2024, 'sui_change']].sort_values(by='sui_change', ascending=False).to_string(index=False))

print("\n" + "="*60)
print("만족도 점수 상승 폭이 가장 큰 지역 (2020년 대비 2024년)")
print("="*60)
df_pivot_sat = df_regions.pivot(index='region', columns='year', values='satisfaction_score').reset_index()
df_pivot_sat['sat_change'] = df_pivot_sat[2024] - df_pivot_sat[2020]
print(df_pivot_sat[['region', 2020, 2024, 'sat_change']].sort_values(by='sat_change', ascending=False).to_string(index=False))
