import pandas as pd
import random

import pandas as pd
import random
import pandas as pd
import random

def generate_balanced_test_data_with_10_prios(num_persons, num_locations, max_capacity, file_index):
    # Generiere Personen
    persons = [f"Person{i}" for i in range(1, num_persons + 1)]
    # Locations: Erste 20 bevorzugt
    preferred_locations = [f"Location{j}" for j in range(1, 21)]
    other_locations = [f"Location{j}" for j in range(21, num_locations + 1)]
    locations = preferred_locations + other_locations

    preferences_data = []
    for person in persons:
        # Höhere Wahrscheinlichkeit für bevorzugte Locations in den ersten Prioritäten
        choices = []
        for i in range(10):  # Für alle 10 Prioritäten
            if random.random() < 0.7:  # 70% Wahrscheinlichkeit für bevorzugte Locations
                choice = random.choice(preferred_locations)
            else:
                choice = random.choice(other_locations)
            
            # Verhindere doppelte Einträge in den Präferenzen
            while choice in choices:
                if random.random() < 0.7:
                    choice = random.choice(preferred_locations)
                else:
                    choice = random.choice(other_locations)
            choices.append(choice)

        preferences_row = {"Person": person}
        for i, choice in enumerate(choices, start=1):
            preferences_row[f"Preference{i}"] = choice
        preferences_data.append(preferences_row)
    
    preferences_df = pd.DataFrame(preferences_data)
    preferences_df.to_csv(f"person_preferences_{file_index}.csv", index=False)

    # Generiere Kapazitäten der Locations
    location_data = []
    for location in locations:
        capacity = random.randint(1, max_capacity)
        location_data.append({"Location": location, "Capacity": capacity})
    
    locations_df = pd.DataFrame(location_data)
    locations_df.to_csv(f"location_capacities_{file_index}.csv", index=False)



# Generiere 5 Testdatensätze
for i in range(1, 6):
    generate_balanced_test_data_with_10_prios(num_persons=170, num_locations=165, max_capacity=3, file_index=i)

# Ausgabe der generierten Dateien
test_files = [f"person_preferences_{i}.csv" for i in range(1, 6)] + [f"location_capacities_{i}.csv" for i in range(1, 6)]
test_files