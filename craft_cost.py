import name_and_price as np
import pandas as pd
import matplotlib.pyplot as plt
from datetime import datetime
import os

def craft_cost_df(craft_name, item_dict):
    dir_path = r'C:\Users\farns\python_practice\python_stuff\tarkov_api_test'
    try:
        df = pd.read_csv(os.path.join(dir_path, craft_name + '_craft.csv'),
                         index_col='date', parse_dates=True)
    except FileNotFoundError:
        df = pd.DataFrame(columns=['date', 'price', 'item name'])

    for item, value in item_dict.items():
        price = np.get_item_price(item) * value
        date = datetime.now().strftime('%Y-%m-%d')
        new_row = {'item name': item, 'price': price, 'date': date}
        df = pd.concat([pd.DataFrame([new_row]), df], ignore_index=True)
    
    file_path = os.path.join(dir_path, craft_name + '_craft.csv')
    df.to_csv(file_path, index=False)
    print(f"Item price for {craft_dict} successfully updated.")
    
    cost = df['price'].sum()
    
    return cost

craft_name = '7.62x39_bp'
craft_dict = {'kite' : 3, 'eagle': 3, 'ps' : 120}

