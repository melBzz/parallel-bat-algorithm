### Notes de lecture – Paper sur les algorithmes métaheuristiques  

Le paper traite des **algorithmes métaheuristiques**, un type d’algorithmes d’optimisation.  

**D’après Wikipédia :**  
Une *métaheuristique* est un algorithme conçu pour résoudre des **problèmes d’optimisation complexes** — souvent issus de la recherche opérationnelle, de l’ingénierie ou de l’intelligence artificielle — pour lesquels il n’existe **aucune méthode classique plus efficace**.  

Un **algorithme**, par définition, est une suite d’instructions permettant d’obtenir un résultat à partir de données en entrée. Il sert à **résoudre un problème** ou à **accomplir une tâche spécifique**.  

À ce stade, on se pose deux questions importantes se posent :  
1. **Quelles sont les entrées d’un algorithme métaheuristique ?**  
2. **Qu’est-ce qu’on cherche à optimiser dans le cadre de notre projet ?**

---

The Bat Algorithm  
Le paper explique :  
> “We also intend to combine the advantages of existing algorithms into the new bat algorithm.”  

Donc, **le Bat Algorithm** cherche à **combiner les avantages** de plusieurs algorithmes existants.  

---

### Inspirations biologiques et physiques  
> “The vast majority of heuristic and metaheuristic algorithms have been derived from the behaviour of biological systems and/or physical systems in nature.”  

Autrement dit, la majorité de ces algorithmes s’inspirent de la **nature** ou de **phénomènes physiques**.  
Une nouvelle question se pose :  
➡️ *Comment traduit-on mathématiquement le comportement d’animaux (comme les oiseaux) ?*

---

### Les algorithmes cités dans le paper  

**1. PSO (Particle Swarm Optimization)**  
→ Inspiré du comportement collectif des oiseaux et des poissons.  
Chaque individu apprend à la fois de sa propre expérience et de celle des autres, puis **se déplace collectivement vers une meilleure solution**.  

**2. Simulated Annealing (SA)**  
→ Inspiré du **recuit des métaux** en métallurgie : on chauffe un métal puis on le refroidit lentement pour atteindre un **état d’énergie minimale**.  
En optimisation, cela revient à **explorer des solutions** puis à **se stabiliser progressivement** vers la meilleure.  

**3. Harmony Search**  
→ Inspiré de l’**improvisation musicale** : les musiciens testent différentes “notes” jusqu’à obtenir une harmonie agréable.  
En optimisation, cela revient à **tester plusieurs combinaisons de variables** pour trouver la plus “harmonieuse” (la meilleure solution).  

**4. Firefly Algorithm**  
→ Inspiré du **comportement lumineux des lucioles**.  
Chaque luciole représente une solution ; plus une solution est “brillante” (meilleure), plus elle **attire les autres**.  

---

### Objectif du paper  
> “Each of these algorithms has certain advantages and disadvantages [...] A natural question is whether it is possible to combine major advantages of these algorithms and try to develop a potentially better algorithm? This paper is such an attempt to address this issue.”  

Chaque algorithme a **ses points forts et ses points faibles**. (lequels ? une étude des autres algorithmes peut être intéréssante) 
L’objectif du paper est donc de **s’inspirer de l’écholocalisation des chauves-souris** pour **combiner les principaux avantages** de ces approches et créer un **algorithme potentiellement plus performant**.  


### L’écholocation 

"Microbats use a type of sonar, called echolocation, to detect prey, avoid obstacles, and locate their roosting crevices in the dark. These bats emit a very loud sound pulse and listen for the echo that bounces back from the surrounding objects."

Les micro-chauves-souris utilisent un sonar appelé **écholocation** pour repérer leurs proies, éviter les obstacles et trouver leurs abris dans le noir.  
Elles envoient une **impulsion** (un cri fort) et écoutent **l’écho** qui revient des objets autour d’elles.  

"Each pulse only lasts a few thousandths of a second (up to about 8 to 10 ms) [...] frequency [...] 25kHz to 150kHz."

Chaque impulsion dure **quelques millisecondes** (8 à 10 ms) avec une **fréquence très élevée**, large au-dessus de ce que l’oreille humaine peut entendre (environ 20 kHz).  

"Microbats emit about 10 to 20 such sound bursts every second [...] can speed up to about 200 pulses per second when they fly near their prey."  
"Such short sound bursts imply the fantastic ability of the signal processing power of bats [...] integration time of the bat ear is typically about 300 to 400 µs."

Elles émettent **10 à 20 impulsions par seconde**, mais montent jusqu’à **200** quand elles s’approchent de leur proie.  
C’est possible grâce à leur **ouïe très fine** : leur cerveau analyse un écho en **300 à 400 microsecondes** (soit environ 0,0003 s).  

---

### Calcul de la longueur d’onde λ  

On sait que la **vitesse du son** est :  
v = 340 m/s  

et que la **fréquence des ultrasons** des chauves-souris varie entre **25 kHz et 150 kHz**.  

