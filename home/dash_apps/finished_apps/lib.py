import pandas as pd
import pathlib

PATH = pathlib.Path(__file__).parent # lấy thư mục chứa file python
DATA_PATH = PATH.joinpath("./data").resolve() # nối với
def get_df():
    df = pd.read_excel(DATA_PATH.joinpath('data.xlsx'), sheet_name=0)

    #rename column
    mapping = {df.columns[0]: 'ID', df.columns[1]: 'MONTH', df.columns[2]: 'YEAR', df.columns[3]: 'TAX_CODE',
               df.columns[4]: 'IMPORTER_NAME', df.columns[5]: 'INDUSTRY',
               df.columns[6]: 'INDUSTRY_CODE', df.columns[7]: 'CLASS', df.columns[8]: 'CLASS_CODE',
               df.columns[9]: 'COMPANY_CLASSIFICATION', df.columns[10]: 'COMPANY_CLASSIFICATION_CODE',
               df.columns[11]: 'CITY', df.columns[12]: 'HSCODE', df.columns[13]: 'DESCRIPTION_VN',
               df.columns[14]: 'TYPE_OF_OIL', df.columns[15]: 'BASE_OIL_FINISH_GOOD', df.columns[16]: 'MOTHER_BRAND',
               df.columns[17]: 'MOTHER_BRAND_CODE',
               df.columns[18]: 'OIL_APPLICATION_CODE', df.columns[19]: 'OIL_APPLICATION_CHECK',
               df.columns[20]: 'VICOSITY_SPEC',
               df.columns[21]: 'QTY', df.columns[22]: 'UOM', df.columns[23]: 'PACK_SIZE',
               df.columns[24]: 'PACK_SPEC', df.columns[25]: 'QUANTITY_PER_PACK', df.columns[26]: 'VOLUME',
               df.columns[27]: 'SEGMENT',
               df.columns[28]: 'TOTAL_INV_VALUE', df.columns[29]: 'CURRENCY', df.columns[30]: 'EXCHANGE_TO_USD',
               df.columns[31]: 'INVOICE_VALUE_USD',
               }
    df.rename(columns=mapping, inplace=True)

    df['TOTAL_AMT'] = df['INVOICE_VALUE_USD']
    df['Class'] = df['CLASS'].apply(lambda x: "Client" if str(x)[0] == '3' else "Trading" if str(x)[0] == '2' else "Competitor")
    df['CLASSIFICATION'] = df['CLASS'].apply(lambda x: "Client" if str(x)[0] == '3' else "Lubricant, Gas, Fuel & Oil")

    df[['QTY','VOLUME','TOTAL_AMT']] = df[['QTY','VOLUME','TOTAL_AMT']].replace('UNSPECIFY',0)
    df[['QTY','VOLUME','TOTAL_AMT']] = df[['QTY','VOLUME','TOTAL_AMT']].fillna(0)
    return df

def human_format(num):
    num = float('{:.3g}'.format(num))
    magnitude = 0
    while abs(num) >= 1000:
        magnitude += 1
        num /= 1000.0
    return '{}{}'.format('{:f}'.format(num).rstrip('0').rstrip('.'), ['', 'K', 'M', 'B', 'T'][magnitude])


def format_percent_df(df, round_digit, lst_df_not_in):
    for col_ in df.columns:
        if col_ not in lst_df_not_in:
            df[col_] = round(df[col_] / df[col_].sum() * 100, round_digit).astype(str) + '%'
    return df


def revert_month(df, lst_df_col, lst_df_not_in):
    # df: dataframe origin
    # lst_df_col: list(df.columns)
    # lst_df_not_in: list column not month that want to add in
    month_list = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']
    month_list = month_list[::-1]
    # append list column not in
    df_col_update = []
    for col_ in lst_df_not_in:
        df_col_update.append(col_)

    # append month
    for mon in month_list:
        if mon in lst_df_col:
            df_col_update.append(mon)
    df = df[df_col_update]
    return df


def rename_pivot_column(df, format_number: bool):
    df.columns = ['_'.join(str(s).strip() for s in col if s) for col in df.columns]
    for col_name in df.columns:
        if col_name[:4] == 'sum_':
            df.rename({col_name: col_name[4:]}, axis=1, inplace=True)
            if format_number == True:
                df[col_name[4:]] = df[col_name[4:]].map('{:,.2f}'.format)
    return df


def revert_month_pivot_table(df, lst_df_not_in):
    df = df.swaplevel(0, 2, axis=1)
    # df3 = df.swaplevel(0,2, axis=1).sort_index(1).reindex(['VOLUME','TOTAL_AMT'], level=1, axis=1)
    month_list = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']
    month_list = month_list[::-1]
    # append list column not in
    # lst_df_not_in = [('', '', 'MOTHER_BRAND'),('', '', 'YEAR')]
    df_col_update = lst_df_not_in
    for col_ in month_list:
        for col__ in list(df.columns):
            if col_ == col__[0]:
                df_col_update.append(col__)

    df = df[df_col_update]

    return df