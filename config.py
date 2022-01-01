

class Names:
    """
    Config classes that stores state codes and names as required for
    both the API as well as the java script library to display the map
    """

    state_names = {
        'an': 'Andaman and Nicobar',
        'ap': 'Andhra Pradesh',
        'ar': 'Arunanchal Pradesh',
        'as': 'Assam',
        'br': 'Bihar',
        'ch': 'Chandigarh',
        'ct': 'Chhattisgarh',
        'dl': 'NCT of Delhi',
        'dn': 'Dadra and Nagar Haveli',
        'ga': 'Goa',
        'gj': 'Gujarat',
        'hp': 'Himachal Pradesh',
        'hr': 'Haryana',
        'jh': 'Jharkhand',
        'jk': 'Jammu and Kashmir',
        'ka': 'Karnataka',
        'kl': 'Kerala',
        'la': 'Ladakh',
        'ld': 'Lakshadweep',
        'mh': 'Maharashtra',
        'ml': 'Meghalaya',
        'mn': 'Manipur',
        'mp': 'Madhya Pradesh',
        'mz': 'Mizoram',
        'nl': 'Nagaland',
        'or': 'Odisha',
        'pb': 'Punjab',
        'py': 'Puducherry',
        'rj': 'Rajasthan',
        'sk': 'Sikkim',
        'tg': 'Telangana',
        'tn': 'Tamil Nadu',
        'tr': 'Tripura',
        'tt': 'India',
        'un': 'Unknown',
        'up': 'Uttar Pradesh',
        'ut': 'Uttarakhand',
        'wb': 'West Bengal'
    }

    @staticmethod
    def get_code_from_name(name):
        """
        Method to fetch the state code from the name of the state
        :param name:
        :return: str
        """
        state_names = Names.state_names
        codes = list(state_names.keys())
        names = list(state_names.values())
        state_code = codes[names.index(name)]
        return state_code
