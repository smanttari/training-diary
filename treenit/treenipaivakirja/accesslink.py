import re
import requests
from datetime import datetime
from urllib.parse import urlencode

from django.conf import settings
from django.contrib import messages

from treenipaivakirja.models import PolarSport, PolarSleep, PolarRecharge


def build_auth_url():
    params = {
        'response_type': 'code', 
        'state': 'recovery',
        'client_id': settings.ACCESSLINK_CLIENT_KEY
        }
    auth_url = f'{settings.ACCESSLINK_AUTH_URL}?{urlencode(params)}'
    return auth_url
    

def get_access_token(auth_code):
    headers = {
        'Content-Type' : 'application/x-www-form-urlencoded',
        'Accept' : 'application/json;charset=UTF-8'
        }
    data = {
        'grant_type' : 'authorization_code',
        'code' : auth_code
        }
    response = requests.post(settings.ACCESSLINK_ACCESS_TOKEN_URL, 
        headers = headers, 
        data = data,
        auth = requests.auth.HTTPBasicAuth(settings.ACCESSLINK_CLIENT_KEY, settings.ACCESSLINK_CLIENT_SECRET)
        )
    return response


def create_headers(token):
    headers = {
        'Content-Type': 'application/json',
        'Accept': 'application/json, application/gpx+xml',
        'Authorization': f'Bearer {token}'
        }
    return headers


def register_user(token, user_id):
    url = '{}/users'.format(settings.ACCESSLINK_URL)
    headers = create_headers(token)
    data = {'member-id': str(user_id)}
    response = requests.post(url, headers=headers, json=data)
    return response


def delete_user(token, user_id):
    url = '{}/users/{}'.format(settings.ACCESSLINK_URL, user_id)
    headers = create_headers(token)
    response = requests.delete(url, headers=headers)
    return response


def get_user_information(token, user_id):
    url = '{}/users/{}'.format(settings.ACCESSLINK_URL, user_id)
    headers = create_headers(token)
    response = requests.get(url, headers=headers)
    return response


def create_exercise_transaction(token, user_id):
    url = '{}/users/{}/exercise-transactions'.format(settings.ACCESSLINK_URL, user_id)
    headers = create_headers(token)
    response = requests.post(url, headers=headers)
    return response


def commit_exercise_transaction(token, user_id, transaction_id):
    url = '{}/users/{}/exercise-transactions/{}'.format(settings.ACCESSLINK_URL, user_id, transaction_id)
    headers = create_headers(token)
    response = requests.put(url, headers=headers)
    return response
    

def list_exercises(token, user_id, transaction_id):
    url = '{}/users/{}/exercise-transactions/{}'.format(settings.ACCESSLINK_URL, user_id, transaction_id)
    headers = create_headers(token)
    response = requests.get(url, headers=headers)
    return response


def get_exercise_summary(token, user_id, url):
    headers = create_headers(token)
    response = requests.get(url, headers=headers)
    return response


def get_exercise_gpx(polar_user, exrecise_id):
    user_id = polar_user.polar_user_id
    token = polar_user.access_token
    transaction_id = polar_user.latest_exercise_transaction_id
    url = '{}/users/{}/exercise-transactions/{}/exercises/{}/gpx'.format(
        settings.ACCESSLINK_URL, user_id, transaction_id, exrecise_id)
    headers = create_headers(token)
    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        return response.text
    else:
        return None


def list_sleep(token):
    url = '{}/users/sleep'.format(settings.ACCESSLINK_URL)
    headers = create_headers(token)
    response = requests.get(url, headers=headers)
    return response


def list_nightly_recharge(token):
    url = '{}/users/nightly-recharge'.format(settings.ACCESSLINK_URL)
    headers = create_headers(token)
    response = requests.get(url, headers=headers)
    return response


def create_transaction(request, polar_user):
    user_id = polar_user.polar_user_id
    token = polar_user.access_token
    transaction = create_exercise_transaction(token, user_id)
    if transaction.status_code == 204:
        messages.add_message(request, messages.ERROR, 'Polar Accesslink Error: 204 No Content.')
        return
    elif transaction.status_code != 201:
        messages.add_message(request, messages.ERROR, 'Polar Accesslink Error: {} {}'.format(transaction.status_code,transaction.reason))
        return
    else:
        transaction_id = transaction.json()['transaction-id']
        polar_user.latest_exercise_transaction_id = transaction_id
        polar_user.save()
        return transaction_id


