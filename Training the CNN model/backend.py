# -*- coding: utf-8 -*-
"""cnn_run_backend.ipynb

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/1s5v0p75U4peWJdAJN1djgMYUigHclF9-
"""

def run_model():
  import warnings
  warnings.filterwarnings("ignore")
  print("""Enter 
        \n1 to make forecast 
        \n2 to view historical data 
        \n3 to test model """)

  a = int(input())
  if a == 1:
    return make_forecast()
  if a == 2:
    return view_historical_data()
  if a == 3:
    return test_predictions()

  else:
    return print('Please only enter a number between 1 and 3')

def make_forecast(df_provided=None, start=None, end=None, a=None):
  
  import pandas as pd
  import numpy as np
  import datetime
  import pytz

  df = pd.read_csv(r'/content/drive/My Drive/megawatts.csv')

  fest = pd.read_csv(r'/content/drive/My Drive/festival.csv')

  df['datetime'] = pd.to_datetime(df['datetime'])
  fest['date'] = pd.to_datetime(fest['date'])

  if start == None:

    print()
    print('Forecast is available from "{}" to "{}"'.format(df['datetime'].iloc[-1] + datetime.timedelta(minutes=15), df['datetime'].iloc[-1] + datetime.timedelta(minutes=15*93)))

    print()
    print('Enter datetimes to predict in this range only')

    print()
    print('Forecast Start datetime (YYYY-MM-DD h:m): ')
    start = pd.to_datetime(input())
  
  if end== None:
    print()
    print('Forecast end datetime (YYYY-MM-DD h:m): ')
    end =  pd.to_datetime(input())

  if start > end :
    print()
    return print('ERROR : End datetime should be later than start datetime')
    
  if (df['datetime'] == start).sum()!= 0 and df_provided==None:
    print()
    return print('ERROR: Some or all of Prediction horizon dates entered already exist in the database. Try again')

  if df_provided == None:
    no_of_predictions = int(((end - start).total_seconds()/900) + 1)

    df_more = pd.DataFrame(np.zeros((no_of_predictions))).rename(columns={0:'load'})
    df_more['datetime'] = pd.date_range(start, end, freq = '0.25H')

    df_copy = pd.concat([df, df_more], sort=False, axis=0)
    df_new = mach3(df_copy, fest, [-1, -2, -3, 0, 1, 2, 3], 12, 12)
    df_new = df_new.drop(columns = ['load'], axis=1)

  else:
    df_new = mach3(df, fest, [-1, -2, -3, 0, 1, 2, 3], 12, 12)
    df_copy = df_new.reset_index(drop=True)
    df_copy['datetime'] = df_new.index
    df_new = df_new.drop(columns = ['load'], axis=1)

  from sklearn.preprocessing import MinMaxScaler
  scaler = MinMaxScaler()
  scaler.fit(df_new)
  X = scaler.transform(df_new.loc[start:end])
  X = X.reshape(X.shape[0], 6, 7, 4)

  from tensorflow.keras.models import load_model
  model = load_model('/content/drive/My Drive/sE19_R83.hdf5')
  Y = model.predict(X)

  target_scaler = MinMaxScaler()
  target_scaler.fit(np.array(df['load']).reshape(-1, 1))
  Y_scaled_back = target_scaler.inverse_transform(Y)

  df_copy.set_index('datetime', inplace=True, drop='True')
  df_copy.loc[start:end, 'load'] = Y_scaled_back.reshape(-1,)
  
  result = df_copy.loc[start:end, 'load']
  print(result)
  local_timezone = pytz.timezone('Asia/Kolkata')
  utc_time = datetime.datetime.now()
  local_time = utc_time.astimezone(local_timezone).strftime('%d%b%l:%M%p')

  s = datetime.datetime.strftime(start, '%d%b%l:%M%p')
  e = datetime.datetime.strftime(end, '%d%b%l:%M%p')
  result.to_csv("/content/drive/My Drive/Download Results/Foreacast__{}__{}__at__{}.csv".format(s, e, local_time))

  if a == 3:
    print()
    return plot(result, start, end, 3)

  else:
    print()
    return plot(result, start, end, 1)

