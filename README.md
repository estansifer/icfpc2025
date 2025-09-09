# icfpc2025 - Team House of Lambdas

Terse rundown:

Two person team

Did not participate in lightning round

We had a huge amount of fun with the contest this year!

## v1

First solver was a deterministic solver that used individual queries to explore
each door one at a time, using relabelings to verify if a room repeats on our path
(we ran two paths, one with and one without the label).
We would explore a vertex behind an unknown door by first checking all edges to
find the returning one (using markings), and then relabeling the new vertex and
traversing the whole graph to see if it's indeed new or another label changed
(then we merge with an existing vertex).
This brought us to top 15 even though we used thousands of expeditions per
problem, as very few teams had any submissions to the full round problems at
this time. While we had ideas on how to improve this exact algorithm, we could
barely do it by a constant of 2, which was not enough to challenge the top teams.

The rest of the contest we found successively better solutions, but the effect was
merely to maintain our standing, and not to advance.

## v2

Next solver issued k concurrent queries, each with the same completely random
path, but with different relabelings. In this way the labels can distinguish
4^k - 4 different nodes (the minus 4 is because we do not use the labels
(0, 0, ..., 0), (1, 1, ..., 1), (2, 2, ..., 2), (3, 3, ..., 3) so that we can
distinguish new nodes from nodes we have relabeled).

A single random path passes through each door an average of 3 times in each
direction for the first five problems, so while some doors are missed, enough
of the graph is fully explored that you can use the bidirectionality to infer
the missing information for those problems.

This brought our score down to 6 or less for the first five problems.

## v3

For the latter problems, the shorter limit means that each door is only seen
an average of 1 time each direction, so a large amount of the graph will
still be missing. 

To fix this, after the initial slew of queries, we do another set of parallel
k queries, which starts with a DFS over the distinct nodes, granting each of
them a unique label, and then performs a random walk. This random walk will
hit about 2/3 to 3/4 of unexplored doors (and for each door we know both ends
from the k combined labels). Repeating this enough times gave us enough
information to deduce the missing doors. 

This brought our score on the later problems down to 30 or less.

## v4

A long series of small refinements and optimizations brought our score down to
15 or less for most problems. These included deducting missing vertices (if there
were few enough) and returning edges, as well as optimising our DFS walk to get
longer remaining paths and batching all the follow-up requests.

## v5

We started exploiting the symmetry present in the later problems; the initial
pass explored enough of the graph that we could almost always reliably
identify which nodes are "mirrors" of each other, which then heavily constrains
where the unknown doors can lead, and increases how many holes in the graph
we can paper over. Now we only needed a single further expedition to finish
them off, bringing our highest score down to 11 for iod.

## v6

For the follow-up expeditions, rather than doing k parallel expeditions with
the same path, we do a single expedition with a completely random path and
random markings. (This can also be batched with the initial parallel expeditions.)
We simulate running this random expedition on the graph, branching the simulation
whenever it encounters an unknown door, and unifying the different branches
to identify as many doors as possible. Often doors identified from this
random walk feed into further deductions being possible on the graph, and
vice versa, so the various deduction functions are now being run in a loop.

Our score is now down to 7 or less for all problems.

## v7

We were willing to tolerate an increased chance of failures, and slightly
truncated the initial k parallel expeditions, using the extra space to do
more random walks, rather than having an extra expedition in parallel.
This means the node graph has even more holes, and we have to run submissions
dozens of times to get a successful completion, but this brings our
score down to 6 at worst.

Being more aggressive with lowering k greatly increases the chance
of label collisions for certain problems, and it now takes perhaps ~100
attempts to submit iod, but brings iod down to 5 (and reduces the score of
several other problems).

I solve primus by hand for a score of 2.

We stop a few hours before the deadline in 10th place on the leaderboard.
