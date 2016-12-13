from PyQt5.Qt import QImage, QPixmap
from datetime import datetime
import sqlite3, os, json


def get_pixmap_in_db(icon_id, icon_type='itemicons'):
    if 'eq2localdb.sqlite' not in os.listdir():
        print('Local database does not exists or broken, please keep the file "eq2localdb.sqlite" with application.')
        return
    icon_sql = sqlite3.connect('eq2localdb.sqlite')
    icon_cmd = icon_sql.cursor().execute
    try:
        icon_byte = icon_cmd('SELECT icon FROM {} WHERE id=?'.format(icon_type), (icon_id,)).fetchall()[0][0]
    except IndexError:
        # print('The icon {} can not be found.'.format(icon_id))
        icon_byte = icon_cmd('SELECT icon FROM eq2icon_reserve WHERE id=0').fetchall()[0][0]
    img = QImage()
    img.loadFromData(icon_byte)
    icon_sql.close()
    return QPixmap(img)


def get_db_content(table, value, targets):
    if 'eq2localdb.sqlite' not in os.listdir():
        print('Local database does not exists or broken, please keep the file "eq2localdb.sqlite" with application.')
        return
    conn_sql = sqlite3.connect('eq2localdb.sqlite')
    sqlexe = conn_sql.cursor().execute
    trees = {}
    for each in targets:
        tree = sqlexe('SELECT detail FROM {} WHERE {}={}'.format(table, value, each)).fetchall()[0][0]
        trees[each] = json.loads(tree)
    conn_sql.close()

    return trees


def draw_color(text):
    if 'MYTHICAL' in text or 'MASTERCRAFTEDMYTHICAL' in text:
        return '#FF00FF'
    elif 'FABLED' in text or 'MASTERCRAFTEDFABLED' in text:
        return '#9F000F'
    elif 'ETHEREAL' in text:
        return '#FFA500'
    elif 'LEGENDARY' in text or 'MASTERCRAFTEDLEGENDARY' in text:
        return '#E8A317'
    elif 'MASTERCRAFTED' in text or 'TREASURED' in text:
        return '#43C6DB'
    elif 'HANDCRAFTED' in text or 'UNCOMMON' in text:
        return '#4CC417'
    elif text == '':
        return '#000000'
    else:
        print('Can not color {}, check it!'.format(text))


def status_translate(status):
    status_trans = {
        'trackingavoidance': ' Tracking Avoidance',
        'critchance': '% Crit Chance',
        'basemodifier': '% Potency',
        'pvptoughness': ' PVP Toughness',
        'stealthinvisspeedmod': ' Stealth or Invisible Speed',
        'all': ' Ability Modifier',
        'ripostechance': '% Riposte Chance',
        'offensivespeed': '% In-Combat Run Speed',
        'spelltimereusepct': '% Ability Reuse',
        'maxhpperc': '% Max Health',
        'doubleattackchance': '% Multi Attack Chance',
        'spelltimecastpct': '% Ability Casting',
        'critbonus': '% Crit Bonus',
        'meleedamage': ' Melee Damage',
        'maxmanaperc': '% Max Power',
        'blockchance': '% Block Chance',
        'armormitigationincrease': '% Mitigation',
        'dps': '% Damage Per Second',
        'attackspeed': '% Attack Speed',
        'parrychance': '% Extra Parry',
        'spelldoubleattackchance': '% Doublecast Chance',
        'additionalripostechance': '% Extra Riposte',
        'aeautoattackchance': '% AOE Auto Attack',
        'spelltimerecoverypct': '% Recovery Speed',
        'ripostedamage': ' Riposte Damage',
        'combatmpregenppt': ' Combat Power Regen',
        'combathpregenppt': ' Combat Health Regen'
    }
    try:
        ret = status_trans[status]
    except KeyError:
        ret = ' ' + status.capitalize()
    return ret


def slot2position(slot):
    posDict = {0: ['l', 7],
               1: ['l', 8],
               2: ['l', 0],
               3: ['l', 1],
               4: ['l', 2],
               5: ['l', 3],
               6: ['l', 4],
               7: ['l', 5],
               8: ['l', 6],
               9: ['r', 4],
               10: ['r', 5],
               11: ['r', 2],
               12: ['r', 3],
               13: ['r', 1],
               14: ['r', 6],
               15: ['r', 7],
               16: ['l', 9],
               17: ['l', 10],
               18: ['r', 8],
               19: ['r', 0],
               20: ['r', 9],
               21: ['r', 10],
               22: ['l', 11],
               23: ['r', 11]}
    return posDict[slot]


