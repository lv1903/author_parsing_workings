import psycopg2
import pandas as pd
import json
from sqlalchemy import create_engine


def get_config(config_path):

    if config_path == None:
        config_path = 'sqlConfig.json'
    
    try:
        c = json.load(open(config_path)) 
        return c
    except:
        print('error: no query params config \neither add config path or place sqlConfig.json in same directory \nrequired:')
        print(' { \n  "dbname":string, \n  "user": string, \n  "host": string, \n  "dbpass": string \n }')
        return False
        
    
                
        

def query(query_string, config_path=None):

    c = get_config(config_path)
    if c == False: return
    
    try:
        conn = psycopg2.connect("dbname='{dbname}' user='{user}' host='{host}' password='{dbpass}'"
                                .format(dbname=c['dbname'], user=c['user'], host=c['host'], dbpass=c['dbpass']))

    except:
        print("I am unable to connect to the database")
        return
        
    df = pd.read_sql_query(query_string, con=conn)
    
    conn.close()
    
    return df
    
 
def append(df, table, config_path=None): 
 
    config = get_config(config_path)
    if config == False: return

    engine = create_engine('postgresql://{user}:{dbpass}@{host}/{dbname}'.format(
        user=config['user'],
        dbpass=config['dbpass'],
        host=config['host'],
        dbname=config['dbname']
    ))
    
    df.to_sql(table, engine, index=False, if_exists='append')
    
    
 


