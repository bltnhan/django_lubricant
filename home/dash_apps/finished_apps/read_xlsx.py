import pandas as pd
import pathlib

PATH = pathlib.Path(__file__).parent # lấy thư mục chứa file python
DATA_PATH = PATH.joinpath("./data").resolve() # nối với
def get_df():
    df = pd.read_excel(DATA_PATH.joinpath('data.xlsx'), sheet_name=0)

    #rename column
    mapping = {df.columns[0]: 'ID',df.columns[1]: 'MONTH',df.columns[2]: 'YEAR',df.columns[3]: 'TAX_CODE',df.columns[4]: 'IMPORTER_NAME',df.columns[5]: 'INDUSTRY',
            df.columns[6]: 'INDUSTRY_CODE',df.columns[7]: 'CLASS',df.columns[8]: 'CLASS_CODE',df.columns[9]: 'COMPANY_CLASSIFICATION',df.columns[10]: 'COMPANY_CLASSIFICATION_CODE',
            df.columns[11]: 'CITY',df.columns[12]: 'HSCODE',df.columns[13]: 'DESCRIPTION_VN',df.columns[14]: 'TYPE_OF_OIL',df.columns[15]: 'TYPE_CODE',df.columns[16]: 'BASE_OIL_FINISH_GOOD',
            df.columns[17]: 'OIL_CLASS_CODE',df.columns[18]: 'MOTHER_BRAND',df.columns[19]: 'MOTHER_BRAND_CODE',
            df.columns[20]: 'MAIN_BRAND_PRODUCT', df.columns[21]: 'MAIN_BRAND_CODE',df.columns[22]: 'OIL_APPLICATION_CODE',
            df.columns[23]: 'OIL_APPLICATION_CHECK', df.columns[24]: 'VICOSITY_SPEC',df.columns[25]: 'QTY',df.columns[26]: 'UOM',df.columns[27]: 'PACK_SIZE',df.columns[28]: 'PACK_SPEC',
            df.columns[29]: 'QUANTITY_PER_PACK',df.columns[30]: 'VOLUME',df.columns[31]: 'SEGMENT',
            }
    df.rename(columns=mapping, inplace=True)

    df['TOTAL_AMT'] = df['INVOICE_VALUE_USD']
    df['Class'] = df['CLASS'].apply(lambda x: "Client" if str(x)[0] == '3' else "Trading" if str(x)[0] == '2' else "Competitor")
    df['CLASSIFICATION'] = df['TYPE_CODE'].apply(lambda x: "Client" if x == 3 else "Lubricant, Gas, Fuel & Oil")

    df[['QTY','VOLUME','TOTAL_AMT']] = df[['QTY','VOLUME','TOTAL_AMT']].replace('UNSPECIFY',0)
    df[['QTY','VOLUME','TOTAL_AMT']] = df[['QTY','VOLUME','TOTAL_AMT']].fillna(0)
    return df