# Dashboard

Produktová specifikace hlavního desktopového dashboardu. Tento dokument popisuje
schválené chování MVP a rozhodnutí, která má frontend respektovat. Neurčuje
konkrétní vizuální design ani implementační postup.

## Vue Struktura

```vue
<template>
    <AppShell>
        <aside class="dashboard-navigation">
            <UserProfile />
            <TeamSwitcher />
            <NavMenu />
        </aside>

        <section class="dashboard-workspace">
            <header class="dashboard-topbar">
                <SearchBar />
                <TopbarActions>
                    <SortDropdown />
                    <FilterButton />
                </TopbarActions>
            </header>

            <main class="kanban-container">
                <KanbanToolbar>
                    <LayerSwitcher />
                    <MyTasksSwitch />
                </KanbanToolbar>

                <KanbanBoard />
            </main>
        </section>

        <FilterSidebar />
    </AppShell>
</template>
```

`FilterSidebar` je uvnitř `AppShell`, ale mimo hlavní pracovní sloupec. Je
absolutně umístěný panel, který překrývá dashboard zprava a zabírá celou výšku
aplikace. Okolní dashboard zůstává interaktivní.

## Rozsah Dashboardu

Dashboard je pracovní plocha právě zvoleného workspace. Nikdy nekombinuje úkoly
z více týmů nebo workspace do jednoho Kanbanu.

Aktivním kontextem může být:

- jeden sdílený tým,
- soukromý workspace aktuálního uživatele.

Team switcher je umístěný pod `UserProfile`, nikoliv uvnitř `NavMenu`. Přepnutí
týmu načte jeho Kanban. Přepnutí zároveň zavře otevřený detail úkolu, filter
sidebar a případné modaly.

Výchozí tým po přihlášení určuje backend podle aktuálního uživatelského
nastavení. Dashboard pouze respektuje aktivní tým, který dostane z auth/session
kontextu.

Kanban zobrazuje všechny úkoly aktivního týmu. Výjimkou je aktivní lokální filtr
nebo sort aktuálního uživatele.

Dashboard je v MVP určen pouze pro desktop. Mobilní layout není součástí
tohoto rozsahu.

## Navigace

### UserProfile

`UserProfile` zobrazuje identitu přihlášeného uživatele. Pod ním je `TeamSwitcher`
pro přepnutí mezi dostupnými týmovými a soukromým workspace.

Vytváření a správa týmů bude dostupná pouze administrátorům po dokončení role
systému. V MVP se týmová správa z dashboardu neřeší.

### NavMenu

`NavMenu` je svislá navigace pod profilem a přepínačem týmu. V MVP obsahuje jako
první akci `Add Task`.

Další moduly mohou být do navigace přidány později. Položky mimo MVP nemají být
zobrazované jako nefunkční akce.

Ikony navigace jsou zobrazené v kruhových tlačítkách a při najetí zobrazují
tooltip. Levý sloupec se v MVP nesbalí.

## Topbar

Topbar je součástí pracovního sloupce. Aktivní tým se v něm neduplikuje, protože
je viditelný v `TeamSwitcher`.

### SearchBar

Search bar je součástí navržené struktury, ale funkční vyhledávání není v MVP
scope. MVP proto nemusí řešit hledání podle názvu, popisu, ID, uživatelů nebo
vrstev.

### TopbarActions

V MVP obsahuje:

- tlačítko pro výběr sortu,
- tlačítko pro otevření `FilterSidebar`.

Tlačítko filtrů zobrazuje počet právě aktivních filtrů. Další globální akce se do
topbaru v MVP nepřidávají.

## Kanban

Kanban je jediný hlavní typ boardu. List View se nepoužívá.

Kanban má pevné sloupce v tomto pořadí:

1. `Backlog`
2. `To do`
3. `In progress`
4. `Review`
5. `Done`

Sloupce nelze přejmenovat, přidávat ani odstranit. Uživatel může jednotlivé
sloupce sbalit nebo skrýt. Toto skrytí je pouze lokální pohled a nemění týmová
data.