def commit_transaction(request, polar_user):
    user_id = polar_user.polar_user_id
    token = polar_user.access_token
    transaction_id = polar_user.latest_exercise_transaction_id
    commit = commit_exercise_transaction(token, user_id, transaction_id)
    if commit.status_code == 200:
        polar_user.latest_exercise_transaction_id = None
        polar_user.save()
    else:
        messages.add_message(request, messages.ERROR, 'Polar Accesslink Error: {} {}'.format(commit.status_code,commit.reason))


def get_exercises(request, polar_user):
    user_id = polar_user.polar_user_id
    token = polar_user.access_token
    transaction_id = polar_user.latest_exercise_transaction_id

    if transaction_id is None:
        transaction_id = create_transaction(request, polar_user)
        if transaction_id is None:
            return

    exercises = list_exercises(token, user_id, transaction_id)
    if exercises.status_code == 404:  # transaction was not found, create new
        transaction_id = create_transaction(request, polar_user)
        if transaction_id is None:
            return
        else:
            exercises = list_exercises(token, user_id, transaction_id)
    
    if exercises.status_code != 200:
        messages.add_message(request, messages.ERROR, 'Polar Accesslink Error: {} {}'.format(exercises.status_code,exercises.reason))
        return
    
    exercises_list = []
    for exercise_url in exercises.json()['exercises']:
        exercise = get_exercise_summary(token, user_id, exercise_url)
        if exercise.status_code == 200:
            exercises_list.append(exercise.json())
    return exercises_list


def parse_duration(duration):
    h = re.findall('(\d+)H',duration)
    m = re.findall('(\d+)M',duration)
    if len(h) > 0:
        h = int(h[0])
    else:
        h = 0
    if len(m) > 0:
        m = int(m[0])
    else:
        m = 0
    return (h,m)


def parse_exercises(polar_user, exercises):
    polar_sports = PolarSport.objects.filter(polar_user=polar_user.polar_user_id).values_list('polar_sport','laji_id')
    polar_sports = {sport[0]:sport[1] for sport in polar_sports}
    trainings = {
        'form-TOTAL_FORMS': len(exercises),
        'form-INITIAL_FORMS': len(exercises)
        }
    for i,e in enumerate(exercises):
        duration = parse_duration(e.get('duration',''))
        trainings[f'form-{i}-pvm'] = datetime.strptime(e.get('start-time')[:10], '%Y-%m-%d')
        trainings[f'form-{i}-vuorokaudenaika'] = 1 if int(e.get('start-time')[11:13]) < 12 else 2
        trainings[f'form-{i}-laji'] = polar_sports.get(e.get('detailed-sport-info'))
        trainings[f'form-{i}-polar_sport'] = e.get('detailed-sport-info')
        trainings[f'form-{i}-kesto_h'] = duration[0]
        trainings[f'form-{i}-kesto_min'] = duration[1]
        trainings[f'form-{i}-keskisyke'] = e.get('heart-rate').get('average')
        trainings[f'form-{i}-matka'] = round(e.get('distance',0)/1000,1) if e.get('distance',0) != 0 else None
        trainings[f'form-{i}-vauhti_km_h'] = round(e.get('distance',0)/(duration[0]+duration[1]/60)/1000,1) if e.get('distance',0) != 0 else None
        trainings[f'form-{i}-kalorit'] = e.get('calories')
        trainings[f'form-{i}-has_route'] = e.get('has-route')
        trainings[f'form-{i}-polar_exercise_id'] = e.get('id')
    return trainings


def parse_sleep_data(polar_user, sleep):
    sleep_objects = []
    for entry in sleep.json()['nights']:
        sleep_objects.append(PolarSleep(
            polar_user = polar_user,
            date = entry['date'],
            start_time = datetime.strptime(entry['sleep_start_time'][:19], '%Y-%m-%dT%H:%M:%S'),
            end_time = datetime.strptime(entry['sleep_end_time'][:19], '%Y-%m-%dT%H:%M:%S'),
            continuity = entry['continuity'],
            light_sleep = int(entry['light_sleep'])/3600,
            deep_sleep = int(entry['deep_sleep'])/3600,
            rem_sleep = int(entry['rem_sleep'])/3600,
            sleep_score = entry['sleep_score'],
            total_interruption_duration = int(entry['total_interruption_duration'])/3600
        ))
    for s in sleep_objects:
        s.duration = (s.end_time - s.start_time).seconds/3600
    return sleep_objects


def parse_recharge_data(polar_user, recharge):
    recharge_objects = []
    for entry in recharge.json()['recharges']:
        recharge_objects.append(PolarRecharge(
            polar_user = polar_user,
            date = entry['date'],
            heart_rate_avg = entry['heart_rate_avg'],
            heart_rate_variability_avg = entry['heart_rate_variability_avg'],
            nightly_recharge_status = entry['nightly_recharge_status']
        ))
    return recharge_objects