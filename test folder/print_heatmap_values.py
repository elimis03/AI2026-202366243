import pandas as pd
import os
import sys

if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')

merged_csv_path = r"C:\Users\user\.gemini\antigravity\brain\249a9ade-e931-4e78-a47f-45eb16e7a859\merged_data.csv"
df = pd.read_csv(merged_csv_path)

# Filter regions only, gender='계'
df_regions_t = df[(df['region'] != '전국') & (df['gender'] == '계')]

corr_cols = [
    'suicide_rate', 'satisfaction_score', 'satisfaction_rate', 'dissatisfaction_rate',
    '매우 만족', '약간 만족', '보통', '약간 불만족', '매우 불만족'
]
corr_matrix = df_regions_t[corr_cols].corr(method='pearson')

print("="*60)
print("자살률과 삶의 만족도 세부 항목 간 상관계수 (Pearson)")
print("="*60)
print(corr_matrix['suicide_rate'].to_string())
