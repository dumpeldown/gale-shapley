import os
from itertools import islice

NUM_OF_PREFERENCES_TO_USE = 10
NUM_OF_PERSONS = 170
NUM_TESTS = 1

def take(n, iterable):
    """Return the first n items of the iterable as a list."""
    return list(islice(iterable, n))


# Erweiterte Funktion zum Ausführen von Tests
def run(test_count=0, iteration=0):
    # Dateinamen abhängig von test_count setzen
    if test_count == 0:
        runs = [(None, "person_preferences.csv", "location_capacities.csv", "location_assignments.csv")]
    else:
        runs = [
            (i, f"tests/person_preferences_{i}.csv", f"tests/location_capacities_{i}.csv", f"tests/location_assignments_{i}.csv")
            for i in range(1, test_count + 1)
        ]

    for run_id, person_csv, location_csv, output_csv in runs:
        # Überprüfen, ob Dateien existieren
        if not os.path.exists(person_csv) or not os.path.exists(location_csv):
            print(f"Dateien fehlen: '{person_csv}' oder '{location_csv}'")
            continue

        # Daten laden
        person_preferences, location_capacities = load_data(person_csv, location_csv)
        person_preferences = {person: take(NUM_OF_PREFERENCES_TO_USE, preferences) for person, preferences in person_preferences.items()}
        duplicates = check_duplicate_preferences(person_csv)
        
        if duplicates:
            print(f"Warnung: {len(duplicates)} Personen haben doppelte Präferenzen.")
            for person, preferences in duplicates.items():
                print(f"  - {person}: Präferenzen: {preferences}")
            return

        # Zuordnung durchführen
        assignments = gale_shapley(person_preferences, location_capacities)

        # Ergebnisse speichern
        save_results(assignments, person_preferences, output_csv)
        
        # Prioritätsanalyse
        priority_percentages = analyze_priorities(assignments, person_preferences)
        if run_id is None:
            print("Prioritätsanalyse für den regulären Lauf:")
        else:
            print(f"Prioritätsanalyse für Test {run_id}:")

        for priority, percentage in priority_percentages.items():
            print(f"  Priorität {priority}: {percentage:.2f}% -- Kumuliert: {sum(list(priority_percentages.values())[:priority]):.2f}%")
        print(f"Prozent der Personen ohne Zuweisung: {100 - sum(list(priority_percentages.values())):.2f}%")
        
        if run_id is None:
            print(f"Run nach {i} Iterationen abgeschlossen. Ergebnisse gespeichert in '{output_csv}'.")
        else:
            print(f"Test {run_id} nach {i} Iteration abgeschlossen. Ergebnisse gespeichert in '{output_csv}'.")
        print("---------------------------------------------------------------------------------------")
    return priority_percentages
def analyze_priorities(assignments, person_preferences):
    # Zähle die Häufigkeiten der Prioritäten
    priority_counts = {1: 0, 2: 0, 3: 0, 4: 0, 5: 0, 6: 0, 7: 0, 8: 0, 9: 0, 10: 0}
    priority_counts = {k: priority_counts[k] for k in list(priority_counts)[:NUM_OF_PREFERENCES_TO_USE]}

    for location, assigned_persons in assignments.items():
        for person in assigned_persons:
            if person in person_preferences:
                # Finde die Priorität, die für diese Zuordnung verwendet wurde
                preferences = (person_preferences[person])
                for priority, preferred_location in enumerate(preferences, start=1):
                    if preferred_location == location:
                        priority_counts[priority] += 1
                        break

    # Berechne die Prozentwerte basierend auf der Gesamtzahl der Personen
    priority_percentages = {
        priority: (count / NUM_OF_PERSONS) * 100 for priority, count in priority_counts.items()
    }

    return priority_percentages


import pandas as pd
from collections import defaultdict
import random

