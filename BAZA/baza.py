
#do poprawy bo chujowo wyswietla, zobacz se w ipynb - tam git

import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

# Użycie surowego ciągu znaków (raw string) do ścieżki pliku CSV
file_path = r'C:\Users\janek\Documents\dopa\WebsiteProject\BAZA\dane.csv'

# Wczytanie pliku CSV z odpowiednim separatorem
data = pd.read_csv(file_path, sep=';')

# Konwersja kolumn do odpowiednich typów
data['wartosc'] = pd.to_numeric(data['wartosc'], errors='coerce')
data['rok'] = pd.to_numeric(data['rok'], errors='coerce')

# Usunięcie wierszy z brakującymi danymi
data = data.dropna(subset=['wartosc', 'rok'])

# Filtracja danych tylko dla przystępujących
przystepujacy = data[data['status_zdajacych'].str.contains('przystąpił', case=False, na=False)]

# Główny wykres: średnia liczba osób przystępujących do egzaminu maturalnego w poszczególnych województwach
avg_values = przystepujacy.groupby('wojewodztwo')['wartosc'].mean().reset_index()

plt.figure(figsize=(15, 7))
sns.barplot(data=avg_values, x='wojewodztwo', y='wartosc', hue='wojewodztwo', palette='viridis', dodge=False)
plt.title('Średnia liczba osób przystępujących do egzaminu maturalnego w poszczególnych województwach')
plt.xlabel('Województwo')
plt.ylabel('Średnia liczba osób')
plt.xticks(rotation=45)
plt.grid(True)
plt.legend(loc='upper right')
plt.tight_layout()
plt.show()

# Tworzenie wykresów szczegółowych dla każdego województwa w jednym oknie figure z możliwością przewijania

# Ustawienie liczby wierszy i kolumn w oknie figure
num_rows = len(data['wojewodztwo'].unique())
num_cols = 3  # Każde województwo ma trzy wykresy

# Utworzenie okna figure i osi (axes) dla każdego wykresu
fig, axes = plt.subplots(num_rows, num_cols, figsize=(18, 7 * num_rows))

# Iteracja po każdym województwie i jego wykresach
for i, wojewodztwo in enumerate(data['wojewodztwo'].unique()):
    dane_wojewodztwo = data[data['wojewodztwo'] == wojewodztwo]

    # Wykres dla przystąpiło i zdało ogółem
    sns.lineplot(ax=axes[i, 0], data=dane_wojewodztwo, x='rok', y='wartosc', hue='status_zdajacych', style='status_zdajacych', markers=True, palette='viridis')
    
    axes[i, 0].set_title(f'Liczba osób przystąpiło i zdało w województwie {wojewodztwo}')
    axes[i, 0].set_xlabel('Rok')
    axes[i, 0].set_ylabel('Liczba osób')
    axes[i, 0].legend(title='Status', loc='upper right')
    axes[i, 0].grid(True)
    
    # Wykres dla przystępujących ogółem, mężczyzn i kobiet
    przystepujacy_woj = dane_wojewodztwo[dane_wojewodztwo['status_zdajacych'].str.contains('przystąpił', case=False, na=False)]
    
    sns.lineplot(ax=axes[i, 1], data=przystepujacy_woj, x='rok', y='wartosc', hue='plec', style='plec', markers=True, palette='viridis')
    
    axes[i, 1].set_title(f'Liczba osób przystępujących w województwie {wojewodztwo}')
    axes[i, 1].set_xlabel('Rok')
    axes[i, 1].set_ylabel('Liczba osób')
    axes[i, 1].legend(title='Płeć', loc='upper right')
    axes[i, 1].grid(True)
    
    # Wykres dla zdających ogółem, mężczyzn i kobiet
    zdajacy_woj = dane_wojewodztwo[dane_wojewodztwo['status_zdajacych'].str.contains('zdał', case=False, na=False)]
    
    sns.lineplot(ax=axes[i, 2], data=zdajacy_woj, x='rok', y='wartosc', hue='plec', style='plec', markers=True, palette='viridis')
    
    axes[i, 2].set_title(f'Liczba osób zdających w województwie {wojewodztwo}')
    axes[i, 2].set_xlabel('Rok')
    axes[i, 2].set_ylabel('Liczba osób')
    axes[i, 2].legend(title='Płeć', loc='upper right')
    axes[i, 2].grid(True)

    # Ustawienie stylu i palety dla wszystkich wykresów
    for ax in axes[i]:
        ax.lines[0].set_linestyle('-')
        ax.lines[1].set_linestyle('--')
        ax.lines[2].set_linestyle(':')
        ax.set_prop_cycle(None)

# Ustawienie odstępów pomiędzy wykresami
fig.tight_layout()

# Pokazanie okna figure
plt.show()
