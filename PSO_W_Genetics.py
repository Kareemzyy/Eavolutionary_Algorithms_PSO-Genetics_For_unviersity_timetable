import pandas as pd
import numpy as np
import random
import copy
from multiprocessing import Pool
from GUI import *
from Genetics_Main import *

from math import ceil, floor
MAXI_NUM_BEST_SOL = 30
Max_Lec_Per_Day = 7
NUM_OF_PARTICLES = 70
NUM_OF_ITERATIONS = 100

data = pd.read_csv('Data_Folder/data.csv')
days = ['Sunday', 'Monday', 'Tuesday', 'Wednesday', 'Thursday']
time_slots = data['Time Slot'].tolist()
halls = data['Hall'].tolist()
course_professors = data['Course & Professsor'].tolist()


class Particle:  # --- here is the class of particle so that to create particles from ----#
    def __init__(self):  # -------  init makes a class iterable  -------##
        self.schedule = self.create_schedule()
        self.score = 0  # --  creates particles when called  ---#

    def create_schedule(self):
        schedule = []
        for _ in range(len(course_professors)):  # ---- randomly create the schedule ---#
            day = random.choice(days)
            time_slot = random.choice(time_slots)
            hall = random.choice(halls)

            course_professor = course_professors[_]  # --  pick a doctor not randomly ---#
            schedule.append(
                (day, time_slot, hall, course_professor))  # -------  appending a tuple to the sechdule  -------##
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


# Your imports and class definition here...

def evaluate_particle(particle):
    particle.fitness_func()
    return particle

if __name__ == "__main__":
    particles = [Particle() for _ in range(NUM_OF_PARTICLES)]  # create particles
    best_particles = []

    with Pool() as pool:
        for _ in range(NUM_OF_ITERATIONS):
            # Evaluate all particles in parallel.
            particles = pool.map(evaluate_particle, particles)

            for particle in particles:
                scores = [p.score for p in best_particles]  # List of scores in best_particles
                # Check if the particle is already in the best particles or not and if its better than one in the list
                if particle.score not in scores and (len(best_particles) < MAXI_NUM_BEST_SOL or particle.score > min(scores)):
                    # Check if it's at the maximum set or not
                    if len(best_particles) == MAXI_NUM_BEST_SOL:
                        # Remove the particle with the lowest score
                        best_particles = [p for p in best_particles if p.score != min(scores)]
                    # Copy them into the best ones list
                    best_particles.append(copy.copy(particle))
                    best_particles.sort(key=lambda x: x.score, reverse=True)  # Sort in descending order





    # Create a dictionary to store the best particles and their scores
    best_particles_dict = {}

    for particle in best_particles:
        # Convert the schedule of the particle to a tuple so it can be used as a key in the dictionary
        schedule_tuple = tuple(tuple(x) for x in particle.schedule)

        # Add the particle and its score to the dictionary
        best_particles_dict[schedule_tuple] = particle.score

    # Now you can print the dictionary


    population = best_particles_dict




    ft,df = start(population,0.6,'PSOwGENETICS.csv')

    displaying_table(df,ft)