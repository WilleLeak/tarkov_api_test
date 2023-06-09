import requests
import json
from datetime import datetime
import os
import matplotlib.pyplot as plt
import pandas as pd

windows_dir_path = r'C:\python_practice\python_stuff\tarkov_api_test\crafts'
#mac_dir_path = r''
# This code is kind of redundant now. A better price storage system has been created. 
# Will keep this running till end of wipe.

def craft_query():
    return """
        {
        crafts{
            rewardItems{
                item{
                    name
                    id
                }
                count
            }
            requiredItems{
                item{
                    name
                    buyFor{
                        priceRUB
                    }
                }
                count
                attributes{
                    name
                    value
                }
            } 
        } 
        }
        """ 
    
def find_craft(crafted_item):
    cost_dict = {'Crafted item': crafted_item, 'ID': '', 'Required items': {}} 
    reward_count = 0
    id = ''
    total_cost = 0

    response = requests.post('https://api.tarkov.dev/graphql', json={'query': craft_query()})
    if response.status_code != 200:
        raise Exception('Query failed to run by returning code of {}. {}'.format(response.status_code, craft_query()))
    else:
        crafts = response.json()['data']['crafts']
        
    for craft in crafts:
        for reward_item in craft['rewardItems']:
            if reward_item['item']['name'] == crafted_item:
                reward_count = reward_item['count']
                id = reward_item['item']['id']
                for required_items in craft['requiredItems']:
                    name = required_items['item']['name']
                    if len(required_items['attributes']) > 0:
                        cost = 0
                    else:
                        cheapest_item_cost = 1_000_000_000
                        cheapest_total = 0
                        for price in required_items['item']['buyFor']:
                            if price['priceRUB'] < cheapest_item_cost:
                                cheapest_item_cost = price['priceRUB']
                                cheapest_total = cheapest_item_cost * required_items['count']
                        cost = cheapest_total
                    cost_dict['Required items'][name] = cost
                    
            
    for name, cost in cost_dict['Required items'].items():
        total_cost += cost
            
    current_date = datetime.now().strftime('%Y-%m-%d')
    
    cost_dict['ID'] = id
    cost_dict['Price (RUB)'] = total_cost
    cost_dict['Items crafted'] = reward_count
    cost_dict['Price per item'] = round((total_cost / reward_count), 2)
    cost_dict['Date'] = current_date
    #print(f'The current cost of the {crafted_item} craft is: {total_cost} RUB')
    
    return cost_dict

def save_craft_json(crafted_item):
    file_name = crafted_item + '_craft_data.json'
    file_path = windows_dir_path + '\\' + file_name
    cost_dict = find_craft(crafted_item)
    
    
    if os.path.exists(file_path):
        print('file found')
        with open(file_path, 'r') as file:
            existing_data = json.load(file)
            
    else:
        print('file not found: creating new file')
        existing_data = []
        
    existing_data.append(cost_dict)
    
    with open(file_path, 'w') as file:
        json.dump(existing_data, file, indent=4)
        
def graph_costs(crafted_item):
    file_path = windows_dir_path + '\\' + crafted_item +  '_craft_data.json'
    with open(file_path, 'r') as file:
        df = pd.read_json(file)
    plt.plot(df['Date'], df['Price (RUB)'])
    plt.show()
    
            
# common crafted items:
#     7.62x39mm BP gzh
#     9x21mm BT gzh
#     5.56x45mm M995
#     9x19mm RIP
#     Ox bleach
#     Soap
#     Fleece fabric
#     Propital regenerative stimulant injector
#     Pile of meds
#     AI-2 medkit
