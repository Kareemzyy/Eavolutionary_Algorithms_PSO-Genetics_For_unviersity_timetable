import random
from math import ceil, floor
import pandas as pd
import numpy as np

# --------- Possible values for columns. --------- #
Days = ['Saturday', 'Sunday', 'Monday', 'Tuesday', 'Wednesday', 'Thursday']
Time_Slots = [8, 10, 12, 14, 16]
Halls = ['1', '2', '6A', '15A', '6B', '17B', '18Z']


# ['Day', 'Time Slot', 'Hall', 'Course & Professor'] #


def fitness_funcs(solution):
    lec_hall_con = []
    prof_con = []
    prof_consecutive_lec = {}
    lec_num_per_day = {}

    max_lec_per_day = 3
    score = 100

    for rw in solution:
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
        if nm > max_lec_per_day:
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

    return round(score, 2)


def mutation(sol, mutation_rate):
    sz = len(sol)
    num_of_rw = floor(sz * mutation_rate)

    for i in range(num_of_rw):
        pos = random.randint(0, sz-1)
        # print(f"{pos}, ", end='')
        sol[pos][0] = Days[random.randint(0, len(Days)-1)]
        sol[pos][1] = Time_Slots[random.randint(0, len(Time_Slots)-1)]
        sol[pos][2] = Halls[random.randint(0, len(Halls)-1)]

    # print("\n", sol)
    return sol


def uniform_crossover(par_1, par_2):
    p = 0.5
    ch_1, ch_2 = [], []

    for i in range(len(par_1)):
        rand_num = random.random()
        # Taking a gene from parent_1 to child_1 if rand_num < p #
        if rand_num < p:
            ch_1.append(par_1[i])
            ch_2.append(par_2[i])
        else:
            ch_1.append(par_2[i])
            ch_2.append(par_1[i])

    return np.array(ch_1), np.array(ch_2)


def start(population, mutation_rate_per_gene, file_name, num_of_gen=50, crossover_rate=0.6, mutation_rate_per_pop=0.1):
    pop_sz = len(population)

    # --------- Starting the genetic algorithm. --------- #
    for generation in range(num_of_gen):
        # --------- Applying uniform parent selection for crossover. --------- #
        par_num = int(crossover_rate * pop_sz)
        par_num -= (0 if par_num % 2 == 0 else 1)  # Making the number of parent even for crossover.
        parents = random.sample(list(population.keys()), par_num)  # Getting random parents.

        # --------- Applying uniform crossover on selected parents. --------- #
        idx = 0
        while idx < par_num-1:
            # Making crossover between two consecutive items in the parents array. #
            ch_1, ch_2 = uniform_crossover(np.array(parents[idx]).reshape(45, 4),
                                           np.array(parents[idx+1]).reshape(45, 4))

            # Adding the children to the population. #
            population[tuple(ch_1.flatten())] = fitness_funcs(ch_1)
            population[tuple(ch_2.flatten())] = fitness_funcs(ch_2)

            idx += 2

        # --------- Applying mutation for random individuals. --------- #
        mut_num = ceil(mutation_rate_per_pop * pop_sz)
        for i in range(mut_num):
            # Getting random individual then remove it from dictionary. #
            individual = random.choice(list(population.keys()))
            del population[individual]

            # Converting the individual to 2D NumPy array for mutation then inserting it into the dictionary. #
            individual = np.array(individual).reshape(45, 4)
            mutation(individual, mutation_rate_per_gene)
            population[tuple(individual.flatten())] = fitness_funcs(individual)

        # --------- Applying GENITOR(delete-worst) Survivor Selection. --------- #
        # Sorting ascending based on the fitness function. #
        population = dict(sorted(population.items(), key=lambda item: item[1]))

        # Deleting the worst individuals. #
        while len(population) > pop_sz:
            key = next(iter(population))  # Getting the first key in the dictionary.
            del population[key]

    #-- Getting the best schedule --#
    # Getting the key with the maximum fitness then printing its fitness.
    schedule = max(population, key=population.get)
    fitness = population[schedule]

    # Converting the schedule into a 2D NumPy array, then sorting it based on the days.
    schedule = np.array(schedule).reshape(45, 4)
    sorting_key = np.argsort([Days.index(day) for day in schedule[:, 0]])
    sorted_schedule = schedule[sorting_key]

    # Converting the schedule into a data frame, printing it, then saving it as csv file.
    df = pd.DataFrame(sorted_schedule, columns=['Day', 'Time Slot', 'Hall', 'Course & Professor'])
    df.to_csv(file_name, index=False)
    return fitness,df