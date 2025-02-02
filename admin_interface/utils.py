import cv2
import tensorflow as tf
import numpy as np
from sklearn.metrics.pairwise import cosine_similarity

# Load Pretrained Model Globally (to avoid reloading in every function call)
cnn_model = tf.keras.applications.VGG16(include_top=False, input_shape=(224, 224, 3), weights="imagenet")

def extract_features(image_path):
    """Extract features from an image using a CNN model."""
    img = cv2.imread(image_path)
    img = cv2.resize(img, (224, 224))  # Resize to model input shape
    img = img / 255.0  # Normalize pixel values
    img = np.expand_dims(img, axis=0)  # Expand dimensions for batch processing
    
    # Extract CNN features
    features = cnn_model.predict(img)
    features = tf.keras.layers.GlobalAveragePooling2D()(features)  # Flatten features
    
    return features.numpy().flatten()  # Convert to 1D array

def cnn_knn_matching(image1_path, image2_path):
    """Match two images using CNN features and cosine similarity."""
    features1 = extract_features(image1_path)
    features2 = extract_features(image2_path)
    
    # Compute cosine similarity (ranges from -1 to 1, higher means more similar)
    match_score = cosine_similarity([features1], [features2])[0][0]
    
    return match_score  # Returns similarity score (closer to 1 means a match)