def gale_shapley(person_preferences, location_capacities):
    # Personen und Locations initialisieren
    free_persons = list(person_preferences.keys())
    random.shuffle(free_persons)
    location_matches = defaultdict(list)
    remaining_slots = location_capacities.copy()
    
    # Präferenzliste für Personen
    person_next_proposals = {person: 0 for person in person_preferences}

    # Personen, die keine Zuweisung bekommen können
    unassigned_persons = []

    while free_persons:
        person = free_persons.pop(0)  # Nimm eine freie Person
        preferences = person_preferences[person]
        current_choice_index = person_next_proposals[person]

        if current_choice_index < len(preferences):
            location = preferences[current_choice_index]  # Nächste Präferenz
            person_next_proposals[person] += 1

            if len(location_matches[location]) < remaining_slots[location]:
                # Platz verfügbar
                location_matches[location].append(person)
            else:
                # Kein Platz, finde die "schlechteste" Person auf Basis der Präferenz
                def get_preference_index(p):
                    try:
                        return preferences.index(p)
                    except ValueError:
                        return float('inf')  # Unendlich, wenn die Person nicht in der Liste ist

                worst_person = max(
                    location_matches[location],
                    key=lambda p: get_preference_index(p)
                )
                
                # Tausche, falls die aktuelle Person eine höhere Priorität hat
                if get_preference_index(person) < get_preference_index(worst_person):
                    location_matches[location].remove(worst_person)
                    location_matches[location].append(person)
                    free_persons.append(worst_person)
                else:
                    free_persons.append(person)
        else:
            # Keine Präferenzen mehr übrig -> keine Zuweisung möglich
            unassigned_persons.append(person)

    # Ausgabe einer Warnung für alle nicht zugewiesenen Personen
    if unassigned_persons:
        print(f"Warnung: {len(unassigned_persons)} Personen konnten keine Location aus ihren Präferenzen zugewiesen werden.")
        for unassigned_person in unassigned_persons:
            preferences = person_preferences[unassigned_person]
            print(f"  - {unassigned_person}: Präferenzen: {preferences}")

    # Überprüfung auf freie Kapazitäten
    unused_capacities = {
        location: remaining_slots[location] - len(location_matches[location])
        for location in location_matches
        if len(location_matches[location]) < remaining_slots[location]
    }
    if unused_capacities:
        print("\nLocations mit verbleibender Kapazität:")
        for location, remaining in unused_capacities.items():
            print(f"  - {location}: {remaining} Plätze frei")

    return location_matches



def check_duplicate_preferences(file_path):
    # Load the preferences CSV
    df = pd.read_csv(file_path)

    # Check for duplicate preferences per person
    duplicates = {}
    for index, row in df.iterrows():
        person = row['Person']
        preferences = row[1:].dropna().tolist()  # Get all preferences
        if len(preferences) != len(set(preferences)):
            duplicates[person] = preferences
    return duplicates


# CSV-Dateien laden
def load_data(person_csv, location_csv):
    persons_df = pd.read_csv(person_csv)
    locations_df = pd.read_csv(location_csv)

    # Präferenzen und Kapazitäten extrahieren
    person_preferences = {
        row["Person"]: [row[f"Preference{i}"] for i in range(1, 10) if pd.notna(row[f"Preference{i}"])]
        for _, row in persons_df.iterrows()
    }
    location_capacities = {row["Location"]: row["Capacity"] for _, row in locations_df.iterrows()}

    return person_preferences, location_capacities

# Ergebnisse speichern
def save_results(results, person_preferences, output_csv):
    result_rows = []
    for location, persons in results.items():
        for person in persons:
            # Finde die Priorität, nach der die Person dieser Location zugeordnet wurde
            preferences = person_preferences.get(person, [])
            priority = next((index + 1 for index, pref in enumerate(preferences) if pref == location), None)
            result_rows.append({"Location": location, "Person": person, "Prio": priority})
    
    results_df = pd.DataFrame(result_rows)
    results_df.to_csv(output_csv, index=False)

def optimize_for_cumulative_perct_in_preference_num(perct,pref_num, stats):
    if pref_num == 0:
        return sum(list(stats.values())) >= perct
    else:
        return sum(list(stats.values())[:pref_num]) >= perct

def check_new_highest(stats, highest_percts):
    for priority, percentage in stats.items():
        if priority not in highest_percts or sum(list(stats.values())[:priority]) > highest_percts[priority]:
            highest_percts[priority] = sum(list(stats.values())[:priority])
    return highest_percts


# Main-Skript
if __name__ == "__main__":
    # Für n Iterationen laufen lassen, um auf eine bestimmte Eigenschaft zu optimieren
    highest_percts = {}
    for i in range(1, 10000):
        print(f"Iteration {i}:")
        stats = run(NUM_TESTS, i)
        
        highest_percts = check_new_highest(stats, highest_percts) 
        print(f"Höchste Prozentwerte: {highest_percts}")
        # 1. Parameter: Prozentwert, 2. Parameter: Prioritätsnummer, 3. Parameter: Statistik Daten
        # Setze Prioritätsnummer auf 0, um auf eine hohe Gesamtzuweisung zu optimieren
        if optimize_for_cumulative_perct_in_preference_num(88,5,stats)\
            and optimize_for_cumulative_perct_in_preference_num(100,10,stats):
            break