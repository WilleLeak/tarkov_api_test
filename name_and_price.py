import requests
import pandas as pd
from datetime import datetime
import matplotlib.pyplot as plt
import os


#print(f'directory is {os.getcwd()}')
def create_query(item_name):
    query = """
    {
        items(name: "%s") {
            name
            avg24hPrice
        }
    }
    """ % item_name
    return query


def get_item_price(item_name):
    headers = {"Content-Type": "application/json"}
    query = create_query(item_name)
    response = requests.post('https://api.tarkov.dev/graphql', headers=headers, json={'query': query})

    if response.status_code == 200:
        query_response = response.json()
        item_data = query_response['data']['items'][0]
        price = item_data['avg24hPrice']  
        print(f"Price for {item_name} successfully found.")
        return price
    else:
        raise Exception("Query failed to run by returning code of {}. {}".format(response.status_code, query))
    
def update_dataframe(name):
    dir_path = r'C:\Users\farns\python_practice\python_stuff\tarkov_api_test'
    try:
        df = pd.read_csv(os.path.join(dir_path, name + '_price_data.csv'), index_col='date', parse_dates=True)
    except FileNotFoundError:
        df = pd.DataFrame(columns=['date', 'price'])
        

    price = get_item_price(name)
    date = datetime.now().strftime('%Y-%m-%d')
    new_row = {'price': price, 'date': date}
    df = pd.concat([pd.DataFrame([new_row]), df], ignore_index=True)

    file_path = os.path.join(dir_path, name + '_price_data.csv')
    df.to_csv(file_path, index=False)
    print(f"Item price for {name} successfully updated.")

def plot_df(name):
    dir_path = r'C:\Users\farns\python_practice\python_stuff\tarkov_api_test'
    df = pd.read_csv(os.path.join(dir_path, name + '_price_data.csv'), parse_dates=['date'], index_col='date')
    df_daily = df.resample('D').mean()

    plt.plot(df_daily.index, df_daily['price'])
    plt.xlabel('Date')
    plt.ylabel('Flea Price (RUB)')
    plt.title(name + ' price over time')
    plt.show()
    
# finds the directory location of this file 
# print(os.getcwd())

# test for individual items: passed
#update_dataframe('thermite')

# test for indiviual items: passed
#plot_df('thermite')