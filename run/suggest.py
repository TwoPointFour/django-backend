import math
from functools import reduce
from operator import itemgetter
from statistics import pstdev

from .models import Workout

# All constants below TBC
rho = 7.0
# tePace, ltPace, vPace, stPace
phi = [1, 1, 1, 1]
paceConstants = [1.243, 1.19, 1.057, 0.89]
deltas = [0.41, 0.49, 0.55, 0.65, 0.73]
kValue = 0.25
yValue = 1.25
def getPace(time):
    return time/2400
def convertSecToHour(timeInSec):
    return timeInSec / (60 * 60)
def getTargetPaces(targetTime):
    targetPace = getPace(targetTime)
    displayPace = math.floor(targetPace * 100 * 1000)
    return {'targetPace': targetPace, 'displayPace': displayPace}
def convertToVelocity(currentTime):
    return 2.4 / convertSecToHour(currentTime)
def getPrescribedRest(restMultiple, targetPace):
    return round((restMultiple * targetPace * 100) / 5) * 5
def restRatio(restMultiple, targetPace):
    return getPrescribedRest(restMultiple, targetPace) / (restMultiple * targetPace * 100)
def restMultiplier(workout, targetPace):
    return 1 / math.exp(0.0024 * restRatio(workout['parts'][0]["restMultiplier"], targetPace))
def convertToSeconds(input):
    split_array = input.split(":")
    return int(split_array[0]) * 60 + int(split_array[1])
def sanitiseWeekDateStamp(timestamp):
    return timestamp - (timestamp % 86400000)
def getPaces(targetPace, cNewbieGains):
    return [targetPace * paceConstants[i] * cNewbieGains * x for i, x in enumerate(phi)]
def getVelocities(paces):
    return [(1 / pace) * 3.6 for pace in paces]
def getGoalSetTime(previousWorkout): # in ms
  return (float(previousWorkout['parts'][0]["pace"]) * float(previousWorkout['parts'][0]["distance"])) / 100
def getAverageTime(previousWorkout): #in seconds
  timings = previousWorkout['parts'][0]["timings"]
  return (math.fsum(timings) / len(timings))
def getStandardDeviation(previousWorkout):
    return pstdev(previousWorkout['parts'][0]["timings"])
# todo get rid of the retarded parseFloat all over the place
def getMissed(previousWorkout):
    return previousWorkout['parts'][0]["sets"] - len(previousWorkout['parts'][0]["timings"])
def penaliseMissed(missed, previousWorkout):
    return (math.exp(missed / float(previousWorkout['parts'][0]["sets"])) - 1) * yValue

def getUserInfo(questionnaireData, previousFitness):
  duration, workoutFrequency = itemgetter('duration', 'workoutFrequency')(questionnaireData)
  # todo fix currentFitness
  return {
    'currentTime': convertToSeconds(questionnaireData['latest']),
    'targetTime': convertToSeconds(questionnaireData['target']),
    'duration': duration,
    'workoutFrequency': workoutFrequency,
    'currentFitness': previousFitness
  }

def generateConstants(questionnaireData):
  #todo verify personalbests below
  beta = 1 if questionnaireData['regular'] else 0.975
  alpha = max(0, min(1, (1 / 3) * beta * ((questionnaireData['frequency'] * questionnaireData['distance']) / 30 + questionnaireData['experience'] / 36 + questionnaireData['frequency'] / 3)))
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

def checkDiff(diffs, diff):
    if diff in diffs:
        return diffs[diff]
    return 100

