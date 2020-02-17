from flask_wtf import FlaskForm
from wtforms import IntegerField, SubmitField
from wtforms.validators import DataRequired

class MoneylineForm(FlaskForm):
    first_odd = IntegerField(label='Team One Odds', validators=[DataRequired()])
    second_odd = IntegerField(label='Team Two Odds', validators=[DataRequired()])
    bet_amount = IntegerField(label='Bet Amount', validators=[DataRequired()])
    submit = SubmitField('Calculate')
