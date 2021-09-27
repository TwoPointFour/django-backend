from django.test import TestCase
from run.models import Workout
import run.algorithms.suggest as suggest
from operator import itemgetter


class WorkoutTest(TestCase):
    questionnaireData = {'frequency': 0, 'experience': 0, 'distance': 0, 'latest': "13:00", 'workoutFrequency': 3, 'target': "12:00", 'duration': 8, 'regular': False}
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

    @classmethod
    def setUpTestData(cls):
        cls.userInfo = suggest.get_user_info(WorkoutTest.questionnaireData, 100)
        cls.cNewbieGains = itemgetter('cNewbieGains')(suggest.generate_constants(WorkoutTest.questionnaireData))
        cls.targetPace = itemgetter('targetPace')(suggest.get_target_paces(cls.userInfo['targetTime']))
        cls.velocities = suggest.get_velocities(suggest.get_paces(cls.targetPace, cls.cNewbieGains))
        cls.speedDifficulty = suggest.get_speed_difficulty(11.076923076923077, 11.999999999999998, cls.velocities)
        cls.prescribedRest = suggest.get_prescribed_rest(4.5, cls.targetPace)

    def test_user_info(self):
        """
        Checking the user info returned
        """
        self.assertEqual(WorkoutTest.userInfo['currentTime'], 780)
        self.assertEqual(WorkoutTest.userInfo['targetTime'], 720)
        self.assertEqual(WorkoutTest.userInfo['duration'], 8)
        self.assertEqual(WorkoutTest.userInfo['currentFitness'], 100)

    def test_helper_functions(self):
        """
        Checking cNewbieGains, target pace, velocities
        """
        self.assertEqual(WorkoutTest.cNewbieGains, 1.2454688326370063)
        self.assertEqual(WorkoutTest.targetPace, 0.3)
        self.assertEqual(WorkoutTest.velocities, [7.751348326370826, 8.09657644510835, 9.115350964691519, 10.825759516493187])

    def test_speed_difficulty(self):
        """
        Speed difficulty
        """
        self.assertEqual(WorkoutTest.speedDifficulty, 115.4117657370535)

    def test_prescribed_rest(self):
        """
        Prescribed rest
        """
        self.assertEqual(WorkoutTest.prescribedRest, 135)

    def test_workout_scorer_functions(self):
        """"
        Everything related to workout scorer
        """
        self.assertEqual(suggest.get_missed(WorkoutTest.previousWorkout), 3)
        self.assertEqual(suggest.get_workout_score(WorkoutTest.previousWorkout)['workoutScore'], 37.985266824813856)
        self.assertEqual(suggest.penalise_missed(suggest.get_missed(WorkoutTest.previousWorkout), WorkoutTest.previousWorkout), 0.5687392682727516)
        self.assertEqual(suggest.get_standard_deviation(WorkoutTest.previousWorkout), 50562.40161384742)
        self.assertEqual(suggest.get_goal_set_time(WorkoutTest.previousWorkout), 75000)
        self.assertEqual(suggest.get_average_time(WorkoutTest.previousWorkout), 105933.2)

    def test_overall_fitness(self):
        """
        Overall fitness
        """
        self.assertEqual(suggest.get_overall_fitness(WorkoutTest.speedDifficulty, WorkoutTest.userInfo['duration'], WorkoutTest.userInfo['currentFitness'], WorkoutTest.previousWorkout), {"newFitness": 100, "targetDifficulty": 101.92647071713169})

    def test_interval_workouts(self):
        """
        Interval workouts
        """
        pri_and_sec_workouts = suggest.generate_training_plans(WorkoutTest.speedDifficulty, WorkoutTest.targetPace, WorkoutTest.userInfo, WorkoutTest.previousWorkout)
        self.assertEqual(pri_and_sec_workouts['trainingPlanPrimary'][1]['id'], 'primary-6')
        self.assertEqual(pri_and_sec_workouts['trainingPlanSecondary'][1]['id'], 'secondary-9')
        self.assertEqual(suggest.get_training_plan(WorkoutTest.questionnaireData)['trainingPlan']['id'], 'primary-6')

    def test_predicted_time(self):
        """
        Predicted time
        """
        self.assertEqual(suggest.get_predicted_time(WorkoutTest.questionnaireData, 115.4117657370535)['predicted_time'], 12.0)