def getDiffs(velocityToCompare, velocities, intermediateFunc, x = 1, differences=None):
    if differences is None:
        differences = {}
    diffs = {}
    teVelocity, ltVelocity, vVelocity, stVelocity = velocities
    if (velocityToCompare < teVelocity):
        diffs['teDiff'] = checkDiff(differences, "teDiff") + x * (deltas[0] * teVelocity * math.exp(teVelocity - velocityToCompare))
    elif (velocityToCompare < ltVelocity):
        diffs['teDiff'] = checkDiff(differences, "teDiff") - x * intermediateFunc(deltas[1], teVelocity, velocityToCompare)
    elif (velocityToCompare < vVelocity):
        diffs['ltDiff'] = checkDiff(differences, "ltDiff") - x * intermediateFunc(deltas[2], ltVelocity, velocityToCompare)
    elif (velocityToCompare < stVelocity):
        diffs['vDiff'] = checkDiff(differences, "vDiff") - x * intermediateFunc(deltas[3], vVelocity, velocityToCompare)
    else:
        diffs['stDiff'] = checkDiff(differences, "stDiff") -x * intermediateFunc(deltas[4], stVelocity, velocityToCompare)
    return diffs

def getSpeedDifficulty(currentVelocity, targetVelocity, velocities):
    #todo why so many diffs. floating around? get rid of them
    teVelocity, ltVelocity, vVelocity, stVelocity = velocities
    def intermediateFunc(delta, velocityOne, velocityTwo):
      return delta * velocityOne * math.exp(velocityTwo - velocityOne)
    diffs = getDiffs(currentVelocity, velocities, intermediateFunc)
    while (len(diffs) < 4):
        if ('teDiff' in diffs and 'ltDiff' not in diffs):
            diffs['ltDiff'] = diffs['teDiff'] + intermediateFunc(deltas[1], teVelocity, ltVelocity)
        if ('ltDiff' in diffs and not ('teDiff' in diffs and 'vDiff' in diffs)):
            if ('teDiff' not in diffs):
                diffs['teDiff'] = diffs['ltDiff'] - intermediateFunc(deltas[1], teVelocity, ltVelocity)
            if ('vDiff' not in diffs):
                diffs['vDiff'] = diffs['ltDiff'] + intermediateFunc(deltas[2], ltVelocity, vVelocity)
        if ('vDiff' in diffs and not ('ltDiff' in diffs and 'stDiff' in diffs)):
            if ('ltDiff' not in diffs):
                diffs['ltDiff'] = diffs['vDiff'] - intermediateFunc(deltas[2], ltVelocity, vVelocity)
            if ('stDiff' not in diffs):
                diffs['stDiff'] = diffs['vDiff'] + intermediateFunc(deltas[3], vVelocity, stVelocity)
        if ('stDiff' in diffs and 'vDiff' not in diffs):
            diffs['vDiff'] = diffs['stDiff'] - intermediateFunc(deltas[3], vVelocity, stVelocity)
    finalDiffs = getDiffs(targetVelocity, velocities, intermediateFunc, -1, diffs)
    finalDiffsKeys = [*finalDiffs]
    if (len(finalDiffsKeys) == 1):
        return finalDiffs[finalDiffsKeys[0]]
    return 0

def getWorkoutScore(previousWorkout):
  if not len(previousWorkout['parts'][0]["timings"]):
    return {'goalTimePerSet': 0, 'averageTime': 0, 'standardDeviation': 0, 'missed': 0, 'workoutScore': 0}
  goalTimePerSet = getGoalSetTime(previousWorkout) # in ms
  averageTime = getAverageTime(previousWorkout) # in ms
  standardDeviation = getStandardDeviation(previousWorkout)
  missed = getMissed(previousWorkout) # integer value
  workoutScore = 100 * (goalTimePerSet / averageTime + (math.exp(standardDeviation / goalTimePerSet) - 1) * kValue - penaliseMissed(missed, previousWorkout))
  return {'workoutScore': workoutScore} # {goalTimePerSet, averageTime, standardDeviation, missed, workoutScore}

def getOverallFitness(speedDifficulty, duration, currentFitness, previousWorkout):
  deltaDifficulty = speedDifficulty - 100
  deltaDifficultyPerWeek = deltaDifficulty / duration
  if len(previousWorkout) < 1:
      return {'newFitness': 100, 'targetDifficulty': 100 + deltaDifficultyPerWeek}
  # todo if workout large success, use all the previous workouts
  previousWorkoutScore = getWorkoutScore(previousWorkout)
  if previousWorkoutScore['workoutScore'] < 94:
    return {'newFitness': currentFitness, 'targetDifficulty': currentFitness + deltaDifficultyPerWeek}
  return {
    'newFitness': previousWorkout['personalisedDifficultyMultiplier'],
    'targetDifficulty': previousWorkout['personalisedDifficultyMultiplier'] + deltaDifficultyPerWeek,
  }

