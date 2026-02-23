


# loud csv file for RL dataset training
import os
# from turtle import pd
import pandas as pd 

TILE_SIZE = 32
GRID_WIDTH = 20
GRID_HEIGHT = 15
SCREEN_WIDTH = TILE_SIZE * GRID_WIDTH
SCREEN_HEIGHT = TILE_SIZE * GRID_HEIGHT

def debug_suspicious_move(turn_df, female_row):
    # build occupied_positions
    occupied_positions = set(turn_df["location"])
    # build pos_to_row mapping
    pos_to_row = {row["location"]: row for _, row in turn_df.iterrows()}
    # compute N/S/W/E positions
    x, y = female_row["location"]
    adjacent_positions = [
    (x, y - 1),  # North
    (x, y + 1),  # South
    (x - 1, y),  # West
    (x + 1, y)   # East
    ]

    # print female info
    print(f"Female bunny at location {female_row['location']}") 
    # for each neighbor position:  
    for pos in adjacent_positions:
        # print if occupied? if yes print bunny info
        if pos in occupied_positions:
            neighbor_row = pos_to_row[pos]
            # print neighbor info of turn_df,bunny_id, age, sex, mutant,event_type,location
            print(f"  Occupied by bunny {neighbor_row['bunny_id']} at location {neighbor_row['location']} with age {neighbor_row['age']}, sex {neighbor_row['sex']}, mutant {neighbor_row['mutant']}, event_type {neighbor_row['event_type']}")
            # print(f"  Occupied by bunny {neighbor_row['bunny_id']} at location {neighbor_row['location']}")
        else:
            # print if empty if not out of bounds
            if 0 <= pos[0] < GRID_WIDTH and 0 <= pos[1] < GRID_HEIGHT:
                print(f"  Empty tile at location {pos}")
            else:
                print(f"  Out of bounds at location {pos}")
    
    # print computed features
    adjacent_adult_male_bunnies = turn_df[(turn_df["location"].isin(adjacent_positions)) & (turn_df["sex"] == "M") & (turn_df["age"] >= 2) & (turn_df["mutant"] == False)]
    adjacent_empty_tile = any( 
        pos not in occupied_positions for pos in adjacent_positions
    )

    print(f"Adjacent adult male bunnies: {adjacent_adult_male_bunnies.shape[0]}")
    print(f"Adjacent empty tile: {adjacent_empty_tile}")

    X = [
        female_row["age"],
        int(female_row["mutant"]),
        int(not adjacent_adult_male_bunnies.empty),
        int(adjacent_empty_tile)
    ]

    #y = 1 if female_row["event_type"] == "breeding" else 0 if female_row["event_type"] == "move" else -1  # -1 for no action
    y = 1 if female_row["event_type"] == "breeding" else 0
    print(f"Features: {X}, Label: {y}")




#load file
# csv_file = "log_test.csv"  # Replace with your actual file path
# df = pd.read_csv(csv_file)

# get all csv files in logs folder and concatenate them into one dataframe
logs_folder = os.path.dirname(__file__)
csv_files = [f for f in os.listdir(logs_folder) if f.endswith(".csv")]
df_list = [pd.read_csv(os.path.join(logs_folder, f)) for f in csv_files]

# Sort by turn
df = pd.concat(df_list, ignore_index=True)
df = df.sort_values("turn")

# Process location column to extract x and y coordinates
df["location"] = df["location"].str.strip("()")
df[["x", "y"]] = df["location"].str.split(",", expand=True)
df["x"] = df["x"].astype(int)
df["y"] = df["y"].astype(int)
df["location"] = list(zip(df["x"], df["y"]))
# print(df.head())

suspicious_count = 0

X_data = []
y_data = []

