# gale-shapley
Implementation of the Gale-Shapley for a specific use-case algorithm in Python.   
Match a set of people to a set of locations with varying number of availabilities (capabilities) based on preferences.

## How to run
1. Clone the repository
2. Have Python 3 installed
3. **Optional**: Create test data by running `python gen_test.py`
3. Run the Gale-Shapley algorithm by running `python run_gale_shapley.py`

## Input data
``location_capabilities.csv`` and ``person_preferences.csv`` are the input files for the algorithm.
See the example files provided for the format of the input files.

## gen_test.py
Generates `NUM_TESTS` sets of test data for the Gale-Shapley algorithm. The number of locations, people and capabilities per location can be changed in the script.
The script does a **weighted random selection** of locations and people to generate the preferences. The number of generated preferences is always 10. The parameters for the weighted random selection can be changed in the script, `PROBABILITY_FOR_PREFERRED_LOC` and `NUM_OF_PREFERRED_LOCS`

## run_gale_shapley.py
By default, runs the Gale-Shapley algorithm on the test data generated by ``gen_test.py``.
set to 0 or remove the parameter of the function call `run()` in `__main__` function to run the algorithm on data NOT generated by `gen_test.py`.
The input files are ``location_capabilities.csv`` and ``person_preferences.csv`` and must be located in the same directory as the script.

The change the number of set preferences for each person, change the parameter `NUM_PREFS` in the script.

## Output
The output of the algorithm is the list of pairs. It will be saved in a csv called `location_assignments.csv` of the form (with headers):

|Location   |Person   |Prio
|-----------|---------|----
|Location8  |Person35 |1
|Location19 |Person20 |1
|Location82 |Person117|1
|Location82 |Person125|2
|Location152|Person90 |3
|Location152|Person36 |4
|Location149|Person167|4

**Not every person may be assigned a location. The remaining people are not assigned any location!**

See the output of the script for info of not assigned people and remaining capacity of locations.
This is an extract of a possible output in the console.

    Warnung: 2 Personen konnten keine Location aus ihren Präferenzen zugewiesen werden.
    - Person169: Präferenzen: ['Location17', 'Location9', 'Location19', 'Location91', 'Location4', 'Location15', 'Location1', 'Location20', 'Location8']
    - Person142: Präferenzen: ['Location11', 'Location3', 'Location1', 'Location20', 'Location6', 'Location9', 'Location4', 'Location15', 'Location12']

    Locations mit verbleibender Kapazität:
    - Location109: 2 Plätze frei
    - Location51: 1 Plätze frei
