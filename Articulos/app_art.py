from pathlib import Path

directory = Path('./Scopus/')
archivos = directory.glob("*.bib")

for archivo in archivos:
    a = open(archivo, 'r', encoding="utf-8")
    fc = a.read()
    fL = fc.split('\n')

    desired_fields = ('author', 'title', 'doi', 'year', 'abstract', 'journal')
    count = 0

    for i in fL:
        try:
            key, value = i.split("=", 1)
            key = key.strip()
            if key in desired_fields:
                print(f"{key}: {value.strip()}")
            elif('@' in i):
                count += 1
                print("------------------------------------")
                print(f'Articulo número {count}')
        except:
            try:
                if(i[0] == '@'):
                    count += 1
                    print("------------------------------------")
                    print(f'Articulo número {count}')
            except:
                pass