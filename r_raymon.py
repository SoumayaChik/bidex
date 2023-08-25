
import pandas as pd
import requests
import pygsheets
from pprint import pprint
import warnings
import tabulate
import re



warnings.filterwarnings('ignore')

brand = 'R Raymon'
brand_code = 4495
BIKE_NOT_FOUND_IMG = 'https://bowcycleebikes.com/wp-content/uploads/woocommerce-placeholder-500x288.png'

def read_sheet(key, sheet_name):
    client = pygsheets.authorize(service_account_file='client_secretkey.json')
    sheet = client.open_by_key(key)
    wks = sheet.worksheet_by_title(sheet_name)
    return wks, pd.DataFrame(wks.get_all_records(numericise_data=False))

def printdf(df):
    print(df.to_markdown())

def extractImage(ims):
    try:
        return ims[0]['Url']
    except:
        return ''

def pickImage(variant_im, model_im):
    if variant_im != '':
        return variant_im
    elif model_im != '':
        return model_im
    else:
        return BIKE_NOT_FOUND_IMG

def transform_attrs(attrs):
    return {bidex_mapping[int(list(pair.values())[0].split('/')[-1])]: list(pair.values())[1] for pair in attrs}

bidex_mapping = {1: 'Zielgruppe', 2: 'Bremsen', 3: 'Bremshebel', 4: 'Einsatzzweck', 6: 'Einsatzbereich', 7: 'Bremstyp', 8: 'Rahmen', 11: 'Rahmen-Material', 12: 'Schaltung', 13: 'Schalthebel', 14: 'Umwerfer', 16: 'Schaltungstyp', 17: 'Gabel', 18: 'Dämpfer', 19: 'Gabel Federweg (mm)', 20: 'Dämpfer Federweg (mm)', 22: 'Frontleuchte', 23: 'Rückleuchte', 24: 'Dynamo', 25: 'Pedale', 26: 'Innenlager', 27: 'Kurbelsatz', 28: 'Zahnkranz', 29: 'Antrieb', 30: 'Lenker', 31: 'Griffe', 32: 'Lenkerband', 33: 'Vorbau', 34: 'Steuersatz', 35: 'Felgen', 36: 'Reifen', 37: 'Naben', 38: 'Speichen', 39: 'Laufradsatz', 40: 'Laufradgröße', 41: 'Sattel', 42: 'Sattelstütze', 43: 'Sattelklemmung', 44: 'Schutzbleche', 45: 'Kettenschutz', 46: 'Ständer', 47: 'Schloss', 48: 'Gepäckträger', 49: 'Gepäckträger vorne', 50: 'Straßenzulassung', 52: 'Beschreibung lang', 54: 'Zulässiges Gesamtgewicht (kg)', 55: 'Gewicht (kg)', 56: 'Lenkeraufsatz / Triathlon-Aufsatz', 57: 'Stützräder', 58: 'Rahmen-Hauptfarbe', 60: 'Motor', 61: 'Akku', 62: 'Display', 63: 'Motorposition', 65: 'Rahmen-Formen', 66: 'Material', 67: 'Gewicht (g)', 68: 'Höhe (mm)', 70: 'Durchmesser (mm)', 74: 'Alter', 75: 'Getriebe', 76: 'Hubraum', 77: 'Kraftstoff', 80: 'Bremsscheibengröße max. (mm)', 81: 'Dämpfer Einbaulänge (mm)', 82: 'Bremsaufnahme', 83: 'Achssystem', 85: 'Motor-Typ', 86: 'Motor-Marke', 88: 'Zustand', 95: 'Federungstechnik', 97: 'Lagertyp', 99: 'Schraubversion (mit Gewinde)', 101: 'Gabelschaftlänge (mm)', 102: 'Gabelschaftdurchmesser oben (mm)', 104: 'Steuerrohr-Innendurchmesser oben (mm)', 105: 'Steuerrohr-Innendurchmesser unten (mm)', 106: 'Lochzahl', 107: 'Lochkreisdurchmesser (mm)', 109: 'Kurbelaufnahme Innenlager', 110: 'Länge (mm)', 113: 'Tretlagergehäuse-Typen', 114: 'Anzahl Kettenglieder/Zähne', 120: 'Faltbar', 121: 'eBike-Zulassung', 123: 'Zähnezahl größtes Zahnrad', 124: 'Zähnezahl kleinstes Zahnrad', 126: 'Anzahl Gänge', 127: 'Befestigungsart (-system)', 128: 'Kettenlinie', 129: 'Winkel (Grad)', 134: 'Spannung (V)', 142: 'Klemmdurchmesser (mm)', 145: 'Beleuchtungsstärke (Lux)', 148: 'Breite innen (cm)', 149: 'Höhe innen (cm)', 150: 'Länge innen (cm)', 152: 'Volumen (ml)', 157: 'Maximaldruck (bar)', 158: 'Maximale Zuladung (kg)', 165: 'Leistung (W)', 168: 'Stromversorgung', 170: 'Leistungsaufnahme (W)', 172: 'Achsdurchmesser (mm)', 173: 'Ventilart', 174: 'Sitzplätze', 176: 'Breite (mm)', 179: 'Montagezustand', 180: 'Körpergröße', 181: 'Akku-Kapazität (Wh)', 182: 'Reach (mm)', 183: 'Stack (mm)', 184: 'Sitzrohrlänge (mm)', 185: 'Oberrohrlänge (mm)', 186: 'Steuerrohrwinkel (Grad)', 187: 'Sitzrohrwinkel (Grad)', 189: 'Kettenstrebenlänge (mm)', 190: 'Steuerrohrlänge (mm)', 191: 'Tretlagerabsenkung (mm)', 192: 'Gabelvorbiegung (mm)', 193: 'Überstandshöhe (mm)', 194: 'Gabeleinbauhöhe (mm)', 195: 'Vorbaulänge (mm)', 196: 'Vorbauwinkel (Grad)', 197: 'Spacer (mm)', 198: 'Lenker Breite (mm)', 199: 'Lenker Rise (mm)', 200: 'Lenker Backsweep (Grad)', 201: 'Kurbellänge (mm)', 202: 'Radstand (mm)', 203: 'Tretlagerhöhe (mm)', 204: 'Bremsscheiben', 205: 'Ladegerät', 206: 'Akku-Montage', 207: 'Akku-Typ', 208: 'Akku-Spannung (V)', 212: 'Herkunftsland', 227: 'Zolltarifnummer', 229: 'Verpackung Breite (mm)', 230: 'Verpackung Höhe (mm)', 231: 'Verpackung Länge (mm)', 238: 'Brutto-Gewicht (g)', 239: 'Beschreibung kurz', 240: 'Antriebsart', 241: 'Bontext', 242: 'Körpergröße Min.', 243: 'Körpergrösse Max', 244: 'Zusätzliche Ausstattung', 245: 'Gefahrenhinweise', 246: 'Inhaltsstoffe', 247: 'Biozid', 248: 'Bremse vorne', 249: 'Bremse hinten', 250: 'Bremshebel Vorderrad', 251: 'Bremshebel Hinterrad', 252: 'Bremsscheibe vorne', 253: 'Bremsscheibe hinten', 254: 'Felge vorne', 255: 'Felge hinten', 256: 'Reifen vorne', 257: 'Reifen hinten', 259: 'Nabe vorne', 260: 'Nabe hinten', 261: 'Sattelstütze Verstellweg', 262: 'Kapazität (Wh)', 263: 'BOSCH', 264: 'Hauptfarbe', 265: 'Umfang (mm)', 266: 'Bedieneinheit', 267: 'Freigabe Anhänger', 268: 'Warnhinweise', 269: 'Status'}

