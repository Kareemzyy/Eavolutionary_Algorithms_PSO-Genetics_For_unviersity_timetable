from Genetics_Main import *
from GUI import *
Course_and_prof = np.array(pd.read_csv('Data_Folder/data.csv')['Course & Professsor'])
def initialization(pop_sz):
    population = {}

    for i in range(pop_sz):
        ind = np.array([])
        for cr_pr in Course_and_prof:
            # --------- Creating an individual as 1D NumPy array. --------- #
            rw = np.array([random.choice(Days), random.choice(Time_Slots), random.choice(Halls), cr_pr])
            ind = np.append(ind, rw)

        # --------- Reshaping an individual into 45 rows and 4 columns. --------- #
        ind = ind.reshape(45, 4)

        # --------- Converting an individual into a tuple and append it to the population. --------- #
        population[tuple(ind.flatten())] = fitness_funcs(ind)

    return population


pop = initialization(50)
ft,df = start(pop, 0.7, 'Schedule.csv')
displaying_table(df,ft)