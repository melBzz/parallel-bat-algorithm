## Introduction au **Bat Algorithm**

Pour introduire et comprendre le **Bat Algorithm**, nous allons commencer par étudier une fonction simple en deux dimensions :

$$
f(x, y) = e^{-(x^2 + y^2)}
$$

Elle dépend donc de **deux variables** :

- \(x_1 = x\)
- \(x_2 = y\)

Chaque point de cet espace est un couple :

$$
(x_1, x_2)
$$

Dans le Bat Algorithm, chaque chauve-souris est représentée par une position :

$$
\mathbf{x}_i = (x_{i1}, x_{i2}), \qquad \mathbf{x}_i \in \mathbb{R}^2
$$

Partons de ce pseudo-code :

```pseudo
Input : Objective function f(x)
Output: Best solution x*

Initialize bat population xi and velocities vi   for i = 1..n
Initialize frequencies fi, pulse rates ri and loudness Ai

while t < MaxIterations do

    # 1. Adjust frequency
    generate fi using Eq. (1)

    # 2. Global update
    update velocity vi using Eq. (2)
    update position xi using Eq. (3)

    # 3. Local search around best solutions
    if rand > ri then
        select a solution among the best
        generate a local solution around it
    end if

    # 4. Random flight + acceptance condition
    if rand < Ai  and  f(xi) < f(x*) then
        accept new solution
        increase ri and reduce Ai
    end if

    # 5. Rank bats and update global best
    update x*

end while

return x*
```


---




## Règles du Bat Algorithm

Dans un espace de dimension \(d\), à un instant \(t\), les équations sont :

**Génération de la fréquence**

$$
f_i = f_{\min} + (f_{\max} - f_{\min}) \, \beta \tag{1}
$$

**Mise à jour de la vitesse (attraction vers la meilleure solution)**

$$
v_i^{t+1} = v_i^{t} + (x_i^{t} - x_*) \, f_i \tag{2}
$$

**Déplacement global**

$$
x_i^{t+1} = x_i^{t} + v_i^{t+1} \tag{3}
$$

**Variable aléatoire \(\beta\)**

$$
\beta = (\beta_1, \beta_2, \ldots, \beta_d)
$$

où chaque \(\beta_j\) est tiré uniformément dans \([0,1]\)


\(\beta\) permet d’introduire **une fréquence différente par dimension** (aléatoire).



**Meilleure solution globale**


\(x_*\) = meilleure solution trouvée jusqu’à maintenant parmis toute les bats




**Rôle de la fréquence \(f_i\)**

On utilise la relation physique :

$$
\lambda_i f_i = v_{\text{sound}}
$$

où :

- \(\lambda_i\) = longueur d’onde de la bat \(i\)  
- \(f_i\) = fréquence  
- \(v_{\text{sound}}\) = vitesse du son

Comme le produit \(\lambda_i f_i\) est constant, on peut faire varier l’un pour ajuster l’autre.

Dans l’algorithme on **fait varier la fréquence \(f_i\)** et on fixe implicitement \(\lambda_i\) ce qui modifie la vitesse (équation 2). 

Ici je trouve que c'est contre intuitif. En effet, dans la nature, les chauves souris modifie la fréquence de leurs ultras son de la manière suivante : 
 - haute fréquence pour la précision une fois qu'elle ont detecter une proie 
 - basse fréquence lorsqu'elle sont en recherche (longue portée)

Or dans cet algorithm plus \(f_i\) est grand → plus le mouvement est grand.
Après reflexion j'ajouterais même qu'on  pourrait obtenir exactement le même effet en remplaçant la fréquence \(f_i\) par un simple coefficient aléatoire appliqué à la vitesse. Ce choix de "fréquence" semble surtout venir du storytelling du Bat Algorithm, pour rester cohérent avec l’idée d’écholocation des chauves-souris, plutôt que d’une nécessité mathématique.


Dans la version standard du Bat Algorithm :

$$
f_{\min} = 0, \qquad f_{\max} = O(1)
$$

Initialement, **chaque bat tire une fréquence aléatoire entre \(f_{\min}\) et \(f_{\max}\)**, ce qui donne des comportements différents (exploration variée).



Implémentation séquentiel : 







---

Algorithm 11.1: Bat algorithm.

Data: Objective functions f(x)
Result: Best or optimal solution

1  Initialize the bat population xi and vi  (i = 1, 2, ..., n);
2  Initialize frequencies fi, pulse rates ri and the loudness Ai;
3  while (t < Max number of iterations) do
4      Generate new solutions by adjusting frequency;
5      Update velocities and locations/solutions [(11.1) to (11.3)];
6      if (rand > ri ) then
7          Select a solution among the best solutions;
8          Generate a local solution around the selected best solution;
9      end if
10     Generate a new solution by flying randomly;
11     if (rand < Ai  &  f(xi) < f(x*)) then
12         Accept the new solutions;
13         Increase ri and reduce Ai;
14     end if
15     Rank the bats and find the current best x*;
16 end


Les règles : 

Dans une dimension de recherche d, à un temps t donné :

$$
f_i = f_{\min} + (f_{\max} - f_{\min}) \beta \tag{11.1}
$$

attraction vers la meilleure solution: 
$$
v_i^{t+1} = v_i^{t} + (x_i^{t} - x_*) f_i \tag{11.2}
$$
déplacement global :
$$
x_i^{t+1} = x_i^{t} + v_i^{t+1} \tag{11.3}
$$

β est un nombre ou un vecteur de valeurs aléatoires uniformes dans [0,1].
β=(β1​,β2​,...,βd​)
Permet une fréquence différente par dimension.
x∗= meilleure solution trouvée par toutes les bats jusqu’à maintenant.

On utilise fi car λi​fi​=vsound​ 
(λ = longueur d’onde, f = fréquence, λf = vitesse du son)
Because
the product
˜
λ
i
f
i
is a constant, we can use f
i
(or
˜
λ
i
) to adjust the velocity change while ﬁxing the other
factor
˜
λ
i
(or f
i
), depending on the type of the problem of interest.

Ici on utilise fmin =0 et fmax =O(1) (ordre de 1)

Initialement, chaque bat tire une fréquence aléatoire entre f_min et f_max.