On peut calculer la **longueur d’onde** avec la formule :  
λ = v / f  

---

**Pour 25 kHz :**  
λ = 340 / 25 000 = 0.0136 m = **13.6 mm**  

**Pour 150 kHz :**  
λ = 340 / 150 000 = 0.0023 m = **2.3 mm**  

---

### Interprétation  

Plus la fréquence est **grande**, plus la longueur d’onde est **petite**.  
Autrement dit :  
- sons aigus → ondes petites  
- sons graves → ondes longues  

Chez les chauves-souris, les sons qu’elles émettent ont une longueur d’onde entre **2 et 14 mm**, soit à peu près la taille de leurs **proies (insectes)**.  
Du coup, les ondes rebondissent dessus et leur permettent de **les localiser précisément**.  

### L’intensité et la précision de l’écholocation 🦇  

"Amazingly, the emitted pulse could be as loud as 110 dB [...]. The loudness also varies from the loudest when searching for prey and to a quieter base when homing towards the prey."

En gros, elles crient de zinzin, genre au niveau sonore d’un marteau-piqueur (≈110 dB).  
Quand elles **cherchent une proie**, elles crient fort pour détecter plus loin.  
Mais quand elles **se rapprochent**, elles **baissent le volume** pour obtenir une détection plus fine et éviter de saturer leurs oreilles.  

---

"Studies show that microbats use the time delay from the emission and detection of the echo, the time diﬀerence between their two ears, and the loudness variations of the echoes to build up three dimensional scenario of the surrounding."

Les chauves-souris mesurent le **temps entre l’émission d’un son et le retour de l’écho**.  
Ce délai leur permet de **calculer la distance** d’un objet, un peu comme un **sonar**.  

Formule :  
distance = (v × t) / 2


avec :  
- v = vitesse du son (≈ 340 m/s)  
- t = temps entre l’émission et la réception (divisé par 2 car le son fait un aller-retour)

---

Elles ont aussi **deux oreilles ultra sensibles** qui captent une toute petite différence de temps entre le son perçu à gauche et à droite.  
Cette différence leur permet de **déterminer la direction précise** du son.  

Elles utilisent ensuite les **variations d’intensité** de l’écho pour estimer :  
- la **taille**,  
- la **forme**,  
- et la **texture** de la cible.  

En combinant **temps**, **direction** et **intensité**, elles se construisent une **carte mentale en 3D** de leur environnement.  
Elles sont grave boosté carrement elle peuvent éviter des obstacles de la taille d’un cheveu humain?

---

Elles peuvent donc :  
- calculer la **distance** et la **direction** d’une proie,  
- distinguer le **type d’insecte**,  
- mesurer sa **vitesse de mouvement**.  

---

"Indeed, studies suggested that bats seem to be able to discriminate targets by the variations of the Doppler effect induced by the wing-flutter rates of the target insects."

Le **Doppler effect** correspond au changement de fréquence d’un son quand la source bouge :  
- si la proie **s’approche**, la fréquence perçue devient **plus haute**,  
- si elle **s’éloigne**, la fréquence devient **plus basse**.  

Les chauves-souris sont capables de détecter ces **minuscules variations de fréquence**, ce qui leur permet de savoir **si un insecte bouge**, **à quelle vitesse** et **dans quelle direction**.  


### Le Bat Algorithm 

On fait ici des **hypothèses simplificatrices** sur le comportement réel des chauves-souris.  
À partir de ces simplifications, on peut développer **plusieurs variantes** du *Bat Algorithm*.  

---

➡️ **Chaque chauve-souris :**  
- peut **mesurer les distances** grâce à l’écholocalisation ;  
- et est capable de **reconnaître une proie** (la bonne solution) parmi le **bruit** de l’environnement (les mauvaises solutions).  

**En algorithmique :**  
- chaque chauve-souris évalue la **qualité de sa solution** (*fitness function*) ;  
- et sait si elle se rapproche du **but** (*optimum global*).  

---

À **chaque itération**, la chauve-souris peut :  
- **ajuster sa fréquence** → changer la manière dont elle explore l’espace de recherche ;  
- **modifier son taux d’émission de pulses**  
 r ∈ [0,1]
  selon sa proximité avec la cible (la bonne solution).  

---

Donc :  
- si elle est **loin de la proie** → elle **explore plus largement**  
  (vitesses élevées, sons forts, faibles fréquences) ;  
- si elle est **proche** → elle **se déplace moins**, **émet plus souvent**, et devient **plus précise**.  

---

Dans la réalité, le **volume** des ultrasons change de façon complexe,  
mais ici, on simplifie :  

- au **départ** :  
  A0 = fort (la chauve-souris cherche loin)

- à la **fin** :  
  Amin = faible (elle s’approche du but)
















"Amazingly, the emitted pulse could be as loud as 110 dB [...]. The loudness also varies from the loudest when searching for prey and to a quieter base when homing towards the prey."