Každý sloupec:

- zobrazuje počet právě viditelných úkolů,
- má vlastní vertikální scroll,
- zachovává stabilní hlavičku a ovládání,
- může být prázdný bez změny rozložení ostatních sloupců.

Pokud se sloupce nevejdou do dostupné šířky, Kanban používá horizontální scroll.
Sloupce se nemají násilně zmenšovat tak, aby se karty staly nepoužitelnými.

Kanban toolbar zůstává viditelný při vertikálním scrollování obsahu sloupců.
Globální souhrnný počet všech a filtrovaných úkolů není v MVP nutný; počet v
hlavičce každého sloupce je dostačující.

### Prázdné stavy

Pokud tým nemá úkoly, zobrazí se běžných pět prázdných sloupců.

Vytvoření nového úkolu je možné přímo ze sloupců, kde backend povoluje vstupní
stav. Proto se tlačítko `+` zobrazuje v:

- `Backlog`,
- `To do`,
- `In progress`.

`Review` a `Done` nemají v MVP tlačítko pro vytvoření nového úkolu, protože nový
úkol do těchto stavů nelze přímo vytvořit.

Pokud aktivní filtry nenajdou žádný úkol, zůstanou zobrazené stejné sloupce a
jejich prázdný stav. Nad příslušným tlačítkem `+` se zobrazí krátká informace,
že filtr nenašel požadovaný úkol.

## Úkolová Karta

Karta zobrazuje dostatek informací pro orientaci bez nutnosti otevírat detail,
ale nesmí se změnit v plný editor.

Minimální obsah karty v MVP:

- název úkolu,
- zkrácený náhled popisu,
- priorita,
- všechny přiřazené layer chips,
- assignee,
- reviewer, pokud je nastavený,
- effort, pokud je nastavený,
- review date a due date, pokud jsou nastavené,
- switch pro `should_review`.

Switch `should_review` musí respektovat pravidlo backendu: úkol vyžadující review
musí mít reviewera a úkol bez review nesmí mít reviewera. UI nesmí zobrazit stav,
který backend odmítne.

Název lze upravit přímo na kartě. Ostatní vlastnosti se upravují v detailu
úkolu. Kliknutí na kartu otevře detailní modal.

Detail se po zavření vrátí na původní kartu. Samostatný dlouhodobý výběr karty
pro hromadné operace v MVP neexistuje; karta může mít pouze aktuální focus nebo
otevřený detail.

Kontextové menu se třemi tečkami není v MVP. Nemá zatím dostatek samostatných
rychlých akcí, které by ospravedlnily další ovládací prvek.

### Pohyb a pořadí

Drag and drop přesouvá vždy jednu kartu. Při přesunu lze určit konkrétní pozici
v cílovém sloupci. Týmové pořadí karet a samotný přesun jsou sdílená data,
viditelná po synchronizaci všem uživatelům týmu.

Když se karta přesune do jiného sloupce bez určení pozice, vloží se na konec
cílového sloupce. Toto pravidlo platí také pro budoucí klávesový přesun.

Aktivní automatický sort určuje pouze lokální zobrazení. Ruční přeřazení uvnitř
sloupce je při automatickém sortu vypnuté. Přesun karty mezi stavy zůstává
možný, ale týmové pořadí se mění pouze explicitním ručním přesunem.

Hromadný výběr a přesun více karet není v MVP.

## Vytváření Úkolů

Nový úkol lze v MVP otevřít dvěma místy:

- tlačítkem `Add Task` v `NavMenu`,
- tlačítkem `+` ve sloupci.

Obecné klávesové ovládání není součástí MVP. Proto je základním MVP vstupem
tlačítko v navigaci a tlačítko ve sloupci.

Vytvoření probíhá v modalu. Kliknutí na `+` předvybere stav odpovídajícího
sloupce. Výchozí stav z obecného `Add Task` je `Backlog`.

