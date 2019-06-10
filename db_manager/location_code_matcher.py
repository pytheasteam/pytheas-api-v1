# country : city
countries_cities = {
    'london': 'LCY',
    'paris': 'PAR',
    'rome': 'ROM',
    'vatican': 'ROM',
    'crete': 'HER',
    'bali': 'DPS',
    'phuket': 'HKT',
    'barcelona': 'BCN',
    'istanbul': 'IST',
    'marrakech': 'RAK',
    'dubai': 'DXB',
    'prague': 'PRG',
    'siem reap': 'REP',
    'new york city': 'NYC',
    'jamaica': 'JM',
    'hanoi': 'HAN',
    'tokyo': 'TYO',
    'playa del carmen': 'PCM',
    'lisbon': 'LIS',
    'kathmandu': 'KTM',
    'jaipur': 'JAI',
    'hurghada': 'HRG',
    'hong kong': 'HKG',
    'cusco': 'CUZ',
    'sydney': 'SYD',
    'tel aviv': 'TLV'
}

cities_booking_codes = {
    'london': '-2601889',
    'paris': '-1456928',
    'rome': '-126693',
    'vatican': '-126693',  # 57962
    'crete': '811',
    'bali': '835',
    'phuket': '-3253342',
    'barcelona': '-372490',
    'istanbul': '-755070',
    'marrakech': '-38833',
    'dubai': '-782831',
    'prague': '-553173',
    'siem reap': '-1032755',
    'new york city': '20088325',
    'jamaica': '20087322',
    'hanoi': '-3714993',
    'tokyo': '-246227',
    'playa del carmen': '-1689065',
    'lisbon': '-2167973',
    'kathmandu': '-1022136',
    'jaipur': '-2098033',
    'hurghada': '-290029',
    'hong kong': '-1353149',
    'cusco': '-345275',
    'sydney': '-1603135',
    'tel aviv': '-781545'
}


class LocationMatcher:

    @staticmethod
    def get_iata_for_city(city_name):
        city_name = city_name.lower()
        if city_name in countries_cities.keys():
            return countries_cities[city_name]
        return None

    @staticmethod
    def get_booking_code_for_city(city_name):
        city_name = city_name.lower()
        if city_name in cities_booking_codes.keys():
            return cities_booking_codes[city_name]
        return None

