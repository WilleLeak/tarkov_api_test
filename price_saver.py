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
    
def historical_price_query(id):
    return'''
    query{
    historicalItemPrices(id:"%s"){
        timestamp
        price
    }
    }
    ''' % id
    
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
    existing_data = []
    with open(item_price_file, 'r') as file:
        existing_data = json.load(file)
        print('starting backfill')
        for item in existing_data:
            print('first for loop')
            item_id = item['id']
            response = requests.post('https://api.tarkov.dev/graphql', json={'query':historical_price_query(item_id)})
            if response.status_code != 200:
                raise Exception('Query failed to run by returning code of {}. {}'.format(response.status_code, historical_price_query(item_id)))
            else:
                item_prices = response.json()['data']['historicalItemPrices']

            for time in item_prices:
                print('second for loop')
                timestamp = int(time['timestamp'])
                date = datetime.fromtimestamp(timestamp / 1000).strftime('%Y-%m-%d')
                price = time['price']
                new_values = {'date': date, 'price': price}
                item['prices'].append(new_values)

    with open(item_price_file, 'w') as file:
        json.dump(existing_data, file, indent = 4)
    print('prices successfully backfilled')    

def graph_item_price(id):
    if not os.path.exists(item_price_file):
        print('File not found')
        return

    with open(item_price_file, 'r') as file:
        item_list = json.load(file)

        prices = {}
        name = ''

        for item in item_list:
            item_id = item['id']
            if id == item_id:
                name = item['name']
                for value in item['prices']:
                    date = value['date']
                    price = value['price']
                    if date in prices:
                        prices[date].append(price)
                    else:
                        prices[date] = [price]
                break

        avg_prices = []
        dates = []

        for date, price_list in prices.items():
            avg_price = sum(price_list) / len(price_list)
            avg_prices.append(avg_price)
            dates.append(date)

        plt.plot(dates, avg_prices)
        plt.xlabel('Date')
        plt.ylabel('Average Price')
        plt.title(f'Average Price History of {name}')
        plt.xticks(rotation=45)
        plt.tight_layout()

        plt.show()

        print('Prices successfully graphed')
        
def sort_by_date():
    if os.path.exists(item_price_file):
        with open(item_price_file, 'r') as file:
            item_list = json.load(file)
            
            for item in item_list:
                prices = item['prices']
                prices.sort(key=lambda x: x['date'])
                
            with open(item_price_file, 'w') as file:
                json.dump(item_list, file, indent = 4)
                
            print('prices successfully sorted')
            

# def graph_item_price(id):
#     if not os.path.exists(item_price_file):
#         print('file not found')
#         return
    
#     with open(item_price_file, 'r') as file:
#         item_list = json.load(file)
        
#         prices = []
#         dates = []
#         name = ''
#         price_by_date = {}  # Dictionary to store prices by date
        
#         for item in item_list:
#             item_id = item['id']
#             if id == item_id:
#                 name = item['name']
#                 # Group prices by date and calculate average
#                 for value in item['prices']:
#                     date = value['date']
#                     price = value['price']
#                     if price is not None:  # Exclude null prices
#                         if date in price_by_date:
#                             price_by_date[date].append(price)
#                         else:
#                             price_by_date[date] = [price]
        
#         for date, price_list in price_by_date.items():
#             average_price = sum(price_list) / len(price_list)
#             prices.append(average_price)
#             dates.append(date)
        
#         plt.plot(dates, prices)
#         plt.xlabel('Date')
#         plt.ylabel('Average Price')
#         plt.title(f'Average Price History of {name}')
        
#         plt.show()
        
#         print('Prices successfully graphed')


# test item ids:
# 591094e086f7747caa7bb2ef -> body armor repair kit
# 5d1b33a686f7742523398398 -> canister with purified water
# 59e0d99486f7744a32234762 -> 7.62x39mm BP gzh
# 59e3556c86f7741776641ac2 -> ox bleach
# 5c0d56a986f774449d5de529 -> 9x19mm RIP

#save_item_price()
#sort_by_date()

#backfill_data()        
graph_item_price('59e3556c86f7741776641ac2')
        