Formulář pro vytvoření obsahuje title, description, assignee, reviewer, layers,
priority, review date, due date, effort a `should_review` podle pravidel
backendového create kontraktu.

Backend umožňuje přímé vytvoření pouze v `Backlog`, `To do` nebo `In progress`.
Přímé vytvoření v `Review` nebo `Done` není povolené.

Bulk Triage není v MVP.

Možnost nastavit výchozí stav nových úkolů na `To do` bude řešena později jako
team setting.

## Detail Úkolu

Detail úkolu je modal nad dashboardem. V MVP se ukládá celý formulář jedním
potvrzením, nikoliv automaticky po každé změně pole.

Editovat lze vlastnosti odpovídající backendovému `TaskUpdate`:

- assignee,
- reviewer,
- title,
- description,
- layers,
- priority,
- review date,
- due date,
- effort,
- `should_review`.

Backend v současnosti obsahuje jedno pole `layer`; produktové rozhodnutí pro MVP
je však libovolný počet layers. Frontendový detail proto pracuje s kolekcí
layers a backendový kontrakt musí tento požadavek podporovat.

Komentáře, přílohy, subtasks a activity history nejsou v MVP.

Mazání úkolu je určeno pro assigneeho nebo administrátora. Role a autorizace
ještě nejsou dokončené, takže tato hranice není v aktuálním MVP backendu plně
vynucená. Do dokončení role systému zůstává autorizační hranicí členství v
aktivním týmu.

## Layers

Layer je týmový tag podobný tagu v Obsidianu. Zobrazuje se jako hashtag, například
`#frontend` nebo `#api`.

Jeden úkol může mít libovolný počet layers. Layer patří do konkrétního týmu a
stejný layer může být přiřazen mnoha úkolům.

Layers jsou spravované entity, ne anonymní JSON metadata. Zamýšlený datový model
je samostatná týmová layer a vazba mezi taskem a layer. To umožňuje pozdější
přejmenování, archivaci, barvu, validaci a efektivní filtrování bez duplicitních
řetězců v úkolech.

Vytvářet, přejmenovávat, barvit a archivovat layers smí administrátor. Role systém
a správa layers nejsou v MVP hotové.

### LayerSwitcher

`LayerSwitcher` je hlavní rychlé filtrování přímo nad Kanbanem. V MVP je dropdown,
ne samostatný board.

Obsahuje:

- `All`,
- dostupné layers aktivního workspace,
- rychlý pohled pouze na úkoly, kde je aktuální uživatel assignee nebo reviewer.

Běžné kliknutí vybere jednu layer a nahradí předchozí výběr. Držení `Shift` při
kliknutí přidá nebo odebere další layer. Vybrané layers se kombinují pomocí
`AND`: úkol musí obsahovat všechny vybrané layers.

Při velkém počtu layers se méně používané položky schovají pod `More`.

LayerSwitcher a layer filtr ve `FilterSidebar` používají jeden společný stav.
Změna v jednom místě se okamžitě projeví v druhém místě i na Kanbanu.

`MyTasksSwitch` je samostatný rychlý lokální filtr. Zobrazuje úkoly, u kterých je
aktuální uživatel assignee nebo reviewer, a kombinuje se pomocí `AND` s ostatními
aktivními filtry.

## Filtrování

Filtrování je lokální pohled aktuálního uživatele. Backend stále načítá a
autorizuje úkoly podle aktivního týmu, ale uživatelovy filtry se neukládají do
databáze a nemění pohled ostatních uživatelů.

V MVP se načtou úkoly aktivního týmu a kombinace filtrů se vyhodnocuje na
frontendu. To zajišťuje okamžitou reakci při změně filtru a je vhodné pro malý
týmový board bez stránkování.

### MVP filtry

`FilterSidebar` v MVP nabízí:

- layers,
- assignee včetně `Me` a `Unassigned`,
- reviewer včetně `Me` a `No reviewer`,
- priority,
- effort,
- review required / no review required,
- review date,
- due date.

