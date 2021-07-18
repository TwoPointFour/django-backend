import math
from functools import reduce
from operator import itemgetter
from statistics import pstdev
from time import time
from run.models import Workout
from run.algorithms.functions import getSpeedDifficulty

# All constants below TBC
rho = 7.0
# tePace, ltPace, vPace, stPace
phi = [1, 1, 1, 1]
paceConstants = [1.243, 1.19, 1.057, 0.89]
kValue = 0.25
yValue = 1.25


def get_pace(timeInput):
    return timeInput / 2400


def convert_sec_to_hour(time_in_sec):
    return time_in_sec / (60 * 60)


def get_target_paces(targetTime):
    targetPace = get_pace(targetTime)
    displayPace = math.floor(targetPace * 100 * 1000)
    return {'targetPace': targetPace, 'displayPace': displayPace}


def convert_to_velocity(currentTime):
    return 2.4 / convert_sec_to_hour(currentTime)


def get_prescribed_rest(restMultiple, targetPace):
    return round((restMultiple * targetPace * 100) / 5) * 5


def restRatio(restMultiple, targetPace):
    return get_prescribed_rest(restMultiple, targetPace) / (restMultiple * targetPace * 100)


def restMultiplier(workout, targetPace):
    return 1 / math.exp(0.0024 * restRatio(workout['workoutInfo'][0]["restMultiplier"], targetPace))


def convert_to_seconds(input_array):
    split_array = input_array.split(":")
    return int(split_array[0]) * 60 + int(split_array[1])


def sanitise_week_date_stamp(timestamp):
    return timestamp - (timestamp % 86400000)


def get_paces(targetPace, cNewbieGains):
    return [targetPace * paceConstants[i] * cNewbieGains * x for i, x in enumerate(phi)]


def get_velocities(paces):
    return [(1 / pace) * 3.6 for pace in paces]


def get_goal_set_time(previousWorkout):  # in ms
    return (float(previousWorkout['workoutInfo'][0]["pace"]) * float(
        previousWorkout['workoutInfo'][0]["distance"])) / 100


def get_average_time(previousWorkout):  # in seconds
    timings = previousWorkout['workoutInfo'][0]["timings"]
    return math.fsum(timings) / len(timings)


def get_standard_deviation(previousWorkout):
    return pstdev(previousWorkout['workoutInfo'][0]["timings"])


# todo get rid of the retarded float all over the place
def get_missed(previousWorkout):
    return previousWorkout['workoutInfo'][0]["sets"] - len(previousWorkout['workoutInfo'][0]["timings"])


def penalise_missed(missed, previousWorkout):
    return (math.exp(missed / float(previousWorkout['workoutInfo'][0]["sets"])) - 1) * yValue


def get_rounded_distance(timeInput, tempoPace):
    return math.ceil((timeInput * 60 / tempoPace) / 0.5) * 0.5


def get_user_info(questionnaireData, previousFitness):
    duration, workoutFrequency = itemgetter('duration', 'workoutFrequency')(questionnaireData)
    # todo fix currentFitness
    return {
        'currentTime': convert_to_seconds(questionnaireData['latest']),
        'targetTime': convert_to_seconds(questionnaireData['target']),
        'duration': duration,
        'workoutFrequency': workoutFrequency,
        'currentFitness': previousFitness
    }


def generate_constants(questionnaireData):
    # todo verify personalbests below
    beta = 1 if questionnaireData['regular'] else 0.975
    alpha = max(0, min(1, (1 / 3) * beta * (
            (questionnaireData['frequency'] * questionnaireData['distance']) / 30 + questionnaireData['experience'] / 36 + questionnaireData['frequency'] / 3)))
    # old code
    #     Math.min(
    #     1,
    #     (1 / 3) *
    #       beta *
    #       ((answers.fFrequency * answers.dDistance) / 30 +
    #         answers.lMonths / 36 +
    #         answers.fFrequency / 3)
    #   )
    # )
    cNewbieGains = (1 / rho) * math.exp(1 - alpha) + (rho - 1) / rho
    return {'alpha': alpha, 'beta': beta, 'cNewbieGains': cNewbieGains}


