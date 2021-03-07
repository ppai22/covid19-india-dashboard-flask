import os

from flask import Flask, render_template, request, redirect
from flask_wtf.csrf import CSRFProtect

from config import Names
from forms import SelectState
from service import Service


app = Flask(__name__, template_folder='templates')
# 'set SECRET_KEY=<secret_key>' in terminal for debug mode
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY')
csrf = CSRFProtect(app)
csrf.init_app(app)


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


@app.route('/<state_code>/')
def details(state_code):
    """
    Generic endpoint to get to a state page via state_code
    :param state_code: str name of the state
    :return:
    """
    dataset, dates, seven_day_avg = Service().load_state_data(state_code)
    recovery_rate = Service().get_recovery_rate()[Names.get_code_from_name(state_code)]
    if state_code != 'all':
        name = Names.state_names[Names.get_code_from_name(state_code)]
    else:
        name = Names.state_names['tt']
    context = {
        'dataset': dataset,
        'dates': dates,
        'name': name,
        'states': [v for k, v in Names.state_names.items()],
        'seven_day_avg': seven_day_avg,
        'dates_seven_day_avg': dates[7:],
        'recovery_rate': recovery_rate
    }
    return render_template('display.html', context=context)


@app.route('/')
def home_page():
    """
    App route to display the home page with the map
    :return:
    """
    dataset = Service().get_total_active_all_states()
    all_data = Service().get_all_stats_last_day_all()
    table_data = [[], [], [], [], []]
    for state, state_data in all_data.items():
        if state != "India":
            table_data[0].append(state)
            table_data[1].append(state_data['total_confirmed'])
            table_data[2].append(state_data['total_active'])
            table_data[3].append(state_data['total_recovered'])
            table_data[4].append(state_data['total_deceased'])
    india_data, _, _ = Service().load_state_data('India')
    data = []
    for state in Names.state_names.keys():
        data.append([Names.state_names[state].lower(), dataset[state]])
    context = {
        'data': data,
        'states': [v for k, v in Names.state_names.items()],
        'dataset': india_data,
        'table_data': table_data
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
    dataset, dates, seven_day_avg = Service().tabulate()
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
        'top_ten_active_states': top_ten_active_states
    }
    return render_template('comparison.html', context=context)


@app.route('/recovery/')
def recovery_rate():
    """
    App route to display the recovery rates
    :return:
    """
    recovery_data = Service().get_recovery_rate()
    data = []
    for state in Names.state_names.keys():
        data.append([Names.state_names[state].lower(), recovery_data[state]])
    india_recovery = recovery_data['tt']
    context = {
        'data': data,
        'states': [v for k, v in Names.state_names.items()],
        'india_recovery': india_recovery
    }
    return render_template('recovery_rate.html', context=context)


@app.route('/vaccination/')
def vaccination_view():
    """
    App route to display India level vaccination data
    :return:
    """
    dates, cumulative_data, daily_data, fully_vaccinated, daily_fully_vaccinated = Service().vaccination_data()
    context = {
        'dates': dates.tolist(),
        'cumulative_data': cumulative_data.tolist(),
        'daily_data': [0] + daily_data.tolist(),
        'fully_vaccinated': fully_vaccinated.tolist(),
        'daily_fully_vaccinated': [0] + daily_fully_vaccinated.tolist(),
        'states': [v for k, v in Names.state_names.items()],
    }
    return render_template('vaccination.html', context=context)


if __name__ == '__main__':
    app.run()
