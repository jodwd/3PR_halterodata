#!/bin/bash

# Step 1: Run the Ruby script
#echo "Running Ruby script..."
#ruby C:\Users\joris\PycharmProjects\halterodata\ruby\athletes_scoresheet.rb

# Step 2: Run the Python script
cd C:/Users/joris/PycharmProjects/halterodata
git checkout uat

python --version
echo "Running Python script..."
python C:\Users\joris\PycharmProjects\halterodata\data_transform.py


# Step 3: Add changes to Git
echo "Adding changes to Git..."

git add .

# Step 4: Commit changes
echo "Committing changes..."
git commit -m "Auto-executed scripts and pushed results"

# Step 5: Push to GitHub
echo "Pushing to GitHub..."
git push origin uat