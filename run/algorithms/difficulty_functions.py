from math import exp, log

deltas = [0.41, 0.49, 0.55, 0.65, 0.73]


# for the first time we are calling get_diffs, we use 100. For the second stage, we use the calculated diff
def check_diff(diffs, diff):
    if diff in diffs:
        return diffs[diff]
    return 100


def intermediate_func(delta, velocityOne, velocityTwo):
    return delta * velocityOne * exp(velocityTwo - velocityOne)


def get_diffs(velocityToCompare, velocities, x=1, differences=None):
    if differences is None:
        differences = {}
    diffs = {}
    teVelocity, ltVelocity, vVelocity, stVelocity = velocities
    if velocityToCompare < teVelocity:
        diffs['teDiff'] = check_diff(differences, "teDiff") + x * (
                deltas[0] * teVelocity * exp(teVelocity - velocityToCompare))
    elif velocityToCompare < ltVelocity:
        diffs['teDiff'] = check_diff(differences, "teDiff") - x * intermediate_func(deltas[1], teVelocity,
                                                                                    velocityToCompare)
    elif velocityToCompare < vVelocity:
        diffs['ltDiff'] = check_diff(differences, "ltDiff") - x * intermediate_func(deltas[2], ltVelocity,
                                                                                    velocityToCompare)
    elif velocityToCompare < stVelocity:
        diffs['vDiff'] = check_diff(differences, "vDiff") - x * intermediate_func(deltas[3], vVelocity,
                                                                                  velocityToCompare)
    else:
        diffs['stDiff'] = check_diff(differences, "stDiff") - x * intermediate_func(deltas[4], stVelocity,
                                                                                    velocityToCompare)
    return diffs


def calculate_difficulties(currentVelocity, velocities):
    # todo why so many diffs. floating around? get rid of them
    teVelocity, ltVelocity, vVelocity, stVelocity = velocities
    diffs = get_diffs(currentVelocity, velocities)
    while len(diffs) < 4:
        if 'teDiff' in diffs and 'ltDiff' not in diffs:
            diffs['ltDiff'] = diffs['teDiff'] + intermediate_func(deltas[1], teVelocity, ltVelocity)
        if 'ltDiff' in diffs and not ('teDiff' in diffs and 'vDiff' in diffs):
            if 'teDiff' not in diffs:
                diffs['teDiff'] = diffs['ltDiff'] - intermediate_func(deltas[1], teVelocity, ltVelocity)
            if 'vDiff' not in diffs:
                diffs['vDiff'] = diffs['ltDiff'] + intermediate_func(deltas[2], ltVelocity, vVelocity)
        if 'vDiff' in diffs and not ('ltDiff' in diffs and 'stDiff' in diffs):
            if 'ltDiff' not in diffs:
                diffs['ltDiff'] = diffs['vDiff'] - intermediate_func(deltas[2], ltVelocity, vVelocity)
            if 'stDiff' not in diffs:
                diffs['stDiff'] = diffs['vDiff'] + intermediate_func(deltas[3], vVelocity, stVelocity)
        if 'stDiff' in diffs and 'vDiff' not in diffs:
            diffs['vDiff'] = diffs['stDiff'] - intermediate_func(deltas[3], vVelocity, stVelocity)
    return diffs


def get_speed_difficulty(currentVelocity, targetVelocity, velocities):
    diffs = calculate_difficulties(currentVelocity, velocities)
    finalDiffs = get_diffs(targetVelocity, velocities, -1, diffs)
    finalDiffsKeys = [*finalDiffs]
    if len(finalDiffsKeys) == 1:
        return finalDiffs[finalDiffsKeys[0]]
    return 0


def get_estimated_twopointfour(currentVelocity, velocities, currentFitness):
    diffs = calculate_difficulties(currentVelocity, velocities)
    teVelocity, ltVelocity, vVelocity, stVelocity = velocities
    if diffs['teDiff'] > currentFitness:
        predicted_time = teVelocity - log((diffs['teDiff'] - currentFitness) / (deltas[0] * teVelocity))
        if predicted_time < teVelocity:
            return predicted_time
    if currentFitness > diffs['teDiff']:
        predicted_time = teVelocity + log((currentFitness - diffs['teDiff']) / (deltas[1] * teVelocity))
        if predicted_time < ltVelocity:
            return predicted_time
    if currentFitness > diffs['ltDiff']:
        predicted_time = ltVelocity + log((currentFitness - diffs['ltDiff']) / (deltas[2] * ltVelocity))
        if predicted_time < vVelocity:
            return predicted_time
    if currentFitness > diffs['vDiff']:
        predicted_time = vVelocity + log((currentFitness - diffs['vDiff']) / (deltas[3] * vVelocity))
        if predicted_time < stVelocity:
            return predicted_time
    predicted_time = stVelocity + log((currentFitness - diffs['stDiff']) / (deltas[4] * stVelocity))
    return predicted_time
