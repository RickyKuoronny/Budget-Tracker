from pathlib import Path
import csv
import re

CATEGORY_RULES = {
    'Transfers': [
        'INTERNET TRANSFER DEBIT TO', 'INTERNET TRANSFER CREDIT FROM', 'INTERNET TRANSFER FROM'
    ],

    'Giving': [
        'TITHE', 'TITHES',
        'INTERNATIONAL CITY CHURCH', 'CITY CHURCH',
        'ICC_BRISBANE', 'INTNL CITY CHURCH'
    ],

    'Refunds': [
        'REFUND', 'REVERSAL', 'RETURN', 'ADJUSTMENT'
    ],

    'Reimbursements': [
        'NPP PAYMENT FROM', 'REIMBURSEMENT', 'PAYING YOU BACK', 'PAID BACK',
        'PAYBACK', 'REPAY', 'OSKO PAYMENT FROM', 'OSKO PAYMENT TO', 'TAX'
    ],

    'Income': [
        'SALARY', 'PAYROLL', 'DIRECT CREDIT',
        'BONUS', 'CREDIT INTEREST'
    ],

    'Mobile Phone': [
        'FELIX MOBILE', 'E TEL'
    ],

    'Utilities & Subscriptions': [
        'APPLE.COM/BILL', 'APPLE COM BILL', 'SPOTIFY', 'DOCCY',
        'ICLOUD', 'GOOGLE', 'MICROSOFT', 'ADOBE',
        'EVERYDAY EXTRA'
    ],

    'Groceries': [
        'WOOLWORTH', 'COLES', 'IGA',
        'ALDI', 'HARRIS FARM', 'MARKET', 'SUPERMARKET', 'GROCERY',
        'FRUIT', 'GREENGROCER', 'BUTCHER', 'SEAFOOD', 'ASIAN GROCER', 'FRESH FOOD', 'SUNLIT', 'PLUSMART', 'GENKI MART'
    ],

    'Food & Dining': [
        'RESTAURANT', 'CAFE', 'COFFEE', 'ESPRESSO', 'BAKERY', 'FOOD COURT',
        'RAMEN', 'SUSHI', 'KOREAN', 'JAPANESE', 'CHICKEN', 'BURGER', 'PIZZA', 'KEBAB',
        'NOODLE', 'BUBBLE TEA', 'TEA', 'MCDONALD', 'KFC', 'SUBWAY', 'DOMINO', 'GUZMAN', 'GRILLD', 'FISHBOWL', 'CHATIME', 'MIXUE',
        'MERLO', 'HEY JUICE', 'BAR MERLO', 'GU DESSERT', 'HANARO', 'ZHANG LIANG', 'SHALOM', 'PHO PHO', 'SEOUL BITES', 'YOKO', 'DAVID MASTER POT', 'SATAY BOSS', 'SHIBUSAWA', 'LITTLE MARU', 'LUCHA', 'WALKWAY TO CEYLON', 'YIROS', 'NOOSA CHOCOLATE',
        'THAI', 'FISH AND CHIPS', 'VIETNAM', 'KITCHEN', 'BAPSANG', 'AUTHENTIC', 'GERBINOS', 'KHUSHI', 'ZIA', 'BINGGO', 'ORIENTAL',
        'WENDYS', 'BIRRIA', 'FISHBOWL', 'PHIA', 'YOZO', 'TEPPAN', 'HOT BREAD', 'BREWER', 'COFFE',
        'GELATERI', 'GRILLD', 'THE YIROS SHOP NEWMARKET', 'TARTS', 'MASSIMO', 'JIUBO', 'TIANXIA', 'COCOART', 'SUNSHINE', 'AMFOODS'
    ],

    'Transport': [
        'TRANSLINK', 'PARKING', 'CAR PARK', 'CELLOPARK', 'PETROL', 'UNITED PETROLEUM',
        'BP', 'SHELL', 'AMPOL', '7 ELEVEN', 'REDDY EXPRESS', 'FUEL', 'MODI', 'CHEAP AUTO', 'AUTO'
    ],

    'Sports & Recreation': ['URBAN CLIMB', 'UQ SPORT', 'BADMINTON', 'TENNIS', 'GOLF', 'ICEWORLD', 'Q-MASTERS', 'GOODLIFE', '9 DEGREES'],

    'Health': ['CHEMIST', 'PHARMACY', 'PRICELINE', 'TERRYWHITE', 'AMCAL', 'BLOOMS', 'OPTICAL', 'SPECSAVERS'],

    'Shopping': ['KMART', 'BIG W', 'UNIQLO', 'DAVID JONES', 'OFFICEWORKS', 'JB HI FI', 'REBEL', 'SPOTLIGHT', 'JAYCAR', 'FLOWER', 'FLOWERS', 'FLORIST', 'UNIVERSITY', 'QUT', 'COURSE', 'TEXTBOOK', 'UDEMY', 'COURSERA', 'REJECT', 'CAMBRIDGE', 'DUSK', 'KOORONG', 'MADEINEARTH', 'CLOTHING'],

    'Entertainment': ['RIOT GAMES', 'SUPERCELL', 'STEAM', 'EB GAMES', 'POKEMON', 'XSOLLA'],

    'Travel': ['AIRBNB', 'BOOKING', 'KLOOK', 'AUNT BETTY', 'SMARTE CARTE', 'STATION', 'HOWARDSMITH', 'TURO'],

    'Experiences': [
        'PLANETARIUM', 'STATE LIBRARY', 'MUSEUM', 'GRADUATION', 'EVENT', 'TICKET',
        'UQU', 'THE SUMMIT', 'KIOSK', 'BCC PLANETARIUM'
    ]
}


