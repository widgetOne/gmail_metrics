import httplib2
import os
from pprint import pprint
from apiclient import discovery
import datetime
import pandas as pd
import gmail_api_quickstart
from datadog import statsd


def get_service():
    credentials = gmail_api_quickstart.get_credentials()
    http = credentials.authorize(httplib2.Http())
    service = discovery.build('gmail', 'v1', http=http)
    return service


def get_inbox_email_id_list_response():
    service = get_service()
    messages = service.users().messages().list(userId='me', labelIds=[u'INBOX']).execute()
    return messages


def get_message_contents(message_id='15fbc427c317a243'):
    service = get_service()
    message = service.users().messages().get(userId='me', id=message_id).execute()
    return message


def get_current_inbox_emails():
    message_id_response = get_inbox_email_id_list_response()
    message_ids = [msg['id'] for msg in message_id_response['messages']]
    inbox_emails = list(map(get_message_contents, message_ids))
    return inbox_emails


def get_inbox_email_metrics():
    inbox_emails = get_current_inbox_emails()
    date_of_email = lambda email: datetime.datetime.fromtimestamp(float(email[u'internalDate']) / 1000.0)
    timestamps = map(date_of_email, inbox_emails)
    deltas = list(map(lambda x: (datetime.datetime.now() - x).total_seconds() / 86400.0, timestamps))
    if not deltas:
        deltas = [0]
    sum_squares = sum(map(lambda x: x**2, deltas))
    average = sum(deltas) / len(deltas)
    metrics = {'count': len(inbox_emails), 'oldest': max(deltas), 'average': average,
               'sum_squares': sum_squares, 'statdate': datetime.datetime.now()}
    df = pd.DataFrame([metrics])
    df.index.name = 'index'
    return df


def get_local_df(file_path='scratch/local_copy.csv'):
    df = pd.read_csv(file_path)
    return df


def dataframe_to_datadog(df):
    for column in df.items():
        name, value = column[0], column[1][0]
        if name != 'index' and type(value) != str:
            print(name, value)
            print('gmail_{}'.format(name))
            statsd.gauge('gmail_{}'.format(name), value)


def collect_and_save():
    conn_url = os.environ['METRICS_SQL_AUTH']  # I want this to fail (and fail early) if it is not present
    df = get_inbox_email_metrics()
    df.to_sql('metrics', conn_url, if_exists='append')
    dataframe_to_datadog(df)


if __name__ == '__main__':
    collect_and_save()

