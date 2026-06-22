import pandas as pd
import numpy as np
from datetime import datetime

main = 'S26U'
base = 'S25U'
n = 89
# main = 'A57'
# base = 'A56'
# n = 60
marketing_name = f'Galaxy {main}'
last_updated = datetime.now().strftime("%d %b %Y")

base_dir = rf".\{main} Data\{n}days"
file_path = rf"{base_dir}\raw_main.xlsx"
comparison_path_overall = rf"{base_dir}\overall.xlsx"
comparison_path_domestic = rf"{base_dir}\domestic.xlsx"
comparison_path_export = rf"{base_dir}\export.xlsx"
file_base_path = rf"{base_dir}\raw_base.xlsx"
asrdata_path = rf"{base_dir}\asr_compare.xlsx"
msclist_path = r".\MSC_list.xlsx"

def get_data():
    df = pd.read_excel(file_path, skiprows=8)
    df.columns = df.columns.str.replace('\n', ' ')
    df = df.replace("착하판정", "Return")
    df['ASC Code'] = df['ASC Code'].replace([np.inf, -np.inf], 0)  # Replace inf with 0
    df['TR NO'] = df['TR NO'].astype(int)
    df['ASC Code'] = np.where(df['ASC Code'].isna(), df['TR NO'], df['ASC Code'])
    # df['ASC Code'] = df['ASC Code'].fillna(0)  # Replace NaN with 0
    df['ASC Code'] = df['ASC Code'].astype(int)  # float64 -> int64
    df['Repair Description'] = df['Repair Description'].fillna('Return')
    df["Service Date"] = df["Service Date"].astype(str)
    df['Date'] = pd.to_datetime("20" + df['Service Date'], format='%Y%m%d', errors='coerce')
    df = df.dropna(subset=['Date'])  # Remove invalid dates
    df3, sell_out_domestic, launch_date = get_domestic_comparison_data()
    if not isinstance(launch_date, pd.Timestamp):
        launch_date = pd.to_datetime(launch_date)
    df['Day'] = (df['Date'] - launch_date).dt.days + 1
    df['week_num'] = df['Date'].dt.isocalendar().week
    df['WK'] = 'WK ' + df['week_num'].astype(str)
    return df

def get_overall_comparison_data():
    df2 = pd.read_excel(comparison_path_overall, sheet_name='Sheet2')
    df2.columns = [str(col) for col in df2.columns]
    df2 = df2.fillna('')
    df2 = df2.rename(columns={
        df2.columns[2]: f"{main}",
        df2.columns[3]: f"{base}"
    })
    sell_out_str = df2.iloc[3, 2]
    sell_out_overall = int(sell_out_str.replace(',', ''))
    improvement = df2.iloc[6, 2]
    if improvement and '↓' in improvement:
        improvement = f"<span style='color: #2ecc71;'>{improvement}</span>"
    else:
        improvement = f"<span style='color: #e55039;'>{improvement}</span>"
    df2.iloc[6, 2] = improvement
    return df2, improvement, sell_out_overall

def get_domestic_comparison_data():
    df3 = pd.read_excel(comparison_path_domestic, sheet_name='Sheet2')
    df3.columns = [str(col) for col in df3.columns]
    df3 = df3.fillna('')
    df3 = df3.rename(columns={
        df3.columns[2]: f"{main}",
        df3.columns[3]: f"{base}"
    })
    sell_out_str = df3.iloc[3, 2]
    sell_out_domestic = int(sell_out_str.replace(',', ''))
    improvement = df3.iloc[6, 2]
    if improvement and '↓' in improvement:
        improvement = f"<span style='color: #2ecc71;'>{improvement}</span>"
    else:
        improvement = f"<span style='color: #e55039;'>{improvement}</span>"
    df3.iloc[6, 2] = improvement
    launch_date = df3.iloc[1,2]
    return df3, sell_out_domestic, launch_date

df3, sell_out_domestic, launch_date = get_domestic_comparison_data()

def get_export_comparison_data():
    df4 = pd.read_excel(comparison_path_export, sheet_name='Sheet2')
    df4.columns = [str(col) for col in df4.columns]
    df4 = df4.fillna('')
    df4 = df4.rename(columns={
        df4.columns[2]: f"{main}",
        df4.columns[3]: f"{base}"
    })
    sell_out_str = df4.iloc[3, 2]
    sell_out_export = int(sell_out_str.replace(',', ''))
    improvement = df4.iloc[6, 2]
    if improvement and '↓' in improvement:
        improvement = f"<span style='color: #2ecc71;'>{improvement}</span>"
    else:
        improvement = f"<span style='color: #e55039;'>{improvement}</span>"
    df4.iloc[6, 2] = improvement
    return df4, sell_out_export

def get_base_data():
    df_base = pd.read_excel(file_base_path, skiprows=9)
    df_base.columns = df_base.columns.str.replace('\n', ' ')
    df_base = df_base.replace("착하판정", "Return")
    df_base['ASC Code'] = df_base['ASC Code'].replace([np.inf, -np.inf], 0)  # Replace inf with 0
    df_base['ASC Code'] = df_base['ASC Code'].fillna(0)  # Replace NaN with 0
    df_base['ASC Code'] = df_base['ASC Code'].astype(int)  # float64 -> int64
    df_base['Repair Description'] = df_base['Repair Description'].fillna('Return')
    df_base["Service Date"] = df_base["Service Date"].astype(str)
    df_base['Date'] = pd.to_datetime("20" + df_base['Service Date'], format='%Y%m%d', errors='coerce')
    df_base = df_base.dropna(subset=['Date'])  # Remove invalid dates
    df_base['week_num'] = df_base['Date'].dt.isocalendar().week
    df_base['WK'] = 'WK ' + df_base['week_num'].astype(str)
    return df_base

def get_asrdata():
    df5 = pd.read_excel(asrdata_path, skiprows=9, header=None)
    df5 = df5.iloc[:, :5]
    df5.columns = ["Days", "main_service", "main_sell_out", "base_service", "base_sell_out"]
    df5 = df5.dropna(subset=['Days'])
    df5["Day"] = df5["Days"].astype(str).str.split().str[0].astype(int)
    df5 = df5[df5["Day"] >= 1]
    numeric_cols = ["main_service", "main_sell_out", "base_service", "base_sell_out"]
    for col in numeric_cols:
        df5[col] = pd.to_numeric(df5[col], errors='coerce')
    df5["main_ratio"] = (
        (df5["main_service"] / df5["main_sell_out"] * 100)
        .round(3)
        .apply(lambda x: "{:.3f}".format(x))
    )
    df5['main_ratio'] = pd.to_numeric(df5['main_ratio'], errors='coerce')

    df5["base_ratio"] = (
        (df5["base_service"] / df5["base_sell_out"] * 100)
        .round(3)
        .apply(lambda x: "{:.3f}".format(x))
    )
    df5['base_ratio'] = pd.to_numeric(df5['base_ratio'], errors='coerce')
    df5['Defect Date'] = pd.Timestamp(launch_date) + pd.to_timedelta(df5['Day'] - 1, unit='D')

    # Calculate dates and format as "WK {week_number}"
    df5['Week'] = (pd.Timestamp(launch_date) + pd.to_timedelta(df5["Day"] - 1, unit='D')
                   ).dt.isocalendar().week.apply(lambda x: f'WK {x}')
    return df5

def get_msclist():
    df6 = pd.read_excel(msclist_path)
    return df6
