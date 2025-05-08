import os
import re
import shutil

# Set the paths
openai_folder = "results/openai"
target_folder = "results/prompt_default_prompt/openai"

# Create target folder if it doesn't exist
os.makedirs(target_folder, exist_ok=True)

# Process each file
for filename in os.listdir(openai_folder):
    if filename.startswith("openai_") and filename.endswith(".json"):
        # Rename the file
        new_filename = filename.replace("openai_", "gpt-4o-mini_")
        old_path = os.path.join(openai_folder, filename)
        new_path = os.path.join(openai_folder, new_filename)
        os.rename(old_path, new_path)
        
        # Move the file
        target_path = os.path.join(target_folder, new_filename)
        shutil.move(new_path, target_path)
        print(f"Processed: {filename} -> {new_filename} (moved to {target_folder})")