def get_workout_score(previousWorkout):
    if not len(previousWorkout['workoutInfo'][0]["timings"]):
        return {'goalTimePerSet': 0, 'averageTime': 0, 'standardDeviation': 0, 'missed': 0, 'workoutScore': 0}
    goalTimePerSet = get_goal_set_time(previousWorkout)  # in ms
    averageTime = get_average_time(previousWorkout)  # in ms
    standardDeviation = get_standard_deviation(previousWorkout)
    missed = get_missed(previousWorkout)  # integer value
    workoutScore = 100 * (goalTimePerSet / averageTime + (
            math.exp(standardDeviation / goalTimePerSet) - 1) * kValue - penalise_missed(missed, previousWorkout))
    return {'workoutScore': workoutScore}  # {goalTimePerSet, averageTime, standardDeviation, missed, workoutScore}


def get_overall_fitness(speedDifficulty, duration, currentFitness, previousWorkout):
    deltaDifficulty = speedDifficulty - 100
    deltaDifficultyPerWeek = deltaDifficulty / duration
    if len(previousWorkout) < 1:
        return {'newFitness': 100, 'targetDifficulty': 100 + deltaDifficultyPerWeek}
    # todo if workout large success, use all the previous workouts
    previousWorkoutScore = get_workout_score(previousWorkout)
    if previousWorkoutScore['workoutScore'] < 94:
        return {'newFitness': currentFitness, 'targetDifficulty': currentFitness + deltaDifficultyPerWeek}
    return {
        'newFitness': previousWorkout['personalisedDifficultyMultiplier'],
        'targetDifficulty': previousWorkout['personalisedDifficultyMultiplier'] + deltaDifficultyPerWeek,
    }


# todo edit this again
def get_best_trainingPlan(trainingPlanPrimary, trainingPlanSecondary):
    return trainingPlanPrimary[0] > trainingPlanSecondary[0]  # and trainingPlanPrimary[0] - trainingPlanSecondary[0] < 3 and trainingPlanPrimary[1]["personalisedDifficultyMultiplier"] < trainingPlanSecondary[1]["personalisedDifficultyMultiplier"]


def get_interval_training_plan(targetPace, cNewbieGains, userInfo, previousWorkout, displayPace):
    velocities = get_velocities(get_paces(targetPace, cNewbieGains))
    # velocities in km/hr, paces in s/m
    speedDifficulty = getSpeedDifficulty(convert_to_velocity(userInfo['currentTime']), convert_to_velocity(userInfo['targetTime']), velocities)  # getSpeedDifficulty(currentVelocity, paces);
    trainingPlanPrimary, trainingPlanSecondary, newFitness = itemgetter('trainingPlanPrimary', 'trainingPlanSecondary', 'newFitness')(generate_training_plans(speedDifficulty, targetPace, userInfo, previousWorkout))
    trainingPlan = trainingPlanSecondary[1] if get_best_trainingPlan(trainingPlanPrimary, trainingPlanSecondary) else trainingPlanPrimary[1]
    trainingPlan['workoutInfo'][0]["rest"] = get_prescribed_rest(trainingPlan['workoutInfo'][0]["restMultiplier"],
                                                                  targetPace)
    trainingPlan['workoutInfo'][0]["pace"] = displayPace
    return {'newFitness': newFitness, 'trainingPlan': trainingPlan}


