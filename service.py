import numpy
import pandas
import requests
import io

from config import Names


class Service:
    """
    Class with all services
    """

    # API path from covid19india.org to fetch the data
    URL = "https://data.incovid19.org/csv/latest/state_wise_daily.csv"
    # State codes used in th API
    STATES = ['an', 'ap', 'ar', 'as', 'br', 'ch', 'ct', 'dl', 'dn',
              'ga', 'gj', 'hp', 'hr', 'jh', 'jk', 'ka', 'kl', 'la', 'ld',
              'mh', 'ml', 'mn', 'mp', 'mz', 'nl', 'or', 'pb', 'py', 'rj',
              'sk', 'tg', 'tn', 'tr', 'tt', 'un', 'up', 'ut', 'wb']
    # Vaccination data
    VACCINATION_URL = \
        "https://raw.githubusercontent.com/owid/covid-19-data/master/public/data/vaccinations/country_data/India.csv"

    def __init__(self):
        self.data = self.load_data()

    def load_data(self):
        """
        Method to load data from the API
        :return: dict
        """
        s = requests.get(self.URL).content
        data = pandas.read_csv(io.StringIO(s.decode('utf-8')))
        data = data.rename(columns=str.lower)
        data = {'states_daily': data.to_dict('records')}

        return data

    def fetch_dates(self):
        """
        Method to fetch dates only
        :return:
        """
        data = self.data
        dates = []
        for item in data['states_daily']:
            dates.append(item['date'])
            dates = list(dict.fromkeys(dates))
        return dates

    def tabulate(self):
        """
        Method that tabulates the data into a dictonary in the required format
        :return: dict
        """
        data = self.data
        dataset = {}
        seven_day_avg = {}
        seven_day_avg_deaths = {}
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
            try:
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
            except:
                pass

        for state in self.STATES:
            seven_day_avg[state] = [round(sum([int(val) for val in dataset[state]['Confirmed'][i-6:i+1]])/7)
                                    for i in range(7, len(dataset[state]['Confirmed']))]
            seven_day_avg_deaths[state] = [round(sum([int(val) for val in dataset[state]['Deceased'][i-6:i+1]])/7)
                                           for i in range(7, len(dataset[state]['Deceased']))]

        return dataset, dates, seven_day_avg, seven_day_avg_deaths

    def get_all_stats_last_day_all(self):
        """
        Returns latest data for all states for all parameters
        :return: dict
        """
        dataset, dates, seven_day_avg, seven_day_avg_deaths = self.tabulate()
        states = [k for k, v in Names.state_names.items() if k != 'tt']
        return_dict = {}
        for state in states:
            try:
                active = dataset[state]['Total Active'][-1]
                recovered = dataset[state]['Total Recovered'][-1]
                deceased = dataset[state]['Total Deceased'][-1]
                confirmed = active + recovered + deceased
                return_dict[Names.state_names[state]] = {
                    'total_confirmed': confirmed,
                    'total_active': active,
                    'total_recovered': recovered,
                    'total_deceased': deceased
                }
            except:
                pass
        return return_dict

    def get_recovery_rate(self):
        """
        Method to get latest recovery rate of all states
        :return: dict
        """
        dataset, _, _, _ = self.tabulate()
        recovery_data = {}
        recovery_data_trend = {}
        for state in Names.state_names:
            try:
                active = dataset[state]['Total Active'][-1]
                recovered = dataset[state]['Total Recovered'][-1]
                deceased = dataset[state]['Total Deceased'][-1]
                active_total = numpy.array([int(i) for i in dataset[state]['Total Active']])
                recovered_total = numpy.array([int(i) for i in dataset[state]['Total Recovered']])
                deceased_total = numpy.array([int(i) for i in dataset[state]['Total Deceased']])
                confirmed = active + recovered + deceased
                confirmed_total = active_total + recovered_total + deceased_total
                if int(confirmed) != 0:
                    recovery_data[state] = round(int(recovered) / int(confirmed) * 100, 2)
                else:
                    recovery_data[state] = 100
                recovery_data_trend[state] = numpy.nan_to_num(numpy.round(recovered_total / confirmed_total * 100, 2))
                recovery_data_trend[state] = recovery_data_trend[state].tolist()
            except:
                pass
        return recovery_data, recovery_data_trend

    def get_total_active_all_states(self):
        """
        Method to fetch only the active cases to display on home page
        :return: dict
        """
        data = self.data
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
            dataset, dates, seven_day_avg, seven_day_avg_deaths = self.tabulate()
            return dataset['tt'], dates, seven_day_avg['tt'], seven_day_avg_deaths['tt']
        else:
            dataset, dates, seven_day_avg, seven_day_avg_deaths = self.tabulate()
            return dataset[state], dates, seven_day_avg[state], seven_day_avg_deaths[state]

    def vaccination_data(self):
        """
        Method that fetches and serves the country level vaccination data
        :return:
        """
        data = pandas.read_csv(self.VACCINATION_URL)
        dates = numpy.array(data['date'])
        cumulative_vaccination = numpy.array(data['total_vaccinations'])
        daily_vaccination = numpy.diff(cumulative_vaccination)
        fully_vaccinated = numpy.array(data['people_fully_vaccinated'])
        daily_full_vaccination = numpy.diff(fully_vaccinated)
        sources = numpy.array(data['source_url'])
        return dates, cumulative_vaccination, daily_vaccination, fully_vaccinated, daily_full_vaccination, sources

    def get_recent_active_cases_increasing_trend(self):
        """
        Method that fetches states with increasing trend in active cases
        :return: dict - {'state_code': increase}
        """
        active_cases, dates, seven_day_avg, seven_day_avg_deaths = self.tabulate()
        increase_count = {}
        for state, data in active_cases.items():
            try:
                this_week = data['Total Active'][-7:]
                this_week_increase = this_week[-1] - this_week[0]
                # TODO: Figure out best estimate (Increase or percentage increase?)
                if this_week_increase > 0:
                    if max(this_week) == this_week[-1]:
                        increase_count[state] = this_week_increase
                    else:
                        if max(this_week) - this_week[-1] <= 0.10 * this_week[0]:
                            increase_count[state] = this_week_increase
            except:
                pass
        return increase_count

    def get_recent_active_cases_decreasing_trend(self):
        """
        Method that fetches states with decreasing trend in active cases
        :return: dict - {'state_code': decrease}
        """
        active_cases, dates, seven_day_avg, seven_day_avg_deaths = self.tabulate()
        decrease_count = {}
        for state, data in active_cases.items():
            try:
                this_week = data['Total Active'][-7:]
                this_week_decrease = this_week[-1] - this_week[0]
                # TODO: Figure out best estimate (Decrease or percentage decrease?)
                if this_week_decrease <= 0:
                    decrease_count[state] = this_week_decrease
            except:
                pass
        return decrease_count
