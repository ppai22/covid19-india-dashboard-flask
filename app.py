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
    dataset, dates = Service().load_state_data(state_code)
    if state_code != 'all':
        name = Names.state_names[Names.get_code_from_name(state_code)]
    else:
        name = Names.state_names['tt']
    context = {
        'dataset': dataset,
        'dates': dates,
        'name': name
    }
    return render_template('display.html', context=context)


@app.route('/')
def home_page():
    """
    App route to display the home page with the map
    :return:
    """
    dataset = Service().get_total_active_all_states()
    data = []
    for state in Names.state_names.keys():
        data.append([Names.state_names[state].lower(), dataset[state]])
    return render_template('home.html', data=data)


if __name__ == '__main__':
    app.run()
