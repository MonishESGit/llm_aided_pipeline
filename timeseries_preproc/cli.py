# timeseries_preproc/cli.py
from .pipeline import preprocess_csv

def main():
    path = "/Users/monish/Desktop/Monish/melio/Scripts/timeseries.csv"
    normalized_curves, annotations  = preprocess_csv(path)

    print(normalized_curves)

    print(annotations)

if __name__ == "__main__":
    main()