for turn in sorted(df["turn"].unique()):
    turn_df = df[df["turn"] == turn]

    occupied_positions = set(turn_df["location"])

    female_df = turn_df[(turn_df["sex"] == "F") & (turn_df["age"] >= 2) & (turn_df["mutant"] == False)]

    for index, female_row in female_df.iterrows():
        # skip unwanted event types
        if female_row["event_type"] not in ["breeding", "move"]:
            continue
        
        # debug_suspicious_move for any suspicious breeding without adjacent
        # debug_suspicious_move(turn_df, female_row)

        x, y = female_row["location"]
        adjacent_positions = [
            (x, y - 1),  # North
            (x, y + 1),  # South
            (x - 1, y),  # West
            (x + 1, y)   # East
        ]
        
        # filter out out of bounds positions
        adjacent_positions = [(nx, ny) for (nx, ny) in adjacent_positions if 0 <= nx < GRID_WIDTH and 0 <= ny < GRID_HEIGHT]

        adjacent_adult_male_bunnies = turn_df[(turn_df["location"].isin(adjacent_positions)) & (turn_df["sex"] == "M") & (turn_df["age"] >= 2) & (turn_df["mutant"] == False)]
        adjacent_empty_tile = any(
        pos not in occupied_positions 
        for pos in adjacent_positions)

        X = [
            female_row["age"],
            int(female_row["mutant"]),
            bool(adjacent_adult_male_bunnies.shape[0] > 0),
            bool(adjacent_empty_tile)
            # int(adjacent_adult_male_bunnies.shape[0] > 0),
            # int(adjacent_empty_tile)
        ]

        y = 1 if female_row["event_type"] == "breeding" else 0

        X_data.append(X)
        y_data.append(y)

        if (
            int(adjacent_adult_male_bunnies.shape[0] > 0) == 1
            and int(adjacent_empty_tile) == 1
            and female_row["event_type"] == "move"
        ):
            suspicious_count += 1

print("Suspicious cases:", suspicious_count)


print("Total samples:", len(y_data))
print("Breeding (1):", sum(y_data))
print("Move (0):", len(y_data) - sum(y_data))


import random

# Separate indices
breeding_indices = [i for i, label in enumerate(y_data) if label == 1]
move_indices = [i for i, label in enumerate(y_data) if label == 0]

# print("Breeding:", len(breeding_indices))
# print("Move:", len(move_indices))

# Randomly select from move_indices to match the number of breeding samples
# random.seed(42)

# selected_move_indices = random.sample(
#     move_indices,
#     len(breeding_indices)
# )

# final_indices= 0
# if len(move_indices) >= len(breeding_indices):
#     selected_move_indices = random.sample(move_indices, len(breeding_indices))
#     final_indices = breeding_indices + selected_move_indices
# else:
#     # print("Warning: Not enough move samples to balance. Using all move samples.")
#     # selected_move_indices = move_indices
#     # print("There more breeding then move")
#     selected_move_indices = random.sample(breeding_indices, len(move_indices))
#     final_indices = move_indices + selected_move_indices

# final_indices = breeding_indices + selected_move_indices
# final_indices = move_indices + selected_move_indices
# print("Final dataset samples:", len(final_indices))

# random.shuffle(final_indices)

# Create balanced dataset
# X_balanced = [X_data[i] for i in final_indices]
# y_balanced = [y_data[i] for i in final_indices]


# print("Balanced dataset samples:", len(y_balanced))
# print("Breeding (1):", sum(y_balanced)) 
# print("Move (0):", len(y_balanced) - sum(y_balanced))


# 1) Turn your balanced lists into arrays for ML training
import numpy as np

# X = np.array(X_balanced, dtype=float)
# y = np.array(y_balanced, dtype=int)

X = np.array(X_data, dtype=float)
y = np.array(y_data, dtype=int)

print("X shape:", X.shape)  # (num_samples, num_features)
print("y shape:", y.shape)  # (num_samples,)
print("Breeding rate:", y.mean())

# 2) Train/test split for ML training

from sklearn.model_selection import train_test_split

X_train, X_test, y_train, y_test = train_test_split(
    X, y,
    test_size=0.2,
    random_state=42,
    stratify=y
)


# import numpy as np
# from sklearn.model_selection import train_test_split
# 
# def safe_train_test_split(X, y, preferred_test_size=0.2, random_state=42):
#     y = np.asarray(y)
#     n = len(y)
# 
#     # Count classes
#     class_counts = np.bincount(y)  # y must be 0/1/2...
#     n_classes = len(class_counts)
# 
#     # If only one class or too few samples per class, skip split
#     if n_classes < 2 or class_counts.min() < 2:
#         print("Too few samples per class to split. Train on all data; skip test.")
#         return X, None, y, None
# 
#     # Ensure test set has at least 1 sample per class
#     min_test_n = n_classes
#     test_n = max(int(np.ceil(preferred_test_size * n)), min_test_n)
# 
#     # Also ensure train set has at least 1 sample per class
#     # (so we don't take too many into test)
#     max_test_n = n - n_classes
#     if test_n > max_test_n:
#         print("Dataset too small for a stratified split without breaking class coverage.")
#         print("Train on all data; skip test.")
#         return X, None, y, None
# 
#     test_size = test_n / n
# 
#     X_train, X_test, y_train, y_test = train_test_split(
#         X, y,
#         test_size=test_size,
#         random_state=random_state,
#         stratify=y
#     )
#     return X_train, X_test, y_train, y_test
# 
# X_train, X_test, y_train, y_test = safe_train_test_split(X, y)
# 
# import numpy as np
# from sklearn.model_selection import StratifiedKFold, cross_val_score
# from sklearn.linear_model import LogisticRegression
# 
# model = LogisticRegression(max_iter=2000)
# 
# y = np.asarray(y)
# class_counts = np.bincount(y)
# 
# if len(class_counts) < 2 or class_counts.min() < 2:
#     print("Too few samples per class for stratified CV.")
# else:
#     n_splits = min(5, class_counts.min())  # can't have more splits than smallest class count
#     cv = StratifiedKFold(n_splits=n_splits, shuffle=True, random_state=42)
# 
#     scores = cross_val_score(model, X, y, cv=cv, scoring="f1")  # f1 focuses on positive class balance
#     print("F1 scores:", scores)
#     print("Mean F1:", scores.mean())



