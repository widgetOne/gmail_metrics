import httplib2
import os
from pprint import pprint
from apiclient import discovery
import datetime
import pandas as pd
import gmail_api_quickstart
from datadog import statsd


label_cypher = None


def get_label_id(label):
    global label_cypher
    if label_cypher is None:
        service = get_service()
        response = service.users().labels().list(userId='me').execute()
        label_cypher = {e['name']:e['id'] for e in response['labels']}
    return label_cypher[label]


def get_service():
    credentials = gmail_api_quickstart.get_credentials()
    http = credentials.authorize(httplib2.Http())
    service = discovery.build('gmail', 'v1', http=http)
    return service


def get_emails_ids_for_label_id(label_id):
    service = get_service()
    resp = service.users().messages().list(userId='me', labelIds=[label_id]).execute()
    return resp.get('messages', [])


def get_message_contents(message_id='15fbc427c317a243'):
    service = get_service()
    message = service.users().messages().get(userId='me', id=message_id).execute()
    return message


def get_emails_for_label(label):
    label_id = get_label_id(label)
    message_ids = get_emails_ids_for_label_id(label_id)
    message_ids = [msg['id'] for msg in message_ids]
    inbox_emails = list(map(get_message_contents, message_ids))
    return inbox_emails


def get_email_count_for_label(label):
    label_id = get_label_id(label)
    service = get_service()
    resp = service.users().messages().list(userId='me', labelIds=[label_id]).execute()
    return resp['resultSizeEstimate']


def get_email_metrics_for_label(label):
    email_list = get_emails_for_label(label)
    date_of_email = lambda email: datetime.datetime.fromtimestamp(float(email[u'internalDate']) / 1000.0)
    timestamps = map(date_of_email, email_list)
    deltas = list(map(lambda x: (datetime.datetime.now() - x).total_seconds() / 86400.0, timestamps))
    if not deltas:
        deltas = [0]
    sum_squares = sum(map(lambda x: x**2, deltas))
    average = sum(deltas) / len(deltas)
    metrics = {'count': len(email_list), 'oldest': max(deltas), 'average': average,
               'sum_squares': sum_squares, 'statdate': datetime.datetime.now()}
    df = pd.DataFrame([metrics], index=[label.lower()])
    return df


def get_local_df(file_path='scratch/local_copy.csv'):
    df = pd.read_csv(file_path)
    return df


def dataframe_to_datadog(df):
    metric_target = df.index[0]
    for column in df.items():
        name, value = column[0], column[1][0]
        if name != 'index' and type(value) != str:
            metric_label = '{}.gmail_{}'.format(metric_target, name).replace('/', '.')
            print(metric_label, value)
            statsd.gauge(metric_label, value)


def record_df_metrics(df):
    conn_url = os.environ['METRICS_SQL_AUTH']  # I want this to fail (and fail early) if it is not present
    df.to_sql('gmail_metrics', conn_url, if_exists='append')
    dataframe_to_datadog(df)


def collect_and_save_metrics():
    label_list = ['INBOX', 'a_todo/a_This_Week', 'a_todo/b_This_Month',
                  'a_todo/do_at_home', 'a_todo/c_This_Year']
    #label_list = ['INBOX']
    email_metrics_list = list(map(get_email_metrics_for_label, label_list))
    list(map(record_df_metrics, email_metrics_list))


if __name__ == '__main__':
    label_list = ['INBOX', 'a_todo/a_This_Week', 'a_todo/b_This_Month',
                  'a_todo/do_at_home', 'a_todo/c_This_Year']
    #pprint({label: get_email_count_for_label(label) for label in label_list})
    #pprint({label: get_email_count_for_label(label) for label in label_list})
    #list_labels()
    #pprint(get_email_ids_w_label('a_todo/c_This_Year'))
    collect_and_save_metrics()

