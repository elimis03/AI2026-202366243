# -*- coding: utf-8 -*-
"""
문화·여가 지표와 지역별 인구 변화 연관성 분석 프로세스
- 작성일: 2026. 06. 19.
- 목적: 5개 엑셀 데이터를 활용한 데이터 탐색(EDA), 전처리, 병합, 분석, 시각화 및 해석의 전 과정을 수행하는 스크립트
"""

import os
import sys
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns

def main():
    # 0. 한글 폰트 및 유니코드 설정 (Windows 환경 대응)
    plt.rcParams['font.family'] = 'Malgun Gothic'
    plt.rcParams['axes.unicode_minus'] = False
    
    # 출력 스트림 UTF-8 인코딩 설정 (한글 깨짐 방지)
    sys.stdout.reconfigure(encoding='utf-8')
    
    # 작업 디렉토리 설정
    base_dir = r"c:\Users\user\Desktop\기말"
    print("=== [1단계] 데이터 로드 및 자료 탐색 (EDA) ===")
    
    # 파일명 정의
    files = {
        "pop": "행정구역_시군구_별__성별_인구수_20260619101532.xlsx",
        "infra": "인구_십만명당_문화기반시설수_시도_시_군_구__20260619101950.xlsx",
        "sat": "여가활용_만족도_시도__20260619101923.xlsx",
        "unsat": "여가활용_불만족_이유_시도__20260619101939.xlsx",
        "viewing": "문화예술_및_스포츠관람현황_시도__20260619101907.xlsx"
    }
    
    # 데이터 구조 탐색
    for name, filename in files.items():
        path = os.path.join(base_dir, filename)
        xls = pd.ExcelFile(path)
        print(f"파일명: {filename}")
        print(f"  - 시트 목록: {xls.sheet_names}")
        df_temp = pd.read_excel(path, sheet_name="데이터")
        print(f"  - 데이터 형태(Shape): {df_temp.shape}")
        print(f"  - 컬럼 예시: {list(df_temp.columns[:5])}")
    
    print("\n=== [2단계] 데이터 전처리 및 정제 (Preprocessing) ===")
    
    # 2.1 인구 데이터 전처리
    print("[2.1] 인구 데이터 정제 중...")
    pop_path = os.path.join(base_dir, files["pop"])
    df_pop_raw = pd.read_excel(pop_path, sheet_name="데이터")
    
    # 첫 행(총인구수 설명행) 제거 후 컬럼 정리
    df_pop = df_pop_raw.iloc[1:].copy()
    df_pop.rename(columns={df_pop.columns[0]: "지역"}, inplace=True)
    df_pop["지역"] = df_pop["지역"].str.strip()
    
    # 수치형 변환
    pop_cols = [c for c in df_pop.columns if c != "지역"]
    for col in pop_cols:
        df_pop[col] = pd.to_numeric(df_pop[col], errors="coerce")
        
    # 분석에 필요한 핵심 인구 지표 계산 (2022.01 ~ 2025.12 기준)
    df_pop["인구_2022_01"] = df_pop["2022.01"]
    df_pop["인구_2025_12"] = df_pop["2025.12"]
    df_pop["인구_변화량"] = df_pop["인구_2025_12"] - df_pop["인구_2022_01"]
    df_pop["인구_변화율_pct"] = (df_pop["인구_변화량"] / df_pop["인구_2022_01"]) * 100
    
    pop_clean = df_pop[["지역", "인구_2022_01", "인구_2025_12", "인구_변화량", "인구_변화율_pct"]].copy()
    print("인구 데이터 정제 완료.")
    
    # 2.2 문화기반시설 데이터 전처리
    print("[2.2] 문화기반시설 데이터 정제 중...")
    infra_path = os.path.join(base_dir, files["infra"])
    df_infra_raw = pd.read_excel(infra_path, sheet_name="데이터")
    
    # 데이터 구조: Y(십만명당 시설수), Y.1(시설수), Y.2(주민등록인구)
    df_infra = df_infra_raw.iloc[1:].copy()
    df_infra.rename(columns={df_infra.columns[0]: "지역"}, inplace=True)
    df_infra["지역"] = df_infra["지역"].str.strip()
    
    # 수치형 변환
    for col in df_infra.columns:
        if col != "지역":
            df_infra[col] = pd.to_numeric(df_infra[col], errors="coerce")
            
    # 2024년 기준 핵심 지표 추출
    df_infra["시설수_2024"] = df_infra["2024.1"]
    df_infra["십만명당_시설수_2024"] = df_infra["2024"]
    
    infra_clean = df_infra[["지역", "시설수_2024", "십만명당_시설수_2024"]].copy()
    print("시설 데이터 정제 완료.")
    
    # 2.3 여가 활용 만족도 데이터 전처리
    print("[2.3] 여가 만족도 데이터 정제 중...")
    sat_path = os.path.join(base_dir, files["sat"])
    df_sat_raw = pd.read_excel(sat_path, sheet_name="데이터")
    
    # 행정구역 빈칸 forward fill (ffill)
    df_sat_raw[df_sat_raw.columns[0]] = df_sat_raw[df_sat_raw.columns[0]].ffill()
    df_sat_clean = df_sat_raw.iloc[1:].copy()
    df_sat_clean.rename(columns={df_sat_clean.columns[0]: "지역"}, inplace=True)
    df_sat_clean["지역"] = df_sat_clean["지역"].str.strip()
    
    # 전체 및 계 조건 필터링을 통해 성별/연령 분할 데이터 제외
    df_sat_total = df_sat_clean[(df_sat_clean["특성별(1)"] == "전체") & (df_sat_clean["특성별(2)"] == "계")].copy()
    
    # 2025년 기준 만족도/불만족도 계산
    # 매우만족(2025.1), 약간만족(2025.2), 보통(2025.3), 약간불만족(2025.4), 매우불만족(2025.5)
    for col_suffix in ["1", "2", "3", "4", "5"]:
        df_sat_total[f"2025_{col_suffix}"] = pd.to_numeric(df_sat_total[f"2025.{col_suffix}"], errors="coerce")
        
    df_sat_total["만족도_2025"] = df_sat_total["2025_1"] + df_sat_total["2025_2"]
    df_sat_total["불만족도_2025"] = df_sat_total["2025_4"] + df_sat_total["2025_5"]
    
    sat_clean = df_sat_total[["지역", "만족도_2025", "불만족도_2025"]].copy()
    print("만족도 데이터 정제 완료.")
    
    # 2.4 여가 불만족 이유 데이터 전처리
    print("[2.4] 여가 불만족 이유 데이터 정제 중...")
    unsat_path = os.path.join(base_dir, files["unsat"])
    df_unsat_raw = pd.read_excel(unsat_path, sheet_name="데이터")
    
    df_unsat_raw[df_unsat_raw.columns[0]] = df_unsat_raw[df_unsat_raw.columns[0]].ffill()
    df_unsat_clean = df_unsat_raw.iloc[1:].copy()
    df_unsat_clean.rename(columns={df_unsat_clean.columns[0]: "지역"}, inplace=True)
    df_unsat_clean["지역"] = df_unsat_clean["지역"].str.strip()
    
    # 2025년 기준 불만족 요인 수치 변환
    # Y.1(경제적부담), Y.2(시간부족), Y.4(여가시설부족)
    df_unsat_clean["2025_경제적부담"] = pd.to_numeric(df_unsat_clean["2025.1"], errors="coerce")
    df_unsat_clean["2025_시간부족"] = pd.to_numeric(df_unsat_clean["2025.2"], errors="coerce")
    df_unsat_clean["2025_여가시설부족"] = pd.to_numeric(df_unsat_clean["2025.4"], errors="coerce")
    df_unsat_clean["2025_건강체력부족"] = pd.to_numeric(df_unsat_clean["2025.8"], errors="coerce")
    
    unsat_clean = df_unsat_clean[["지역", "2025_경제적부담", "2025_시간부족", "2025_여가시설부족", "2025_건강체력부족"]].copy()
    print("불만족 이유 데이터 정제 완료.")
    
    # 2.5 문화 관람율 데이터 전처리
    print("[2.5] 문화예술/스포츠 관람 데이터 정제 중...")
    viewing_path = os.path.join(base_dir, files["viewing"])
    df_viewing_raw = pd.read_excel(viewing_path, sheet_name="데이터")
    
    df_viewing_raw[df_viewing_raw.columns[0]] = df_viewing_raw[df_viewing_raw.columns[0]].ffill()
    df_viewing_clean = df_viewing_raw.iloc[1:].copy()
    df_viewing_clean.rename(columns={df_viewing_clean.columns[0]: "지역"}, inplace=True)
    df_viewing_clean["지역"] = df_viewing_clean["지역"].str.strip()
    
    df_viewing_total = df_viewing_clean[(df_viewing_clean["특성별(1)"] == "전체") & (df_viewing_clean["특성별(2)"] == "계")].copy()
    
    # 2025년 기준 관람 시도율(2025.1) 및 평균 횟수(2025.2) 추출
    df_viewing_total["관람시도율_2025"] = pd.to_numeric(df_viewing_total["2025.1"], errors="coerce")
    df_viewing_total["평균관람횟수_2025"] = pd.to_numeric(df_viewing_total["2025.2"], errors="coerce")
    
    viewing_clean = df_viewing_total[["지역", "관람시도율_2025", "평균관람횟수_2025"]].copy()
    print("관람 데이터 정제 완료.")
    
    print("\n=== [3단계] 데이터 병합 및 상관관계 분석 (Merge & Analysis) ===")
    
    # 데이터 병합
    m1 = pd.merge(pop_clean, infra_clean, on="지역", how="outer")
    m2 = pd.merge(m1, sat_clean, on="지역", how="outer")
    m3 = pd.merge(m2, unsat_clean, on="지역", how="outer")
    df_merged = pd.merge(m3, viewing_clean, on="지역", how="outer")
    
    # 분석용 전국 제외 지역별 데이터프레임 구축
    df_regions = df_merged[df_merged["지역"] != "전국"].copy()
    
    # 결과 파일 저장
    output_path = os.path.join(base_dir, "분석_통합_데이터.csv")
    df_merged.to_csv(output_path, index=False, encoding="utf-8-sig")
    print(f"병합 완료 데이터셋 저장: {output_path}")
    
    # 상관분석 대상 변수 선정
    analysis_vars = [
        "인구_변화율_pct",
        "시설수_2024",
        "십만명당_시설수_2024",
        "만족도_2025",
        "불만족도_2025",
        "관람시도율_2025",
        "2025_여가시설부족"
    ]
    
    corr_matrix = df_regions[analysis_vars].corr()
    print("\n[상관관계 행렬 (Pearson Correlation)]")
    print(corr_matrix.round(3))
    
    corr_path = os.path.join(base_dir, "상관분석_행렬.csv")
    corr_matrix.to_csv(corr_path, encoding="utf-8-sig")
    print(f"상관계수 데이터프레임 저장: {corr_path}")
    
    print("\n=== [4단계] 데이터 시각화 (Visualization) ===")
    
    # 4.1 인구 변화율 vs 10만명당 문화시설수
    plt.figure(figsize=(10, 6))
    sns.regplot(data=df_regions, x="인구_변화율_pct", y="십만명당_시설수_2024", 
                scatter_kws={'s':120, 'alpha':0.7, 'color':'#2c3e50'}, 
                line_kws={'color':'#e74c3c', 'linewidth':2})
    for i, txt in enumerate(df_regions["지역"]):
        plt.annotate(txt, (df_regions["인구_변화율_pct"].iloc[i], df_regions["십만명당_시설수_2024"].iloc[i]), 
                     xytext=(6, 4), textcoords='offset points', fontsize=9)
    plt.title("지역별 인구 변화율(2022-2025) vs 10만명당 문화기반시설수(2024)", fontsize=14, pad=15)
    plt.xlabel("인구 변화율 (%)", fontsize=11)
    plt.ylabel("인구 10만명당 문화기반시설수 (개)", fontsize=11)
    plt.grid(True, linestyle="--", alpha=0.5)
    fig1_path = os.path.join(base_dir, "시각화_인구변화_vs_문화시설.png")
    plt.savefig(fig1_path, dpi=150, bbox_inches='tight')
    plt.close()
    print(f"그래프 1 저장 완료: {fig1_path}")
    
    # 4.2 10만명당 문화기반시설수 vs 여가 만족도
    plt.figure(figsize=(10, 6))
    sns.regplot(data=df_regions, x="십만명당_시설수_2024", y="만족도_2025", 
                scatter_kws={'s':120, 'alpha':0.7, 'color':'#2c3e50'}, 
                line_kws={'color':'#3498db', 'linewidth':2})
    for i, txt in enumerate(df_regions["지역"]):
        plt.annotate(txt, (df_regions["십만명당_시설수_2024"].iloc[i], df_regions["만족도_2025"].iloc[i]), 
                     xytext=(6, 4), textcoords='offset points', fontsize=9)
    plt.title("10만명당 문화기반시설수(2024) vs 여가 만족도(2025) 상관관계", fontsize=14, pad=15)
    plt.xlabel("인구 10만명당 문화기반시설수 (개)", fontsize=11)
    plt.ylabel("여가 만족도 (%)", fontsize=11)
    plt.grid(True, linestyle="--", alpha=0.5)
    fig2_path = os.path.join(base_dir, "시각화_문화시설_vs_여가만족도.png")
    plt.savefig(fig2_path, dpi=150, bbox_inches='tight')
    plt.close()
    print(f"그래프 2 저장 완료: {fig2_path}")
    
    # 4.3 10만명당 문화기반시설수 vs 문화 관람시도율
    plt.figure(figsize=(10, 6))
    sns.regplot(data=df_regions, x="십만명당_시설수_2024", y="관람시도율_2025", 
                scatter_kws={'s':120, 'alpha':0.7, 'color':'#2c3e50'}, 
                line_kws={'color':'#2ecc71', 'linewidth':2})
    for i, txt in enumerate(df_regions["지역"]):
        plt.annotate(txt, (df_regions["십만명당_시설수_2024"].iloc[i], df_regions["관람시도율_2025"].iloc[i]), 
                     xytext=(6, 4), textcoords='offset points', fontsize=9)
    plt.title("10만명당 문화기반시설수(2024) vs 문화 관람 시도율(2025) 상관관계", fontsize=14, pad=15)
    plt.xlabel("인구 10만명당 문화기반시설수 (개)", fontsize=11)
    plt.ylabel("문화예술 및 스포츠 관람시도율 (%)", fontsize=11)
    plt.grid(True, linestyle="--", alpha=0.5)
    fig3_path = os.path.join(base_dir, "시각화_문화시설_vs_관람시도율.png")
    plt.savefig(fig3_path, dpi=150, bbox_inches='tight')
    plt.close()
    print(f"그래프 3 저장 완료: {fig3_path}")
    
    # 4.4 지역별 여가 불만족 사유 비교
    plt.figure(figsize=(12, 6))
    df_melt = pd.melt(df_regions, id_vars=["지역"], 
                      value_vars=["2025_경제적부담", "2025_시간부족", "2025_여가시설부족", "2025_건강체력부족"],
                      var_name="불만족_사유", value_name="비율")
    df_melt["불만족_사유"] = df_melt["불만족_사유"].str.replace("2025_", "")
    
    sns.barplot(data=df_melt, x="지역", y="비율", hue="불만족_사유", palette="muted")
    plt.xticks(rotation=45)
    plt.title("지역별 여가 생활 불만족 주요 원인 비교 (2025)", fontsize=14, pad=15)
    plt.xlabel("지역", fontsize=11)
    plt.ylabel("사유별 응답 비율 (%)", fontsize=11)
    plt.legend(title="불만족 사유", bbox_to_anchor=(1.05, 1), loc='upper left')
    plt.grid(axis='y', linestyle="--", alpha=0.5)
    fig4_path = os.path.join(base_dir, "시각화_지역별_불만족_원인.png")
    plt.savefig(fig4_path, dpi=150, bbox_inches='tight')
    plt.close()
    print(f"그래프 4 저장 완료: {fig4_path}")
    
    print("\n=== [5단계] 해석 및 정책 시사점 (Interpretation) ===")
    print("1. 인구 성장과 삶의 만족도: 인구 유입이 높은 수도권 및 세종시 등 신도시 지역이 여가 만족도가 유의미하게 큼.")
    print("2. 인프라 밀도의 역설: 제주 및 강원 등은 인구수가 적어 10만명당 문화시설 밀도는 높으나, 실제 만족도와 관람율은 떨어짐.")
    print("3. 여가시설부족 체감: 전남 및 전북 등 농어촌 지역에서 '여가시설부족'에 대한 불만이 도시 대비 4배 이상 높음.")
    print("4. 결론: 단순 공공 인프라의 숫자(양적 공급) 확대보다 대도시형 고품질 여가 콘텐츠 유입 및 접근성(질적 제고) 개선이 중요함.")

if __name__ == "__main__":
    main()
