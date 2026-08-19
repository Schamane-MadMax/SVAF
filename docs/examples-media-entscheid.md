# Warum es (noch) kein examples/ mit echtem Audio gibt

**Entscheidungsnotiz, 2026-08-19.** Ein `examples/`-Ordner mit einer echten
Beispiel-Session ist gewollt, aber bewusst zurückgestellt. Diese Notiz hält
fest, welche Quellen geprüft wurden und woran sie gescheitert sind, damit die
Prüfung nicht wiederholt werden muss.

Die Regeln aus [CONTRIBUTING.md](../CONTRIBUTING.md) (Abschnitt "Privacy and
Data Protection") und [RFC-0001 §11](rfcs/RFC-0001-core.md) gelten unverändert:
verifizierte Lizenz (CC0/CC BY), dokumentierte Consent-Basis für jede
erkennbare Person, keine Embeddings oder Face-Crops realer Personen.

## Geprüfte Quellen

**Öffentlich abrufbare Podcasts/Videocasts ("die sind doch für die
Öffentlichkeit bestimmt"):** verworfen. Öffentliche Abrufbarkeit ist keine
Nutzungslizenz — sie erlaubt das Anhören (§ 19a UrhG), nicht Vervielfältigung,
eigene Veröffentlichung oder Bearbeitung. Ein Transkript ist rechtlich eine
Vervielfältigung des Sprachwerks; Zitatschranke (§ 51 UrhG) und
TDM-Schranke (§ 44b UrhG) tragen eine dauerhafte Weiterverbreitung als
Beispieldatei nicht. Eine Stichprobe bekannter deutscher und englischer
Podcasts ergab zudem: Die meisten tragen gar keine freie Lizenz, die übrigen
fast immer NC- oder ND-Varianten (schließen Bearbeitung bzw. kommerzielle
Nachnutzung aus) oder Share-Alike (würde die abgeleiteten Beispieldaten
copyleft-infizieren, siehe unten).

**CC-BY-Podcasts mit bekannten Sprechern:** verworfen, auch bei sauberer
Lizenz. Eine CC-Lizenz regelt nur das Urheberrecht, ausdrücklich nicht
Persönlichkeits- und Publicity-Rechte (CC BY 4.0 Sec. 2(b)(1)). Bekannte
Stimmen haben einen geschützten Vermarktungswert (BGH-Linie "Marlene
Dietrich"); ein Projekt, das mit erkennbaren Prominentenstimmen wirbt,
braucht deren Einwilligung unabhängig von der Lizenz. Dazu kommt ein
Spec-eigenes Problem: Bei bekannten Stimmen sind Pseudonym-IDs wirkungslos —
die Stimme identifiziert die Person, das Beispiel bliebe personenbezogen
(genau der Fall aus RFC-0001 §11.3 zu Recital 26). Ein Löschbegehren nach
Art. 17 DSGVO ist gegen Git-Historie, Forks und Paket-Registries praktisch
nicht erfüllbar; eine Pflicht, die man nicht erfüllen kann, lässt man nicht
entstehen.

**NASA-Material:** verworfen (Publicity-Rights der abgebildeten Personen
kollidieren mit der freien Nachnutzbarkeit).

**media.ccc.de:** nur mit Lizenzprüfung je Talk; viele Talks sind CC BY-SA.
Share-Alike würde Audio-Ausschnitt und Transkript erfassen und `examples/`
zu einer Copyleft-Insel machen, deren Inhalte nicht mehr frei als
Test-Fixtures in beliebige Werkzeuge übernommen werden könnten. Als
Referenz-Beispiel damit ungeeignet.

## Gangbare Wege (wenn das Thema wieder aufgenommen wird)

1. **Eigenaufnahme unter CC0**: zwei einwilligende Sprecher, ca. 90 Sekunden
   Gespräch mit echten Sprecherwechseln und Overlap; schriftliche
   Einwilligung dokumentiert. Kein Lizenz- und kein Persönlichkeitsrisiko,
   und `privacy.consent: "given"` wäre ehrlich belegbar.
2. **AMI Meeting Corpus** (CC BY 4.0, University of Edinburgh / AMI
   Consortium): für Forschung erhobene Meeting-Aufnahmen mit dokumentiertem
   Teilnehmer-Consent; erfordert eine kostenlose Registrierung. Auflagen:
   kurzer Ausschnitt plus abgeleitete Daten mit Pseudonym-IDs, keine
   Embeddings/Face-Crops, `examples/LICENSE` mit CC-BY-Volltext,
   `examples/NOTICE` mit Attribution und Änderungshinweis, Abgrenzung
   "Code/Spec MIT, examples CC BY 4.0" im Root-README.
3. Nur nachrangig: ein CC0/CC-BY-Podcast **ohne** prominente Sprecher und
   **ohne** Gäste (alle Sprecher müssen zugleich die Lizenzgeber sein),
   Lizenz an der Originalquelle verifiziert und archiviert, kurzer, inhaltlich
   neutraler Ausschnitt ohne Musik/Jingles, Klarnamen nirgends in den
   strukturierten Daten.

Auswahlkriterium für den Ausschnitt ist in allen Fällen der technische Wert
(Sprecherwechsel, Overlap, saubere Diarization-Referenz) — nicht der
Unterhaltungswert und nicht die Bekanntheit der Stimmen.
