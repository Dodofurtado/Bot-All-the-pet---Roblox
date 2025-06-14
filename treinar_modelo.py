# novo arquivo: treinar_modelo.py
import os
import cv2
import numpy as np
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
import joblib

DATASET_DIR = "dataset"
IMG_SIZE = 64

X = []
y = []

for pet_name in os.listdir(DATASET_DIR):
    pet_dir = os.path.join(DATASET_DIR, pet_name)
    if not os.path.isdir(pet_dir):
        continue
    for fname in os.listdir(pet_dir):
        img_path = os.path.join(pet_dir, fname)
        img = cv2.imread(img_path)
        if img is None:
            continue
        img = cv2.resize(img, (IMG_SIZE, IMG_SIZE)).flatten()
        X.append(img)
        y.append(pet_name)

X = np.array(X)
y = np.array(y)

# Divide em treino e teste (opcional)
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

# Treina o modelo
clf = RandomForestClassifier(n_estimators=100, random_state=42)
clf.fit(X_train, y_train)

# Salva o modelo
joblib.dump(clf, "modelo_pet.joblib")

# Avalia (opcional)
print("Acurácia:", clf.score(X_test, y_test))