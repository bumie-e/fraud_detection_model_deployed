from flask import Flask, render_template, request
from wtforms import Form, TextAreaField, validators, BooleanField, SubmitField, IntegerField, RadioField
import pickle
import sqlite3
import os
import numpy as np
import pandas as pd
from preprocessing import time
from datetime import datetime

app = Flask(__name__)

######## Preparing the Classifier
cur_dir = os.path.dirname(__file__)
clf = pickle.load(open(os.path.join(cur_dir,
                                    'pkl_objects/classifier.pkl'), 'rb'))

db = os.path.join(cur_dir, 'account.sqlite')

def classify(data):
    label = {0:'not_fradulent', 1:'fradulent'}
    X = time(data)
    y = clf.predict(X)[0]
    proba = np.max(clf.predict_proba(X))
    print(label[y], proba)
    return y, proba

def train(data, y):
    X = time(data)
    clf.fit(X, [y])
    
def sqlite_entry(path, a, b, d, e, f, g, h, i, y):
    conn = sqlite3.connect(path)
    c = conn.cursor()
    c.execute('INSERT INTO account_db'\
          ' (current_bank_amount, last_bank_amount, transaction_time, most_recent_bank_amount, account_type, credit_card_type, account_source_verification, transaction_source_method, account_destination_verification) VALUES'\
          ' (?, ?, DATETIME("now"), ?, ?, ?, ?, ?, ?)', (a, b, d, e, f, g, h, i))
    conn.commit()
    conn.close()

class ReviewForm(Form):
    current_bank_amount = IntegerField('current_bank_amount',[validators.DataRequired()])
    last_bank_amount = IntegerField('last_bank_amount',[validators.DataRequired()])
    most_recent_bank_amount = IntegerField('most_recent_bank_amount',[validators.DataRequired()])
   # account_type = TextAreaField('Savings or Current',[validators.DataRequired()])
   # card_type = TextAreaField('Verve or Master Card',[validators.DataRequired()])
    account_type = RadioField('Savings or Current', choices=[('saving','Savings'),('current','Current')])
    card_type = RadioField('Verve or Master Card', choices=[('verve','Verve Card'),('master','Master Card')])
    verification1 = RadioField('Account Source verified?', choices=[('True','Yes'),('False','No')])
    verification2 = RadioField('Transaction_source_verified?', choices=[('True','Yes'),('False','No')])
    verification3 = RadioField('account_destination_verified?', choices=[('True','Yes'),('False','No')])
@app.route('/')
def index():
    form = ReviewForm(request.form)
    return render_template('reviewform.html', form=form)

@app.route('/results', methods=['POST'])
def results():
    form = ReviewForm(request.form)
    if request.method == 'POST'and form.validate():
        a = request.form['current_bank_amount']
        b = request.form['last_bank_amount']
        d = request.form['most_recent_bank_amount']
        e = request.form['account_type']
        f = request.form['card_type']
        g = request.form['verification1']
        h = request.form['verification2']
        i = request.form['verification3']
        data = pd.DataFrame({'current bank amount': int(a), 'last bank amount': int(b)
                             ,'transaction time': datetime.now(),
                             'most recent bank amount': int(d), 
                             'account type': e,'credit card type': f,
                             'account source verification': g,
                             'transaction source method': h, 
                             'account destination verification': i }, index=[0])
        data1 = data.copy()
        y, proba = classify(data1)
        inv_label = {0:'not_fradulent', 1:'fradulent'}
        return render_template('results.html',
                               content1=a,
                               content2=b,
                               content3=d,
                               content4=e,
                               content5=f,
                               content6=g,
                               content7=h,
                               content8=i,
                               prediction=y,
                               frad = inv_label[y],
                               probability=round(proba*100, 2))
    return render_template('reviewform.html', form=form)

@app.route('/thanks', methods=['POST'])
def feedback():
    feedback = request.form['feedback_button']
    a = request.form['data1']
    b = request.form['data2']
    d = request.form['data3']
    e = request.form['data4']
    f = request.form['data5']
    g = request.form['data6']
    h = request.form['data7']
    i = request.form['data8']
    
    data = pd.DataFrame({'current bank amount': int(a), 'last bank amount': int(b)
                         ,'transaction time': datetime.now(),
                         'most recent bank amount': int(d), 
                         'account type': e,'credit card type': f,
                         'account source verification': g,
                         'transaction source method': h, 
                         'account destination verification': i }, index=[0])
    
    prediction = request.form['prediction']
    
    inv_label = {0:'not_fradulent', 1:'fradulent'}
    
    prediction = int(prediction)
    y = inv_label[prediction]
    if feedback == 'Incorrect':
        y = int(not(y))
    train(data, y)
    sqlite_entry(db, a, b, d, e, f, g, h, i, y)
    return render_template('thanks.html')

if __name__ == '__main__':
    app.run(debug=True)