def worldid2name(wid):
    try:
        wdict = {
            100: 'Test',
            101: 'Guk',
            103: 'Everfrost',
            104: 'Antonia Bayle',
            105: 'Unrest',
            108: 'Butcherblock',
            120: 'Nagafen',
            202: 'Permafrost',
            203: 'Crushbone',
            206: 'Oasis',
            301: 'Valor',
            302: 'Storms',
            303: 'Splitpaw',
            311: 'Barren Sky',
            312: 'Harla Dar',
            401: 'Sebilis',
            409: 'Battlegrounds Test',
            505: 'Freeport',
            402: 'Battlegrounds',
            404: 'Battlegrounds DE',
            406: 'Battlegrounds FR',
            405: 'Battlegrounds RU',
            407: 'Battlegrounds JP',
            600: 'Stormhold',
            601: 'Isle of Refuge',
            602: 'Deathtoll',
            603: 'Drunder',
            604: 'Maj\'Dul',
            605: 'Halls of Fate',
            606: 'Skyfire',
            701: 'Thurgadin',
            607: 'Race To Trakanon'
        }
    except KeyError:
        return "Unknown World"
    return wdict[wid]


def aquire_modifiers():
    return {'Defense': 'defense', 'int': 'intelligence', 'Resolve': 'resolve', 'noxious': 'noxious',
            'Ministration': 'ministration', 'Max Health': 'maxhpperc', 'wis': 'wisdom', 'str': 'strength',
            'Strikethrough': 'strikethrough', 'Attack Speed': 'attackspeed', 'Extra Riposte Chance': 'ripostechance',
            'Disruption': 'disruption', 'All': 'all', 'mana': 'mana', 'Ability Casting Speed': 'spelltimecastpct',
            'Weapon Damage Bonus': 'weapondamagebonus', 'agi': 'agility',
            'Mitigation Increase': 'armormitigationincrease', 'arcane': 'arcane', 'Weapon Skills': 'weapon_skills',
            'Ordination': 'ordination', 'Spell Weapon Damage Bonus': 'spellweapondamagebonus',
            'Block Chance': 'blockchance', 'sta': 'stamina', 'health': 'health', 'Extra Parry Chance': 'parrychance',
            'Flurry Chance': 'flurry', 'Ability Reuse Speed': 'spelltimereusepct',
            'Doublecast Chance': 'spelldoubleattackchance', 'Crit Bonus': 'critbonus', 'Subjugation': 'subjugation',
            'elemental': 'elemental', 'Focus': 'focus', 'Crit Chance': 'critchance',
            'Potency': 'basemodifier', 'Fervor': 'fervor', 'Deflection': 'deflection',
            'Multi Attack Chance': 'doubleattackchance', 'Ability Recovery Speed': 'spelltimerecoverypct',
            'Damage Per Second': 'dps', 'AE Autoattack Chance': 'aeautoattackchance'}


def get_aa_tree_grid_modifier(tab_name):
    if tab_name in ('Warrior', 'Crusader', 'Brawler', 'Cleric', 'Druid', 'Shaman', 'Shaper',
                    'Sorcerer', 'Enchanter', 'Summoner', 'Bard', 'Predator', 'Rogue', 'Animalist'):
        return {'x': 1.2, 'y': 2}
    if tab_name in ('Guardian', 'Berserker', 'Paladin', 'Shadowknight', 'Monk', 'Bruiser', 'Templar', 'Inquisitor',
                    'Warden', 'Fury', 'Mystic', 'Defiler', 'Channeler', 'Wizard', 'Warlock', 'Illusionist', 'Coercer',
                    'Conjuror', 'Necromancer', 'Ranger', 'Assassin', 'Swashbuckler', 'Troubador', 'Dirge', 'Beastlord'):
        return {'x': 0.3, 'y': 0.7}
    if tab_name == 'Shadows':
        return {'x': 0.3, 'y': 0.7}
    if tab_name == 'Heroic':
        return {'x': 0.3, 'y': 0.7}
    if tab_name == 'Dragon':
        return {'x': 1.2, 'y': 2.5}
    if tab_name == 'Prestige':
        return {'x': 0.3, 'y': 0.7}
    if tab_name == 'General':
        return {'x': 0.3, 'y': 0.8}
    if tab_name == 'Far Seas':
        return {'x': 0.3, 'y': 0.7}
    if tab_name == 'Tradeskill':
        return {'x': 0.3, 'y': 0.7}
    else:
        print('Tab name "{}" can not find.'.format(tab_name))
        return None