Bref elle crie de zinzins genre même niveau de bruit qu'un marteau piqueur.
Quand elles cherchent une proie elle crient fort pour detecter plus loin. Quand elles se rapprochent d'une proie elles baissent de volume (pour détecter de manière plus précise).

"Studies show that microbats use the time delay from the emission and detection of
the echo, the time diﬀerence between their two ears, and the loudness variations of the
echoes to build up three dimensional scenario of the surrounding. "

En gros les chauves-souris mesurent le temps entre le moment où elles émettent un son et le moment où l’écho revient. 
Ce temps de retour leur donne la distance jusqu’à l’objet (comme un sonar).t
 Formule :

distance=v×t2
distance=
2
v×t
	​


où 
v
v = vitesse du son, 
t
t = temps entre émission et réception (divisé par 2 car le son fait un aller-retour).
Les chauves-souris ont deux oreilles ultra sensibles, et elles détectent une minuscule différence de temps entre l’arrivée du son à gauche et à droite.
Cela leur permet de déterminer l’angle (la direction exacte) d’où vient le son.
Elles utilisent aussi les variations d’intensité de l’écho pour estimer la taille, la forme et la texture de la cible.
En combinant temps, direction et intensité, elles se créent une carte mentale 3D de leur environnement. 
Elles sont booster de dingues carrement elles peuvent éviter des obstacles de la taille d'un cheveux humain !!

Elles peuvent : 
calculer la distance et la direction de la proie,

distinguer le type d’insecte,

mesurer sa vitesse de mouvement 

"Indeed, studies suggested that bats seem to be able to discriminate targets by the variations of the Doppler effect induced by the wing-flutter rates of the target insects."

le Doppler effect est le changement de fréquence d’un son quand la source bouge

quand la proie s’approche → fréquence perçue plus haute,

quand elle s’éloigne → fréquence plus basse.

Les chauves-souris utilisent ces variations minuscules pour savoir si un insecte bouge, à quelle vitesse, et dans quelle direction.


















L'echolocation

" Microbats use a type of sonar, called, echolocation,
to detect prey, avoid obstacles, and locate their roosting crevices in the dark. These bats
emit a very loud sound pulse and listen for the echo that bounces back from the surrounding objects. "

“Each pulse only lasts a few thousandths of a second (up to about 8 to 10 ms) [...] frequency [...] 25kHz to 150kHz.”

Chaque impulsion (cri) d'une chauve souris dure quelques milisecondes (de 8 à 10ms) avec une dréquence très élévé (bien au dessus de ce qu'entends l'oreille humaine qui est environnt 20kHz). 

"Microbats emit about 10 to 20 such sound bursts every second [...] can speed up to about 200 pulses per second when they fly near their prey. "
"Such short sound bursts imply the fantastic ability of the signal processing power of bats [...] integration time of the bat ear is typically about 300 to 400 µs"


Elles font 10 à 20 impulsions par secondes, mais augmentent à 200 lorqu'elles se rapprochent de leur proie. Cela est en partie possible grâce à leur oui tres fine : leur cerveau analyse un écho en 300 à 400 microsecondes (0,0003 s). 

Sachant la vitesse du son v= 340m/s
f, la frequence des impulsion d'une chauves-souris 
on peux calculer lambda (λ) la longeur d'onde grâce à la formule : 

λ=v/f

D'après la formule lus la fréquence (f) est grande, plus la longueur d’onde (λ) est petite.
Autrement dit Des sons très aigus produisent des ondes petites.
Des sons graves, des ondes plus longues.

Pour les chauves souris, 

La fréquence de leurs ultrasons varie entre 25 000 Hz (25 kHz) et 150 000 Hz (150 kHz).
On calcule :

Pour 25 kHz :

λ=34025 000=0.0136 m=13.6 mm
λ=
25000
340
	​

=0.0136m=13.6mm

Pour 150 kHz :

λ=340150 000=0.0023 m=2.3 mm
λ=
150000
340
	​

=0.0023m=2.3mm


La longueur d’onde des sons qu’elles émettent (2 à 14 mm) est de la même taille que leurs proies (petits insectes). Donc les ondes bont "rebondir" dessus et leur permettre de les localisé.
















same input size -> fill with 0 
et inversisement si trop petit skip the first n packet (le reste jeté)

si n=5 ou 100 trade off -> accuracy pas si différente dans certains cas ou peux préferer n=5


convolutional layer, filter move seulement à la vertical 

h'=(n-h+2P (padding) / s ) +1 (avec 2p =0)

ref slide petit carré -> on passe 1 fois ? si le minimum c'est la taille du filtre (et le max n), et qu'on bouge verticalement ? on bouge aussi verticalement sur le petit carrré ?? je croyais qu'on jetait à la poubelle 


grey -> padding part 
le filtre move partout (même sur le padding) -> en fait il comprends lui même que y'a du padding ?? a force de passer et de trouver des 0 à un certains points 