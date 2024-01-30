# Project idea

## Flowchart of Savings Manager

![[Diagram.svg]]

# Description of the app

Es soll eine Webapp programmiert werden, die helfen soll, regelmäßige Sparbeträge (in der Regel einmal monatlich) auf ein physikalisches Geldkonto (z.B. einem Tagesgeldkonto) zu verwalten.

Sprich: es besteht der Wunsch, dass der Sparbetrag, der auf dem Konto landet, in virtuelle Konten (Kassen) verteilt wird. Diese Kassen dienen zur Organisation der gesamten Sparsumme und soll dem Sparer die Möglichkeit bieten, sich eigene Sparziele zu setzen, die er sich durch die einzelnen Kassen verwirklicht.

Somit kann (optional) jeder Kasse ein Sparziel festgelegt werden. Ist dieser erreicht, soll diese Kasse nicht weiter bespart werden. Jeder Kasse muss ein gewünschter Sparbetrag festgelegt werden, der dazu dient, den monatlich eingesparten Betrag mit dieser festgelegten Sparhöhe zu belasten und der jeweiligen Kasse gutzuschrieben. Dieser Vorgang gilt für alle angelegten Kassen, die mit ihren individuellen Sparwünschen von der eingezahlten Sparsumme zehren. Welche Kasse zuerst bespart werden soll, legt eine Prioritätenliste fest. Jede Kasse erhält eine eigene, individuelle Gewichtung und ordnet sich somit linear in der Prioritätenliste ein. Ist nach allen Abzügen der Kassen-Sparwünsche (durch Ablaufen der Prioritätenliste) vom Sparbetrag ein Restbetrag übrig, landet dieser monatliche Sparbetrag in der "Reste-Kasse". Die Reste-Kasse steht immer am Ende der Prioritätenliste. Diese Kasse ist immer vorhanden, hat keinen Sparwunsch und keinen Sparziel. Er dient als Sammelbecken für die Beträge, die in einem Sparmonat nicht komplett verteilt werden konnten (über die Sparwünsche der Kassen). 

Die Summe aller Beträge in allen Kassen (inklusive Restekasse) entspricht der Guthabens auf dem physikalischen Bankkonto oder kleiner. Die Summe der App darf die Summe auf dem physikalischen Konto nicht überschreiten.

## Requirements

- Ein physikalisches Sparkonto ist in virtuelle Konten unterteilt (Kassen), die in der App verwaltet werden. Das physikalische Konto wird zyklisch (standardmäßig monatlich) mit einer einzigen Sparsumme bespart. Dieser Sparbetrag verteilt sich jedoch virtuell in den existierenden Kassen (verwaltet in der App). Die Höhe der monatlichen (zyklischen) Sparsumme in den jeweiligen Kassen (Summe der Verteilung) legen die Kassen selbst fest und die Reihenfolge des Besparens der Kassen eine Prioritätenliste.

- Die Anwendung muss initial einen Sparbetrag definiert bekommen. Dieser wird automatisiert, zyklisch, zu einen festgelegten Zeitpunkt in die Kassen automatisch verteilt (verrechnet). Nach Ablauf der Verteilung wird der neue Zustand der Kassen samt ihrer Einsparungen in diesem Zyklus protokolliert. Der Sparbetrag kann vom Benutzer jederzeit neu festgelegt werden. Der Sparbetrag Muss größer als 0 sein (mindestens 1 Cent.)

- Eine Prioritätenliste beinhaltet Kassen. Mindestens eine Reste-Kasse, die immer am Ende der Liste steht. Alle anderen zusätzlichen Kassen, werden höher priorisiert, das heißt sie stehen weiter vorne in der Liste. Keine Kasse ist gleich priorisiert, die Liste ist linear.

- Die Reste-Kasse ist eine spezielle Kasse und dient zum Aufsammeln nicht verteilter Sparbeträge. Diese Kasse hat keinen Sparziel und keinen Spar-Wunsch-Betrag.

- In der App kann eine Kasse angelegt, gelöscht oder deaktivier und reaktiviert werden. Sie kann mit einem Sparziel und einem Spar-Wunsch-Betrags belegt werden. Das Sparziel ist optional. Jede Kasse muss allerdings über ein Spar-Wunsch-Betrag verfügen. Dieser Betrag entscheidet, maximal wieviel vom monatlichen Sparbetrag in dieser Kasse in der Spariteration (Sparzyklus) landet. Wenn der zyklische Sparbetrag kleiner ist, als die Kasse abzweigen möchte, wird der kleinere Betrag entnommen. Eine Kasse kann über eine Obergrenze verfügen (Sparziel), dieser Wert ist optional. Werte des Sparziels und Wunsch-Spar-Betrags müssen >= 0 sein. Ist Sparwunschbetrag 0, gleicht es einer inaktiven Kasse und soll dem Nutzer als solches signalisiert werden.

