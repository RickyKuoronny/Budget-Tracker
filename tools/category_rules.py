CATEGORY_RULES = {
    'Transfers': [
        'INTERNET TRANSFER DEBIT TO', 'INTERNET TRANSFER CREDIT FROM', 'INTERNET TRANSFER FROM',
        "INTERNET EXTERNAL TRANSFER TO"
    ],

    'Revolut': [
        'REVOLUT', 'REVOLUT LTD', 'REVOLUT LIMITED',    
    ],

    'Giving': [
        'TITHE', 'TITHES', 'ICC BRISBANE',
        'INTERNATIONAL CITY CHURCH', 'CITY CHURCH',
        'ICC_BRISBANE', 'INTNL CITY CHURCH',
    ],

    'Refunds': [
        'REFUND', 'REVERSAL', 'RETURN', 'ADJUSTMENT',
    ],

    'Reimbursements': [
        'OSKO PAYMENT TO', 'NPP PAYMENT FROM', 'REIMBURSEMENT', 'PAYING YOU BACK', 'PAID BACK',
        'PAYBACK', 'REPAY', 'OSKO PAYMENT FROM', 'TAX', 'BEEM',
    ],

    'Income': [
        'SALARY', 'PAYROLL', 'DIRECT CREDIT', 'BONUS', 'CREDIT INTEREST',
    ],

    'Mobile Phone': [
        'FELIX MOBILE', 'E TEL',
    ],

    'Utilities & Subscriptions': [
        'APPLE COM BILL', 'SPOTIFY', 'DOCCY', 'ICLOUD', 'GOOGLE',
        'MICROSOFT', 'ADOBE', 'EVERYDAY EXTRA',
    ],

    'Groceries': [
        'WOOLWORTH', 'COLES', 'IGA', 'YUENS', 'ROSALIE GOURMET MARKET', 'FOODWORKS',
        'ALDI', 'HARRIS FARM', 'SUPERMARKET', 'GROCERY', 'PHAM S FAMILY FRESH',
        'FRUIT', 'GREENGROCER', 'BUTCHER', 'SEAFOOD', 'ASIAN GROCER', 'METRO',
        'FRESH FOOD', 'SUNLIT', 'PLUSMART', 'GENKI MART', 'BWS', 'LIQUORLAND', 'DAN MURPHY',
    ],

    'Food & Dining': [
        # Chains
        'MCDONALD', 'KFC', 'SUBWAY', 'DOMINO', 'GUZMAN', 'GRILLD', 'NANDOS', 'WENDYS', 'STARBUCKS',
        # Generic food types
        'RESTAURANT', 'CAFE', 'COFFEE', 'ESPRESSO', 'BAKERY', 'FOOD COURT',
        'RAMEN', 'SUSHI', 'KOREAN', 'JAPANESE', 'CHICKEN', 'BURGER', 'PIZZA', 'KEBAB',
        'NOODLE', 'BUBBLE TEA', 'TEA', 'GELATO', 'ACAI', 'TARTS',
        'THAI', 'FISH AND CHIPS', 'VIETNAM', 'KITCHEN', 'BAPSANG', 'ORIENTAL',
        'TEPPAN', 'HOT BREAD', 'GELATERI', 'DESSERT', 'PHO', 'COFFEE',
        # Named venues
        'FISHBOWL', 'CHATIME', 'MIXUE', 'MERLO', 'HEY JUICE', 'BAR MERLO',
        'GU DESSERT', 'HANARO', 'ZHANG LIANG', 'SHALOM', 'PHO PHO', 'SEOUL BITES',
        'YOKO', 'DAVID MASTER POT', 'SATAY BOSS', 'SHIBUSAWA', 'LITTLE MARU',
        'LUCHA', 'WALKWAY TO CEYLON', 'YIROS', 'NOOSA CHOCOLATE',
        'GERBINOS', 'KHUSHI', 'ZIA', 'BINGGO', 'BIRRIA', 'PHIA', 'YOZO',
        'MASSIMO', 'JIUBO', 'TIANXIA', 'COCOART', 'AMFOODS', 'HAIDILAO',
        'KIN TENERIFFE', 'ZAM', 'MILKI', 'A YI', 'K WANT EAT', 'MR DENO',
        'TARTE', 'FALALALAH', 'U GO', 'MESSINA', 'GRIDDLE', 'KATSU',
        'LUCKY BOWL', 'UDONYA', 'ODAYA', 'KUAFOOD', 'MY STREET FOOD',
        'UNCLE DON', 'KINGWU', 'BARRY UNION', 'MENAGERIE', 'MEKONG',
        'PKATSU', 'IKKAKU', 'MALAYACNR', 'MALAYA CORN', 'NOA EVEN',
        'FOOD EMPEROR', 'K GARDEN', "WIL'S RESTO", 'WIL S RESTO', 'SAINT LUCY CAFFE',
        '5 BOROUGHS', 'BIG KID ICE', 'NONOS', 'INSANE ACAI', 'ANITA GELATO',
        'BEING RICHBRO', 'MISS CLAUDES', 'ALLORA', 'CYD HOLDING',
        'BNE BROTHERS', 'CLOVERAUS', 'OTBO', 'SUNSHINE', 'OCEAN TUCKER',
        'HAEDURI', 'EATCLUB', 'ADDICTEA', 'HEERETEA', 'HEYTEA',
        'KAIKAI', 'SLIMS', '2 BROS', 'GOUKARI', 'AUTHENTIC', 'Supernumerary Coffe',
        'BREWER', 'COFFEE', 'CIAO BELLO', 'BONGSDONB', 'DOORDASH',
    ],

    'Transport': [
        'TRANSLINK', 'PARKING', 'CAR PARK', 'CELLOPARK',
        'UNITED', 'PETROL', 'AMPOL', 'SHELL', 'EG GROUP',
        'BP ', '7 ELEVEN', 'REDDY EXPRESS', 'FUEL', 'MODI', 'CHEAP AUTO',
    ],

    'Sports & Recreation': [
        'URBAN CLIMB', 'UQ SPORT', 'BADMINTON', 'TENNIS', 'GOLF',
        'ICEWORLD', 'Q MASTERS', 'GOODLIFE', '9 DEGREES',
    ],

    'Health': [
        'CHEMIST', 'PHARMACY', 'PRICELINE', 'TERRYWHITE', 'AMCAL',
        'BLOOMS', 'OPTICAL', 'SPECSAVERS',
    ],

    'Shopping': [
        'KMART', 'BIG W', 'UNIQLO', 'DAVID JONES', 'DAVIDJONESL', 'OFFICEWORKS',
        'JB HI FI', 'REBEL', 'T CUT', 'SPOTLIGHT', 'JAYCAR',
        'FLOWER', 'FLOWERS', 'FLORIST', 'BOOKSHOP', 'MADE IN EARTH',
        'COURSE', 'TEXTBOOK', 'UDEMY', 'COURSERA', 'CAMBRIDGE',
        'DUSK', 'KOORONG', 'MADEINEARTH', 'CLOTHING',
        'STACKS VARIETY', 'NOVO SHOES', 'IKEA', 'EBAY', 'PETSTOCK',
        'DOLLARS AND SENSE', 'W RETAIL GROUP', 'REJECT', 'POST',
    ],

    'Entertainment': [
        'RIOT GAMES', 'RIOTGAMESLI', 'SUPERCELL', 'STEAM', 'EB GAMES', 'POKEMON', 'XSOLLA',
    ],

    'Travel': [
        'AIRBNB', 'BOOKING', 'KLOOK', 'AUNT BETTY', 'AUNTBETTY',
        'SMARTE CARTE', 'HOWARDSMITH', 'TURO', 'TRAVELKON', 
    ],

    'Experiences': [
        'PLANETARIUM', 'STATE LIBRARY', 'MUSEUM', 'GRADUATION', 'EVENT', 'TICKET',
        'UQU', 'THE SUMMIT', 'KIOSK', 'BCC PLANETARIUM', 'BOUNCE', 'ESCAPEKIT',
    ],

    'Cash': [
        'ATM',
    ],
}


PRIORITY_CATS = [
    'Transfers', 'Giving', 'Refunds', 'Reimbursements', 'Income', 'Revolut'
]
 
STANDARD_CATS = [
    'Mobile Phone', 'Utilities & Subscriptions', 'Food & Dining', 'Groceries',
    'Transport', 'Sports & Recreation', 'Beauty & Grooming', 'Health',
    'Shopping', 'Travel', 'Entertainment', 'Experiences', 'Cash',
]
 