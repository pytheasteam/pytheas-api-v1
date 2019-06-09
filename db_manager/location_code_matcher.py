

# country : city
countries_cities = {
    'london' : 'LCY',
    'paris' : 'PAR',
    'rome' : 'ROM',
    'vatican' : 'ROM',
    'crete' : 'HER',
    'bali' : 'DPS',
    'phuket' : 'HKT',
    'barcelona' : 'BCN',
    'istanbul' : 'IST',
    'marrakech' : 'RAK',
    'dubai' : 'DXB',
    'prague' : 'PRG',
    'siem reap' : 'REP',
    'new york city' : 'NYC',
    'jamaica' : 'JM',
    'hanoi' : 'HAN',
    'tokyo' : 'TYO',
    'playa del carmen' : 'PCM',
    'lisbon' : 'LIS',
    'kathmandu' : 'KTM',
    'jaipur' : 'JAI',
    'hurghada' : 'HRG',
    'hong kong' : 'HKG',
    'cusco' : 'CUZ',
    'sydney' : 'SYD',
    'tel aviv' : 'TLV'
}


class LocationMatcher:

    @staticmethod
    def get_iata_for_city(city_name):
        city_name = city_name.lower()
        if city_name in countries_cities.keys():
            return countries_cities[city_name]
        return None