def create_regressor_attributes(df, attribute, list_of_t_instants) :

  import pandas as pd
              
  list_of_t_instants.sort()
  start = -1 * list_of_t_instants[0] 
  if list_of_t_instants[-1] > 0 :
      end = len(df) - list_of_t_instants[-1] 
  else:
      end = len(df)
  if df.index.name == None:
      dummy = 0
      df.loc[:, 'new_index'] = df.index 
  else:
      dummy = 1
      new_index_name = df.index.name
      df.loc[:, new_index_name] = df.index
  df.reset_index(drop=True)

  df_copy = df.iloc[start:end]
  df_copy.reset_index(inplace=True, drop=True)

  for attribute in attribute :
          foobar = pd.DataFrame()

          for t in list_of_t_instants :
              if t>0:
                  sign = '+'
              else:
                  sign = ''
              new_col = pd.DataFrame(df.loc[:, attribute].iloc[(start + t) : (end + t)])
              new_col.reset_index(drop=True, inplace=True)
              new_col.rename(columns={attribute : '{}_(t{}{})'.format(attribute, sign, t)}, inplace=True)
              foobar = pd.concat([foobar, new_col], sort=False, axis=1)

          df_copy = pd.concat([df_copy, foobar], sort=False, axis=1)
          
  if dummy == 0:   
      df_copy.set_index(['new_index'], drop=True, inplace=True)
      df.drop(columns=['new_index'], inplace=True)
  elif dummy == 1:
      df_copy.set_index([new_index_name], drop=True, inplace=True)
      df.drop(columns=[new_index_name], inplace=True)
  return df_copy

def create_daily_reg(df, window, day_slots):

    import pandas as pd

    day_regressors = []
    for j in window:
        for i in day_slots:
            day_regressors .append(i+j)

    day_regressors = [-i for i in sorted(day_regressors)]
    day_df = create_regressor_attributes(df, ['load'], day_regressors)
    return day_df

def create_week_reg(df, fest, window, week_slots):

    import pandas as pd
    import datetime

    df['datetime'] = pd.to_datetime(df['datetime'])
    fest['date'] = pd.to_datetime(fest['date'])
    df = df.set_index(df['datetime'].dt.date)
    fest = fest.set_index('date')
    df = df.join(fest)
    df['occasion'] = (~df['occasion'].isnull()).astype(int)
    df['weekday'] = df['datetime'].dt.weekday
    holiday = set(df.loc[df['occasion'] == 1].index)
    Sunday = set(df.loc[df['weekday'] == 6].index)
    next_to_holiday = [day + datetime.timedelta(days=1) for day in holiday]
    next_to_holiday = [day for day in next_to_holiday if day not in holiday]
    next_to_holiday = set([day for day in next_to_holiday if day not in Sunday])
    df.loc[holiday, 'weekday'] = 6
    df.loc[next_to_holiday, 'weekday'] = 0
    df = df.set_index('datetime')
    df = df.drop(columns =['occasion'])

    week_regressors = []
    for j in window:
        for i in week_slots:
          week_regressors .append(i+j)

    week_regressors = [-i for i in sorted(week_regressors)]
    weekwise = []
    for day in set(df['weekday']):
        weekwise.append(df.loc[df['weekday'] == day])

    week_col_names = pd.DataFrame(['t-w{}'.format(len(week_regressors)-i) for i in range(len(week_regressors))])
    week_col_names  = week_col_names.set_index(pd.Series([f'load_(t{j})' for j in sorted(week_regressors)]))
    week_col_names = week_col_names.to_dict()[0]
    for i in range(len(weekwise)):
        weekwise[i] = create_regressor_attributes(weekwise[i], ['load'], week_regressors).rename(columns=week_col_names)

    week_df = pd.concat(weekwise)
    week_df = week_df.sort_index()

    return week_df

