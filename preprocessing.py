import re
import os
import pickle
import pandas as pd
import numpy as np
from sklearn.preprocessing import Normalizer
from datetime import datetime

def dummies(data):
    data['account type'][data['account type']=='current'] = int(0)
    data['account type'][data['account type']=='saving'] = int(1)
    data['credit card type'][data['credit card type']=='master'] = int(0)
    data['credit card type'][data['credit card type']=='verve'] = int(1)
    return data
    
def debit_or_credit(data):
    data['credit_or_debit'] =  int(data['current bank amount']) - int(data['last bank amount'])
    data['credit_or_debit'] = np.where(data['credit_or_debit'] < 0, 0, 1)
    return data

def set_index(data):
    data.set_index(['transaction time'], inplace=True)
    return data

#def drop(data):
#    data.drop(['occupation', 'marital_status', 'time taken (seconds)', 'age', 'id', 'fradulent'],axis=1, inplace=True)
#    return data
    
def time(data):
  #  data = dummies(data)
 #   data = drop(data)
    data = set_index(data)
    data['transaction_hour'] = datetime.now().hour
    data = debit_or_credit(data)
    
    data['transaction_hour'] = data['transaction_hour'].astype('int64')
    
    data['account type'][data['account type']=='current'] = int(0)
    data['account type'][data['account type']=='saving'] = int(1)
    
    data['credit card type'][data['credit card type']=='master'] = int(0)
    data['credit card type'][data['credit card type']=='verve'] = int(1)
    
    data['account type'] = data['account type'].astype('int64')
    data['credit card type'] = data['credit card type'].astype('int64')
    data['account source verification'] = data['account source verification'].astype(bool)
    data['transaction source method'] = data['transaction source method'].astype(bool)
    data['account destination verification'] = data['account destination verification'].astype(bool)
    
    data[['last bank amount', 'current bank amount','most recent bank amount']] = Normalizer().fit_transform(data[['last bank amount', 'current bank amount','most recent bank amount']])
    return data
    

#housing_num_tr = num_pipeline.fit_transform(housing_num)
    