def count_time(t):
    tm = {'S': 0, 'M': 0, 'H': 0, 'D': 0}
    if not isinstance(t, int) and not isinstance(t, float):
        print('Bad argument received.')
        return 'NULL'
    if t >= 60:
        tm['S'] = t % 60
        tm['M'] += int(t / 60)
    else:
        tm['S'] = t
    if tm['M'] >= 60:
        t = tm['M']
        tm['M'] = t % 60
        tm['H'] += int(t / 60)
    if tm['H'] >= 24:
        t = tm['H']
        tm['H'] = t % 24
        tm['D'] = int(t / 24)
    ret = ''
    for x in ['D', 'H', 'M', 'S']:
        if tm[x]:
            ret += '{} {} '.format(tm[x], x)
    return ret


def get_distinct_list(arg, qtype, query=''):
    import json, requests
    distinct_title = {}
    if query == '':
        query = \
            'http://census.daybreakgames.com/s:fyang/get/eq2/item?c:has={}&c:show={}&c:limit=10000'.format(arg, arg)
    l = json.loads(requests.get(query).text)['item_list']
    print(query)
    if qtype == 1:
        for each in l:
            if len(each[arg]):
                for e in each[arg].keys():
                    try:
                        distinct_title[e] += 1
                    except KeyError:
                        distinct_title[e] = 1
    elif qtype == 2:
        for each in l:
            for e in each[arg]:
                for x in e.keys():
                    try:
                        distinct_title[x] += 1
                    except KeyError:
                        distinct_title[x] = 1
    elif qtype == 3:
        for each in l:
            if len(each[arg]):
                for e in each[arg]:
                    try:
                        distinct_title[e['name']] += 1
                    except KeyError:
                        distinct_title[e['name']] = 1
    for each in distinct_title:
        print(each, ':', distinct_title[each])

    print(distinct_title.keys())


def get_modifiers_dict():
    import json, requests
    modifiers = {}
    query = \
        'http://census.daybreakgames.com/s:fyang/get/eq2/item?leveltouse=]100&c:show=modifiers&c:limit=5000'
    l = json.loads(requests.get(query).text)['item_list']
    for each in l:
        mod = each['modifiers']
        if len(mod):
            for e in mod:
                try:
                    modifiers[mod[e]['displayname']] = e
                except TypeError:
                    pass
    return modifiers


def CookSpellText(rawObj):
    detail = ''
    if 'name' in rawObj.keys():
        detail += '<b><h3>{}</h2></b><br>'.format(rawObj['name'])
    detail += '<font size="4">'
    if 'description' in rawObj.keys() and len(rawObj['description']):
        detail += '{}<br><br>'.format(rawObj['description'])
    if 'target_type' in rawObj.keys():
        detail += 'Target: {}<br>'.format(rawObj['target_type'])
    try:
        for e in rawObj['cost']:
            if e == 'per_tick':
                for _e in rawObj['cost']['per_tick']:
                    if rawObj['cost']['per_tick'][_e]:
                        detail += '{}: {} {}'.format('PerTick: ', rawObj['cost']['per_tick'][_e], _e.capitalize())
            elif rawObj['cost'][e]:
                detail += '{}: {}<br>'.format(e.capitalize(), rawObj['cost'][e])
    except KeyError:
        pass
    if 'alternate_advancement' in rawObj.keys() and rawObj['alternate_advancement']:
        detail += 'AA Cost: {}<br>'.format(rawObj['alternate_advancement'])
    if 'cast_secs_hundredths' in rawObj.keys() and rawObj['cast_secs_hundredths']:
        detail += 'Casting: {}<br>'.format(rawObj['cast_secs_hundredths']/100)
    if 'recast_secs' in rawObj.keys() and rawObj['recast_secs']:
        detail += 'Reuse: {}<br>'.format(rawObj['recast_secs'])
    if 'recovery_secs_tenths' in rawObj.keys() and rawObj['recovery_secs_tenths']:
        detail += 'Recovery: {}<br>'.format(rawObj['recovery_secs_tenths']/100)
    try:
        if rawObj['duration']['max_sec_tenths']:
            detail += 'Duration: {}<br>'.format(rawObj['duration']['max_sec_tenths']/10)
    except KeyError:
        pass
    if 'max_targets' in rawObj.keys() and rawObj['max_targets']:
        detail += 'Max Targets: {}<br>'.format(rawObj['max_targets'])
    if 'aoe_radius_meters' in rawObj.keys() and rawObj['aoe_radius_meters']:
        detail += 'AoE Targets: {}<br>'.format(rawObj['aoe_radius_meters'])
    if 'effect_list' in rawObj.keys():
        detail += '<br>Effects:<br>'
        for e in rawObj['effect_list']:
            intend = e['indentation']
            desc = '{}{}<br>'.format('&nbsp;' * intend, e['description'])
            detail += desc
    detail += '</font>'
    return detail

