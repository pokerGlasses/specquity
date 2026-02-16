import time
from src.buttons import PokerState
from src.vision import capture_and_identify
from src.poker_math import calculate_win_rate
from src.ui_driver import PokerHUD

class TexasHoldemBot:
    def __init__(self):
        self.player_cards = []
        self.board = []
        # The 4 main betting rounds of Texas Hold'em
        self.stages = ["PRE-FLOP", "FLOP", "TURN", "RIVER"]
        self.current_stage_idx = 0
        self.hardware = PokerState(self.on_capture, self.on_reset)
        self.hud = PokerHUD()

    def on_capture(self, channel):
        if self.current_stage_idx >= len(self.stages):
            print("Hand finished. Please reset.")
            return

        print(f"\n[!] CAPTURING: {self.stages[self.current_stage_idx]}")
        detected = capture_and_identify()
        
        if self.current_stage_idx == 0: # PRE-FLOP
            self.player_cards = detected[:2]
            if len(self.player_cards) < 2:
                print("Error: Could only see", len(self.player_cards), "cards. Try again.")
                return
        else: # FLOP, TURN, or RIVER
            # Add cards seen by camera that aren't already in your hand or on board
            for card in detected:
                if card not in self.player_cards and card not in self.board:
                    self.board.append(card)
        
        self.current_stage_idx += 1
        self.output_results()

    def on_reset(self, channel):
        self.player_cards = []
        self.board = []
        self.current_stage_idx = 0
        self.hud.show_reset()
        print("\n[RESET] New Hand. Capture your hole cards...")

    def output_results(self):
        win_rate = calculate_win_rate(self.player_cards, self.board)
        self.hud.update(self.stages[self.current_stage_idx-1], self.player_cards, win_rate)
        print(f"--- {self.stages[self.current_stage_idx-1]} RESULTS ---")
        print(f"Your Hand: {self.player_cards}")
        print(f"Community: {self.board}")
        print(f"WIN PROBABILITY: {win_rate:.2f}%")
        
        if win_rate > 70: print("ADVICE: Very Strong - The Nuts!")
        elif win_rate > 50: print("ADVICE: Strong Hand.")
        else: print("ADVICE: Be Cautious.")

if __name__ == "__main__":
    bot = TexasHoldemBot()
    try:
        while True: time.sleep(0.1)
    except KeyboardInterrupt:
        bot.hardware.cleanup()