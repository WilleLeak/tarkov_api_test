import json
import requests
import os
import matplotlib.pyplot as plt

craft_file = r'C:\python_practice\python_stuff\tarkov_api_test\tarkov_crafts\tarkov_crafts_wipe_winter_2022.json'
item_price_file = r'C:\python_practice\python_stuff\tarkov_api_test\tarkov_item_prices\prices_wipe_winter_2022.json'


craft_query = '''
{
    crafts{
        rewardItems{
            item {
                id
            }
            count
        }
        requiredItems{
            item {
                id
            }
            count
            attributes{
                value
            }
        }
        duration
    }
}
'''

def query_item_by_id(item_id):
    existing_crafts = []
        
    if os.path.exists(craft_file):
        with open(craft_file, 'r') as file:
            existing_crafts = json.load(file)
            
        for craft in existing_crafts:
            reward_item = craft['rewardItems']
            for id in reward_item:
                if id['item']['id'] == item_id:
                    return craft
        print('craft does not exist')
    else:
        print('file not found')
    
    
# update craft file or create new one. If file is updated it is overwritten completely.
def create_or_update_craft_file():
    response = requests.post('https://api.tarkov.dev/graphql', json={'query': craft_query})
    if response.status_code != 200:
        raise Exception('Query failed to run by returning code of {}. {}'.format(response.status_code, craft_query()))
    else:
        crafts = response.json()['data']['crafts']
        
    if os.path.exists(craft_file):
        print('file already exists: overwriting old crafts')
        with open(craft_file, 'w') as file:
            json.dump(crafts, file, indent = 4)
            
    else: 
        print('file does not exist: creating new file')
        with open(craft_file, 'w') as file:
            json.dump(crafts, file, indent = 4)

def calculate_craft_cost(item_id, include_tools = False):
    crafted_item = query_item_by_id(item_id)
    item_prices = []
    total_cost = 0
    price_per_item = 0
    total_profit = 0
    reward_item_price = 0
    return_vals = ''
    profit_per_hour = 0
    
    with open(item_price_file, 'r') as file:
        item_prices = json.load(file)
    
    if include_tools:
        for required_item in crafted_item['requiredItems']:
            for item in item_prices:
                if item['id'] == required_item['item']['id']:
                    total_cost += required_item['count'] * item['prices'][-1]['price']
                    break
    else:
        for required_item in crafted_item['requiredItems']:
            if len(required_item['attributes']) == 0:
                for item in item_prices:
                    if item['id'] == required_item['item']['id']:
                        total_cost += required_item['count'] * item['prices'][-1]['price']
                        break
            
    reward_item_count = crafted_item['rewardItems'][0]['count']
    reward_item_id = crafted_item['rewardItems'][0]['item']['id']
    price_per_item = total_cost / reward_item_count
    reward_item_name = ''
    
    for item in item_prices:
        if item['id'] == reward_item_id:
            reward_item_price = item['prices'][-1]['price']
            reward_item_name = item['name']
            break
    
    total_cost = round(total_cost, 0)
    price_per_item = int(round(price_per_item, 0))                              
    duration_in_hours = crafted_item['duration'] / 3600

    if reward_item_price == None:
        return_vals = f'Item name: {reward_item_name}\n' \
                      f'Total cost: {total_cost}\n' \
                      f'Price per item: {price_per_item}\n' \
                      f'Total profit: {None} due to not being listable on the flea market'
        return return_vals
    else:
        total_profit = (reward_item_price * crafted_item['rewardItems'][0]['count']) - total_cost
        profit_per_hour = total_profit / duration_in_hours
        return_vals = f'Item name: {reward_item_name}\n' \
                      f'Total cost: {total_cost}\n' \
                      f'Price per item: {price_per_item}\n' \
                      f'Total profit: {total_profit}\n' \
                      f'Profit per hour: {profit_per_hour}'
        return return_vals

def graph_total_craft_cost(item_id, include_tools = False):
    if not os.path.exists(craft_file):
        print('file not found: doing nothing')
        return
    
    total_cost = 0
    crafted_item = query_item_by_id(item_id)
    prices = {}
    name = ''
    
     
    
#print(query_item_by_id('590c678286f77426c9660122'))
#print(calculate_craft_cost('5d1b33a686f7742523398398', False))
graph_total_craft_cost('59e0d99486f7744a32234762', False)
#create_or_update_craft_file()