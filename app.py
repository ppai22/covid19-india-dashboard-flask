from flask import Flask, render_template

from config import Names
from service import Service


app = Flask(__name__, template_folder='templates')


@app.route('/<state_code>/')
def state_data(state_code):
    """
    App route to display the state data
    :param state_code: str name of the state
    :return:
    """
    dataset, dates, seven_day_avg = Service().load_state_data(state_code)
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
        'dates_seven_day_avg': dates[7:]
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


if __name__ == '__main__':
    app.run(debug=True)
