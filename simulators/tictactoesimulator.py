from abstract import abssimulator
from actions import tictactoeaction
from states import tictactoestate
from copy import deepcopy

"""
Simulator Class for TicTacToe

NOTE :
------

1. self.winningplayer = None -> Implies that the game is a draw. 
							    Otherwise this variable holds the winning player's number.
								Player number 1 for X. 2 for O.
"""


class TicTacToeSimulatorClass(abssimulator.AbstractSimulator):
	def __init__(self, starting_player, num_players):
		self.playerturn = starting_player
		self.current_state = tictactoestate.TicTacToeStateClass()
		self.numplayers = num_players

		self.starting_player = starting_player
		self.winningplayer = None

	def reset_simulator(self):
		self.playerturn = self.starting_player
		self.winningplayer = None
		initial_state = tictactoestate.TicTacToeStateClass()
		self.set_state(initial_state.get_current_state())

	def change_simulator_values(self, current_state, player_turn):
		self.playerturn = player_turn
		self.winningplayer = None
		self.set_state(current_state)

	def change_turn(self):
		self.playerturn += 1
		self.playerturn = self.playerturn % self.numplayers

		if self.playerturn == 0:
			self.playerturn = self.numplayers

	def take_action(self, action):
		actionvalue = action.get_action()
		position = actionvalue['position']
		value = actionvalue['value']
		self.current_state.get_current_state()[position[0]][position[1]] = value

	def get_valid_actions(self):
		actions_list = []

		for x in xrange(len(self.current_state.get_current_state())):
			for y in xrange(len(self.current_state.get_current_state()[0])):
				if self.current_state.get_current_state()[x][y] == 0:
					action = {}
					action['position'] = [x, y]
					action['value'] = self.playerturn
					actions_list.append(tictactoeaction.TicTacToeActionClass(action))

		return actions_list

	def set_state(self, state):
		self.current_state = deepcopy(state)

	def is_terminal(self):
		xcount = 0
		ocount = 0

		# Horizontal check for hit
		for x in xrange(len(self.current_state.get_current_state())):
			for y in xrange(len(self.current_state.get_current_state()[0])):
				if self.current_state.get_current_state()[x][y] == 1:
					xcount += 1
				elif self.current_state.get_current_state()[x][y] == 2:
					ocount += 1

			if xcount == 3:
				self.winningplayer = 1
			elif ocount == 3:
				self.winningplayer = 2
			else:
				xcount = 0
				ocount = 0

		# Vertical check for hit
		if self.winningplayer == None:
			for y in xrange(len(self.current_state.get_current_state()[0])):
				for x in xrange(len(self.current_state.get_current_state())):
					if self.current_state.get_current_state()[x][y] == 1:
						xcount += 1
					elif self.current_state.get_current_state()[x][y] == 2:
						ocount += 1

				if xcount == 3:
					self.winningplayer = 1
				elif ocount == 3:
					self.winningplayer = 2
				else:
					xcount = 0
					ocount = 0

		# Diagonal One Check for Hit
		x = 0
		y = 0
		xcount = 0
		ocount = 0

		if self.winningplayer == None:
			while x < len(self.current_state.get_current_state()):
				if self.current_state.get_current_state()[x][y] == 1:
					xcount += 1
				elif self.current_state.get_current_state()[x][y] == 2:
					ocount += 1

				x += 1
				y += 1

				if xcount == 3:
					self.winningplayer = 1
				elif ocount == 3:
					self.winningplayer = 2
				else:
					xcount = 0
					ocount = 0

		# Diagonal Two Check for Hit
		x = 0
		y = len(self.current_state.get_current_state()[0]) - 1
		xcount = 0
		ocount = 0

		if self.winningplayer == None:
			while x < len(self.current_state.get_current_state()):
				if self.current_state.get_current_state()[x][y] == 1:
					xcount += 1
				elif self.current_state.get_current_state()[x][y] == 2:
					ocount += 1

				x += 1
				y -= 1

				if xcount == 3:
					self.winningplayer = 1
				elif ocount == 3:
					self.winningplayer = 2
				else:
					xcount = 0
				ocount = 0

		if self.winningplayer == None:
			#CHECK IF THE BOARD IS FULL
			x = 0
			y = 0
			game_over = True

			for x in xrange(len(self.current_state.get_current_state())):
				for y in xrange(len(self.current_state.get_current_state()[0])):
					if self.current_state.get_current_state()[x][y] == 0:
						game_over = False
						break

			if game_over == True:
				return True
			else:
				return False
		else:
			return True