import os
import requests

from flask import Flask, render_template, request, redirect
from flask_wtf.csrf import CSRFProtect

from config import Names
from forms import DataDurationBox, SelectState
from service import Service
from states import get_states_linked_list


app = Flask(__name__, template_folder='templates')
# 'set SECRET_KEY=<secret_key>' in terminal for debug mode
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY')
csrf = CSRFProtect(app)
csrf.init_app(app)

service = Service()


@app.route('/states/', methods=['GET', 'POST'])
def state_data():
    """
    App route to display the state data
    Options available via drop down menu to select state
    :return:
    """
    form = SelectState()
    if form.is_submitted():
        response = request.form
        state_code = Names.state_names[response['state']]
        return redirect(f'/{state_code}')
    else:
        context = {
            'form': form,
            'states': [v for k, v in Names.state_names.items()]
        }
    return render_template('display.html', context=context)


@app.route('/<state_code>/', methods=['GET', 'POST'])
def details(state_code):
    """
    Generic endpoint to get to a state page via state_code
    :param state_code: str name of the state
    :return:
    """
    dataset, dates, seven_day_avg, seven_day_avg_deaths = service.load_state_data(state_code)
    recovery_rate = service.get_recovery_rate()[0][Names.get_code_from_name(state_code)]
    recovery_rate_trend = service.get_recovery_rate()[1][Names.get_code_from_name(state_code)]
    if state_code != 'all':
        name = Names.state_names[Names.get_code_from_name(state_code)]
    else:
        name = Names.state_names['tt']
    # Checkbox form to display last 30 days data only
    data_duration_form = DataDurationBox()
    if data_duration_form.validate_on_submit():
        checkbox_value = data_duration_form.checkbox.data
        if checkbox_value:
            for k, v in dataset.items():
                dataset[k] = v[-30:]
            dates = dates[-30:]
            seven_day_avg = seven_day_avg[-30:]
            seven_day_avg_deaths = seven_day_avg_deaths[-30:]
            recovery_rate_trend = recovery_rate_trend[-30:]
    state_nodes = get_states_linked_list()
    context = {
        'dataset': dataset,
        'dates': dates,
        'name': name,
        'states': [v for k, v in Names.state_names.items()],
        'seven_day_avg': seven_day_avg,
        'seven_day_avg_deaths': seven_day_avg_deaths,
        'dates_seven_day_avg': dates[7:],
        'recovery_rate': recovery_rate,
        'recovery_rate_trend': recovery_rate_trend,
        'data_duration_form': data_duration_form,
        'state_nodes': state_nodes
    }
    return render_template('display.html', context=context)


@app.route('/', methods=['GET', 'POST'])
def home_page():
    """
    App route to display the home page with the map
    :return:
    """
    dataset = service.get_total_active_all_states()
    all_data = service.get_all_stats_last_day_all()
    table_data = [[], [], [], [], []]
    for state, state_data in all_data.items():
        if state != "India":
            table_data[0].append(state)
            table_data[1].append(state_data['total_confirmed'])
            table_data[2].append(state_data['total_active'])
            table_data[3].append(state_data['total_recovered'])
            table_data[4].append(state_data['total_deceased'])
    india_data, _, _, _ = service.load_state_data('India')
    data = []
    for state in Names.state_names.keys():
        data.append([Names.state_names[state].lower(), dataset[state]])

    # Increasing and Decreasing trends
    increase_states = service.get_recent_active_cases_increasing_trend()
    decrease_states = service.get_recent_active_cases_decreasing_trend()
    increasing_states = [(Names.state_names[state_code], round(val, 2))
                         for state_code, val in increase_states.items() if state_code not in ('un', 'tt')]
    decreasing_states = [(Names.state_names[state_code], round(val, 2))
                         for state_code, val in decrease_states.items() if state_code not in ('un', 'tt')]
    increasing_states.sort(key=lambda x: x[-1], reverse=True)
    decreasing_states.sort(key=lambda x: x[-1])

    # States Active cases pie chart data
    state_codes = table_data[0]
    state_active_cases = table_data[2]
    state_active_cases_data = list(zip(state_codes, state_active_cases))
    state_active_cases_data.sort(key=lambda x: x[-1], reverse=True)
    roi_sum = sum([v for _, v in state_active_cases_data[10:]])
    state_active_cases_data = state_active_cases_data[:10]
    state_active_cases_data_states = [k for k, v in state_active_cases_data]
    state_active_cases_data_values = [v for k, v in state_active_cases_data]
    context = {
        'data': data,
        'states': [v for k, v in Names.state_names.items()],
        'dataset': india_data,
        'table_data': table_data,
        'increasing_states': increasing_states[:10],
        'decreasing_states': decreasing_states[:10],
        'active_cases_pie_states': state_active_cases_data_states + ['Rest of India'],
        'active_cases_pie_values': state_active_cases_data_values + [roi_sum],
    }
    return render_template('home.html', context=context)


