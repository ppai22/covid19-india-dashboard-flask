import requests

from config import Names


class Service:
    """
    Class with all services
    """

    # API path from covid19india.org to fetch the data
    URL = "https://api.covid19india.org/states_daily.json"
    # State codes used in th API
    STATES = ['an', 'ap', 'ar', 'as', 'br', 'ch', 'ct', 'dd', 'dl', 'dn',
              'ga', 'gj', 'hp', 'hr', 'jh', 'jk', 'ka', 'kl', 'la', 'ld',
              'mh', 'ml', 'mn', 'mp', 'mz', 'nl', 'or', 'pb', 'py', 'rj',
              'sk', 'tg', 'tn', 'tr', 'tt', 'un', 'up', 'ut', 'wb']

    def load_data(self):
        """
        Method to load data from the API
        :return: dict
        """
        r = requests.get(self.URL)
        data = r.json()
        return data

    def tabulate(self):
        """
        Method that tabulates the data into a dictonary in the required format
        :return: dict
        """
        data = self.load_data()
        dataset = {}
        dates = []
        for state in self.STATES:
            dataset[state] = {
                'Confirmed': [],
                'Recovered': [],
                'Deceased': [],
                'Total Active': [],
                'Total Recovered': [],
                'Total Deceased': []
            }

        for item in data['states_daily']:
            status = item['status']
            dates.append(item['date'])
            for state in item.keys():
                if state in dataset.keys():
                    dataset[state][status].append(item[state])
            dates = list(dict.fromkeys(dates))

        for state in dataset.keys():
            dataset_state = dataset[state]
            for i in range(len(dates)):
                active = int(dataset_state['Confirmed'][i]) - \
                         (int(dataset_state['Recovered'][i]) +
                          int(dataset_state['Deceased'][i]))
                if i == 0:
                    dataset_state['Total Recovered'].append(int(dataset_state['Recovered'][i]))
                    dataset_state['Total Deceased'].append(int(dataset_state['Deceased'][i]))
                    dataset_state['Total Active'].append(active)
                else:
                    dataset_state['Total Recovered'].append(
                        int(dataset_state['Total Recovered'][-1]) +
                        int(dataset_state['Recovered'][i])
                    )
                    dataset_state['Total Deceased'].append(
                        int(dataset_state['Total Deceased'][-1]) +
                        int(dataset_state['Deceased'][i])
                    )
                    dataset_state['Total Active'].append(
                        int(dataset_state['Total Active'][-1]) +
                        active
                    )

        return dataset, dates

    def get_total_active_all_states(self):
        """
        Method to fetch only the active cases to display on home page
        :return: dict
        """
        data = self.load_data()
        dataset = {}
        active_cases_states = {}
        for state in self.STATES:
            dataset[state] = {
                'Confirmed': [],
                'Recovered': [],
                'Deceased': []
            }

        for item in data['states_daily']:
            status = item['status']
            for state in item.keys():
                if state in dataset.keys():
                    dataset[state][status].append(item[state])

        for state in self.STATES:
            active_cases_states[state] = sum([int(item) for item in dataset[state]['Confirmed']]) - \
                                         sum([int(item) for item in dataset[state]['Recovered']]) - \
                                         sum([int(item) for item in dataset[state]['Deceased']])
        return active_cases_states

    def load_state_data(self, name):
        """
        Method to load the state data to display in the state page
        :param name:
        :return:
        """
        state = Names.get_code_from_name(name)
        if name == 'all':
            dataset, dates = self.tabulate()
            return dataset['tt'], dates
        else:
            dataset, dates = self.tabulate()
            return dataset[state], dates