Status se v MVP nepoužívá jako samostatný filtr. Status je již přímo vyjádřený
sloupci Kanbanu a sloupce lze skrýt nebo sbalit.

Vyhledávání podle textu, uložené oblíbené filtry a pokročilé odvozené filtry
nejsou v MVP.

### Kombinace

Filtry z různých kategorií se kombinují pomocí `AND`. Například:

```text
assignee = Me
AND priority = Urgent
AND layer = #frontend
```

Více vybraných layers používá také `AND`.

U vlastnosti, která může mít jen jednu hodnotu, se více hodnot uvnitř stejné
kategorie chová jako `OR`. Například assignee `Petr` nebo `Jana` znamená úkoly
přiřazené jednomu z nich. `assignee = Petr AND Jana` by nebyla smysluplná
podmínka.

### Chování sidebaru

Změny ve `FilterSidebar` se aplikují okamžitě. Neexistuje tlačítko `Apply`.

Kanban se při každé změně filtru ihned přepočítá. Tlačítko `X` a klávesa `Escape`
sidebar pouze zavřou; aktivní filtry se nezahodí.

Sidebar obsahuje `Clear all` pro odstranění všech filtrů a samostatné resetování
jednotlivých kategorií. Po zavření sidebaru zůstávají aktivní filtry viditelné
jako chips nebo jiný kompaktní indikátor nad Kanbanem.

Sidebar:

- se otevře tlačítkem z topbaru,
- překryje pravou část celé výšky aplikace včetně topbaru,
- má dynamickou šířku podle dostupného viewportu,
- automaticky přijme focus při otevření,
- dovolí Tabem pokračovat zpět na Kanban,
- neuzamkne focus uvnitř sidebaru,
- nezavře se kliknutím mimo panel,
- nezavře se běžným `blur` událostí.

Transparentní okolí sidebaru nesmí blokovat interakci s Kanbanem. Interaktivní
je pouze samotný panel.

## Řazení

Řazení je lokální a nikdy se neukládá do týmového pořadí v databázi.

MVP nabízí:

- ruční pořadí,
- řazení podle priority.

Výchozí je ruční pořadí. Sort se přepíná jediným tlačítkem v `TopbarActions`,
které otevře dropdown.

Prioritní pořadí je:

1. Urgent
2. High
3. Medium
4. Low
5. bez priority

Karty se stejnou prioritou se řadí podle due date. Karty bez due date zůstávají
za kartami s due date; přesná volba směru a chování při shodném termínu zůstává
otevřeným detailem UI specifikace.

Aktivní prioritní sort musí být viditelně označený. Uživatel tak ví, proč nelze
ručně změnit pořadí karet uvnitř sloupce.

## WIP Limit

`NOW` v produktu neexistuje a nesmí se zobrazovat ani odvozovat.

WIP limit se týká sloupce `In progress` a počítá všechny úkoly v tomto sloupci
pro konkrétního assigneeho.

Pokud je limit nastavený na `3`, každý uživatel může mít v aktivním týmu nejvýše
3 své úkoly v `In progress`. Nejde o jednu společnou kapacitu celého týmu.

Při přesunu úkolu do `In progress` se ověří kapacita jeho assigneeho. Pokud je
limit plný, backend přesun odmítne a frontend zobrazí varování.

Stejná kontrola platí pro vytvoření úkolu rovnou v `In progress`. Změna assigneeho
úkolu, který už je v `In progress`, musí respektovat limit nového assigneeho.

V MVP je hodnota limitu společná konfigurační hodnota, ale její kapacita se
počítá samostatně pro každého assigneeho. Konfigurovatelný limit zvlášť pro každý
tým je budoucí team setting.

Pravidlo pro případný neassignee úkol v `In progress` je otevřené a musí být
definované před podporou takového stavu. Vytváření úkolu bez assigneeho se běžně
nepředpokládá, protože nový úkol se standardně přiřadí jeho tvůrci.