@app.route('/comparison/')
def comparison():
    """
    App route to display the states comparison of stats
    :return:
    """
    top_ten_active = {}
    top_ten_active_states = []
    latest_active = []
    tot_active_latest = []
    dataset, dates, seven_day_avg, seven_day_avg_deaths = service.tabulate()
    state_names = Names.state_names
    for state in state_names:
        if state != 'tt':
            latest_active.append((state, int(dataset[state]['Total Active'][-1])))
    latest_active = sorted(latest_active, key=lambda x: x[1], reverse=True)
    latest_active = latest_active[:10]
    for state, val in latest_active:
        top_ten_active[state] = dataset[state]['Total Active']
        top_ten_active_states.append(state)
    context = {
        'states': [v for k, v in Names.state_names.items()],
        'state_names': state_names,
        'dataset': dataset,
        'dates': dates,
        'top_ten_active': top_ten_active,
        'top_ten_active_states': top_ten_active_states,
        'latest_active': [v for _, v in latest_active],
        'latest_active_state_names': [Names.state_names[state_name] for state_name in top_ten_active_states]
    }
    return render_template('comparison.html', context=context)


@app.route('/recovery/')
def recovery_rate():
    """
    App route to display the recovery rates
    :return:
    """
    recovery_data, recovery_data_trend = service.get_recovery_rate()
    dates = service.fetch_dates()
    data = []
    for state in Names.state_names.keys():
        data.append([Names.state_names[state].lower(), recovery_data[state]])
    india_recovery = recovery_data['tt']
    context = {
        'dates': dates,
        'data': data,
        'states': [v for k, v in Names.state_names.items()],
        'india_recovery': india_recovery,
        'recovery_rate_trend': recovery_data_trend['tt'],
    }
    return render_template('recovery_rate.html', context=context)


@app.route('/vaccination/')
def vaccination_view():
    """
    App route to display India level vaccination data
    :return:
    """
    dates, cumulative_data, daily_data, fully_vaccinated, daily_fully_vaccinated, sources = service.vaccination_data()
    context = {
        'dates': dates.tolist(),
        'cumulative_data': cumulative_data.tolist(),
        'daily_data': [0] + daily_data.tolist(),
        'fully_vaccinated': fully_vaccinated.tolist(),
        'daily_fully_vaccinated': [0] + daily_fully_vaccinated.tolist(),
        'sources': sources.tolist(),
        'states': [v for k, v in Names.state_names.items()],
    }
    return render_template('vaccination.html', context=context)


@app.route('/tweets/')
def tweets_view():
    """
    App route to display recent Tweets related to COVID-19
    :return:
    """
    tweets_list = requests.get(
        "https://publish.twitter.com/oembed?url=https://twitter.com/i/lists/1361644157220114433").json()
    context = {
        'states': [v for k, v in Names.state_names.items()],
        'tweets_list': tweets_list,
        'tweets_tab': tweets_list
    }
    return render_template('tweets.html', context=context)


if __name__ == '__main__':
    app.run()