bidex_erp = read_sheet('1_ZNIAW-xnJdpiK-1GTx0KycsT9kKj2C68FDN2JGzuhk', 'mapping')[-1].astype(str)
categ_mapper = read_sheet('1_ZNIAW-xnJdpiK-1GTx0KycsT9kKj2C68FDN2JGzuhk', 'category_mapping')[-1][['bidex_code', 'category_name']].fillna('').astype(str)
categ_mapper = dict(categ_mapper[(categ_mapper['bidex_code'] != '') & (categ_mapper['category_name'] != '')].values)

url = f"https://api.bidex.bike/v2/Products?brandid={brand_code}"

payload = ""
headers = {
  'Accept': 'application/json',
  'Authorization': '1137 85bb4c4c2003d00046216691081f6399e0a11547'
}

response = requests.request("GET", url, headers=headers, data=payload).json()


# ### Transform Data


df = pd.json_normalize(response)
df = df[['Id', 'NameDE', 'Year', 'Variants', 'Images', 'ProductGroup']]
df['brand_name'] = brand
df.columns = ['brand_id', 'model_name', 'model_year', 'variants', 'model_image','category_name', 'brand_name' ]
df['model_image'] = df['model_image'].apply(extractImage)
df['category_name'] = df['category_name'].apply(lambda x: x.split('/')[-1]).map(categ_mapper)
# initial filters
filters = (df['model_year'] > 2019) & (df['category_name'].isin(list(categ_mapper.values())))
df = df[filters]


