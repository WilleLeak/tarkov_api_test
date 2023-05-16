import json
import requests
import os
import matplotlib.pyplot as plt

from datetime import datetime



item_price_file = r'C:\python_practice\python_stuff\tarkov_api_test\tarkov_item_prices\prices_wipe_winter_2022.json'

def craft_query():
    return '''
    {
        crafts {
            rewardItems {
                item {
                    id
                }
            }
            requiredItems {
                item {
                    id
                }
            }
        }
    }
    '''
    
def item_query():
    return '''
    {
        items {
            id
            name
            lastLowPrice
        }
    }
    '''    
    
def backfill_query():
    return'''
    {
        items {
            id
            historicalPrices {
                price
                timestamp
            }
        }
    }
    '''    
    
def save_item_price():
    items_array = []
    
    response = requests.post('https://api.tarkov.dev/graphql', json={'query':item_query()})
    if response.status_code != 200:
        raise Exception('Query failed to run by returning code of {}.'.format(response.status_code))
    else:
        items_array = response.json()['data']['items']

    existing_data = []
    if os.path.exists(item_price_file):
        print('file exists: doing nothing')
        return # since file exists do nothing
    
    print('creating new file') # create new file with all current lowest prices
    for item in items_array:
        current_date = datetime.now().strftime('%Y-%m-%d')
        new_price_dict = {}
        new_price_dict['id'] = item['id']
        new_price_dict['name'] = item['name']
        new_price_dict['prices'] = [{'date': current_date, 'price': item['lastLowPrice']}]  
        existing_data.append(new_price_dict) 
        
    with open(item_price_file, 'w') as file:
        json.dump(existing_data, file, indent = 4)  
            
def update_item_price():
    if not (os.path.exists(item_price_file)):
        print('file not found: nothing happening')
        return
    
    new_item_data = []
    response = requests.post('https://api.tarkov.dev/graphql', json={'query':item_query()})
    if response.status_code != 200:
        raise Exception('Query failed to run by returning code of {}. {}'.format(response.status_code, craft_query()))
    else:
        new_item_data = response.json()['data']['items']
        
    item_dict = {}
    with open(item_price_file, 'r') as file:
        print('file found')
        item_list = json.load(file)
        
        for item in item_list:
            item_dict = item
            item_id = item['id']
            new_price = {} # create empty dict to store new price
            
            for new_val in new_item_data:
                if new_val['id'] == item_id:
                    new_price['date'] = datetime.now().strftime('%Y-%m-%d')
                    new_price['price'] = new_val['lastLowPrice']
                    break
                
            if new_price.get('price') is not None: # only add price if it is not null
                item_dict['prices'].append(new_price)



    with open(item_price_file, 'w') as file:
        json.dump(item_list, file, indent = 4)   
        
    print('prices successfully updated')
    print('prices that are null have not been changed')

def backfill_data():
    if not os.path.exists(item_price_file):
        print('file not found')
        return
    historical_data = []
    response = requests.post('https://api.tarkov.dev/graphql', json={'query':backfill_query()})
    if response.status_code != 200:
        raise Exception('Query failed to run by returning code of {}. {}'.format(response.status_code, craft_query()))
    else:
        historical_data = response.json()['data']['items']
    
    with open(item_price_file, 'r') as file:
        item_list = json.load(file)
        
        for item in item_list:
            item_id = item['id']
            item_dict = item
            item_prices = []
            for historical_val in historical_data:
                if historical_val['id'] == item_id:
                    for historical_price in historical_val['historicalPrices']:
                        time = int(historical_price['timestamp']) / 1000
                        date = datetime.fromtimestamp(time).strftime('%Y-%m-%d')
                        price = historical_price['price']
                        new_price = {'date': date, 'price': price}
                        item_prices.append(new_price)
                        break # only want first price so break out of loop
                    break # break out of loop once item is found
            if new_price.get('price') is not None:
                item_dict['prices'].append(new_price) # only add price if it is not null
                
        with open(item_price_file, 'w') as file:
            json.dump(item_list, file, indent = 4)
            
        print('historial prices successfully added')
                
def graph_item_price(id):
    if not os.path.exists(item_price_file):
        print('file not found')
        return
    
    with open(item_price_file, 'r') as file:
        item_list = json.load(file)
        
        prices = []
        dates = []
        name = ''
        
        
        for item in item_list:
            item_id = item['id']
            if id == item_id:
                name = item['name']
                # get prices and dates from json file and append to arrays to graph later on
                for value in item['prices']:
                    prices.append(value['price'])
                    dates.append(value['date'])
                break
        
        plt.plot(dates, prices)
        plt.xlabel('Date')
        plt.ylabel('Price')
        plt.title(f'Price History of {name}')
        
        plt.show()

            
        print('prices successfully graphed')      
        
#graph_item_price('63ac5c9658d0485fc039f0b8')
        