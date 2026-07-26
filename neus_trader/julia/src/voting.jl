"""
Consensus voting mechanism for aggregating agent decisions.
"""

"""
    consensus_vote(agent_decisions::Dict{Symbol, Decision}, agent_weights::Dict{Symbol, Float64})::VotingResult

Aggregate decisions from all agents using majority voting with confidence weighting.

Rules:
1. Require 3+ agents (of 4 active) to agree on direction (LONG/SHORT)
2. Risk agent is always a gate/filter (veto power if confidence=0)
3. Calculate consensus strength (0-1) based on agreement level
4. Weight agent confidence by their track record (win rate)
5. Track dissent for meta-learning

Returns:
- VotingResult with consensus direction, confidence, and risk approval
"""
function consensus_vote(
    agent_decisions::Dict{Symbol, Decision},
    agent_weights::Dict{Symbol, Float64} = Dict()
)::VotingResult
    timestamp = now()

    # Extract risk management decision first
    risk_decision = get(agent_decisions, :risk_management, nothing)
    risk_approved = !isnothing(risk_decision) && risk_decision.confidence > 0.0

    # If risk agent denies, no trade
    if !risk_approved
        return VotingResult(
            :HOLD,
            0.0,
            agent_decisions,
            0.0,
            false,
            timestamp
        )
    end

    # Collect votes from 4 active agents (exclude risk management)
    active_agents = [:momentum, :mean_reversion, :volatility, :arbitrage]
    long_votes = Float64[]
    short_votes = Float64[]
    hold_votes = Float64[]

    for agent_id in active_agents
        decision = get(agent_decisions, agent_id, nothing)
        if isnothing(decision)
            continue
        end

        # Get agent weight (default 1.0)
        weight = get(agent_weights, agent_id, 1.0)

        # Accumulate votes
        if decision.direction == :LONG
            push!(long_votes, decision.confidence * weight)
        elseif decision.direction == :SHORT
            push!(short_votes, decision.confidence * weight)
        else  # HOLD
            push!(hold_votes, decision.confidence * weight)
        end
    end

    # Count votes
    long_count = length(long_votes)
    short_count = length(short_votes)
    hold_count = length(hold_votes)

    # Determine consensus direction (require 3+ agents)
    if long_count >= 3
        direction = :LONG
        avg_confidence = mean(long_votes)
    elseif short_count >= 3
        direction = :SHORT
        avg_confidence = mean(short_votes)
    else
        # No consensus (fewer than 3 agents agree)
        return VotingResult(
            :HOLD,
            0.0,
            agent_decisions,
            0.0,
            false,
            timestamp
        )
    end

    # Calculate consensus strength (0-1)
    # Strength = how dominant is the majority vs minority
    total_votes = long_count + short_count + hold_count
    if total_votes == 0
        consensus_strength = 0.0
    else
        majority_count = max(long_count, short_count)
        consensus_strength = (majority_count - 2.0) / (total_votes - 2.0)  # 0 if 3 votes, 1 if all 4
        consensus_strength = max(0.0, min(1.0, consensus_strength))
    end

    # Clamp confidence
    avg_confidence = max(0.3, min(1.0, avg_confidence))

    return VotingResult(
        direction,
        avg_confidence,
        agent_decisions,
        consensus_strength,
        risk_approved,
        timestamp
    )
end

"""
    dissent_analysis(decisions::Dict{Symbol, Decision})::Dict

Analyze agent disagreement patterns for meta-learning.

Returns:
- Dictionary of disagreement pairs and their frequency
"""
function dissent_analysis(decisions::Dict{Symbol, Decision})::Dict
    active_agents = [:momentum, :mean_reversion, :volatility, :arbitrage]
    disagreements = Dict()

    for i in 1:length(active_agents)
        for j in (i+1):length(active_agents)
            agent_1 = active_agents[i]
            agent_2 = active_agents[j]

            decision_1 = get(decisions, agent_1, nothing)
            decision_2 = get(decisions, agent_2, nothing)

            if !isnothing(decision_1) && !isnothing(decision_2)
                if decision_1.direction != decision_2.direction
                    key = "$(agent_1)_vs_$(agent_2)"
                    disagreements[key] = (
                        agent_1=agent_1,
                        agent_2=agent_2,
                        dir_1=decision_1.direction,
                        dir_2=decision_2.direction,
                        conf_1=decision_1.confidence,
                        conf_2=decision_2.confidence
                    )
                end
            end
        end
    end

    return disagreements
end

"""
    calculate_agent_weights(performance::Dict{Symbol, NamedTuple})::Dict

Calculate dynamic weights based on agent win rates.

Input: performance[agent_id] = (wins=Int, losses=Int, trades=Int)
Output: weights[agent_id] = Float64 (1.0 baseline, >1.0 for good performers)
"""
function calculate_agent_weights(performance::Dict{Symbol, NamedTuple})::Dict
    weights = Dict()

    for (agent_id, perf) in performance
        if perf.trades > 0
            win_rate = perf.wins / perf.trades
            # Weight formula: 0.5 to 1.5 based on win rate
            # 50% win rate = 1.0 (no change)
            # 60% win rate = 1.1 (10% boost)
            # 40% win rate = 0.9 (10% penalty)
            weight = 0.5 + win_rate
            weights[agent_id] = weight
        else
            weights[agent_id] = 1.0  # Default to equal weight
        end
    end

    return weights
end