# todo edit this again
def getBestTrainingPlan(trainingPlanPrimary, trainingPlanSecondary):
  return trainingPlanPrimary[0] > trainingPlanSecondary[0] and trainingPlanPrimary[0] - trainingPlanSecondary[0] < 3 and trainingPlanPrimary[1]["personalisedDifficultyMultiplier"] < trainingPlanSecondary[1]["personalisedDifficultyMultiplier"]

def generateTrainingPlans(speedDifficulty, targetPace, userInfo, previousWorkout):
  newFitness, targetDifficulty = itemgetter('newFitness', 'targetDifficulty')(getOverallFitness(
    speedDifficulty,
    userInfo['duration'],
    userInfo['currentFitness'],
    previousWorkout,
  ))
  # xyz = Workout.objects.get(id__contains='fartlek')
  # const mapper = (workout) => {
  #   const temp = JSON.parse(JSON.stringify(workout))
  #   temp.personalisedDifficultyMultiplier =
  #     (speedDifficulty / 100) * workout.difficultyMultiplier * restMultiplier(workout, targetPace) # * 100
  #   return temp
  # }
  # const reducer = (variance, workout) => {
  #   const workoutVariance = Math.abs(workout.personalisedDifficultyMultiplier - targetDifficulty)
  #   if (workoutVariance > variance[0]) {
  #     return variance
  #   }
  #   return [workoutVariance, workout] #return [workoutVariance, ...workout]
  # }
  # const primaryIntervalsCopy = primary.map(mapper)
  # const secondaryIntervalsCopy = secondary.map(mapper)
  # const trainingPlanPrimary = primaryIntervalsCopy.reduce(reducer, [10000])
  # const trainingPlanSecondary = secondaryIntervalsCopy.reduce(reducer, [trainingPlanPrimary[1]])
  # return {trainingPlanPrimary, trainingPlanSecondary, newFitness}

def get_training_plan():
    targetPace = itemgetter('targetPace')(getTargetPaces(720))
    questionnaireData = {'frequency': 0, 'experience': 0, 'distance': 0, 'latest': "13:00", 'workoutFrequency': 3,
                         'target': "12:00", 'duration': 8, 'regular': False}
    userInfo = getUserInfo(questionnaireData, 100)
    cNewbieGains = itemgetter('cNewbieGains')(generateConstants(questionnaireData))
    velocities = getVelocities(getPaces(targetPace, cNewbieGains))
    speedDifficulty = getSpeedDifficulty(11.076923076923077, 11.999999999999998, velocities)
    previousWorkout = {
            'difficultyMultiplier': 91,
            'parts': [
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
            'segment': "primary",
            'type': "Distance Interval",
            'workout_ID': "1006"
        }
    return {
        '0.3': targetPace,
        '135': getPrescribedRest(4.5, targetPace),
        '720, 720, 8, 100, 3': userInfo,
        '1.2454688326370063': cNewbieGains,
        '7.751348326370826, 8.09657644510835, 9.115350964691519, 10.825759516493187': velocities,
        '115.4117657370535': speedDifficulty,
        '37.985266824813856': getWorkoutScore(previousWorkout)['workoutScore'],
        '3': getMissed(previousWorkout),
        '0.5687392682727516': penaliseMissed(getMissed(previousWorkout), previousWorkout),
        '50562.40161384742': getStandardDeviation(previousWorkout),
        '75000': getGoalSetTime(previousWorkout),
        '105933.2': getAverageTime(previousWorkout),
        '{"newFitness": 100, "targetDifficulty": 101.92647071713169}': getOverallFitness(speedDifficulty, userInfo['duration'], userInfo['currentFitness'], previousWorkout),
        '2': generateTrainingPlans(speedDifficulty, targetPace, userInfo, previousWorkout)
    }