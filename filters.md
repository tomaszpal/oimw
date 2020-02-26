Do odfiltrowywania trywialnych ruchów zastosowano osiem kolejnych filtrów:

- is_only_possible() - przez ten filtr przechodzą jedynie te ruchy, które nie były jedynymi możliwymi ruchami w danej sytuacji.
- is_variant_loss() - przez ten filtr przechodzą jedynie te ruchy, które nie prowadzą bezpośrednio do przegranej gry.
- is_variant_end() - przez ten filtr przechodzą jedynie te ruchy, które w krótkim wariancie prowadzą do końca gry. Ruchy, które w kilku akcjach prowadzą do końca gry mogą zostać łatwo zauważone przez człowieka i nie stanowią ciekawego elementu.
- is_insufficient_material - jest to filtr, który zapobiega wypisywaniu jako ciekawych ruchów, których dalsza sekwencja nie jest w stanie doprowadzić do wygrania partii.
- is_lomonosov_endgame() - jest to filtr, który zapobiega wypisywaniu jako ciekawych ruchów, które są zawarte w tablicach końcówek (w grze znajduje się mniej niż 8 figur).
- min_centipawn_filter() - filtr, przez który przechodzą pozycje, w których najlepszy ruch jest co najmniej lepszy o zadaną wartość od drugiego najlepszego ruchu
- is_material_gain() - przez ten filtr przechodzą jedynie te ruchy, które nie prowadzą do prostego zyskania materiału (figura o mniejszej wartości bije figurę o większej wartości).
- is_fork() - przeze ten filtr przechodzą jedynie te ruchy, których głównym celem nie było jedynie założenie tzw. widełek, ponieważ jest to ruch prosty do zauważenia przez człowieka.