# extend variants
columns_mapper = {'Id':'model_id', 'Product': 'Product', 'MPN':'mpn', 'Gtin':'gtin', 'Size':'size', 'Color':'color', 'Price':'price','AttributeValuePairs':'attrs', 'Prices':'prices'}
variants = []
for brand_id, variant in df[['brand_id', 'variants']].values:
    variant = pd.json_normalize(variant)
    variant = variant.rename(columns_mapper, axis= 1)
    variant['brand_id'] = brand_id
    try:
        variant['variant_image'] = variant['Images'].apply(extractImage)
    except:
        variant['variant_image'] = ''
    cols = [c for c in ['brand_id', 'model_id', 'mpn', 'gtin', 'size', 'color', 'price','attrs', 'variant_image'] if c in variant.columns]
    variant = variant[cols].to_dict('records')
    variants.extend(variant)
variants = pd.DataFrame(variants)
df = df.merge(variants, how='left', on='brand_id').drop('variants', axis=1)

df['image'] = df[['variant_image', 'model_image']].apply(lambda x: pickImage(x[0], x[1]), axis = 1)
df.drop(['variant_image', 'model_image'], axis = 1, inplace=True)

# extend attributes
data = df.to_dict('records')
complete_data = []
for d in data:
    at = transform_attrs(d.pop('attrs'))
    complete_data.append({**d, **at})
complete_data
df = pd.DataFrame(complete_data).fillna('').replace(['nan', 'Nan'], '')
# map to ERP columns
eng_df = df[['brand_id', 'model_name', 'model_year', 'brand_name', 'model_id', 'mpn', 'gtin', 'size', 'color', 'price', 'image', 'category_name']]
for erp, bidex in bidex_erp.values:
    if bidex in df.columns:
        eng_df[erp] = df[bidex]
    else:
        eng_df[erp] = ''
df = eng_df
printdf(df.head(10))



# Cleaning


df = df.astype(str).replace(['nan', 'NaN'], '').fillna('')


def clean_model_name(model_name, model_year):
    clean_model_name = model_name.replace(model_year,"").strip() 
    return pd.Series([clean_model_name])


df[['model_name']] = df.apply(lambda x: clean_model_name(x['model_name'], x['model_year']), axis=1)


def clean_size(size):
    size = size.replace('“','"').replace('420','42').replace(' cm','cm').strip()
    try: 
        splitted_size = size.split()
        frame_shape  =splitted_size[0].strip()
        try : 
            if '"' not in splitted_size[1]:
                frame_size =splitted_size[1]
                try: 
                    wheel_size =splitted_size[2]
                except: 
                    wheel_size=''
            else : 
                wheel_size =splitted_size[1]
                try: 
                    frame_size =splitted_size[2]
                except: 
                    frame_size=''
        except:
            frame_size =""
            wheel_size =""
        
    except:
        frame_shape  ="" 
        frame_size =""
        wheel_size =""
    return pd.Series([frame_shape, frame_size.replace(')','').replace('uni','unisex').replace('(','/').replace('cm', ' cm'), wheel_size.replace(',','.').replace('".','"').replace('+','')])



df[['frame_shape', 'frame_size', 'wheel_size'] ] = df.apply(lambda x: clean_size(x['size']), axis=1)


def clean_rear_derailleur(rear_derailleur):
    pattern = re.compile(r"\b(\d+)-Speed\b|\b(\d+) Speed\b|\b(\d+)-S\b", re.IGNORECASE)
    match = pattern.search(rear_derailleur)

    if match:
        if match.group(1):
            gear_count = match.group(1)  
        elif match.group(2):
            gear_count = match.group(2)  
        elif match.group(3):
            gear_count = match.group(3)  
    else:
        gear_count =''
    clean_rear_derailleur = re.sub(pattern, '',rear_derailleur).strip()
    
    return pd.Series([ gear_count, clean_rear_derailleur])


df[[ 'gear_count', 'rear_derailleur']] = df.apply(lambda x: clean_rear_derailleur(x['rear_derailleur']), axis=1)


