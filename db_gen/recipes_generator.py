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
        self.nru = ""

class Output:
    def __init__(self, output_string):
        self.output_string = output_string
        self.props = []

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
    
    def is_a_unique_item(self, code):
        for row in self.utils.tables.unique_items_table:
            if row["index"] == code:
                return True
        return False

    def is_a_set_item(self, code):
        for row in self.utils.tables.set_items_table:
            if row["index"] == code:
                return True
        return False

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
            elif s.startswith("nru"):
                item.nru = "(Non Runeword)"
            elif s.startswith("usetype"):
                item.name = "Same Input Type" 
            elif s.startswith("useitem"):
                item.name = "Same Item"
            elif s.startswith("any"):
                item.name = "Any"
            else:
                # This code isn't any of the special ones above, it must be it's name.. check armor/weapon/misc tables first
                item.name = self.utils.get_item_name_from_code(s, False)
                if s == item.name:
                    # Not in armor/weapon/misc table, lets check if it's an item type, and if so, we'll use the comment column
                    # Note that this is the best we can do because item types don't have strings because they don't show up in game
                    # An example of this is tors=Torso or blun=Blunt Weapon
                    item.name = self.utils.get_item_type_name_from_code(s, False)
                    if s == item.name:
                        # So it's not an item type, let's check if it's a unique or set items
                        if not self.is_a_unique_item(s) and not self.is_a_set_item(s):
                            self.utils.log("Could not translate: " + s)
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

            
        ret = re.sub(" +", " ", item.qty + " " + item.quality + " " + item.tier + " " + item.rarity + " " + item.name + " " + item.eth + " " + item.upg + " " + item.rep + " " + item.rch + " " + item.uns + " " + item.rem + " " + item.nru)
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
            ret = ret + self.parse_string(i.output_string) + "<br>"
            for p in i.props:
                ret = ret + self.utils.get_stat_string([p])
        return ret

class Recipe_Generator:
    def __init__(self, utils):
        self.utils = utils

    def proj_specific_recipes(self):
        if self.utils.tables.db_name == "Lord_Of_Destruction":
            return []
        r = Recipe(self.utils)
        r.inputs.append("Gem Can")
        r.inputs.append("Any Gem")
        r.outputs.append(Output("Gem Can"))
        r.outputs.append(Output("Add Corresponding Gem Points"))

        r2 = Recipe(self.utils)
        r2.inputs.append("Gem Can")
        r2.inputs.append("Rerollable Item")
        r2.outputs.append(Output("Gem Can"))
        r2.outputs.append(Output("Subtract Corresponding Gem Points"))
        r2.outputs.append(Output("Rerolled Item"))
        return [r, r2]

    # @TODO make this project specific somehow
    # Return True if you want to block/filter out the recipe, false otherwise
    def proj_specific_filter(self, recipe):
        gem_list = ["gcv", "gfv", "gsv", "gzv", "gpv", "gvb", "6gv",
                    "gcb", "gfb", "gsb", "glb", "gpb", "gbb", "6gy",
                    "gcg", "gfg", "gsg", "glg", "gpg", "ggb", "6gb",
                    "gcr", "gfr", "gsr", "glr", "gpr", "grb", "6gg",
                    "gcw", "gfw", "gsw", "glw", "gpw", "gwb", "6gr",
                    "gcy", "gfy", "gsy", "gly", "gpy", "gyb", "6gw",
                    "gcy", "gfy", "gsy", "gly", "gpy", "gyb", "6sk",
                    "skc", "skf", "sku", "skl", "skz", "skb",
                    "gck", "gfk", "gsk", "gzk", "gpk", "gbk", "6gk"]
        
        if recipe["input 1"] == "can1":
            ret = True
            # If first input is gem can, and all the other inputs are gems, don't add to recipe list
            for i in range(2,8):
                if recipe["input " + str(i)] == "" or recipe["input " + str(i)].split(",")[0] in gem_list:
                    continue
                else:
                    ret = False
            if ret:
                return ret

        if recipe["input 1"] in ["kv0","ky0","kb0","kg0","kr0","kw0","ks0","kk0"]:
            ret = True
            # If first input is gem can, and all other inputs are weapons/armors or ancient decipherers
            for i in range(2,8):
                if recipe["input " + str(i)] == "" or \
                   recipe["input " + str(i)] == "ddd":
                       continue
                ret = False
                for s in recipe["input " + str(i)].split(","):
                    if s == self.utils.get_item_name_from_code(s):
                        ret = True
            if ret:
                return ret
        return False


    def generate_recipes(self):
        recipes = []
        for recipe in self.utils.tables.recipes_table:
            if recipe["enabled"] != "1":
                continue
            if self.proj_specific_filter(recipe):
                continue
            r = Recipe(self.utils)
            for i in range(1,8):
                if recipe["input " + str(i)] != "":
                    r.inputs.append(recipe["input " + str(i)])
            for i in ["", " b", " c"]:
                if recipe["output" + str(i)] != "":
                    output = Output(recipe["output" + str(i)])
                    props = []
                    for j in range(1, 6):
                        column = str(i + " mod").strip()
                        if recipe[column + " " + str(j)] != "":
                            props.append(properties.Property(self.utils,
                                                             recipe[column + " " + str(j)],
                                                             recipe[column + " " + str(j) + " param"],
                                                             recipe[column + " " + str(j) + " min"],
                                                             recipe[column + " " + str(j) + " max"],
                                                             chance=recipe[column + " " + str(j) + " chance"]))
                    output.props = props
                    r.outputs.append(output)
            recipes.append(r)
        
        return recipes + self.proj_specific_recipes()

