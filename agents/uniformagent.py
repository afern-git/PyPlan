from abstract import absagent

'''
Uniformly pull each arm w number of times

Method:
------

1. From the set of valid actions in the given simulator's state, one action is chosen.
2. The chosen action is taken on the simulator and the state is updated.
3. This copy of the simulator is given to simulation using rollout policy until the game comes to an end.
4. The end reward is noted and added to the current arm in arm_rewards[arm]
5. Step 3 is repeated for the specified number of pulls
6. Step 1 is repeated for the next available action until all the available actions are chosen.
7. The final value in arm_rewards will give the value of specified number of pulls for each of the arm i.e., action
8. Return the arm with the maximum reward.

'''

class UniformRolloutAgentClass(absagent.AbstractAgent):
    myname = "UNIFORM"

    def __init__(self, simulator, rollout_policy, pull_count = 5, horizon=5, heuristic=0):
        self.agentname = self.myname
        self.rollout_policy = rollout_policy
        self.heuristicvalue = heuristic
        self.pull_count = pull_count
        self.simulator = simulator.create_copy()
        self.horizon = horizon

    def create_copy(self):
        return UniformRolloutAgentClass(self.simulator.create_copy(), self.rollout_policy.create_copy(), self.pull_count, self.horizon, self.heuristicvalue)

    def get_agent_name(self):
		return self.agentname

    def set_num_pulls(self, pull_count=3):
        self.pull_count = pull_count

    def select_action(self, current_state):
        current_turn = current_state.get_current_state()["current_player"]
        self.simulator.change_simulator_state(current_state)
        valid_actions = self.simulator.get_valid_actions()
        actions_count = len(valid_actions)

        arm_rewards = [[0.0] * self.simulator.numplayers] * actions_count #REWARD PER PLAYER PER ACTION
        if actions_count <= 1:
            return valid_actions[0]

        for arm in xrange(actions_count):
            current_arm_rewards = [] #THIS STORES REWARDS FOR ALL PULLS OF CURRENT ARM

            for pull in xrange(self.pull_count):
                player_number = self.simulator.current_state.get_current_state()["current_player"]

                # TAKE THE ACTION i.e., CREATE THE ARM TO DO ROLLOUT
                current_pull = self.simulator.create_copy()
                actual_reward = current_pull.take_action(valid_actions[arm])
                current_pull.change_turn()

                playout_rewards = []
                h = 0

                # PLAY TILL GAME END
                while current_pull.gameover == False and h <= self.horizon:
                    action_to_take = self.rollout_policy.select_action(current_pull.current_state)
                    reward = current_pull.take_action(action_to_take)
                    playout_rewards.append(reward)
                    current_pull.change_turn()
                    h += 1

                # ADD ACTUAL REWARD + BACKTRACK REWARDS TO THE CURRENT PULL'S REWARD AND ADD TO CURRENT ARM'S REWARD VECTOR
                current_pull_reward = [0] * self.simulator.numplayers
                current_pull_reward = [x + y for x, y in zip(actual_reward, current_pull_reward)]
                for value in xrange(len(playout_rewards)):
                    current_pull_reward = [x + y for x, y in zip(playout_rewards[value], current_pull_reward)]

                current_arm_rewards.append(current_pull_reward)

                del current_pull

            # AVERAGE ALL THE PULL REWARDS FOR THE CURRENT ARM
            for pull in xrange(self.pull_count):
                arm_rewards[arm] = [x + y for x, y in zip(current_arm_rewards[pull], arm_rewards[arm])]
            for player in xrange(self.simulator.numplayers):
                arm_rewards[arm][player] = arm_rewards[arm][player] / self.pull_count

        best_arm = 0
        best_reward = arm_rewards[0][current_turn - 1]

        for arm in xrange(len(arm_rewards)):
            if arm_rewards[arm][current_turn - 1] > best_reward:
                best_reward = arm_rewards[arm][current_turn - 1]
                best_arm = arm

        return valid_actions[best_arm]


