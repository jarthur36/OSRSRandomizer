from osrsbox import items_api
from osrsbox.items_api.item_properties import ItemProperties
import random
from dataclasses import dataclass
import math
from typing import Dict, Any
from base64 import b64decode
import numpy as np

items = items_api.load()
print(f"Loaded {len(items)} from osrsbox api")
all_gear = [item for item in items if item.equipment is not None]
# all_slots = set()
# for item in all_gear:
#     all_slots.add(item.equipment.slot)
# print(all_slots)
all_slots = set(item.equipment.slot for item in all_gear)
def item_by_name(name: str) -> ItemProperties:
    if name.lower() not in set(item.name.lower() for item in all_gear):
        raise ValueError("not valid name")
    for item in all_gear:
        if item.name.lower() == name.lower():
            return item
        

def is_pvp_only(item: ItemProperties) -> bool:
    ancient_warrior_names = ["Statius", "Vesta", "Zuriel", "Morrigan"] 
    if any(item.name.startswith(n) for n in ancient_warrior_names):
        return True
    return False
        
        
        
def is_cosmetic(item: ItemProperties) -> bool:
    not_cos_flag = False
    useful_equipment_stats = {"attack_stab", "attack_slash", "attack_crush", "attack_magic", "attack_ranged", "defence_stab", "defence_slash", "defence_crush", "defence_magic", "defence_ranged", "melee_strength", "ranged_strength", "magic_damage"}
    for stat in useful_equipment_stats:
        if getattr(item.equipment, stat) != 0:
            not_cos_flag = True
    if not_cos_flag == True:
        return False
    else:
        return True

def get_random_item_for_slot(slot: str, exclude_cosmetics: bool = True, only_tradables: bool = True) ->  ItemProperties:
    if slot not in all_slots:
        raise ValueError("slot name not found")
    all_in_chosen_slot = [item for item in all_gear if item.equipment.slot == slot]
    if exclude_cosmetics:
        all_in_chosen_slot = [item for item in all_in_chosen_slot if not is_cosmetic(item)]
    if only_tradables:
        all_in_chosen_slot = [item for item in all_in_chosen_slot if item.tradeable_on_ge]
    return random.choice(all_in_chosen_slot)

def assign_quality(item: ItemProperties, str_scaling=25, att_scaling=5, tank_scaling=1) -> float:
    isweapon = item.weapon is not None
    att_stats = {"attack_stab", "attack_slash", "attack_crush", "attack_magic", "attack_ranged"}
    str_stats = {"melee_strength", "ranged_strength", "magic_damage"}
    highest_att_stat = max(getattr(item.equipment, stat) for stat in att_stats)
    highest_str_stat = max(getattr(item.equipment, stat) for stat in str_stats)
    # print(highest_str_stat)
    if isweapon:
        quality = math.pow(highest_att_stat+65, 0.5)*(highest_str_stat+40)/item.weapon.attack_speed
    else:
        melee_defs = {"defence_stab", "defence_slash", "defence_crush"}
        avg_melee_def = sum([getattr(item.equipment, stat) for stat in melee_defs])/len(melee_defs)
        range_def = item.equipment.defence_ranged
        mage_def = item.equipment.defence_magic
        quality = tank_scaling*sum([avg_melee_def, range_def, mage_def]) + str_scaling*highest_str_stat + att_scaling*highest_att_stat
    return quality

def roll_crate(crate_score: float, number_of_rolls: int, items_list, debug=False):
    if crate_score > 1 or crate_score < 0:
        raise ValueError("crate_score should be between 0 and 1")
    def calc_weight(crate_score: float, quality_ratio: float) -> float:
        power = 2
        if quality_ratio == crate_score:
            return math.pow(20, power)
        return min(math.pow(abs(quality_ratio-crate_score), -power), 20)
    rolled_items = []
    all_slots = ['ring', 'head', 'body', 'feet', 'legs', '2h', 'neck', 'ammo', 'weapon', 'hands', 'shield', 'cape']
    max_quality_list = []
    for roll in range(number_of_rolls):
        chosen_slot = random.choice(all_slots)
        valid_item_list = []
        item_quality_list = []
        for item in items_list:
            if item.equipment.slot == chosen_slot:
                valid_item_list.append(item)
                item_quality_list.append(assign_quality(item))
        max_quality = max(item_quality_list)
        max_quality_list.append(max_quality)
        item_weight_list = [calc_weight(crate_score, quality/max_quality) for quality in item_quality_list]
        # print(valid_item_list)
        total_weight = np.sum(item_weight_list)
        normalised_weight_list = [weight/total_weight for weight in item_weight_list]
        rolled_items.append(np.random.choice(valid_item_list, p=normalised_weight_list))
    if debug:
        return rolled_items, max_quality_list
    return rolled_items
