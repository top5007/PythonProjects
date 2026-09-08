import random as r
import string


def stringGenerator(length):
    all_chars = string.ascii_letters + string.digits + string.punctuation + " "
    return ''.join(r.choices(all_chars, k=length))


def stringRevealer(s, length):
    population = []
    generation = 0
    all_chars = string.ascii_letters + string.digits + string.punctuation + " "
    for i in range(100):
        population.append(''.join(r.choices(all_chars, k=length)))
    while s not in population:
        parent1 = ""
        parent2 = ""
        parent1_Value = 0
        parent2_Value = 0
        for child in population:
            count = 0
            for i in range(length):
                if child[i] == s[i]:
                    count += 1
            if count > parent1_Value:
                parent2, parent2_Value = parent1, parent1_Value
                parent1, parent1_Value = child, count
            elif count > parent2_Value:
                parent2, parent2_Value = child, count
        new_population = [parent1, parent2]
        generation += 1
        for i in range(100):
            child = ""
            for i in range(length):
                if r.random() < 0.05:
                    child += r.choice(all_chars)
                elif r.random() < 0.5:
                    child += parent1[i]
                else:
                    child += parent2[i]
            new_population.append(child)
            population = new_population
    return f'String found in {generation} generations, the string is {s}'


s = stringGenerator(100)
print(s)
print(stringRevealer(s, 100))
