import pandas as pd
import numpy as np
import random
from multiprocessing import Pool
from functools import partial
from GUI import *
MAXI_NUM_BEST_SOL = 30
Max_Lec_Per_Day = 5
NUM_OF_PARTICLES = 70
NUM_OF_ITERATIONS = 600



#--- Data loading ---#

data = pd.read_csv('Data_Folder/data.csv')
days = ['Sunday', 'Monday', 'Tuesday', 'Wednesday', 'Thursday']
time_slots = data['Time Slot'].tolist()
halls = data['Hall'].tolist()
course_professors = data['Course & Professsor'].tolist()
class Particle: # --- here is the class of particle so that to create particles from ----#
    def __init__(self): #-------  init makes a class constructor iterable  -------##
        self.schedule = self.create_schedule()
        self.score = 0 #--  creates particles when called  ---#

    def create_schedule(self):
        schedule = []
        for _ in range(len(course_professors)): #---- randomly create the schedule ---#
            day = random.choice(days)
            time_slot = random.choice(time_slots)
            hall = random.choice(halls)

            course_professor = course_professors[_] #--  pick a doctor not randomly ---#
            schedule.append((day, time_slot, hall, course_professor)) #-------  appending a tuple to the sechdule  -------##
        return schedule


    def fitness_func(self):
        lec_hall_con = []
        prof_con = []
        prof_consecutive_lec = {}
        lec_num_per_day = {}
        score = 100

        for rw in self.schedule:
            day, time_slot, hall, prof = rw[0], rw[1], rw[2], rw[3].split()[1]

            # ----- Checking if two or more Lectures are in the same hall at the same time. ----- #
            lec_hall_itm = f'{day} {time_slot} {hall}'
            if np.isin(lec_hall_itm, lec_hall_con):
                score -= 1
            else:
                lec_hall_con.append(lec_hall_itm)

            # ----- Checking if a professor gives two or more lectures at the same time. ----- #
            prof_itm = f'{day} {time_slot} {prof}'
            if np.isin(prof_itm, prof_con):
                score -= 1
            else:
                prof_con.append(prof_itm)

            # ----- Storing the numer of lectures per day. ----- #
            if day in lec_num_per_day:
                lec_num_per_day[day] += 1
            else:
                lec_num_per_day[day] = 1

            # ----- Storing the lectures of each professor on each day ----- #
            if prof in prof_consecutive_lec and day in prof_consecutive_lec[prof]:
                prof_consecutive_lec[prof][day].append(int(time_slot))
            else:
                prof_consecutive_lec[prof] = {day: [int(time_slot)]}

        # ----- Checking if each day has lectures more than the allowed range. ----- #
        for nm in lec_num_per_day.values():
            if nm > Max_Lec_Per_Day:
                score -= 0.2

        # ----- Checking if a professor gives more than 3 consecutive lectures on the same day. ----- #
        for prf in prof_consecutive_lec:
            for dy in prof_consecutive_lec[prf]:
                cnt_cns_lec = 1
                prof_consecutive_lec[prf][dy].sort()

                for i in range(len(prof_consecutive_lec[prf][dy]) - 1):
                    if prof_consecutive_lec[prf][dy][i] == prof_consecutive_lec[prf][dy][i + 1] - 2:
                        cnt_cns_lec += 1

                if cnt_cns_lec > 3:
                    score -= (cnt_cns_lec - 3) * 0.2

        self.score = score
def evaluate_particle(particle):
    particle.fitness_func()
    return particle
if __name__ == "__main__":
    particles = [Particle() for _ in range(NUM_OF_PARTICLES)]
    best_particle = None
    with Pool() as pool:
     for _ in range(NUM_OF_ITERATIONS):

        particles = pool.map(partial(evaluate_particle), particles)


        best_particle = max(particles, key=lambda p: p.score)
     print("Best Particle Score: ", best_particle.score)
     print("\nSchedule:")
     for day, time_slot, hall, course_professor in best_particle.schedule:
      print(f"Day: {day}, Time Slot: {time_slot}, Hall: {hall}, Course & Professor: {course_professor}")
     schedule_df = pd.DataFrame(best_particle.schedule, columns=[ 'Course & Professor', 'Hall', 'Day', 'Time Slot'])

     schedule_df.to_csv('best_schedule.csv', index=False)
     displaying_table(schedule_df,best_particle.score)