- Aus jeder Kasse soll zu jederzeit ein gewünschter Betrag abgehoben oder in eine andere Kasse verschoben werden können, inklusive Reste-Kasse, auch hier sind Ein-, Auszahlungen und Verschiebungen in und aus der Reste-Kasse möglich.  Es ist nicht möglich, Schulden in den Kassen zu erzeugen. Das Minimumbetrag jeder Kasse (auch der Restekasse) ist 0. Für die Einzahlung gilt: Einzahlungen sind unabhängig des Wunsch-Spar-Betrags und des Sparziels der jeweiligen Kasse (Übersparen hier möglich). Für die Verschiebung gilt: Beträge können zwischen Kassen verschoben werden (was einer Abhebung aus Kasse X und Einzahlung in Kasse Y entspricht). Beträge werden auf den Cent genau verteilt. Die Wunsch-Sparbeträge der Kassen sind Cent genau. Beispielangeben: 150,00 € oder 101,42 €.

- Kassen sollen deaktiviert werden können, was dazu führt, dass sie nicht mehr bespart werden, bis sie wieder aktiviert sind.

- Die Anwendung soll zur Organisation des eigenen Sparens dienen und nicht einschränken und nicht erzwingen. Wenn gewünscht, soll jede Kasse manuell über sein Sparziel hinaus bespart werden können. Das "automatisierte" Besparen soll aber diese definierten Werte einhalten. Negativbeträge sollen in keiner Kasse möglich sein.

- Die Summe aller Beträge aller Kassen muss dem Betrag auf dem physikalischen Konto gleichen, zumindest darf die Summe dem Guthaben auf dem physikalischen Sparkonto nicht überschreiten. Eine Unterschreitung ist denkbar. Eine Überschreitung stellt einen invaliden Zustand dar und weist auf einen Anwendungsfehler hin. Jede Aktion soll geloggt werden (manuelles abheben und einsparen, automatisiertes Besparen, Verschieben von Beträgen etc.). Die Logs sollen dem Entwickler, aber auch dem Anwender, dabei helfen, jeden Zustand der App nachvollziehen zu können.

- Sparzyklus: immer zum 1. jeden Monats, einmalig. Dieser Zeitpunkt soll vom Anwender aktuell nicht änderbar sein. Manuell kann jederzeit gespart werden, jedoch dann in eine bestimme Kasse und NICHT in die "Sparkette", die der Sparzyklus es tut. Sie Sparzyklen müssen geloggt werden, sodass bei Zeitsprünge der App in die Vergangenheit keine Sparzyklen erneut durchgeführt werden. Ein Sprung in die Zukunft - oder einfach weil die App lange nicht ausgeführt wurde - soll verpasste Sparzyklen mit der derzeitigen Sparsumme, die in der App konfiguriert ist nachholen, sofern der Anwender keine expliziten Angaben macht. Ihm soll es grundsätzlich möglich sein, die verpassten Zyklen angezeigt zu bekommen, eher ein Nachrechnen erfolgt. In dieser Auflistung soll es dem Anwender möglich sein, für jeden Monat individuelle Sparbeträge anzugeben.

- Für die Reste-Kasse gibt es zwei Modi: ist in der Reste-Kasse ein Betrag vorhanden, wird dieser in Modus 1 auf den Sparbetrag des aktuell ausgeführten Sparzyklus (immer zum 1.) aufaddiert und im Sinnen der Prioritätenliste mit verteilt, als wäre der Sparbetrag in diesem Monat höher, als sonst. Modus 2: Sobald in der Reste-Kasse ein Betrag landet, wird der Betrag vollständig in der ersten Kasse aus Prioritätenliste eingezahlt, bis sein Sparziel erreicht ist. Ein Überschreiten des Sparziels ist hierbei nicht gewünscht. Wird der Betrag aus der Reste-Kasse nicht gänzlich in die erste Kasse aufgebraucht, landet der restliche Betrag in der nächsten Kasse der Prioritätenliste usw. Modus 3: die Reste-Kasse füllt sich und der Betrag aus der Reste-Kasse wird im Sparzyklus nicht angerührt, d.h. kein Aufbrauchen der Reste-Kasse.

- Der Nutzer hat jederzeit die Möglichkeit die Logs/Protokolle einzusehen. Ein Export in ein Dateiformat ist zum aktuellen Zeitpunkt kein Bestandteil der App.


### Questions

