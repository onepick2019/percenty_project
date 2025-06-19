import pandas as pd

try:
    # login_id 시트 확인
    df_login = pd.read_excel('percenty_id.xlsx', sheet_name='login_id')
    print('=== login_id 시트 ===') 
    print('컬럼명:', list(df_login.columns))
    if len(df_login) > 0:
        print('첫 번째 행:', df_login.iloc[0].to_dict())
    print()
    
    # 모든 시트명 확인
    excel_file = pd.ExcelFile('percenty_id.xlsx')
    sheets = excel_file.sheet_names
    print('모든 시트명:', sheets)
    print()
    
    # 두 번째 시트 확인 (보통 실제 데이터 시트)
    if len(sheets) > 1:
        sheet_name = sheets[1]
        df_data = pd.read_excel('percenty_id.xlsx', sheet_name=sheet_name)
        print(f'=== {sheet_name} 시트 ===')
        print('컬럼명:', list(df_data.columns))
        print('컬럼 인덱스와 이름:')
        for i, col in enumerate(df_data.columns):
            print(f'  {i}: {col}')
        
        if len(df_data) > 0:
            print('\n첫 번째 행 데이터:')
            for i, (col, val) in enumerate(df_data.iloc[0].items()):
                print(f'  {i} ({col}): {val}')
                
        # D열 확인 (인덱스 3)
        if len(df_data.columns) > 3:
            d_column = df_data.columns[3]
            print(f'\nD열 (인덱스 3) 컬럼명: {d_column}')
            print(f'D열 고유값: {df_data[d_column].unique()[:10]}')  # 처음 10개만
            
except Exception as e:
    print(f'오류 발생: {e}')