def normalize_desc(raw_desc: str) -> str:
    if raw_desc is None:
        return ''
    s = str(raw_desc).upper()
    # remove common bank prefixes/markers
    s = re.sub(r'VISA PURCHASE', ' ', s)
    s = re.sub(r'EFTPOS WDL', ' ', s)
    s = re.sub(r'ATM WITHDRAWAL', ' ', s)
    s = re.sub(r'SQ \*', ' ', s)
    s = re.sub(r'LS ', ' ', s)
    s = re.sub(r'ZLR\*', ' ', s)
    s = re.sub(r'SMP\*', ' ', s)
    s = re.sub(r'REVOLUT\*\*\d+\*', 'REVOLUT', s)
    s = re.sub(r'PAYPAL \*', '', s)
    # remove stray non-alphanumeric except spaces
    s = re.sub(r'[^A-Z0-9 ]+', ' ', s)
    # collapse spaces
    s = re.sub(r'\s+', ' ', s).strip()
    return s


def matches_any(desc, keywords):
    return any(k in desc for k in keywords) if keywords else False


def is_income(desc):
    return matches_any(desc, CATEGORY_RULES.get('Income', []))


def classify(description, amount):
    desc = normalize_desc(description)
    amt = str(amount) if amount is not None else ''
    amt_clean = amt.replace('$', '').replace(',', '').strip()
    is_debit = str(amt_clean).startswith('-')

    # Priority checks
    if matches_any(desc, CATEGORY_RULES.get('Transfers')):
        return 'Transfers'
    if matches_any(desc, CATEGORY_RULES.get('Giving')):
        return 'Giving'
    if matches_any(desc, CATEGORY_RULES.get('Refunds')):
        return 'Refunds'
    if matches_any(desc, CATEGORY_RULES.get('Reimbursements')):
        # Only consider reimbursements when the transaction is a credit (positive amount)
        if not is_debit:
            return 'Reimbursements'
    if matches_any(desc, CATEGORY_RULES.get('Gifts')):
        return 'Gifts'

    # Income by keyword (safer than inferring from positive amounts)
    if is_income(desc):
        return 'Income'

    # Category checks (less priority)
    for cat in ['Mobile Phone', 'Utilities & Subscriptions', 'Food & Dining', 'Groceries', 'Gym',
                'Transport', 'Sports & Recreation', 'Shopping', 'Travel', 'Entertainment', 'Health', 'Experiences']:
        if matches_any(desc, CATEGORY_RULES.get(cat)):
            return cat

    return 'Unsorted'

files = ['EVERYDAY OPTIONS.csv','Savings.csv','Short.csv']
for name in files:
    path = Path(name)
    rows=[]
    with path.open('r',encoding='utf-8-sig',newline='') as h:
        rows = list(csv.reader(h))
    cats={}
    for r in rows:
        if len(r)>=4:
            date=r[0].strip()
            desc=r[1].strip()
            amt=r[2].strip()
            if '/' in date and any(ch.isdigit() for ch in date):
                cat=classify(desc,amt)
                cats[cat]=cats.get(cat,0)+1
    print(name)
    for k,v in sorted(cats.items(), key=lambda x:-x[1]):
        print(f'  {k}: {v}')
    print()