## Workflow

Workflow a povolené přechody určuje backend. Frontend nesmí nabízet přesuny,
které backend odmítne.

Pořadí stavů je:

```text
Backlog -> To do -> In progress -> Review -> Done
```

Nový úkol může být vytvořen pouze v `Backlog`, `To do` nebo `In progress`.

Při pohybu dopředu může úkol postoupit pouze o jeden platný krok. Úkol bez
povinného review může postoupit z `In progress` přímo do `Done`. Úkol, který
review vyžaduje, musí projít přes `Review`.

Pohyb dozadu může přeskočit více stavů. Přesun z `Review` zpět zvyšuje
`returned_count`; přesun z `Done` zpět zvyšuje `reopened_count`.

Přesun v rámci stejného sloupce mění pouze pozici, ne životní cyklus úkolu.

Aktuální backend řeší týmové pořadí pomocí pozice a cílové karty. Při konfliktu
nebo neplatném anchoru musí frontend načíst autoritativní stav znovu a nesmí
předpokládat, že část přesunu zůstala uložená.

Role reviewer/admin a jejich oprávnění nejsou v MVP dokončené. Dashboard proto
zatím zobrazuje a používá pouze workflow pravidla, která skutečně poskytuje
backend.

Blokované úkoly, blocker workflow a blocker filtry neexistují.

## Lokální Pohled A URL

Aktivní filtry, vybrané layers, `My tasks`, sort a otevřený detail úkolu patří do
stavu konkrétního uživatele a prohlížeče.

Autoritativním místem aktivního pohledu je URL. URL může obsahovat identifikátor
aktivního týmu nebo workspace, query parametry pohledu a identifikátor otevřeného
úkolu.

Změna lokálního pohledu aktualizuje URL pomocí náhrady aktuální historie, aby
každé kliknutí na filtr nevytvářelo nový krok v historii prohlížeče.

URL stav slouží pro obnovení stránky a navigaci zpět/vpřed. Není to náhrada za
backendovou autorizaci. Backend vždy ověřuje aktivní tým a členství.

`localStorage` slouží pouze pro osobní výchozí preference, například:

- výchozí sort,
- výchozí sbalené sloupce,
- jiné drobné preference zobrazení.

Tyto preference jsou lokální pro uživatele a prohlížeč, ideálně oddělené podle
aktivního týmu. Nejsou týmovým datovým stavem.

Při načtení stránky se nejprve respektuje pohled z URL. Local storage může dodat
výchozí hodnotu jen tehdy, když ji URL neurčuje.

Chování filtrů a sortu při přepnutí na jiný tým je ještě otevřené. Nový Kanban se
načte vždy; filtry, které odkazují na členy nebo layers z původního týmu, se
nesmí slepě přenést.

## Synchronizace

Změny ostatních uživatelů se musí v Kanbanu projevit bez ručního reloadu stránky.
MVP používá periodický polling, nikoliv WebSockety.

Polling v MVP:

- po otevření dashboardu načte úkoly aktivního workspace,
- přibližně každých 5 sekund načte aktuální týmová data znovu,
- při návratu do viditelné záložky provede okamžitý refresh,
- při skryté záložce se zastaví nebo omezí,
- po každé vlastní mutaci může použít optimistickou aktualizaci,
- po potvrzení serverem zachová autoritativní data,
- po chybě nebo konfliktu načte stav z backendu znovu.

Polling znovu načítá týmová data, nikoliv celou HTML stránku. Po každém načtení
se znovu použije lokální filter, layer a sort aktuálního uživatele.

Backendová funkce `move_task` řeší souběžné přesuny a vrací konflikt, pokud je
požadavek neplatný vůči aktuálnímu stavu. Frontend při takovém konfliktu kartu
vrátí nebo opraví podle serverové odpovědi, zobrazí varování a provede refetch.

### SSE po MVP

SSE, Server-Sent Events, je jednosměrné dlouho otevřené HTTP spojení:

