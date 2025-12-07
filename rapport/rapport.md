# Introduction

Ce travail s'inscrit dans le cadre du programme EIT Digital et du cours High-Performance Computing for Data Science, ce projet vise à analyser en détail un algorithme d’optimisation, à en proposer une version séquentielle, puis à en développer une déclinaison parallélisée adaptée aux environnements HPC. Nous avons choisi d’étudier le Bat Algorithm, une métaheuristique bio-inspirée proposée par Xin-She Yang [[Yang, 2010]](https://arxiv.org/abs/1004.4170), dont le fonctionnement repose sur la modélisation du comportement d’écholocation des chauves-souris.
 L’objectif de cette première phase est de comprendre précisément son mécanisme interne, ses paramètres, et la manière dont il explore l’espace de recherche pour résoudre des problèmes d’optimisation dans lesquels les paramètres à ajuster appartiennent à un espace continu.

Les problèmes d’optimisation continue apparaissent dans de nombreux domaines scientifiques et industriels, et consistent à déterminer, parmi toutes les configurations possibles, celle qui minimise ou maximise une fonction objectif. La structure de cette fonction peut rendre la résolution non triviale, comme le soulignent Nocedal & Wright dans leur ouvrage de référence sur l’optimisation numérique [Numerical Optimization (2ᵉ éd.)](https://www.math.uci.edu/~qnie/Publications/NumericalOptimization.pdf).
 Plusieurs travaux de référence soulignent que les méthodes d’optimisation basées sur le gradient deviennent limitées lorsque la fonction objectif est **non dérivable**, **bruitée**, **non convexe** (donc susceptible de présenter plusieurs minima locaux), ou lorsque la **dimension du problème augmente**.  
Par exemple, Rios & Sahinidis (2013) expliquent que l’absence, l’imprécision ou l’inaccessibilité des dérivées rend les méthodes classiques « *of little or no use* » et montrent empiriquement que « *the ability [...] to obtain good solutions diminishes with increasing problem size* ».  
Ces observations, issues de leur revue approfondie de l’optimisation sans dérivées [Derivative-Free Optimization — A Review of Algorithms and Comparison of Software Implementations](https://scispace.com/pdf/derivative-free-optimization-a-review-of-algorithms-and-2qmveq3j89.pdf), motivent le recours à des approches métaheuristiques ou sans dérivées.  

En tant qu’approche stochastique, le Bat Algorithm intègre des mécanismes aléatoires lui permettant d’explorer efficacement l’espace de recherche. Son fonctionnement repose sur un équilibre entre exploration globale et exploitation locale, ce qui le rend adapté à l’optimisation de fonctions non linéaires ou comportant de multiples minima locaux.

#### Fonctionnement

Le Bat Algorithm repose sur la modélisation simplifiée du comportement d’écholocation des chauves-souris. Dans la nature, celles-ci émettent des impulsions ultrasonores dont la fréquence, l’intensité et le taux d’émission varient en fonction de la proximité d’une cible. Yang transpose ces mécanismes biologiques en concepts algorithmiques : chaque chauve-souris est représentée par une position dans l’espace de recherche, une vitesse associée, une fréquence d’exploration, une loudness (A) qui contrôle l’acceptation des nouvelles solutions, et un pulse rate (r) qui influence la transition entre exploration et exploitation. Au cours de l’itération, ces paramètres sont mis à jour de manière stochastique afin de simuler la manière dont une colonie se rapproche progressivement d’une zone optimale. L’algorithme séquentiel alterne ainsi génération de candidats, évaluation de la fonction objectif et ajustement adaptatif des paramètres pour guider la recherche vers la meilleure solution connue.

Les éléments suivants décrivent les principaux aspects de l’écholocation observés chez les microchauves-souris tels que présentés par Xin-She Yang [[Yang, 2010]](https://arxiv.org/abs/1004.4170).

Les microchauves-souris utilisent un sonar biologique appelé écholocation pour détecter leurs proies, identifier des obstacles et se repérer dans l’obscurité. Elles émettent de courtes impulsions ultrasonores et analysent l’écho renvoyé par les objets environnants. Ce mécanisme leur permet d’estimer avec précision la distance, la direction et la nature de la cible.

**Durée, cadence et fréquence des impulsions**

Chaque impulsion dure seulement quelques millisecondes (jusqu’à 8–10 ms) et présente une fréquence généralement comprise entre 25 kHz et 150 kHz (inaudible pour l’être humain, dont la plage auditive se situe entre environ 20 Hz et 20 kHz).  
En phase de recherche, les microbats émettent environ 10 à 20 impulsions par seconde, puis peuvent atteindre jusqu’à 200 impulsions par seconde lorsqu’elles se rapprochent d’une proie. Cette augmentation est rendue possible par leur système auditif, qui peut analyser un écho en 300 à 400 microsecondes (environ 0,0003 s).

**Intensité sonore et adaptation du signal**

Les impulsions peuvent atteindre 110 dB, un niveau sonore comparable à celui d’un marteau-piqueur. L’intensité n’est toutefois pas constante : lorsqu’elles sont éloignées de leur proie, les microbats émettent des signaux puissants afin d’augmenter leur portée de détection. À l’inverse, lorsqu’elles s’en approchent, elles réduisent progressivement l’intensité pour éviter la saturation auditive et améliorer la précision de la détection.

**Analyse de l’écho : distance, direction et caractéristiques de la cible**

À partir de l’écho réfléchi, les microchauves-souris sont capables d’extraire plusieurs types d’informations. Elles estiment d’abord la distance en mesurant le temps séparant l’émission et la réception du signal, selon la relation

$$
\text{distance} = v \cdot \frac{t}{2}
$$

où \(v\) est la vitesse du son et \(t\) le temps aller-retour de l’onde. Elles déterminent également la direction de la cible grâce à la très faible différence de temps d’arrivée du son entre leurs deux oreilles. Les variations d’intensité de l’écho leur permettent ensuite d’inférer certaines propriétés de l’objet, comme sa taille, sa forme ou sa texture. Enfin, les microbats sont capables de détecter le mouvement d’un insecte en analysant les variations de fréquence dues à l’effet Doppler, une fréquence plus élevée indiquant que la cible s’approche, et une fréquence plus basse qu’elle s’éloigne.

En combinant ces différentes informations, elles construisent une représentation tridimensionnelle de leur environnement et peuvent ainsi éviter des obstacles extrêmement fins, parfois de l’ordre du millimètre.



Le Bat Algorithm repose sur une modélisation simplifiée du comportement observé chez les microbats. Xin-She Yang formalise ce comportement à travers trois hypothèses principales afin d’en tirer un modèle mathématiquement exploitable pour l'optimisation [[Yang, 2010]](https://arxiv.org/abs/1004.4170) :

1. chaque bat virtuelle dispose d’un mécanisme d’évaluation de la qualité d’une position, analogue à la capacité des microbats à identifier une proie via l’analyse de l’écho ; cette évaluation est assurée dans l’algorithme par le calcul de la fonction objectif

2. les bats ajustent leur fréquence, leur vitesse et leur taux d’émission de pulses en fonction de leur proximité d’une solution potentiellement optimale, en analogie avec la modulation des impulsions observée lors de la chasse ;

3. la loudness diminue et le pulse rate augmente au fil des itérations, ce qui modélise le passage d’une phase d’exploration globale à une recherche plus locale autour des meilleures solutions.

Dans ce modèle, chaque bat est représentée par un ensemble de paramètres :

- une position \(x_i\), correspondant à une solution candidate ;
- une vitesse \(v_i\) ;
- une fréquence \(f_i\) ;
- une loudness \(A_i\) ;
- un pulse rate \(r_i\).

Les équations de mise à jour proposées par Yang pour la fréquence, la vitesse et la position sont les suivantes :contentReference[oaicite:0]{index=0} :

\[
f_i = f_{\min} + (f_{\max} - f_{\min}) \, \beta,
\]

\[
v_i^{t} = v_i^{t-1} + (x_i^{t-1} - x^*) \, f_i,
\]

\[
x_i^{t} = x_i^{t-1} + v_i^{t},
\]

où \(\beta \in [0,1]\) est un nombre aléatoire uniforme et \(x^*\) désigne la meilleure solution courante (global best). Ces mises à jour définissent le mouvement des bats dans l’espace de recherche et assurent l’exploration globale du domaine.

En phase de recherche locale, l’algorithme génère une nouvelle position par un déplacement aléatoire autour de la solution courante sélectionnée, avec une amplitude contrôlée par la loudness moyenne.

\[
x_{\text{new}} = x_{\text{old}} + \varepsilon A^{t},
\]

où \(\varepsilon \in [-1, 1]\) est un terme aléatoire et \(A^{t}\) représente la loudness moyenne de la population à l’itération \(t\). Cette étape correspond à la phase d’exploitation locale.

La dynamique d’adaptation de la loudness et du pulse rate est modélisée par :

\[
A_i^{t+1} = \alpha A_i^{t}, \qquad
r_i^{t+1} = r_0 \bigl(1 - e^{-\gamma t}\bigr),
\]

avec \(0 < \alpha < 1\), \(\gamma > 0\) et \(r_0\) un paramètre initial. La loudness décroît donc au cours des itérations, tandis que le pulse rate se rapproche progressivement de \(r_0\).

Les mises à jour de \(f_i\) et \(v_i\) assurent l’exploration globale du domaine en modifiant l’amplitude et la direction des déplacements. La phase d’exploitation locale consiste en un déplacement aléatoire autour de la solution courante de la bat sélectionnée, avec une amplitude contrôlée par la loudness \(A_i\). L’évolution de \(A_i\) et du pulse rate \(r_i\) assure la transition entre exploration et exploitation.

**Algorithm 11.1: Bat Algorithm**

**Data:** Objective function \( f(x) \)  
**Result:** Best or optimal solution

1. Initialize the bat population \( x_i \) and velocities \( v_i \)  \((i = 1, 2, ..., n)\);
2. Initialize frequencies \( f_i \), pulse rates \( r_i \), and loudness \( A_i \);

3. **while** \( t < \text{Max number of iterations} \) **do**
    1. Generate new solutions by adjusting frequency;
    2. Update velocities and positions (solutions) using Eqs. (11.1)–(11.3);
    3. **if** \( \text{rand} > r_i \) **then**
        - Select a solution among the best solutions;
        - Generate a local solution around the selected best solution;
      **end if**
    4. Generate a new solution by flying randomly;
    5. **if** \( \text{rand} < A_i \) **and** \( f(x_i) < f(x_*) \) **then**
        - Accept the new solution;
        - Increase \( r_i \) and reduce \( A_i \);
      **end if**
    6. Rank the bats and find the current best \( x_* \);
4. **end while**


L’algorithme commence par initialiser une population de chauves-souris de taille \(n\), chacune définie par une position \(x_i\), une vitesse \(v_i\) et trois paramètres internes : la fréquence \(f_i\), le taux d’impulsion \(r_i\) et la loudness \(A_i\). À chaque itération, dont la limite est fixée par Max number of iterations, de nouvelles solutions sont générées en ajustant la fréquence, ce qui met à jour la vitesse puis la position de chaque chauve-souris.

À cette étape, deux solutions candidates sont générées : une solution locale construite autour d’une des meilleures solutions actuelles (si la condition \( \text{rand} > r_i \), où rand désigne un nombre aléatoire uniformément distribué dans \([0,1]\), est vérifiée), puis une solution globale obtenue par un mouvement aléatoire (« flying randomly »). Les deux solutions sont évaluées, et la meilleure est retenue pour le test d’acceptation basé sur la loudness \(A_i\).

Ainsi, à chaque itération, une seule solution finale peut être acceptée pour mettre à jour la position \(x_i\). En cas d’amélioration, les paramètres \(A_i\) et \(r_i\) sont mis à jour, et la meilleure solution globale \(x^*\) est actualisée.


**Limites conceptuelles concernant la fréquence \(f_i\) et le pulse rate \(r_i\)**

La lecture approfondie du papier original de Yang nous a conduit à nous interroger sur l'interprétation et l’utilité réelle de certains paramètres du Bat Algorithm, en particulier la fréquence \(f_i\) et le pulse rate \(r_i\), dont le rôle théorique présente des incohérences ou des contradictions avec le comportement biologique qu’ils sont censés modéliser.

1. Interprétation discutable de la fréquence \(f_i\)

Yang relie la fréquence \(f_i\) à la relation physique \(\lambda_i f_i = v_{\text{sound}}\), puis fait varier \(f_i\) pour influencer la mise à jour de la vitesse. Or, dans la nature :

- les microchauves-souris utilisent des fréquences basses pour la recherche à longue portée,
- et des fréquences élevées pour affiner la localisation d’une proie.

Dans l’algorithme, l’effet est inversé : une fréquence élevée entraîne un déplacement de grande amplitude, ce qui correspond à un comportement d’exploration globale plutôt qu’à une localisation fine. De plus, le rôle de \(f_i\) dans les équations pourrait être rempli par n’importe quel coefficient aléatoire ; sa présence semble donc davantage motivée par la métaphore biologique que par une nécessité algorithmique.

2. Condition ambiguë sur le pulse rate \(r_i\)

Le modèle définit \(r_i\) comme un paramètre qui augmente lorsque la bat se rapproche de la solution, ce qui est cohérent avec le comportement réel des microbats qui émettent davantage de pulses près de leur cible. Pourtant, le pseudo-code utilise la condition :

if rand > r_i,

pour déclencher la recherche locale. Or cette condition implique :

- début de l’algorithme : \(r_i\) faible → forte probabilité de recherche locale,
- proximité de la solution : \(r_i\) élevé → faible probabilité de recherche locale.

Ce comportement est donc inverse de l’interprétation biologique, où l’on s’attendrait au contraire à renforcer la recherche locale lorsque la bat s’approche de la cible. Une condition plus cohérente serait 

if rand < r_i,

qui permettrait d’augmenter la fréquence de la recherche locale à mesure que \(r_i\) croît.

Ce sont ces observations qui ont motivé nos recherches sur les incohérences conceptuelles du Bat Algorithm. Celles-ci nous ont conduit à identifier une possible erreur importante dans la mise à jour de la vitesse proposée dans le papier original. En effet, la mise à jour de la vitesse y est formulée comme :

\[
v_i^t = v_i^{t-1} + (x_i^t - x^*)\, f_i,
\]

Or, comme l’a souligné une discussion sur le forum [Mathematics Stack Exchange](https://math.stackexchange.com/questions/3386466/error-in-official-paper-about-bat-algorithm), cette formulation est problématique pour au moins deux raisons : d’une part, l’utilisation de \(x_i^t\) pour calculer \(v_i^t\) crée une dépendance circulaire, puisque la position \(x_i^t\) dépend elle-même de la vitesse. D’autre part, le terme \((x_i^t - x^*)\) oriente la mise à jour dans la direction opposée de la meilleure solution connue, ce qui est contraire au principe même de convergence vers un optimum.

La discussion souligne cependant un point important : dans une implémentation MATLAB publiée par Yang lui-même (dans *Nature-Inspired Optimization Algorithms*, édition 2014), la fréquence est calculée comme :

\[
f_i = f_{\min} + (f_{\min} - f_{\max}) \cdot \text{rand},
\]

soit l’inverse de la formule donnée dans l’article. Comme \(f_{\min} = 0\), cette inversion change le signe de \(f_i\). Dès lors, si l’on utilise la formule de vitesse d’origine :

\[
v_i^t = v_i^{t-1} + (x_{\text{current}} - x_{\text{best}})\, f_i,
\]

l’inversion du signe de \(f_i\) conduit à :

\[
v_i^t = v_i^{t-1} + (x_{\text{best}} - x_{\text{current}})\, f_i,
\]

ce qui rétablit, par effet de compensation, une mise à jour orientée vers la meilleure solution.

Autrement dit, l’erreur dans la définition de la fréquence corrige l’erreur dans la mise à jour de la vitesse. À notre niveau, il nous est difficile de savoir si cette compensation est intentionnelle, accidentelle ou simplement issue d’une divergence entre les différentes versions des publications et ouvrages de Yang. Nous constatons simplement que cette incohérence complique l’interprétation de l’algorithme  et qu’il n’existe pas, dans la littérature de Yang, de position clairement stabilisée sur ce point.


**Implémentation séquentielle : inspirations, choix et différences avec le code MATLAB**

Pour implémenter la version séquentielle du Bat Algorithm, nous nous sommes appuyés sur plusieurs sources, et notamment sur l’implémentation MATLAB proposée par Xin-She Yang dans *Nature-Inspired Optimization Algorithms* (Elsevier, 2014). Cette version du code constitue une référence pratique, car elle explicite non seulement la structure générale de l’algorithme, mais également l’ordre des opérations et l’usage concret des paramètres (mise à jour de la fréquence, gestion de la loudness, conditions d’acceptation, etc.).

Nous avons repris plusieurs éléments de cette implémentation, en particulier :

- la structuration générale de la boucle principale (mise à jour fréquence → vitesse → position → éventuel local search),
- l’utilisation d’un tableau d'individus contenant pour chaque bat sa position, sa vitesse, sa fréquence, sa loudness et son pulse rate,
- la présence d’un local random walk déclenché par un test aléatoire,
- et la mise à jour progressive des paramètres \(A_i\) et \(r_i\) suivant les formules données par Yang.

Cependant, nous avons également pris plusieurs libertés par rapport au code MATLAB, soit pour nous rapprocher davantage du pseudo-code du papier original, soit pour corriger certaines incohérences repérées lors de notre analyse théorique.

1. Correction des équations de fréquence et de vitesse

Comme expliqué dans la section précédente, le code MATLAB utilise une inversion  
\(f = f_{\min} + (f_{\min} - f_{\max}) \cdot \text{rand}\)  
qui change le signe de la fréquence. Cette inversion compense involontairement une erreur présente dans la mise à jour de la vitesse, en rétablissant la direction correcte du mouvement.

Dans notre implémentation, nous avons choisi de corriger explicitement ces incohérences :

- la fréquence est calculée conformément à la formule souhaitée dans le papier,
- la mise à jour de la vitesse utilise une expression cohérente avec l'idée d'attraction vers la meilleure solution :
\[
v_i^t = v_i^{t-1} + (x^* - x_i^{t-1})\, f_i.
\]

Cependant, nous n’avons pas modifié la condition de déclenchement du local search :

`if rand > r_i`

Même si plusieurs analyses issues de la littérature secondaire (notamment des discussions techniques en ligne) soulignent que cette condition est conceptuellement contre-intuitive, Yang utilise systématiquement cette formulation dans son article original, dans ses ouvrages et dans son code MATLAB. Nous n’avons trouvé aucune version officielle où la condition serait inversée.

Dans notre implémentation, ce choix reste cohérent avec notre paramétrisation, car nous initialisons \(r_0 = 1\), ce qui fait décroître \(r_i\) au cours des itérations. Dans cette configuration, la condition `rand > r_i` implique :

- en début de recherche : \(r_i\) élevé → local search rare,
- en fin de recherche : \(r_i\) plus faible → local search plus fréquent.

Ce comportement, bien qu’opposé à l’interprétation biologique (où le pulse rate augmente près de la proie), reste compatible avec une logique d’exploration initiale puis d’exploitation progressive, ce qui correspond au comportement attendu d’un algorithme métaheuristique.



Le pseudo-code présenté dans l’article original de Xin-She Yang semble suggérer trois mécanismes distincts de génération de nouvelles solutions :

- une mise à jour globale (fréquence, vitesse, position),
- une recherche locale conditionnelle,
- un “vol aléatoire” supplémentaire (“flying randomly”).

Cependant, cette structure n’apparaît pas dans l’implémentation MATLAB fournie par Yang dans *Nature-Inspired Optimization Algorithms* (2014). Dans ce code, seules deux solutions potentiellement différentes sont effectivement générées pour une même bat au cours d’une itération :

- une solution globale, obtenue après la mise à jour de la fréquence, de la vitesse et de la position :  
  \[
  S_i = x_i + v_i
  \]

- une solution locale, qui remplace la précédente uniquement si la condition `rand > r` est vérifiée :  
  \[
  S_i = x_{\text{best}} + 0.1 \cdot A \cdot \mathcal{N}(0, I)
  \]

Le code MATLAB n’évalue donc qu’une seule solution par itération, puisque la solution globale est éventuellement écrasée par la solution locale, sans comparaison explicite entre les deux.

Dans notre implémentation séquentielle en C, nous avons choisi d’adopter une approche légèrement différente, plus proche de l’esprit du pseudo-code. Nous conservons en effet deux candidats distincts :

- une solution issue de la mise à jour globale,
- une solution locale (si elle est générée),

puis nous évaluons les deux et retenons la meilleure.

Cette distinction explicite améliore la lisibilité algorithmique et clarifie le rôle respectif du mouvement global et de la recherche locale, tout en restant cohérente avec le fonctionnement général décrit dans l’article de Yang.