class CookItemText:
    def __init__(self, rawObj, short=False):
        self.short = short  # for taking a brief info
        self.text = self.cook_main(rawObj)
        self.has_set = False

    def cook_main(self, rawObj):
        # all detail font size option
        if self.short is True:
            detail = '<font size="3"><b>'
        else:
            detail = '<font size="4"><b>'

        if self.short is False:
            # descripition text
            if 'description' in rawObj.keys() and len(rawObj['description']):
                detail += '{}<br><br>'.format(rawObj['description'])

            # tier text
            if 'tier' in rawObj.keys():
                detail += '<b><font color={}>{}</font></b><br>'.format(draw_color(rawObj['tier']), rawObj['tier'])

            # flags
            if 'flags' in rawObj.keys():
                detail += '<font color="#FFA62F">'
                for flag in self.check_flags(rawObj['flags']):
                    detail += '{} '.format(flag.upper())
                detail += '</font><br><br>'

        # status
        if 'modifiers' in rawObj.keys():
            detail += self.add_status_info(rawObj['modifiers'])

        if self.short is False:
            if 'bonusmodlayer_list' in rawObj.keys():
                detail += self.add_addtion_status_info(rawObj['bonusmodlayer_list'])

            # add effect text
            try:
                detail += '<br>'
                for e in rawObj['adornment_list']:
                    detail += '<font color="#0020C2">{}</font><br>'.format(e['name'])
            except KeyError:
                pass

            # build typeinfo addition infomation
            if 'typeinfo' in rawObj.keys():
                detail += self.build_typeinfo_text(rawObj, rawObj['typeinfo'])

            # adornment
            if 'adornmentslot_list' in rawObj.keys() and len(rawObj['adornmentslot_list']):
                detail += self.set_adornment_info(rawObj['adornmentslot_list'])

        # add effects description
        if 'effect_list' in rawObj.keys():
            detail += '<br>Effects:<br>'
            for e in rawObj['effect_list']:
                intend = e['indentation']
                desc = '{}{}<br>'.format('&nbsp;' * intend, e['description'])
                detail += desc

        if self.short is False:
            # sets info
            if 'setbonus_info' in rawObj.keys():
                detail += self.build_sets_text(rawObj)

            # game link
            if 'gamelink' in rawObj.keys():
                detail += '<br><font color="red">[GAME LINK]:<br>'
                detail += '{}</font><br>'.format(rawObj['gamelink'])

                # end
        detail += '</b></font>'
        return detail

    def add_status_info(self, modifers):
        # add status text
        modifers = self.manage_modifier(modifers)
        ret = ''
        if len(modifers['attribute']) > 0:
            ret += '<font color="#254117">'
            for mod in modifers['attribute']:
                ret += '+{} {} '.format(mod[1], mod[0])
            ret += '</font><br>'
        if len(modifers['maxpool']) > 0:
            ret += '<font color="#254117">'
            for mod in modifers['maxpool']:
                ret += '+{} {} '.format(mod[1], mod[0])
            ret += '</font><br>'
        if len(modifers['ac']) > 0:
            ret += '<font color="#254117">'
            for mod in modifers['ac']:
                ret += '+{} {} '.format(mod[1], mod[0])
            ret += '</font><br>'
        if len(modifers['skill']) > 0:
            ret += '<font color="#254117">'
            for mod in modifers['skill']:
                ret += '+{} {} '.format(mod[1], mod[0])
            ret += '</font><br>'
        if len(modifers['modifyproperty']) > 0:
            ret += '<font color="#0020C2">'
            for mod in modifers['modifyproperty']:
                if len(mod) == 3:
                    if 'add' in mod:
                        ret += '<font color="#CD7F32">{}% {}</font><br>'.format(mod[1], mod[0])
                    else:
                        ret += '<font color="#CD7F32">{}% {} ({}%)</font><br>'.format(mod[1], mod[0], mod[2])
                else:
                    ret += '{}% {}<br>'.format(mod[1], mod[0])
            ret += '</font>'
        if len(modifers['normalizedmod']) > 0:
            ret += '<font color="#0020C2">'
            for mod in modifers['normalizedmod']:
                ret += '+{} Ability Mod'.format(mod[1])
            ret += '</font><br>'
        return ret

    def manage_modifier(self, modifers):
        # arrange the raw modifiers infomation
        ret = {'attribute': [], 'ac': [], 'skill': [], 'modifyproperty': [], 'normalizedmod': [], 'maxpool': []}
        for mod in modifers:
            try:
                if 'reforged' in modifers[mod].keys():
                    if 'value_merged' in modifers[mod].keys():
                        ret[modifers[mod]['type']].append([modifers[mod]['displayname'],
                                                           str(round(modifers[mod]['value'], 2)),
                                                           str(round(modifers[mod]['value_merged'], 2))])
                    else:
                        ret[modifers[mod]['type']].append([modifers[mod]['displayname'],
                                                           str(round(modifers[mod]['value'], 2)), 'add'])
                else:
                    ret[modifers[mod]['type']].append([modifers[mod]['displayname'],
                                                       str(round(modifers[mod]['value'], 2))])
            except BaseException as err:
                # print('Modifier Info Error : {}'.format(err))
                pass
        return ret

    def add_addtion_status_info(self, bonusmodlayer):
        ret = '<br>'
        for n, each in enumerate(bonusmodlayer):
            if 'bonusmod_list' in each.keys():
                ret += 'Addtion Status {}:<br>'.format(n)
                for e in each['bonusmod_list']:
                    ret += '{}: {}<br>'.format(round(e['value'], 2), status_translate(e['name']))
                ret += '<br>'
        return ret

    def check_flags(self, source):
        flags = 'harvestable,relic,heirloom,indestructible,refined,novalue,nodestroy,attunable,lore-equip,' \
                'notrade,ornate,lore,nozone,norent,prestige,notrasmute,stacklore,artiface'
        ret = []
        for flag in flags.split(','):
            if source[flag]['value'] == 1:
                ret.append(flag)
        return ret

    def set_adornment_info(self, adorn):
        # adornment slots
        ret = '<br>Adornments Slot:<br>'
        for a in adorn:
            if a['color'] == 'purple':
                ret += ' <font color="#800080">Purple</font>'
            elif a['color'] == 'red':
                ret += ' <font color="#FF0000">Purple</font>'
            elif a['color'] == 'blue':
                ret += ' <font color="#0000FF">Blue</font>'
            elif a['color'] == 'cyan':
                ret += ' <font color="#00FFFF">Cyan</font>'
            elif a['color'] == 'green':
                ret += ' <font color="#008000">Green</font>'
            elif a['color'] == 'yellow':
                ret += ' <font color="#FFA500">Yellow</font>'
            else:
                ret += 'White'
        ret += '<br>'
        return ret

    def build_typeinfo_text(self, rawObj, source):
        ret = '<br>'
        # common position info
        try:
            pos = rawObj['requiredskill']['text']
            ret += '{}<br>'.format(pos.capitalize())
        except KeyError:
            pass
        try:
            for slot in rawObj['slot_list']:
                ret += '{} '.format(slot['name'])
            ret += '<br>'
        except KeyError:
            pass
        # armor info
        if 'knowledgedesc' in source.keys():
            ret += '{}<br>'.format(source['knowledgedesc'])
        if 'minarmorclass' in source.keys():
            ret += 'Protection:&nbsp;{}<br>'.format(source['minarmorclass'])
        # shield info

        # weapon info
        if 'wieldstyle' in source.keys():
            ret += '{} <br>'.format(source['wieldstyle'].capitalize())
        if 'minbasedamage' in source.keys():
            try:
                ret += 'Damage:{}{} - {} ' \
                    .format('&nbsp;' * 2, source['minbasedamage'], source['maxbasedamage'])
                try:
                    ret += '{} '.format(source['damagetype'])
                except KeyError:
                    pass
                ret += '({} Rating)<br>'.format(source['damagerating'])
            except KeyError:
                pass
        if 'delay' in source.keys():
            ret += 'Delay: {}{} seconds<br>'.format('&nbsp;' * 2, source['delay'])
        if 'minrange' in source.keys():
            ret += 'Range: {}{} - {} meters<br>'.format('&nbsp;' * 2, source['minrange'], source['range'])
        # adorn info
        try:
            if source['name'] == 'adornment':
                ret += 'Type:{}{} Adornment<br>'.format('&nbsp;' * 2, source['color'].upper())
        except KeyError:
            pass
        # ammo info
        try:
            ret += 'Damage:{}{} {}<br>'.format('&nbsp;' * 2, source['damage'], source['damagetype'])
            for e in source['itemmodifier_list']:
                ret += '{}: {}{}<br>'.format(e['name'].capitalize(), '&nbsp;' * 2, e['value'])
        except KeyError:
            pass
        # container
        try:
            ret += 'Slots:{}{}<br>'.format('&nbsp;' * 2, source['slots'])
        except KeyError:
            pass
        # expendable
        try:
            if 'duration' in source.keys():
                if source['name'] == 'food':
                    ret += 'Duration:&nbsp;&nbsp;{}<br>'.format(source['duration'])
                else:
                    ret += 'Duration:&nbsp;&nbsp;{}<br>'.format(count_time(source['duration']))
            if 'recasttime' in source.keys():
                ret += 'Recast: &nbsp;&nbsp; {}<br>'.format(count_time(source['recasttime']))
            if 'casttime' in source.keys():
                ret += 'Casting: &nbsp;&nbsp;{}<br>'.format(count_time(source['casttime']))
        except KeyError:
            pass
        # slots info
        try:
            slots = source['slot_list']
            ret += 'Slots:&nbsp;&nbsp;'
            for slot in slots:
                ret += '{} '.format(slot['displayname'])
            ret += '<br>'
        except KeyError:
            pass
        # spell scroll
        if 'spelltarget' in source.keys():
            ret += 'Target: &nbsp;&nbsp; {}<br>'.format(source['spelltarget'])
        if 'spellcasttime' in source.keys():
            ret += 'Casting:&nbsp;&nbsp; {}<br>'.format(count_time(source['spellcasttime']))
        if 'spellrecasttime' in source.keys():
            ret += 'Recast: &nbsp;&nbsp; {}<br>'.format(count_time(source['spellrecasttime']))
        if 'spellrecoverytime' in source.keys():
            ret += 'Recovery:&nbsp;&nbsp;{}<br>'.format(count_time(source['spellrecoverytime']))
        if 'resistability' in source.keys():
            ret += 'Resist: &nbsp;&nbsp; {}<br>'.format(source['resistability'])
        if 'spellrange' in source.keys():
            ret += 'Range : &nbsp;&nbsp; {}<br>'.format(source['spellrange'])
        # common level info
        try:
            ret += 'Level : {}{}&nbsp;(Item Lv. {})<br>' \
                .format('&nbsp;' * 2, rawObj['leveltouse'], rawObj['itemlevel'])
        except KeyError:
            pass
        # build class info
        try:
            ret += '<font color="#254117">'
            if len(source['classes'].keys()) == 26 or len(source['classes'].keys()) == 35:
                ret += 'All Classes'
            else:
                for cla in source['classes'].keys():
                    ret += '{} '.format(cla.capitalize())
            ret += '</font><br>'
        except KeyError:
            pass
        # contains info
        if 'item_list' in source.keys():
            ret += '<br>(Contain Pieces):<br>'
            for x in source['item_list']:
                ret += '&nbsp;{}<br>'.format(x['displayname'])
        return ret

    def build_sets_text(self, rawObj):
        ret = ''
        try:
            ret += '<br><font color="#7F525D">{}<br>'.format(rawObj['setbonus_info']['displayname'])
            for s in rawObj['setbonus_list']:
                require = ''
                effect = ''
                descrip = ''
                status = ''
                for e in s:
                    ek = e
                    if ek == 'requireditems':
                        require = '({}):<br>'.format(s[e])
                    elif ek == 'effect':
                        effect = 'Effect : {}<br>'.format(s[e])
                    elif 'descrip' in ek:
                        descrip += '&nbsp;{}<br>'.format(s[e])
                    else:
                        status += '&nbsp;+{}{}<br>'.format(s[e], status_translate(ek))
                ret += require + effect + descrip + status + '<br>'
            ret += '</font><br>'
            self.has_set = True
        except KeyError:
            pass
        return ret


