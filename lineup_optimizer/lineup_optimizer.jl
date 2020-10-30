# Fantasy NFL Lineup Optimizer

using POMDPs
using POMDPModelTools
using Random
using Distributions
using POMDPSimulators
using POMDPPolicies
using MCTS
using SARSOP
using Printf
using CSV
using Plots
using DataFrames
using LinearAlgebra

rng = Random.GLOBAL_RNG;
pyplot();

HIST_RAND_FILENAME = "rand_results.csv";
HIST_MCTS_FILENAME = "mcts_results.csv";

# Define State, Action, and Model Data Holders
struct FantasyGameState
    proj::Array{Float64}
    sal::Array{Float64}
    pos::Array{Float64}
    team::Array{String}
    inj::Array{String} # Should convert the transition function to sampling from Dirichlet
    week::Int64
end

struct FantasyGameAction
    lineup::Array{Bool}
end

struct FantasyGameMDP <: MDP{FantasyGameState, FantasyGameAction}
    # Define DFS FantasyGameMDP

    # Roster Constrain Params
    rb_max::Int64
    wr_max::Int64
    qb_max::Int64
    te_max::Int64
    sal_max::Int64
end

RB_MAX = 2;
WR_MAX = 2;
QB_MAX = 1;
TE_MAX = 1;
SAL_MAX = 60000; # $60K

FantasyGameMDP() = FantasyGameMDP(RB_MAX, WR_MAX, QB_MAX, TE_MAX, SAL_MAX)

# Define Generative Model
# In theory, none of these state transition functions should impact policy
# because the reward is pretty independent of what the state transition is...
# Like, the action of our agent has no impact on the next state, so yeah...
function update_proj(proj)
    # Add random step sampled from normal dist each week. (this shouldn't impact policy)
    proj_next = proj + rand(Normal(0,0.05*proj),1)
    proj_next = max(proj_next, 0)
    return proj_next
end

function update_sal(sal)
    # Add random step sampled from normal dist each week. (this shouldn't impact policy)
    sal_next = sal + rand(Normal(0,0.05*sal),1)
    sal_next = max(sal_next, 0)
    return sal_next
end

function update_week(week)
    return week+1
end

# TODO: make the update injury function work with arrayed input
function update_inj(inj)
    if false # Using this to mask the following computations until it can be re-written for array input
        heal_prob = 0.3
        inj_prob = 0.03
        if inj != 0
            if rand(Binomial(1,heal_prob),1) == 1
                inj = 0
            end
        else
            if rand(Binomial(1,inj_prob),1) == 1
                inj = "Q"
            end
        end
    end
    return inj
end

function update_team(team)
    return team
end

function update_pos(pos)
    return pos
end

# MDP Generative Model
function POMDPs.gen(m::FantasyGameMDP, s::FantasyGameState, a::FantasyGameAction, rng)
    # Transition Model
    week = update_week(s.week)
    proj = update_proj(s.proj) 
    sal = update_sal(s.sal)
    inj = update_sal(s.inj)
    team = update_team(s.team)
    pos = update_pos(s.pos)

    sp = FantasyGameState(proj, sal, pos, team, inj, week)

    # Observation Model
    # N/A

    # Reward Model
    r = dot(a.lineup, s.proj) # Raw Projected Score
    r += count_te(a.lineup, s.pos) > m.te_max ? m.lineup_penalty : 0
    r += count_qb(a.lineup, s.pos) > m.qb_max ? m.lineup_penalty : 0
    r += count_rb(a.lineup, s.pos) > m.rb_max ? m.lineup_penalty : 0
    r += count_wr(a.lineup, s.pos) > m.wr_max ? m.lineup_penalty : 0
    r += dot(a.lineup, s.sal) > m.sal_max ? m.lineup_penalty : 0

    # create and return a NamedTuple
    return (sp=sp, r=r)
end

fg = FantasyGameMDP();
