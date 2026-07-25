# Residual Risks

- **Enum revision commits before normalization.** Selhání druhé migrační revize zanechá `BACKLOG` v nativním enumu bez změny aplikačního chování. `IF NOT EXISTS` umožňuje opakovaný běh; stará aplikace zůstává kompatibilní se starými řádky.

- **Rebalance je `O(n)` zápis nad jedním cílovým sloupcem.** Akvizuje řádkové zámky přes jednotlivé UPDATE. Explicitní celosloupcový zámek byl záměrně odmítnut.

- **Count-based `IN_PROGRESS` kapacita.** Současná kontrola `_has_in_progress_capacity` používá count-then-write, takže konkurenční přesuny do `IN_PROGRESS` mohou oba projít kapacitní kontrolou. Sémantika zůstává zachována z existujícího kódu a není serializována zámkem.

- **Neznámá verze PostgreSQL serveru.** Při plánování nebyla dostupná živá instance PostgreSQL na nakonfigurované URL, takže aktuální revize a distribuce dat nebyly ověřeny.

- **Disposable PostgreSQL migrační validace nebyla spuštěna.** Před nasazením spustit `alembic upgrade head` proti testovací databázi pro ověření kompozice obou migračních revizí s produkčním schématem.

- **Chybí automatické retry kolizí.** Konkurenční midpoint kolize a kolize pozic vracejí `409`. Klient musí refetchovat autoritativní stav boardu před opakováním; backend neretryuje automaticky.

- **Zdrojový sloupec není kompaktován.** Mezery po přesunutých úkolech zůstávají v původním sloupci a nespouští normalizaci.
