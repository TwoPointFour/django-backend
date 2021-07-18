from math import exp

deltas = [0.41, 0.49, 0.55, 0.65, 0.73]

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
        diffs['teDiff'] = checkDiff(differences, "teDiff") + x * (deltas[0] * teVelocity * exp(teVelocity - velocityToCompare))
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
      return delta * velocityOne * exp(velocityTwo - velocityOne)
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