def clean_engine(engine):
    pattern_engine_torque = re.compile(r'\s\d+\s*Nm', re.IGNORECASE)
    match = pattern_engine_torque.search(engine)
    if match:
        
        engine_torque = match.group(0).replace(' ','')  # Output: 11

    else:
        engine_torque =''
    pattern_engine_power = re.compile(r'\s\d+\s*W,', re.IGNORECASE)
    match = pattern_engine_power.search(engine)
    if match:
        
        engine_power = match.group(0).replace(' ','').replace(',','')  # Output: 11

    else:
        engine_power =''
    engine_speed =''
    clean_engine= re.sub(pattern_engine_power,'',re.sub(pattern_engine_torque , '',engine))
    return pd.Series([ engine_torque, engine_power, engine_speed, clean_engine])


def clean_engine(engine):
    pattern_engine_torque = re.compile(r'\s\d+\s*Nm', re.IGNORECASE)
    match = pattern_engine_torque.search(engine)
    if match:
        
        engine_torque = match.group(0).replace(' ','') 

    else:
        engine_torque =''
    pattern_engine_power = re.compile(r"\s\d+\s*W|(\d)+W", re.IGNORECASE)
    match =re.search(pattern_engine_power,  engine)
    if match:
        engine_power = match.group(0).replace('W','').strip()
    else:
        engine_power =''
    engine_speed =''
    clean_engine= re.sub(pattern_engine_power,'',re.sub(pattern_engine_torque , '',engine))
    return pd.Series([ engine_torque, engine_power, engine_speed, clean_engine])


df[[ 'engine_torque', 'engine_power', 'engine_speed' , 'engine']] = df.apply(lambda x: clean_engine(x['engine']), axis=1)





def clean_battery(battery):
    battery =battery.replace('\u202f', '')
    pattern_battery_capacity = re.compile(r'\s\d+\s*Wh', re.IGNORECASE)
    match = pattern_battery_capacity.search(battery)
    if match:
        
        battery_capacity= match.group(0).replace(' ','')  # Output: 11

    else:
        battery_capacity =''
   
    
    clean_battery= re.sub(pattern_battery_capacity,'',re.sub(pattern_battery_capacity , '',battery)).replace(',,',',')
    if 'Battery' in clean_battery:
        battery_position = clean_battery.split(',')[-1].replace('Battery','').strip()
        clean_battery = ','.join(clean_battery.split(',')[0:-1])
    else:
        battery_position =''
    return pd.Series([ battery_capacity.replace('Wh', ' Wh'), clean_battery,battery_position  ])


df[['battery_capacity', 'battery', 'battery_position'] ] = df.apply(lambda x: clean_battery(x['battery']), axis=1)



df['rrp'] = df['price'].apply(lambda x: x.replace(',00', ''))
df = df.drop('price', axis=1)


df.weight =df['weight'].apply(lambda x: x.replace(',', '.'))
df.max_weight =df['max_weight'].apply(lambda x: x.replace(',', '.'))


# important columns
cols = ['mpn',
 'gtin',
 'brand_name',
 'model_name',
 'model_year',
 'color',
 'category_name',
 'frame_shape',
 'frame_size',
 'wheel_size',
 'rrp',
 'image',
 'battery',
 'battery_capacity',
 'battery_position',
 'gear_count',
 'front_derailleur',
 'rear_derailleur',
 'engine',
 'engine_power',
 'engine_torque',
 'engine_speed',
 'brake_disc',
 'brake_lever',
 'carrier',
 'cassette',
 'chain_guard',
 'charger',
 'crankset',
 'damper',
 'display',
 'dynamo',
 'fork',
 'frame',
 'front_brake',
 'rear_brake',
 'front_hub',
 'rear_hub',
 'rear_tyre',
 'front_tyre',
 'front_wheel',
 'rear_wheel',
 'gear_shift_lever',
 'grips',
 'handlebars',
 'handles',
 'headset',
 'lighting',
 'max_weight',
 'mudguards',
 'pedals',
 'permissible_trailer_load',
 'rear_light',
 'saddle',
 'seat_post',
 'spokes',
 'stand',
 'stem',
 'weight',
 'front_rim',
 'rear_rim',
 'saddle_clamping',
 'lock',
 'description']


for c in cols:
    if c not in df.columns:
        df[c] = ''
printdf(df[cols].head())


df[cols].to_csv('r_raymon.csv', index = 0)


import boto3
s3_resource = boto3.client('s3')
s3_resource.upload_file('/usr/share/tomcat8/r_raymon.csv', 'bi-rebike', 'Bidex/r_raymon.csv')

















