import cv2
import numpy as np
import os

dataset_path = "dataset"

recognizer = cv2.face.LBPHFaceRecognizer_create()

faces = []
labels = []
label_map = {}
label_id = 0

print("🔄 Starting model training...")

for person_name in os.listdir(dataset_path):
    person_folder = os.path.join(dataset_path, person_name)

    if not os.path.isdir(person_folder):
        continue

    label_map[label_id] = person_name
    print(f"Processing: {person_name} (Label ID: {label_id})")

    for image_name in os.listdir(person_folder):
        image_path = os.path.join(person_folder, image_name)

        gray_img = cv2.imread(image_path, cv2.IMREAD_GRAYSCALE)
        if gray_img is None:
            continue

        faces.append(gray_img)
        labels.append(label_id)

    label_id += 1

if not os.path.exists("trainer"):
    os.makedirs("trainer")

print(f"📊 Total faces: {len(faces)}")
print(f"👥 Total persons: {len(label_map)}")

recognizer.train(faces, np.array(labels))
recognizer.save("trainer/trainer.yml")

print("✅ Model trained successfully")
print("📋 Labels:", label_map)
print("💾 Model saved to: trainer/trainer.yml")