def generate_training_plans(speedDifficulty, targetPace, userInfo, previousWorkout):
    newFitness, targetDifficulty = itemgetter('newFitness', 'targetDifficulty')(get_overall_fitness(
        speedDifficulty,
        userInfo['duration'],
        userInfo['currentFitness'],
        previousWorkout,
    ))

    def get_personalised_difficulty(workout):
        workout['personalisedDifficultyMultiplier'] = (speedDifficulty / 100) * workout[
            'difficultyMultiplier'] * restMultiplier(workout, targetPace)
        return workout

    primary = map(get_personalised_difficulty, list(Workout.objects.filter(id__contains='primary').values()))
    secondary = map(get_personalised_difficulty, list(Workout.objects.filter(id__contains='secondary').values()))

    def get_closest_workout(workoutOne, workoutTwo):
        workoutVariance = abs(workoutTwo['personalisedDifficultyMultiplier'] - targetDifficulty)
        if workoutVariance > workoutOne[0]:
            return workoutOne
        return [workoutVariance, workoutTwo]

    trainingPlanPrimary = reduce(get_closest_workout, primary, [10000])
    trainingPlanSecondary = reduce(get_closest_workout, secondary, [10000])
    return {'trainingPlanPrimary': trainingPlanPrimary, 'trainingPlanSecondary': trainingPlanSecondary,
            'newFitness': newFitness}


def get_weeks_and_start_date(firstWorkoutTimestamp, currentDatestamp):
    numberOfWeeksElapsed = 0
    weekStartDatestamp = firstWorkoutTimestamp
    while weekStartDatestamp < currentDatestamp:
        numberOfWeeksElapsed += 1
        weekStartDatestamp += (604800000 * numberOfWeeksElapsed)
    return {'numberOfWeeksElapsed': numberOfWeeksElapsed, 'weekStartDatestamp': weekStartDatestamp}


def get_fartlek_workout(fillerWorkout, tempoPace, goalPace):
    jogTime = ''
    jogDistance = ''
    sprintDistance = itemgetter('sprintDistance')(fillerWorkout['workoutInfo'][0])

    def getJogPace(jogPace):
        y = 0
        for x in jogPace:
            if x == 'tempoPace':
                y += tempoPace
            else:
                y += int(x)
        return y

    jogPace = getJogPace(fillerWorkout['workoutInfo'][0]['jogPace'])
    if fillerWorkout['workoutInfo'][0]['jogByTime']:
        jogTime = fillerWorkout['workoutInfo'][0]['jogByTime']
        jogDistance = jogTime / jogPace
    elif fillerWorkout['workoutInfo'][0]['jogByDistance']:
        jogDistance = fillerWorkout['workoutInfo'][0]['jogByDistance']
        jogTime = jogDistance * jogPace

    def getSprintPace(sprintPace):
        y = 0
        for x in sprintPace:
            if x == 'goalPace':
                y += goalPace
            else:
                y += int(x)
        return y

    sprintPace = getSprintPace(fillerWorkout['workoutInfo'][0]['sprintPace'])
    return {  # pace in s/m, distance in m, time in s
        'sprintDistance': sprintDistance, 'jogTime': jogTime, 'jogPace': jogPace, 'sprintPace': sprintPace,
        'jogDistance': jogDistance}


def get_fartlek_trainingPlan(alpha, weekNumber, tempoPace, targetPace):
    fartlek = list(Workout.objects.filter(id__contains='fartlek').values())
    for workout in fartlek:
        if alpha < float(workout['alpha']):
            if weekNumber == float(workout['workoutInfo'][0]['weekAt']):
                return {**get_fartlek_workout(workout, tempoPace, targetPace),
                        'sprintSets': workout['workoutInfo'][0]['sprintSets']}
            if weekNumber > workout['workoutInfo'][0]['weekAt'] and workout['workoutInfo'][0]['end']:
                if alpha < 0.8:
                    sprintSets = workout['workoutInfo'][0]['sprintSets'] + weekNumber - workout['workoutInfo'][0][
                        'weekAt']
                    return {**get_fartlek_workout(workout, tempoPace, targetPace), 'sprintSets': sprintSets}
                fartlekWorkout = get_fartlek_workout(workout, tempoPace, targetPace)
                fartlekWorkout['sprintPace'] = fartlekWorkout['sprintPace'] - (
                        weekNumber - workout['workoutInfo'][0].weekAt) * 0.00250
                return {**fartlekWorkout, 'sprintSets': workout['workoutInfo'][0]['sprintSets']}


def get_next_date(dateToCompare, previousWorkoutDate):
    if (dateToCompare - sanitise_week_date_stamp(previousWorkoutDate)) < 86400000:
        return dateToCompare + 86400000
    return dateToCompare