```text
Browser otevře EventSource
Server nechá HTTP spojení otevřené
Server po změně úkolu odešle event do připojených browserů
Browser načte aktuální data nebo aktualizuje store
```

Klient dál posílá vytvoření, úpravy a přesuny běžnými HTTP požadavky. SSE pouze
posílá události ze serveru ke klientovi. Není to WebSocket.

SSE je vhodný další krok, pokud bude polling příliš pomalý nebo nákladný. Není v
MVP, protože současný backend nemá event endpoint ani distribuci událostí.

## Načítání A Chyby

Načítání tasků používá globální skeleton pro karty. Ostatní lokální akce mohou
zobrazovat vlastní loading spinner.

Pokud načtení dat selže, MVP zobrazí jednoduché chybové upozornění. Prozatím je
přijatelný `console.error` a `alert`; samostatný systém toastů není podmínkou.

Přesun nebo jiná mutace používá optimistické UI. Při odmítnutí serverem se stav
vrátí na autoritativní serverovou hodnotu a uživatel dostane varování.

## Backendový Kontrakt

Dashboard musí respektovat aktuální backendový kontrakt:

- seznam úkolů je vždy omezený na jeden aktivní tým/workspace,
- backend kontroluje členství a přístup,
- úkoly se vracejí v týmovém pořadí podle stavu a pozice,
- přesun používá samostatný move endpoint,
- `TaskUpdate` nemění status ani pozici,
- status a pozice se mění přes workflow move,
- WIP překročení vrací konflikt,
- neplatný přechod nebo anchor vrací chybu,
- klient má po konfliktu refetchovat data.

Současný backend má na `Task` jedno textové pole `layer`, zatímco schválené
produktové chování vyžaduje mnoho layers. Multi-layer funkcionalita proto není
kompletní, dokud nebude backendový model, API a databázový kontrakt upravený na
vztah tasku k více týmovým layer entitám.

Současný backend také počítá `In progress` kapacitu za celý tým. Požadované MVP
chování je kapacita samostatně pro každého assigneeho, takže backendové pravidlo
musí odpovídat této specifikaci dříve, než bude WIP limit považovaný za hotový.

## Mimo MVP

Následující funkce nejsou součástí první verze dashboardu:

- funkční textové vyhledávání,
- obecné klávesové ovládání a navigace šipkami,
- přímé klávesové přesuny `Shift + šipky` a `Shift + 1–5`,
- hromadný výběr a přesun karet,
- context menu karty,
- hover quick actions,
- komentáře, přílohy, subtasks a activity history,
- Inbox a jeho badge v navigaci,
- uložené nebo oblíbené filtry,
- mobilní rozhraní,
- SSE synchronizace,
- role-based authorization,
- týmové pozvánky,
- vytváření a správa týmů včetně administrátorských team settings,
- samostatný WIP limit pro každý tým,
- nastavitelný výchozí stav nových úkolů,
- další moduly v `NavMenu`.

## Otevřené Detaily

Tyto body nejsou zatím uzavřené a nesmí být skrytě domyšlené v komponentách:

- zda se při přepnutí týmu resetuje sort a filtry, nebo se obnoví poslední lokální
  preference daného týmu,
- přesný směr řazení podle due date a umístění úkolů bez due date,
- pravidlo pro neassignee úkol v `In progress`,
- zda má sdílení URL s lokálním pohledem být oficiálně podporovaným use casem,
- přesný vizuální limit počtu řádků popisu na kartě.

## Provozní Kontext

Pro spolupráci musí aplikace běžet na serveru dostupném ostatním uživatelům a
musí sdílet backend i databázi. Doména není technicky povinná, protože lze použít
veřejnou IP adresu nebo privátní síť, ale pro reálný self-hosted provoz se
doporučuje doména s HTTPS.

`localhost` je vhodný pro lokální vývoj, ne pro spolupráci uživatelů na různých
zařízeních.

