import numpy as np
from flask import render_template, flash, redirect, url_for, request

from app import app
from app.forms import MoneylineForm
from src.redis_grabber import RedisGrabber


@app.route('/')
@app.route('/index')
def index():
    return render_template('index.html', arbs=RedisGrabber().formatted_output())


#BAD SPOT BUT HERE WE ARE
def calculate_prob(x):
    if x > 0:
        dec = x / 100 + 1
    elif x < 0:
        dec = 100 / np.abs(x) + 1
    else:
        pass

    return 1 / dec #implied prob

@app.route('/calculator', methods=['GET', 'POST'])
def calculator():
    form = MoneylineForm()

    if form.is_submitted():
        prob1 = calculate_prob(form.first_odd.data)
        prob2 = calculate_prob(form.second_odd.data)
        edge = (1 - (prob1 + prob2)) * form.bet_amount.data

        if edge < 0:
            f_edge = 'No Edge'
            f_side1_bet = 'Nothing'
            f_side2_bet = 'Nothing'
        else:
            f_edge = f'${edge:.2f}'
            side1_bet = (prob1 / (prob1 + prob2)) * form.bet_amount.data
            side2_bet = (prob2 / (prob1 + prob2)) * form.bet_amount.data
            f_side1_bet = f'${side1_bet: .2f}'
            f_side2_bet = f'${side2_bet: .2f}'

        return render_template('calculator.html', form=form, details=[f_edge, f_side1_bet, f_side2_bet])

    return render_template('calculator.html', form=form)