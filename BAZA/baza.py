
#coś mi tu pierdoli i musze porawić xd bo kurna generuje inaczej niz ja chce a,le dobrze

import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

# Użycie surowego ciągu znaków (raw string) do ścieżki pliku CSV
file_path = r'C:\Users\janek\Desktop\lapo\bazon\dane.csv'

# Wczytanie pliku CSV z odpowiednim separatorem
data = pd.read_csv(file_path, sep=';')

# Wyświetlenie kolumn i podgląd danych
print("Kolumny w danych:")
print(data.columns)

print("\nPodgląd danych:")
print(data.head())

# Konwersja kolumn do odpowiednich typów
data['wartosc'] = pd.to_numeric(data['wartosc'], errors='coerce')
data['rok'] = pd.to_numeric(data['rok'], errors='coerce')

# Usunięcie wierszy z brakującymi danymi
data = data.dropna(subset=['wartosc', 'rok'])

# Filtracja danych tylko dla przystępujących
przystepujacy = data[data['status_zdajacych'].str.contains('przystąpił', case=False, na=False)]

# Główny wykres: średnia liczba osób przystępujących do egzaminu w poszczególnych województwach
avg_values = przystepujacy.groupby('wojewodztwo')['wartosc'].mean().reset_index()

plt.figure(figsize=(15, 7))
sns.barplot(data=avg_values, x='wojewodztwo', y='wartosc', palette='viridis')
plt.title('Średnia liczba osób przystępujących do egzaminu maturalnego w poszczególnych województwach')
plt.xlabel('Województwo')
plt.ylabel('Średnia liczba osób')
plt.xticks(rotation=45)
plt.grid(True)
plt.show()

# Tworzenie wykresów szczegółowych dla każdego województwa
wojewodztwa = data['wojewodztwo'].unique()

for wojewodztwo in wojewodztwa:
    # Dane dla wybranego województwa
    dane_wojewodztwo = data[data['wojewodztwo'] == wojewodztwo]

    # Wykres dla przystępujących
    przystepujacy_woj = dane_wojewodztwo[dane_wojewodztwo['status_zdajacych'].str.contains('przystąpił', case=False, na=False)]
    
    plt.figure(figsize=(10, 5))
    sns.lineplot(data=przystepujacy_woj, x='rok', y='wartosc', marker='o', label='Przystępujący')
    
    # Wykres dla zdających
    zdajacy_woj = dane_wojewodztwo[dane_wojewodztwo['status_zdajacych'].str.contains('zdał', case=False, na=False)]
    
    sns.lineplot(data=zdajacy_woj, x='rok', y='wartosc', marker='o', label='Zdający')
    
    plt.title(f'Liczba osób przystępujących i zdających w województwie {wojewodztwo}')
    plt.xlabel('Rok')
    plt.ylabel('Liczba osób')
    plt.legend()
    plt.grid(True)
    plt.show()
