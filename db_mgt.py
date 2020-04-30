from config import engine, db
import pandas as pd
from sqlalchemy import inspect, Column

# df = pd.read_csv('C:\\Users\\asuer\\Documents\\Google Drive\\ebs 2001-2005\\ebs73.1_2010.csv', engine='python')
# df.columns = [c.lower() for c in df.columns] #postgres doesn't like capitals or spaces
# #write to databas
# df.to_sql("eu_2010", engine)

connection = engine.connect()
metadata = db.MetaData()


def getAllTables():
    inspecter = inspect(engine)
    # tables = []
    # for table_name in inspecter.get_table_names():
    #     tables.append(table_name)
    return [table_name for table_name in inspecter.get_table_names()]


def getColumnNames(table_name):
    inspecter = inspect(engine)
    return [name for name in inspecter.get_columns(table_name)]


def getTableDf(datas, year, table_name):
    connection = engine.connect()
    try:
        query = "SELECT "
        for item in datas:
            query += "{}.{},".format(table_name, item['variable'])
        # query = query[: -1] + " FROM " + table_name
        query = "{} FROM {}".format(query[: -1], table_name)

        ResultProxy = connection.execute(query)
        ResultSet = ResultProxy.fetchall()
        df = pd.DataFrame(ResultSet)
        columns = {}
        for i in range(len(datas)):
            columns[i] = datas[i]['nick_name']
        df.rename(columns=columns, inplace=True)
        df['year'] = year
        df = df.infer_objects()

        for item in datas:
            if item.get('min') and item.get('min') != '':
                df.where((df[item['nick_name']] >= int(item['min'])), inplace=True)
            if item.get('max') and item.get('max') != '':
                df.where((df[item['nick_name']] <= int(item['max'])), inplace=True)

        dfm = pd.melt(df, id_vars=['country', 'year', 'continent'], value_vars=[item['nick_name'] for item in datas if item['nick_name'] not in ['country', 'year', 'continent']])
        dfin = dfm.groupby(['country', 'year', 'variable', 'continent']).mean().reset_index()
        dfin['year'] = dfin['year'].astype(int)
        dfin.rename(columns={'variable': 'Indicator Name', 'value': 'Value', 'year': 'Year', 'country': 'Country Name'}, inplace=True)
        connection.close()
        return dfin
    except Exception as e:
        print(e)
        connection.close()
        return []