def get_suggestedDate(userInfo, previousWorkout=None):
    sanitisedCurrentDatestamp = sanitise_week_date_stamp(time())
    ipptDatestamp = itemgetter('ipptDatestamp')(userInfo)
    # below for if close to IPPT date
    if (sanitise_week_date_stamp(ipptDatestamp) - sanitisedCurrentDatestamp) < (86400000 * 2):
        return None
    if previousWorkout:
        if 'long_distance' not in previousWorkout['type']:
            firstWorkoutTimestamp = int('1622542227000')
            currentDatestamp = time()
            numberOfWeeksElapsed = itemgetter('numberOfWeeksElapsed')(get_weeks_and_start_date(firstWorkoutTimestamp, currentDatestamp))
            nextWeekStart = sanitise_week_date_stamp((604800000 * (numberOfWeeksElapsed + 1)) + firstWorkoutTimestamp)
            return get_next_date(nextWeekStart, previousWorkout['date'])
    #     Test below
    return get_next_date(sanitisedCurrentDatestamp, time())


def get_long_distance_trainingPlan(alpha, weekNumber, tempoPace):
    longDistance = list(Workout.objects.filter(id__contains='long_distance').values())
    for workout in longDistance:
        if alpha < float(workout['alpha']):
            if weekNumber == float(workout['workoutInfo'][0]['weekAt']):
                convertedTempoPace = tempoPace * 1000
                return {  # runTime in min, tempoPace in s/m, distance in km
                    'runTime': workout['workoutInfo'][0].runTime,
                    'tempoPace': tempoPace,
                    'distance': get_rounded_distance(workout['workoutInfo'][0]['runTime'], convertedTempoPace)
                }
            if weekNumber > workout['workoutInfo'][0]['weekAt'] and workout['workoutInfo'][0]['end']:
                convertedTempoPace = tempoPace * 1000
                tempoPaceNew = convertedTempoPace - (weekNumber - workout['workoutInfo'][0]['weekAt']) * 3
                runTime = workout['workoutInfo'][0]['runTime']
                distance = get_rounded_distance(runTime, tempoPaceNew)
                return {'distance': distance, 'runTime': runTime, 'tempoPace': tempoPaceNew / 1000}


def get_one_of_three_trainingPlan(targetPace, cNewbieGains, userInfo, previousWorkout, displayPace, alpha):
    firstWorkoutTimestamp = int('1622542227000')
    workoutFrequency, ipptDatestamp = itemgetter('workoutFrequency', 'ipptDatestamp')(userInfo)
    currentDatestamp = time()
    userInfo['duration'] = 8  # todo Math.floor(ipptDatestamp - currentDatestamp)
    previousWorkoutDatestamp = previousWorkout['date'] if previousWorkout else ''
    numberOfWeeksElapsed, weekStartDatestamp = itemgetter('numberOfWeeksElapsed', 'weekStartDatestamp')(get_weeks_and_start_date(firstWorkoutTimestamp, currentDatestamp))
    weekStartDatestamp = sanitise_week_date_stamp(weekStartDatestamp)
    nextWeekStart = sanitise_week_date_stamp((604800000 * (numberOfWeeksElapsed + 1)) + firstWorkoutTimestamp)
    tempoPace = get_paces(targetPace, cNewbieGains)[0]
    isPreviousWorkoutIntervalWorkout = (
            'primary' in previousWorkout['type'] or 'secondary' in previousWorkout['type'] or 'pyramid' in
            previousWorkout['type']) if previousWorkout else False
    if (ipptDatestamp - currentDatestamp) < 604800000:
        if isPreviousWorkoutIntervalWorkout:
            return get_long_distance_trainingPlan(alpha, numberOfWeeksElapsed, tempoPace)
        return get_fartlek_trainingPlan(alpha, numberOfWeeksElapsed, tempoPace, targetPace)
    if workoutFrequency == 1 or not (len(previousWorkout) > 0):
        return get_interval_training_plan(targetPace, cNewbieGains, userInfo, previousWorkout, displayPace)
    if workoutFrequency == 2:
        if isPreviousWorkoutIntervalWorkout and previousWorkoutDatestamp > weekStartDatestamp and currentDatestamp < nextWeekStart:
            return get_long_distance_trainingPlan(alpha, numberOfWeeksElapsed, tempoPace)
    if workoutFrequency == 3:
        if previousWorkoutDatestamp > weekStartDatestamp and currentDatestamp < nextWeekStart:
            if isPreviousWorkoutIntervalWorkout:
                return get_long_distance_trainingPlan(alpha, numberOfWeeksElapsed, tempoPace)
            return get_fartlek_trainingPlan(alpha, numberOfWeeksElapsed, tempoPace, targetPace)
    return get_interval_training_plan(targetPace, cNewbieGains, userInfo, previousWorkout, displayPace)


