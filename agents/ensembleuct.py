from abstract import absagent
import math
import sys
import multiprocessing

class uctnode:
    def __init__(self, node_state, action_list, is_root):
        self.state_value = node_state
        self.valid_actions = action_list
        self.is_root = is_root
        self.state_visit = 0
        self.children_list = []
        self.reward = []
        self.is_terminal = False

class EnsembleUCTAgentClass(absagent.AbstractAgent):
    myname = "EnsembleUCT"

    def __init__(self, simulator, rollout_policy, tree_policy, num_simulations, uct_constant=1, ensembles = 2, horizon=10, parallel = False, ensemble_method=1):
        self.agentname = self.myname
        self.rollout_policy = rollout_policy
        self.simulator = simulator.create_copy()
        self.tree_policy = tree_policy
        self.uct_constant = uct_constant
        self.simulation_count = num_simulations
        self.ensemble_count = ensembles
        self.horizon = horizon
        self.is_parallel = parallel
        self.method = ensemble_method

    def create_copy(self):
        return EnsembleUCTAgentClass(self.simulator.create_copy(), self.rollout_policy.create_copy(),
                                     self.tree_policy, self.simulation_count, self.uct_constant,
                                     self.ensemble_count, self.horizon)

    def get_agent_name(self):
        return self.agentname

    def _simulate_game(self, current_pull, rollout, horizon):
        sim_reward = [0.0] * current_pull.numplayers
        h = 0
        while current_pull.gameover == False and h <= horizon:
            action_to_take = rollout.select_action(current_pull.current_state)
            current_pull_reward = current_pull.take_action(action_to_take)
            sim_reward = [x + y for x, y in zip(sim_reward, current_pull_reward)]
            current_pull.change_turn()
            h += 1

        del current_pull
        return sim_reward

    '''
    THIS METHOD GENERATES ONE UCT TREE AND RETURNS THE REWARDS OF ALL THE ACTIONS
    AND THE VISIT COUNT.
    COULD BE INVOKED IN PARALLEL OR SEQ.
    '''
    def generate_tree(self, current_simulator, current_state, sim_count, tree_pol, rollout, uct_const, hor, curr_turn):
        current_turn = current_state.get_current_state()["current_player"]
        current_simulator.change_simulator_state(current_state)
        valid_actions = current_simulator.get_valid_actions()
        actions_count = len(valid_actions)

        if actions_count <= 1:
            raise ValueError("Action count can't be less than one here. Check it at select_action() level.")

        global uctnode
        root_node = uctnode(current_state, valid_actions, True)
        current_node = root_node
        visit_stack = [current_node]
        curr_sim_count = 0

        while curr_sim_count < sim_count:
            if len(current_node.valid_actions) > 0 and len(current_node.children_list) == len(current_node.valid_actions):
                #CHOOSE A NODE USING TREE POLICY
                if tree_pol == "UCB":
                    max_val = 0
                    sel_node = 0
                    for node in xrange(len(current_node.children_list)):
                        value = current_node.children_list[node].reward[current_turn - 1]
                        exploration = math.sqrt(math.log(current_node.state_visit) / current_node.children_list[node].state_visit)
                        value += uct_const * exploration

                        if (node == 0):
                            max_val = value
                        else:
                            if value > max_val:
                                max_val = value
                                sel_node = node

                    current_node.state_visit += 1
                    current_node = current_node.children_list[sel_node]
                    visit_stack.append(current_node)
            else:
                #SEE IF THE CURRENT NODE IS A TERMINAL NODE. IF YES, JUST RETURN ITS Q VALUE TO BE BACKTRACKED.
                current_node.state_visit += 1
                current_simulator.change_simulator_state(current_node.state_value)
                curr_sim_count += 1

                if current_node.is_terminal:
                    q_vals = current_node.reward
                else:
                    #PULL A NEW ACTION ARM AND CREATE THE NEW STATE.
                    current_pull = current_simulator.create_copy()
                    actual_reward = current_pull.take_action(current_node.valid_actions[len(current_node.children_list)])
                    current_pull.change_turn()

                    ##SIMULATE TILL END AND GET THE REWARD.
                    sim_reward = [0.0] * current_pull.numplayers
                    h = 0
                    simulation_sim = current_pull.create_copy()
                    while simulation_sim.gameover == False and h <= hor:
                        action_to_take = rollout.select_action(current_pull.current_state)
                        current_pull_reward = simulation_sim.take_action(action_to_take)
                        simulation_sim = [x + y for x, y in zip(sim_reward, current_pull_reward)]
                        current_pull.change_turn()
                        h += 1

                    q_vals = [x+y for x,y in zip(actual_reward, sim_reward)]

                    ##CREATE NEW NODE AND APPEND TO CURRENT NODE.
                    global uctnode
                    child_node = uctnode(current_pull.get_simulator_state(), current_pull.get_valid_actions(), False)
                    child_node.reward = q_vals
                    child_node.state_visit += 1
                    child_node.is_terminal = current_pull.gameover
                    current_node.children_list.append(child_node)

                    del current_pull

                ##BACKTRACK REWARDS UNTIL ROOT NODE
                for node in xrange(len(visit_stack) - 1, -1, -1):
                    if visit_stack[node].is_root == False:
                        visit_stack[node].reward = [x+y for x,y in zip(visit_stack[node].reward, q_vals)]

                ##REVERT BACK TO ROOT
                current_node = root_node
                visit_stack = [current_node]

        # RETURN AN ARRAY OF REWARDS, VISITS OF ALL THE CHILDREN OF ROOT NODE
        rewards = []
        visits = []
        for kid in root_node.children_list:
            rewards.append(kid.reward[curr_turn - 1])
            visits.append(kid.state_visit)

        return [rewards, visits]

    def select_action(self, current_state):
        current_turn = current_state.get_current_state()["current_player"]
        self.simulator.change_simulator_state(current_state)
        valid_actions = self.simulator.get_valid_actions()
        actions_count = len(valid_actions)

        if actions_count <= 1:
            return valid_actions[0]

        '''
        METHOD 1 - ROOT PARALLELIZATION
        METHOD 2 - PLURALITY VOTE
        '''
        best_arm = 0
        if self.method == 1:
            cpu_cores = multiprocessing.cpu_count()
            reward_values = []
            visit_counts = []

            if self.is_parallel:
                process_pool = multiprocessing.Pool(processes = cpu_cores)
                for proc in xrange(self.simulation_count):
                    [rewards, visits] = process_pool.apply_async(self.generate_tree,
                                                                 (self.simulator.create_copy(),
                                                                 current_state.create_copy(),
                                                                 self.simulation_count,
                                                                 self.tree_policy,
                                                                 self.rollout_policy.create_copy(),
                                                                 self.uct_constant,
                                                                 self.horizon,
                                                                 current_turn,))
                    reward_values.append(rewards)
                    visit_counts.append(visits)
                process_pool.close()
                process_pool.join()
            else:
                for proc in xrange(self.simulation_count):
                    [rewards, visits] = self.generate_tree(self.simulator.create_copy(),
                                                           current_state.create_copy(),
                                                           self.simulation_count,
                                                           self.tree_policy,
                                                           self.rollout_policy.create_copy(),
                                                           self.uct_constant,
                                                           self.horizon,
                                                           current_turn)
                    reward_values.append(rewards)
                    visit_counts.append(visits)

            # CALCULATE FIRST ARM'S AVG TOTALS IN ALL UCT TREES FOR FIRST BEST VALUE.
            # NEED NOT WORRY ABOUT GETTING CURRENT PLAYER'S REWARD. WE PASS THE TURN
            # WHILE CREATING UCT AGENT AND WE RETRIEVE ONLY THE PLAYER OF INTEREST'S
            # REWARD.
            best_avg = 0.0
            for ensemble in xrange(self.ensemble_count):
                best_avg += reward_values[ensemble][0] / visit_counts[ensemble][0]

            #COMPARE FOR BEST AVG
            for arm in xrange(1, actions_count):
                curr_avg = 0.0
                for ensemble in xrange(self.ensemble_count):
                    curr_avg += reward_values[ensemble][arm] / visit_counts[ensemble][arm]

                if curr_avg > best_avg:
                    best_avg = curr_avg
                    best_arm = arm

        elif self.method ==  2:
            pass


        return valid_actions[best_arm]

