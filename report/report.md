# Introduction

This work is carried out within the framework of the **EIT Digital** program and the course **High‑Performance Computing for Data Science**. The objective of the project is to conduct an in‑depth analysis of an optimization algorithm, to design a **sequential implementation**, and subsequently to develop a **parallelized version** suitable for **HPC environments**.

We chose to study the **Bat Algorithm (BA)**, a bio‑inspired metaheuristic proposed by **Xin‑She Yang (2010)**, whose mechanism is based on a simplified mathematical modeling of the **echolocation behavior of microbats**. The goal of this first phase is to thoroughly understand the internal mechanisms of the algorithm, its parameters, and the way it explores the search space in order to solve **continuous optimization problems**.

Continuous optimization problems arise in many scientific and industrial domains and consist in finding, among all possible configurations, the one that minimizes or maximizes an objective function. As highlighted by **Nocedal and Wright** in *Numerical Optimization*, such problems can be particularly challenging when the objective function is **non‑convex**, **non‑differentiable**, **noisy**, or when the **dimensionality of the problem increases**. In these cases, gradient‑based methods often become ineffective.

A comprehensive review by **Rios and Sahinidis (2013)** further emphasizes that when derivatives are unavailable or unreliable, classical optimization methods are “*of little or no use*”, and that their performance deteriorates rapidly as the problem dimension grows. These limitations motivate the use of **derivative‑free** and **metaheuristic** approaches.

As a stochastic algorithm, the Bat Algorithm incorporates randomness to efficiently explore the search space. Its design explicitly balances **global exploration** and **local exploitation**, making it well‑suited for highly nonlinear objective functions and multimodal landscapes with multiple local optima.

---

# Principles of the Bat Algorithm

The Bat Algorithm is inspired by the echolocation mechanism used by microbats to navigate and hunt in complete darkness. In nature, bats emit ultrasonic pulses and analyze the returning echoes to estimate the distance, direction, size, and motion of nearby objects. As they approach a target, they adapt the **frequency**, **loudness**, and **pulse emission rate** of these signals.

Yang translates these biological observations into algorithmic concepts. Each bat is modeled as a candidate solution characterized by:

* a **position** $x_i$ in the search space,
* a **velocity** $v_i$,
* a **frequency** $f_i$ controlling the scale of movement,
* a **loudness** $A_i$ governing solution acceptance,
* a **pulse rate** $r_i$ controlling the switch between exploration and exploitation.

At each iteration, these parameters are updated stochastically, simulating the collective behavior of a bat colony progressively converging toward an optimal region.

---

# Echolocation Model and Biological Motivation

Microbats emit ultrasonic pulses with frequencies typically ranging from **25 kHz to 150 kHz**, each pulse lasting only a few milliseconds. During the search phase, bats emit around **10–20 pulses per second**, increasing up to **200 pulses per second** as they approach prey. Pulse loudness may reach **110 dB**, but decreases as the bat nears its target to improve precision and avoid sensory saturation.

From the reflected echoes, bats infer:

* **distance**, via time‑of‑flight measurement,
* **direction**, via interaural time differences,
* **target characteristics**, via echo intensity and Doppler effects.

The distance estimation follows the classical acoustic relation:

$$
\text{distance} = v \cdot \frac{t}{2},
$$

where $v$ is the speed of sound and $t$ is the round‑trip travel time of the signal.

This remarkable sensing capability motivates the abstraction used in the Bat Algorithm, where objective‑function evaluations play the role of echo analysis.

---

# Mathematical Formulation of the Bat Algorithm

Following Yang (2010), the Bat Algorithm is based on three idealized assumptions:

1. Each bat can evaluate the quality of its current position through the objective function.
2. Bats adapt their frequency, velocity, and pulse rate depending on their proximity to promising solutions.
3. Loudness decreases while pulse rate increases over time, modeling a transition from exploration to exploitation.

The **global update** equations are:

$$
f_i = f_{\min} + (f_{\max} - f_{\min}) , \beta, \quad \beta \sim U(0,1),
$$

$$
v_i^{t+1} = v_i^t + (x^* - x_i^t) , f_i,
$$

$$
x_i^{t+1} = x_i^t + v_i^{t+1},
$$

where $x^*$ denotes the current best solution.

The **local search** mechanism is defined as:

$$
x_{\text{new}} = x_{\text{best}} + \sigma , \varepsilon_t , A^{(t)},
$$

with $\varepsilon_t \sim \mathcal{N}(0,1)$ and $\sigma$ a scaling parameter.

The adaptive behavior of loudness and pulse rate follows:

$$
A_i^{t+1} = \alpha A_i^t, \quad r_i^{t+1} = r_{0i} \bigl(1 - e^{-\gamma t}\bigr),
$$

ensuring a gradual shift from exploration to exploitation.

---

# Algorithmic Structure

**Algorithm: Bat Algorithm**

**Input:** Objective function $f(x)$
**Output:** Best solution found

1. Initialize a population of $n$ bats with positions $x_i$ and velocities $v_i$.
2. Initialize frequencies $f_i$, loudness $A_i$, and pulse rates $r_i$.
3. While $t < T_{\max}$:

   * Update frequencies, velocities, and positions.
   * With probability $1 - r_i$, generate a local solution around the current best.
   * Evaluate candidate solutions and apply acceptance criteria based on $A_i$.
   * Update loudness and pulse rate if improvement occurs.
   * Update the global best solution $x^*$.
4. Return $x^*$.

---

# Conceptual Limitations and Critical Analysis

A careful examination of Yang’s original formulation reveals several **conceptual inconsistencies**, particularly regarding the interpretation of the **frequency** $f_i$ and the **pulse rate** $r_i$.

* In biological systems, **higher frequencies correspond to fine‑grained localization**, whereas in the algorithm, higher $f_i$ values produce **larger displacements**, which is more characteristic of global exploration.
* The condition `rand > r_i` used to trigger local search appears counter‑intuitive if $r_i$ is interpreted as increasing near the optimum.

Moreover, an inconsistency exists between the velocity update equation in the original paper and the MATLAB implementation provided by Yang, leading to a **sign compensation effect** between frequency and velocity updates. This ambiguity complicates the theoretical interpretation of the algorithm and motivates careful implementation choices.

---

# Sequential Implementation Choices

Our sequential C implementation is inspired by:

* Yang’s original 2010 paper,
* the MATLAB reference implementation from *Nature‑Inspired Optimization Algorithms* (2014),
* and the clarified equations presented in the 2020 edition.

We explicitly correct the velocity update to ensure attraction toward the best solution, while preserving the original pulse‑rate condition. Two candidate solutions (global and local) are evaluated separately at each iteration, improving algorithmic clarity compared to the MATLAB version, which overwrites the global solution when local search is triggered.

Parameter choices (population size, frequency bounds, loudness, pulse rate, domain limits) strictly follow Yang’s recommendations, with minor adaptations justified by the characteristics of the chosen objective function.

---

*To do:*

* Refine and standardize academic citations.
* Insert and document the sequential C implementation.