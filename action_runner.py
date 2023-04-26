import craft_cost as cc
import schedule
import time


craft_name = '7.62x39_bp'
craft_dict = {'kite' : 3, 'eagle': 3, 'ps' : 120}

def update_craft_cost():
    cc.craft_cost_df(craft_name=craft_name, item_dict=craft_dict)

schedule.every(1).days.do(update_craft_cost)

while True:
    schedule.run_pending()