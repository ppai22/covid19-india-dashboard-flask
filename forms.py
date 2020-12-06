from flask_wtf import FlaskForm
from wtforms import SelectField

from config import Names


class SelectState(FlaskForm):
    """
    Form for selecting state to display data of
    """
    state = SelectField(
        'Select State: ',
        choices=[(key, value) for key, value in Names.state_names.items()],
        default='tt'
    )