class CookCharText:
    def __init__(self, rawObj):
        self.text = self.cook_main(rawObj)

    def cook_main(self, rawObj):
        detail = ''
        try:
            detail = '<font size="4"><b>'
            detail += '<font color="#800000">&nbsp;*** GENERAL***</font><br>'
            detail += '{} {}<br>'\
                .format(rawObj['type']['race'], rawObj['type']['gender'].capitalize())
            detail += '<font size="3">Birthday : {}<br>'\
                .format(datetime.fromtimestamp(rawObj['type']['birthdate_utc']).isoformat().replace('T', ' '))
            detail += 'Played Time: {}<br>'\
                .format(count_time(rawObj['playedtime']))
            detail += 'Update Time: {}</font><br>'\
                .format(datetime.fromtimestamp(round(rawObj['last_update'])).isoformat().replace('T', ' '))
            detail += 'Adventure Class : {}<br>'.format(rawObj['type']['class'])
            detail += 'Adventure Level : {}<br>'.format(rawObj['type']['level'])
            if 'ts_class' in rawObj['type'].keys():
                detail += 'Tradeskill Class : {}<br>'.format(rawObj['type']['ts_class'].capitalize())
                detail += 'Tradeskill Level : {}<br>'.format(rawObj['type']['ts_level'])
            if 'aa_level' in rawObj['type'].keys():
                detail += 'AA Points : {}<br>'.format(rawObj['type']['aa_level'])
            detail += '<br>'
            detail += 'Health :  {}<br>'.format(rawObj['stats']['health']['max'])
            detail += 'Power :   {}<br>'.format(rawObj['stats']['power']['max'])
            detail += '<br>'
            detail += '<font color="#008000">&nbsp;*** ATTRIBUTES ***</font><br>'
            detail += 'Strength :   {}<br>'.format(rawObj['stats']['str']['effective'])
            detail += 'Agility :   {}<br>'.format(rawObj['stats']['agi']['effective'])
            detail += 'Intelligence :   {}<br>'.format(rawObj['stats']['int']['effective'])
            detail += 'Stamina :   {}<br>'.format(rawObj['stats']['sta']['effective'])
            detail += '<br>'
            detail += '<font color="#0000FF">&nbsp;*** DEFENSE ***</font><br>'
            detail += 'Elemental :   {}<br>'.format(rawObj['resists']['elemental']['effective'])
            detail += 'Noxious :   {}<br>'.format(rawObj['resists']['noxious']['effective'])
            detail += 'Arcane :   {}<br>'.format(rawObj['resists']['arcane']['effective'])
            detail += 'Mitigation :   {}<br>'.format(rawObj['resists']['physical']['effective'])
            detail += 'Avoidance :   {}<br>'.format(rawObj['stats']['defense']['avoidance'])
            detail += 'Block Chance :   {}<br>'.format(rawObj['stats']['combat']['blockchance'])
            detail += 'Block :   {}<br>'.format(rawObj['stats']['defense']['block'])
            detail += 'Defense :   {}<br>'.format(rawObj['stats']['defense']['armor'])
            detail += 'Parry :   {}<br>'.format(rawObj['stats']['defense']['parry'])
            if 'baseavoidancebonus' in rawObj['stats']['combat'].keys():
                detail += 'Uncontest Avoid :   {}<br>'.format(rawObj['stats']['combat']['baseavoidancebonus'])
            detail += '<br>'
            detail += '<font color="#FF0000">&nbsp;*** OFFENSE ***</font><br>'
            detail += 'Crit Chance :   {}<br>'.format(rawObj['stats']['combat']['critchance'])
            detail += 'Crit Bonus :   {}<br>'.format(rawObj['stats']['combat']['critbonus'])
            detail += 'Potency :   {}<br>'.format(rawObj['stats']['combat']['basemodifier'])
            if 'resolve' in rawObj['stats']['combat'].keys():
                detail += 'Resolve :   {}<br>'.format(rawObj['stats']['combat']['resolve'])
            if 'fervor' in rawObj['stats']['combat'].keys():
                detail += 'Fervor :   {}<br>'.format(rawObj['stats']['combat']['fervor'])
            if 'abilitymod' in rawObj['stats']['combat'].keys():
                detail += 'Ability Mod :   {}<br>'.format(rawObj['stats']['combat']['abilitymod'])
            if 'spelltimereusepct' in rawObj['stats']['combat'].keys():
                detail += 'Reuse Speed :   {}<br>'.format(rawObj['stats']['ability']['spelltimereusepct'])
            if 'spelltimerecoverypct' in rawObj['stats']['combat'].keys():
                detail += 'Recovery Speed :   {}<br>'.format(rawObj['stats']['ability']['spelltimerecoverypct'])
            if 'spelltimecastpct' in rawObj['stats']['combat'].keys():
                detail += 'Casting Speed :   {}<br>'.format(rawObj['stats']['ability']['spelltimecastpct'])
            if 'hategainmod' in rawObj['stats']['combat'].keys():
                detail += 'Hate Mod :   {}<br>'.format(rawObj['stats']['combat']['hategainmod'])
            if 'toughness' in rawObj['stats']['combat'].keys():
                detail += 'Toughness :   {}<br>'.format(rawObj['stats']['combat']['toughness'])
            detail += '<br>'
            detail += '<font color="#FFA500">&nbsp;*** MELEE ATTACK ***</font><br>'
            detail += 'DPS Mod :   {}<br>'.format(rawObj['stats']['combat']['dps'])
            detail += 'Haste :   {}<br>'.format(rawObj['stats']['combat']['attackspeed'])
            detail += 'Multi Attack :   {}<br>'.format(rawObj['stats']['combat']['doubleattackchance'])
            detail += 'AoE Attack :   {}<br>'.format(rawObj['stats']['combat']['aeautoattackchance'])
            detail += 'Strikethrough :   {}<br>'.format(rawObj['stats']['combat']['strikethrough'])
            detail += 'Accuracy :   {}<br>'.format(rawObj['stats']['combat']['accuracy'])
            if 'flurry' in rawObj['stats']['combat'].keys():
                detail += 'Flurry :   {}<br>'.format(rawObj['stats']['combat']['flurry'])
            if 'weapondamagebonus' in rawObj['stats']['combat'].keys():
                detail += 'Weapon Damage Bonus:   {}<br>'.format(rawObj['stats']['combat']['weapondamagebonus'])
            if 'spellweapondamagebonus' in rawObj['stats']['combat'].keys():
                detail += 'Wand Damage Bonus:   {}<br>'.format(rawObj['stats']['combat']['spellweapondamagebonus'])
            detail += '<br>&nbsp;Primary Weapon<br>'
            detail += 'Damage:   {} - {}<br>'.format(rawObj['stats']['weapon']['primarymindamage'],
                                                     rawObj['stats']['weapon']['primarymaxdamage'])
            detail += 'Delay:   {}<br>'.format(rawObj['stats']['weapon']['primarydelay'])
            detail += '<br>&nbsp;Secondary Weapon<br>'
            detail += 'Damage:   {} - {}<br>'.format(rawObj['stats']['weapon']['secondarymindamage'],
                                                     rawObj['stats']['weapon']['secondarymaxdamage'])
            detail += 'Delay:   {}<br>'.format(rawObj['stats']['weapon']['secondarydelay'])
            detail += '<br>&nbsp;Ranged Weapon<br>'
            detail += 'Damage:   {} - {}<br>'.format(rawObj['stats']['weapon']['rangedmindamage'],
                                                     rawObj['stats']['weapon']['rangedmaxdamage'])
            detail += 'Delay:   {}<br>'.format(rawObj['stats']['weapon']['rangeddelay'])

            detail += '<br><font color="#CBA500">&nbsp;*** MISC ***</font><br>'

            detail += '</b></font>'
        except KeyError as err:
            print('Error info : {}'.format(err))
        return detail


# function test
if __name__ == '__main__':
    print(count_time(10158931))