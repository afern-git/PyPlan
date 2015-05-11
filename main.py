import dealer
from agents import *
from simulators import *
import os

def call_dealer():
    players_count = 2
    simulation_count = 100
    simulation_horizon = 120

    output_file = open("simulation_results.csv", "w")
    for player in xrange(players_count):
        output_file.write("REWARD FOR " + str(player + 1) + ",")
    output_file.write("WINNER\n")

    simulator_obj = connect4simulator.Connect4SimulatorClass(num_players = players_count)
    # simulator_obj = yahtzeesimulator.YahtzeeSimulatorClass(num_players = players_count)
    # simulator_obj = tetrissimulator.TetrisSimulatorClass(num_players = players_count)
    # simulator_obj = tictactoesimulator.TicTacToeSimulatorClass(num_players = players_count)

    agent_one = randomagent.RandomAgentClass(simulator=simulator_obj)

    # agent_temp = egreedyagent.EGreedyAgentClass(simulator=simulator_obj, rollout_policy=agent_one, pull_count=20,
    #                                             epsilon=0.5, horizon=10)
    # agent_two = egreedyagent.EGreedyAgentClass(simulator=simulator_obj, rollout_policy=agent_one, pull_count=20,
    #                                            epsilon=0.5, horizon=10)
    # agent_three = uniformagent.UniformRolloutAgentClass(simulator=simulator_obj, rollout_policy=agent_one,
    #                                                     pull_count=10, horizon=10)
    # agent_four = uniformagent.UniformRolloutAgentClass(simulator=simulator_obj, rollout_policy=agent_three,
    #                                                    pull_count=5, horizon=10)
    agent_five = incuniformagent.IncUniformRolloutAgentClass(simulator=simulator_obj, rollout_policy=agent_one,
                                                              pull_count=10, horizon=100)
    #
    agent_uct = uctagent.UCTAgentClass(simulator=simulator_obj, rollout_policy=agent_one, tree_policy="UCB",
                                        num_simulations=100, uct_constant=5, horizon=10, time_limit=1)
    #
    # agent_uct_2 = uctagent.UCTAgentClass(simulator=simulator_obj, rollout_policy=agent_one, tree_policy="UCB",
    #                                      num_simulations=10, uct_constant=5, horizon=10)
    #

    agent_LP = leafparalleluct.LeafParallelUCTClass(simulator=simulator_obj, rollout_policy=agent_one, tree_policy="UCB",
                                        num_simulations=100, num_threads=8, uct_constant=5, horizon=70, time_limit=1)

    agent_ensemble = ensembleuct.EnsembleUCTAgentClass(simulator=simulator_obj, rollout_policy=agent_one, tree_policy="UCB",
                                         num_simulations=200, uct_constant=5, ensembles=8, horizon=100, parallel=True, time_limit=1)

    agent_TP_NVL = treeparalleluct_NVL.TreeParallelUCTNVLClass(simulator=simulator_obj, rollout_policy=agent_one, tree_policy="UCB",
                                        num_simulations=20, threadcount=2,  uct_constant=10, horizon=10, time_limit=1)

    agent_TP_GM = treeparalleluct_GM.TreeParallelUCTGMClass(simulator=simulator_obj, rollout_policy=agent_one, tree_policy="UCB",
                                        num_simulations=20, threadcount=2, uct_constant=5, horizon=10, time_limit=1)

    agent_block = blockparalleluct.BlockParallelUCTClass(simulator=simulator_obj, rollout_policy=agent_one, tree_policy="UCB",
                                         num_simulations=100, threadcount=2, uct_constant=5, ensembles=4, horizon=100,
                                         parallel=True, time_limit=1)

    agents_list = [agent_TP_NVL, agent_one]

    dealer_object = dealer.DealerClass(agents_list, simulator_obj, num_simulations=simulation_count,
                                       sim_horizon=simulation_horizon, results_file=output_file)
    dealer_object.start_simulation()
    results = dealer_object.simulation_stats()[0]
    winner_list = dealer_object.simulation_stats()[1]

    # RESULTS CALCULATION
    overall_reward = []
    for game in xrange(len(results)):
        game_reward_sum = [0] * players_count

        for move in xrange(len(results[game])):
            game_reward_sum = [x + y for x, y in zip(game_reward_sum, results[game][move][0])]

        print "REWARD OF PLAYERS IN GAME {0} : ".format(game)
        print game_reward_sum
        overall_reward.append(game_reward_sum)

    overall_reward_avg = [0] * players_count
    for game in xrange(len(results)):
        overall_reward_avg = [x + y for x, y in zip(overall_reward_avg, overall_reward[game])]

    for x in xrange(len(overall_reward_avg)):
        overall_reward_avg[x] = overall_reward_avg[x] / simulation_count

    print "\nAVG OF REWARDS (FOR OVERALL SIMULATION) : "
    print overall_reward_avg

    win_counts = [0.0] * players_count

    for val in xrange(len(winner_list)):
        if winner_list[val] is not None:
            win_counts[winner_list[val] - 1] += 1.0

    for val in xrange(players_count):
        print "AVG WINS FOR AGENT {0} : {1}".format(val + 1, win_counts[val] / simulation_count)

    output_file.close()
if __name__ == "__main__":
    call_dealer()