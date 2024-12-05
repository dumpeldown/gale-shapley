import os

# Erweiterte Funktion zum Ausführen von Tests
def run_tests(test_count):
    for i in range(1, test_count + 1):
        # Dateien dynamisch laden
        person_csv = f"person_preferences_{i}.csv"
        location_csv = f"location_capacities_{i}.csv"
        output_csv = f"location_assignments_{i}.csv"

        # Überprüfen, ob Dateien existieren
        if not os.path.exists(person_csv) or not os.path.exists(location_csv):
            print(f"Testdateien für Test {i} fehlen!")
            continue

        # Daten laden
        person_preferences, location_capacities = load_data(person_csv, location_csv)
        duplicates = check_duplicate_preferences(person_csv)
        
        if duplicates:
            print(f"Warnung: {len(duplicates)} Personen haben doppelte Präferenzen.")
            for person, preferences in duplicates.items():
                print(f"  - {person}: Präferenzen: {preferences}")
            quit()
        # Zuordnung durchführen
        assignments = gale_shapley(person_preferences, location_capacities)

        # Ergebnisse speichern
        save_results(assignments, output_csv)
        
        # Prioritätsanalyse
        priority_percentages = analyze_priorities(assignments, person_preferences)
        print(f"Prioritätsanalyse für Test {i}:")
        for priority, percentage in priority_percentages.items():
            print(f"  Priorität {priority}: {percentage:.2f}%")
        
        print(f"Test {i} abgeschlossen. Ergebnisse gespeichert in '{output_csv}'.")
        print("---------------------------------------------------------------------------------------")
        
        
        
        
def calculate_no_preference_assignments(person_preferences, assignments):
    unassigned_count = 0

    for person, preferences in person_preferences.items():
        # Prüfen, ob die Person in den Ergebnissen zu einer ihrer Präferenzen zugeordnet wurde
        assigned = any(
            person in persons and location in preferences
            for location, persons in assignments.items()
        )
        if not assigned:
            unassigned_count += 1

    return unassigned_count
    
    
def analyze_priorities(assignments, person_preferences):
    # Zähle die Häufigkeiten der Prioritäten
    priority_counts = {1: 0, 2: 0, 3: 0, 4: 0, 5: 0, 6: 0, 7: 0, 8: 0, 9: 0, 10: 0}
    total_persons = sum(len(persons) for persons in assignments.values())

    for location, assigned_persons in assignments.items():
        for person in assigned_persons:
            if person in person_preferences:
                # Finde die Priorität, die für diese Zuordnung verwendet wurde
                preferences = person_preferences[person]
                for priority, preferred_location in enumerate(preferences, start=1):
                    if preferred_location == location:
                        priority_counts[priority] += 1
                        break

    # Berechne die Prozentwerte basierend auf der Gesamtzahl der Personen
    priority_percentages = {
        priority: (count / total_persons) * 100 for priority, count in priority_counts.items()
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
def save_results(results, output_csv):
    result_rows = []
    for location, persons in results.items():
        for person in persons:
            result_rows.append({"Location": location, "Person": person})
    results_df = pd.DataFrame(result_rows)
    results_df.to_csv(output_csv, index=False)

# Main-Skript
if __name__ == "__main__":
    # Anzahl der Tests
    TEST_COUNT = 5

    # Tests ausführen
    run_tests(TEST_COUNT)
    '''
    # Dateinamen
    person_csv = "person_preferences.csv"  # Beispiel: "Person,Preference1,Preference2,Preference3,Preference4,Preference5"
    location_csv = "location_capacities.csv"  # Beispiel: "Location,Capacity"
    output_csv = "location_assignments.csv"

    # Daten laden
    person_preferences, location_capacities = load_data(person_csv, location_csv)
    duplicates = check_duplicate_preferences(person_csv)
    
    if duplicates:
        print(f"Warnung: {len(duplicates)} Personen haben doppelte Präferenzen.")
        for person, preferences in duplicates.items():
            print(f"  - {person}: Präferenzen: {preferences}")
        quit()

    # Zuordnung durchführen
    assignments = gale_shapley(person_preferences, location_capacities)

    # Ergebnisse speichern
    save_results(assignments, output_csv)
    # Prioritätsanalyse
    print("------------------------------------------")
    priority_percentages = analyze_priorities(assignments, person_preferences)
    print(f"Prioritätsanalyse:")
    for priority, percentage in priority_percentages.items():
        print(f"  Priorität {priority}: {percentage:.2f}%")
    
    print(f"Die Zuordnungen wurden in '{output_csv}' gespeichert.")
    '''