def mach3(df, fest, window, d_number, w_number):

    import pandas as pd
    week_slots = [96*i for i in range(1, w_number+1)]
    week_df = create_week_reg(df, fest, window, week_slots)
    day_slots = [96*i for i in range(1, d_number+1+d_number//7) if i%7!=0]
    final_df = create_daily_reg(week_df, window, day_slots)
    final_df = final_df[final_df.columns[::-1]]
    final_df = final_df.drop(columns = ['weekday'])
    return final_df


def plot(result, start, end, a):

  from matplotlib import pyplot as plt
  import pandas as pd
  import numpy as np
  
  if len(result) > 15:
    print()
    plt.figure(figsize=(15, 6))
    plt.plot(result, linewidth=2, color='r', linestyle='solid', label='Predicted')
    if a == 1:
      plt.title("Forecast from '{}' to '{}'".format(start, end), weight='bold', fontsize=16)
    if a == 2:
      plt.title("Historical Load from '{}' to '{}'".format(start, end), weight='bold', fontsize=16)
    if a == 3:
      plt.title("Prediction vs Actual from '{}' to '{}'".format(start, end), weight='bold', fontsize=16)
      df = pd.read_csv(r'/content/drive/My Drive/Database/megawatts.csv')
      df['datetime'] = pd.to_datetime(df['datetime'])
      df = df.set_index('datetime', drop=True)
      plt.plot(df.loc[start:end], linewidth=2, color='b', linestyle='dotted', label='Actual')
      plt.legend(loc='best')
    plt.grid(color='y', linewidth=0.5)
    plt.xticks(weight='bold', fontsize=12)
    plt.yticks(weight='bold', fontsize=12)
    plt.xlabel('Datetime', weight='bold', fontsize=14)
    plt.ylabel('MegaWatts', weight='bold', fontsize=14)
    plt.show()
  else:
    print()
    print('Predicted by Model:')
    print(result)
    if a==3:
      df = pd.read_csv(r'/content/drive/My Drive/Database/megawatts.csv')
      df['datetime'] = pd.to_datetime(df['datetime'])
      df = df.set_index('datetime', drop=True)
      print()
      print('Actual Historical data:')
      print(df.loc[start:end])

def view_historical_data():
  import pandas as pd
  import datetime
  df = pd.read_csv(r'/content/drive/My Drive/Database/megawatts.csv')
  df['datetime'] = pd.to_datetime(df['datetime'])

  print()
  print('Data exists from "{}" to "{}"'.format(df['datetime'].iloc[0], df['datetime'].iloc[-1]))

  print()
  print('Enter datetimes to view historical data in this range only')

  print()
  print('Enter Start datetime (YYYY-MM-DD h:m): ')
  start = pd.to_datetime(input())

  if (df['datetime'] == start).sum() == 0:
    print()
    return print('ERROR : Data does not exist in databse')

  print()
  print('Enter end datetime (YYYY-MM-DD h:m): ')
  end =  pd.to_datetime(input())

  if (df['datetime'] == end).sum() == 0:
    print()
    return print('ERROR : Data does not exist in databse')

  if start > end :
    print()
    return print('ERROR : End datetime should be later than start datetime')

  df = df.set_index('datetime', drop=True)

  s = datetime.datetime.strftime(start, '%d%b%l:%M%p')
  e = datetime.datetime.strftime(end, '%d%b%l:%M%p')

  df.loc[start:end].to_csv("/content/drive/My Drive/Historical__load__{}__to__{}.csv".format(s, e))

  return plot(df.loc[start:end], start, end, 2)

def test_predictions():
  import numpy as np
  import pandas as pd
  import datetime

  df = pd.read_csv(r'/content/drive/My Drive/Database/megawatts.csv')
  df['datetime'] = pd.to_datetime(df['datetime'])

  print()
  print('Select Start datetime from range: "{}" to "{}"'.format(df['datetime'].iloc[0] + datetime.timedelta(minutes=15*(12*7*96+15*96+8)), df['datetime'].iloc[-1] ))

  print()
  print('Enter Start datetime (YYYY-MM-DD h:m): ')
  start = pd.to_datetime(input())

  if (df['datetime'] == start).sum() == 0:
    print()
    return print('ERROR : Data does not exist in databse')

  if start < (df['datetime'].iloc[0] + datetime.timedelta(minutes=15*93)):
    print()
    return print('ERROR : Test datetime out of range')

  print('Select End datetime within the range shown earlier')

  print()
  print('Enter end datetime (YYYY-MM-DD h:m): ')
  end =  pd.to_datetime(input())

  if (df['datetime'] == end).sum() == 0:
    print()
    return print('ERROR : Data does not exist in databse')

  if end > (df['datetime'].iloc[-1]):
    print()
    return print('ERROR : Test datetime out of range')

  return make_forecast(df_provided=True, start=start, end=end, a=3)