def getTrainingPlan(questionnaireData, previousWorkout=None, previousFitness=100):
    if previousWorkout is None:
        previousWorkout = {}
    if questionnaireData['regular']:
        pass  # TBC logic
    userInfo = get_user_info(questionnaireData, previousFitness)
    userInfo['ipptDatestamp'] = 1628513171000
    alpha, beta, cNewbieGains = itemgetter('alpha', 'beta', 'cNewbieGains')(generate_constants(questionnaireData))
    targetPace, displayPace = itemgetter('targetPace', 'displayPace')(get_target_paces(userInfo['targetTime']))
    suggestedDate = get_suggestedDate(userInfo, previousWorkout)
    newFitness, trainingPlan = itemgetter('newFitness', 'trainingPlan')(get_one_of_three_trainingPlan(targetPace, cNewbieGains, userInfo, previousWorkout, displayPace, alpha))
    return {'newFitness': newFitness, 'trainingPlan': trainingPlan, 'suggestedDate': suggestedDate}


def get_training_plan():
    targetPace = itemgetter('targetPace')(get_target_paces(720))
    questionnaireData = {'frequency': 0, 'experience': 0, 'distance': 0, 'latest': "13:00", 'workoutFrequency': 3, 'target': "12:00", 'duration': 8, 'regular': False}
    userInfo = get_user_info(questionnaireData, 100)
    cNewbieGains = itemgetter('cNewbieGains')(generate_constants(questionnaireData))
    velocities = get_velocities(get_paces(targetPace, cNewbieGains))
    speedDifficulty = getSpeedDifficulty(11.076923076923077, 11.999999999999998, velocities)
    previousWorkout = {
        'difficultyMultiplier': 91,
        'workoutInfo': [
            {
                'distance': 300,
                'pace': 25000,
                'part_ID': "1006_0",
                'rest': 115,
                'restMultiplier': 4.5,
                'sets': 8,
                'timings': [82000, 207000, 83000, 79430, 78236],
            },
        ],
        'personalisedDifficultyMultiplier': 160.0173922309409,
        'type': "primary"
    }
    return {
        '0.3': targetPace,
        '135': get_prescribed_rest(4.5, targetPace),
        '720, 720, 8, 100, 3': userInfo,
        '1.2454688326370063': cNewbieGains,
        '7.751348326370826, 8.09657644510835, 9.115350964691519, 10.825759516493187': velocities,
        '115.4117657370535': speedDifficulty,
        '37.985266824813856': get_workout_score(previousWorkout)['workoutScore'],
        '3': get_missed(previousWorkout),
        '0.5687392682727516': penalise_missed(get_missed(previousWorkout), previousWorkout),
        '50562.40161384742': get_standard_deviation(previousWorkout),
        '75000': get_goal_set_time(previousWorkout),
        '105933.2': get_average_time(previousWorkout),
        '{"newFitness": 100, "targetDifficulty": 101.92647071713169}': get_overall_fitness(speedDifficulty, userInfo['duration'], userInfo['currentFitness'], previousWorkout),
        'primary-6, secondary-9': generate_training_plans(speedDifficulty, targetPace, userInfo, previousWorkout),
        'primary-6': getTrainingPlan(questionnaireData)
    }
