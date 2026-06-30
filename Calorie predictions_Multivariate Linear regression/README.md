# Calorie Expenditure Prediction

A simple linear regression project to predict calories burned during exercise.

## Author
Areeba Bushra

## Dataset
- Source: [Calorie Expenditure Dataset (Google Drive)](https://drive.google.com/file/d/1tj_WGyspImVxlpzL1KSzu2fzLsTxPKWN/view?usp=sharing)
- 750,000 training rows
- 250,000 test rows
- Target column: `Calories`
- Features: Sex, Age, Height, Weight, Duration, Heart_Rate, Body_Temp

## What This Notebook Does
1. Loads the dataset from Google Drive (Google Colab).
2. Explores the data (info, statistics, missing values, boxplots).
3. Encodes the `Sex` column (male = 1, female = 0).
4. Checks correlation of each feature with `Calories`.
5. Splits data into training and validation sets (80/20).
6. Trains a simple linear regression on each individual feature to compare performance.
7. Trains a multiple linear regression model using all features.
8. Plots Duration vs Calories with regression line.
9. Plots Actual vs Predicted calories.
10. Reports model performance (R², RMSE, MAE).

## Tools / Libraries Used
- pandas
- numpy
- matplotlib
- seaborn
- scikit-learn (LinearRegression, train_test_split, r2_score, mean_squared_error, mean_absolute_error)

## Results
- R² = 0.968 (model explains 96.8% of the variance in calorie burn)
- Duration is the strongest single predictor (R² = 0.922 alone)
- Heart Rate and Body Temp add extra predictive value

## Limitations
- Multicollinearity between Duration, Heart Rate, and Body Temp makes individual coefficients hard to interpret directly.
- Some predictions came out negative since linear regression has no domain constraints; these were clipped to 1.
- A non-linear model (Random Forest, XGBoost, polynomial regression) may capture patterns this model misses.

## How to Run
1. Open the notebook in Google Colab.
2. Mount your Google Drive.
3. Update the dataset path to where you saved the CSV file.
4. Run all cells in order.
