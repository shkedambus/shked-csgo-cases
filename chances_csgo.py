from random import choices

rarity = {"Mil-Spec":0.7981,
          "Restricted":0.1626,
          "Classified":0.0315,
          "Covert":0.0078}

quality = {"Battle-Scarred":0.16,
           "Well-Worn":0.24,
           "Field-Tested":0.33,
           "Minimal Wear":0.24,
           "Factory New":0.03}

stattrack = {"False":0.9, "True":0.1}

def roll(dictionary):
    chance = choices(list(dictionary.keys()), list(dictionary.values()))
    return chance[0]

def get_item(case=None):
    weapon_rarity = roll(rarity)
    weapon_quality = roll(quality)
    weapon_stattrack = roll(stattrack)
    print(weapon_rarity, weapon_quality, weapon_stattrack)