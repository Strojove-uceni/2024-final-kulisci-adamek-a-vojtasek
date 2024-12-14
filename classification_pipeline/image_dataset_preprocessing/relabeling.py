import os
import argparse

def update_labels(label_dir):
    # Get all label files in the directory
    label_files = [f for f in os.listdir(label_dir) if f.endswith(".txt")]

    for label_file in label_files:
        label_path = os.path.join(label_dir, label_file)

        # Read the label file
        with open(label_path, "r") as file:
            lines = file.readlines()

        # Update each line: set class ID to 0
        updated_lines = []
        for line in lines:
            parts = line.strip().split()
            if parts:  # Ensure line isn't empty
                parts[0] = "0"  # Set the class ID to 0
                updated_lines.append(" ".join(parts))

        # Write the updated labels back to the file
        with open(label_path, "w") as file:
            file.write("\n".join(updated_lines))

        print(f"Updated labels in {label_file}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Script that adds 3 numbers from CMD"
    )
    parser.add_argument("--dir", required=True, type=str)
    args = parser.parse_args()
    dir = args.dir
    update_labels(dir)