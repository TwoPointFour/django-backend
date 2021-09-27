import json
f = open('all-workouts.json')
data=json.load(f)
f.close()
for i in data:
	ww = Workout(id=i['id'])
	if 'alpha' in i:
		ww.alpha = i['alpha']
	if 'difficultyMultiplier' in i:
		ww.difficultyMultiplier = i['difficultyMultiplier']
	ww.workoutInfo = i['workoutInfo']
	ww.save()