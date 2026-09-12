# Feature Spec: Kanban Search & Filters

## 1. SearchBar

- Běžný text filtruje tasky podle `title`.
- Přesný task key ve formátu `MAN-{id}`, například `MAN-42`, najde konkrétní task.
- `description`, assignee ani ostatní vlastnosti se fulltextově neprohledávají.
- Textové výsledky se aktualizují okamžitě při psaní.
- Bez debounce.

## 2. Rychlé Filtry

| Znak | Filtr |
|---|---|
| `#` | Layer |
| `@` | Člověk napříč rolemi: assignee, reviewer nebo creator |
| `/` | Effort |
| `!` | Priority |
| `<` | Due date |

- Status se filtrovat nebude, protože jej reprezentují sloupce Kanbanu.
- Zkratky jsou v MVP pevné.
- Do budoucna bude možné zkratky uživatelsky přebindovat.
- Přebindování změní pouze ovládání, ne interní význam uloženého filtru.

## 3. Autocomplete

Po napsání zkratky se SearchBar přepne do režimu autocomplete:

1. Napsání `/x` zobrazí všechny odpovídající hodnoty, například `XXL`, `XL`, `Extra`.
2. První položka je automaticky aktivní.
3. `Tab` vybere následující položku, `Shift+Tab` předchozí.
4. Stejně fungují šipky nahoru a dolů.
5. `Enter` potvrdí aktivní položku; kliknutí myší potvrdí kliknutou položku.

Rozepsaná zkratka ještě není aktivní filtr. Po potvrzení:

- hodnota se uloží do společného filtrovacího stavu;
- zkratka zmizí z textového vstupu;
- filtr se zobrazí jako aktivní ve FilterSidebaru;
- autocomplete se zavře.

Autocomplete filtruje lokální možnosti okamžitě, bez debounce.

## 4. Společný Stav

SearchBar a FilterSidebar používají jeden společný stav strukturovaných filtrů.

- Filtr vytvořený v SearchBaru se zobrazí ve FilterSidebaru.
- Filtr vytvořený nebo změněný ve FilterSidebaru se nepřepisuje zpět jako textová zkratka do SearchBaru.
- SearchBar si samostatně drží běžný text pro hledání podle title/task key.
- Změna jednovýběrového filtru nahradí jeho předchozí hodnotu.
- Více hodnot ve stejné vícevýběrové kategorii se kombinuje pomocí `OR`.

## 5. Kombinování

Textové hledání a strukturované filtry se kombinují pomocí `AND`.

Příklad významu:

> Title/task key odpovídá „OAuth“ **a zároveň** effort je XL **a zároveň** priority je High nebo Urgent.

- Různé kategorie se kombinují pomocí `AND`.
- Více hodnot uvnitř jedné kategorie se kombinuje pomocí `OR`.
- Filtry s nulovým počtem výsledků zůstávají dostupné.
- Prázdná kombinace zobrazí empty state; nebude rozšiřovat výsledky pomocí globálního `OR`.

## Due Date

`<datum` znamená:

> Zobraz tasky s due date menším nebo rovným zadanému datu.

- Hranice je inkluzivní.
- Tasky bez due date jsou odfiltrovány.
- Formát data vychází z uživatelského nastavení.
- Přesné podporované formáty a chování data bez roku ještě nejsou finálně rozhodnuté.

## FilterSidebar

- Je hlavním vizuálním rozhraním pro filtrování.
- Musí být jednoduchý a rychlý.
- Umožní pohodlně vytvářet složitější kompozitní filtry.
- Vždy zobrazí kompletní aktivní filtrovací stav bez ohledu na to, odkud filtr vznikl.
- Jeho detailní layout a interakce ještě nejsou součástí této specifikace.
