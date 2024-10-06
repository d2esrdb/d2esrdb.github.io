import utils
import re
import properties

class Item:
    def __init__(self):
        self.name = ""
        self.qty = ""
        self.rarity = ""
        self.quality = ""
        self.eth = ""
        self.upg = ""
        self.tier = ""
        self.rep = ""
        self.rch = ""
        self.uns = ""
        self.rem = ""
        self.mod = ""
        self.suf = ""
        self.pre = ""

class Recipe:
    def __init__(self, utils):
        self.utils = utils
        self.inputs = []
        self.outputs = []
    
    def get_affix(self, table, row):
        props = []
        for i in range(3):
            if table[int(row)]["mod" + str(i+1) + "code"] != "":
                props.append(properties.Property(self.utils,
                                                 table[int(row)]["mod" + str(i+1) + "code"],
                                                 table[int(row)]["mod" + str(i+1) + "param"],
                                                 table[int(row)]["mod" + str(i+1) + "min"],
                                                 table[int(row)]["mod" + str(i+1) + "max"]))
        return self.utils.get_stat_string(props)

    def parse_string(self, in_str, input_item=None):
        in_strs = in_str.split(",")
        item = Item()
        for s in in_strs:
            if s.startswith("qty="):
                item.qty = s.replace("qty=", "") + "x"
            elif s.startswith("nor"):
                item.rarity = "White" #To not get confused with "normal" (i.e not exceptional or elite)
            elif s.startswith("mag"):
                item.rarity = "Magic"
            elif s.startswith("rar"):
                item.rarity = "Rare"
            elif s.startswith("uni"):
                item.rarity = "Unique"
            elif s.startswith("set"):
                item.rarity = "Set"
            elif s.startswith("crf"):
                item.rarity = "Crafted"
            elif s.startswith("tmp"):
                item.rarity = "Tempered"
            elif s.startswith("noe"):
                item.eth = "Non Ethereal"
            elif s.startswith("eth"):
                item.eth = "Ethereal"
            elif s.startswith("upg"):
                item.upg = "Upgraded"
            elif s.startswith("nos"):
                item.sock = "Non Socketed"
            elif s.startswith("sock="):
                item.sock = "Socketed (" + s.replace("sock=","") + ")"
            elif s.startswith("bas"):
                item.tier = "Normal"
            elif s.startswith("exc"):
                item.tier = "Exceptional"
            elif s.startswith("eli"):
                item.tier = "Elite"
            elif s.startswith("low"):
                item.quality = "Low Quality"
            elif s.startswith("hiq"):
                item.quality = "Superior"
            elif s.startswith("rep"):
                item.rep = "Repair Durability"
            elif s.startswith("rch"):
                item.rch = "Recharge Quantity"
            elif s.startswith("uns"):
                item.uns = "Unsocketed Item (destroys gems)"
            elif s.startswith("rem"):
                item.rem = "Unsocketed Item (removes gems)"
            elif s.startswith("mod"):
                item.mod = "Transfer Properties"
            elif s.startswith("pre="):
                item.pre = self.get_affix(self.utils.tables.prefixes_table, s.replace("pre=",""))
            elif s.startswith("suf="):
                item.suf = self.get_affix(self.utils.tables.suffixes_table, s.replace("suf=",""))
            elif s.startswith("usetype"):
                item.name = "Same Input Type" 
            elif s.startswith("useitem"):
                item.name = "Same Item"
            elif s.startswith("any"):
                item.name = "Any"
            else:
                item.name = self.utils.get_item_name_from_code(s, False)
                if s == item.name:
                    item.name = self.utils.get_item_type_name_from_code(s, False)
                    if s == item.name:
                        print("Cannot translate: " + s)
                        item.name = s
            '''

            elif s.startswith("gem0"):
                item.name = "Chipped Gem"
            elif s.startswith("gem1"):
                item.name = "Flawed Gem"
            elif s.startswith("gem2"):
                item.name = "Normal Gem"
            elif s.startswith("gem3"):
                item.name = "Flawless Gem"
            elif s.startswith("gem4"):
                item.name = "Perfect Gem"
            elif s.startswith("hpot"):
                item.name = "Health Potion"
            elif s.startswith("mpot"):
                item.name = "Mana Potion"
            elif s.startswith("weap"):
                item.name = "Weapon"
            elif s.startswith("armo"):
                item.name = "Armor"
            elif s.startswith("tors"):
                item.name = "Torso"
            elif s.startswith("ring"): # Is this just a typo in the lod recipes? should it just be rin?
                item.name = "Ring"
            elif s.startswith("knif"):
                item.name = "Knife"
            elif s.startswith("spea"):
                item.name = "Spear"
            elif s.startswith("shld"):
                item.name = "Shield"
            elif s.startswith("swor"):
                item.name = "Sword"
            elif s.startswith("staf"):
                item.name = "Staff"
            elif s.startswith("belt"):
                item.name = "Belt"
            elif s.startswith("helm"):
                item.name = "Helm"
            elif s.startswith("Blun"):
                item.name = "Blunt Weapon"
            elif s.startswith("amul"):
                item.name = "Amulet"
            '''

            
        ret = re.sub(" +", " ", item.qty + " " + item.quality + " " + item.tier + " " + item.rarity + " " + item.name + " " + item.eth + " " + item.upg + " " + item.rep + " " + item.rch + " " + item.uns + " " + item.rem)
        if item.mod != "":
            ret = ret + "<br>" + item.mod
        if item.suf != "":
            ret = ret + "<br>" + item.suf
        if item.pre != "":
            ret = ret + "<br>" + item.pre
        return ret

    def input_string(self):
        ret = ""
        for i in self.inputs:
            ret = ret + self.parse_string(i) + "<br>"
        return ret
    
    def output_string(self):
        ret = ""
        for i in self.outputs:
            ret = ret + self.parse_string(i) + "<br>"
        return ret

class Recipe_Generator:
    def __init__(self, utils):
        self.utils = utils

    def generate_recipes(self):
        recipes = []
        for recipe in self.utils.tables.recipes_table:
            if recipe["enabled"] != "1":
                continue
            r = Recipe(self.utils)
            for i in range(1,8):
                if recipe["input " + str(i)] != "":
                    r.inputs.append(recipe["input " + str(i)])
            recipes.append(r)
            for i in ["", " b", " c"]:
                if recipe["output" + str(i)] != "":
                    r.outputs.append(recipe["output" + str(i)])
                
        return recipes