# 3) Train Logistic Regression model
from sklearn.linear_model import LogisticRegression

# model = LogisticRegression(
#     max_iter=2000,
#     class_weight=None,  # you already balanced the dataset
#     random_state=42
# )

model = LogisticRegression(
    max_iter=2000,
    class_weight="balanced",  # also try with balanced class weights to see if it helps
    random_state=42
)

model.fit(X_train, y_train)

# save model for later use in SL dispatcher
import joblib   
model_path = "models/sl"
os.makedirs(model_path, exist_ok=True)  
joblib.dump(model, os.path.join(model_path, "female_sl_logreg.joblib"))


# 4) Evaluate correctly (not just accuracy) on test set
from sklearn.metrics import classification_report, confusion_matrix

y_pred = model.predict(X_test)

print("Confusion matrix:\n", confusion_matrix(y_test, y_pred))
print("\nReport:\n", classification_report(y_test, y_pred, target_names=["move", "breeding"]))


# 5) Interpret the model (this is the best learning part) 
# feature_names = ["adjacent_adult_male", "adjacent_empty_tile"]

feature_names = ["age", "mutant", "adjacent_adult_male", "adjacent_empty_tile"]
weights = model.coef_[0]
bias = model.intercept_[0]

for name, w in zip(feature_names, weights):
    print(f"{name:>20}: {w: .4f}")
print(f"{'bias':>20}: {bias: .4f}")


# print("Total samples:", len(y_data))
# print("Breeding:", sum(y_data))
# print("Move:", len(y_data)-sum(y_data))
# print("Balanced:", len(y_balanced), "Breeding:", sum(y_balanced))






# Example: Get all bunnies that moved at turn 5
# turn_df = df[df["turn"] == 5]
# occupied_positions = set(turn_df["location"])
#print(f"Occupied positions at turn 5: {occupied_positions}")

# compute adjacent for one female bunny
# female_df = turn_df[turn_df["sex"] == "F"]
# for index, row in female_df.iterrows():
#     x, y = row["location"]
#     # adjacent positions (4 surrounding tiles)
#     adjacent_positions = [
#     (x, y - 1),  # North
#     (x, y + 1),  # South
#     (x - 1, y),  # West
#     (x + 1, y)   # East
#     ]
# 
#     # Check which adjacent positions are occupied by bunnies
#     adjacent_bunnies = turn_df[turn_df["location"].isin(adjacent_positions)]
#     # print(f"Bunny {row['bunny_id']} at ({x},{y}) has adjacent bunnies at: {adjacent_bunnies['location'].tolist()}")
# 
#     # Check which adjacent positions are occupied by male bunnies
#     adjacent_adult_male_bunnies = turn_df[(turn_df["location"].isin(adjacent_positions)) & (turn_df["sex"] == "M") & (turn_df["age"] >= 2) & (turn_df["mutant"] == False)]
#     #print(f"Bunny {row['bunny_id']} at ({x},{y}) has adjacent adult male bunnies at: {adjacent_adult_male_bunnies['location'].tolist()}")
# 
#     # Check which adjacent positions are empty
#     occupied_positions = set(turn_df["location"])
#     adjacent_empty_tile = any(
#     pos not in occupied_positions 
#     for pos in adjacent_positions)
#     # print(f"Bunny {row['bunny_id']} at ({x},{y}) has adjacent empty tile: {adjacent_empty_tile}")
# 
#     X = [
#     row["age"],
#     int(row["mutant"]),
#     int(adjacent_adult_male_bunnies.shape[0] > 0),
#     int(adjacent_empty_tile)
#     ]
# 
#     y = 1 if row["event_type"] == "breeding" else 0
#     print(f"Features: {X}, Label: {y}")

   


 