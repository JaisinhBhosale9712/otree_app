from otree.api import *
import random
import pdb

c = Currency

doc = """
Your app description
"""


class Constants(BaseConstants):
    name_in_url = 'yeliz_app'
    players_per_group = None
    num_rounds = 500


class Subsession(BaseSubsession):
    pass


class Group(BaseGroup):
    pass


class Player(BasePlayer):
    correct_ans = models.IntegerField()
    submitted_ans = models.IntegerField()
    correct_ans_result = models.IntegerField(initial=0)
    wrong_ans_result = models.IntegerField(initial=0)



# PAGES

class Start(Page):
    def before_next_page(player: Player, timeout_happened):
        participant = player.participant
        import time

        # remember to add 'expiry' to PARTICIPANT_FIELDS.
        participant.expiry = time.time() + 30  #change time for round one here

    def is_displayed(player: Player):
        return player.round_number == 1


class MyPage(Page):

    form_model = 'player'
    form_fields = ['submitted_ans']

    def get_timeout_seconds(player: Player):
        participant = player.participant
        import time
        return participant.expiry - time.time()


    def vars_for_template(player: Player):
        random_number = random.randint(1,8)  #change number of zeros dispayed here for round 1
        random_zeros = "0"*random_number
        player.correct_ans = random_zeros.count("0")
        return {
            "random_zeros":random_zeros
        }
        #

    def before_next_page(player: Player, timeout_happened):
        if player.submitted_ans == player.correct_ans:
            player.wrong_ans_result = 0
            player.correct_ans_result = 1
            player.payoff = c(0.01)  #change currency here
        else:
            player.wrong_ans_result = 1
            player.correct_ans_result = 0









class Results(Page):
    def vars_for_template(player: Player):
        if player.submitted_ans == player.correct_ans:
            ans = "Correct"
        else:
            ans = "Wrong"
        return {
            "ans":ans
        }

class CombinedResult(Page):
    def is_displayed(player: Player):
        import time
        participant = player.participant
        return participant.expiry - time.time() < 2

    def vars_for_template(player: Player):
        combined_payoff = 0
        total_correct = 0
        total_wrong = 0
        all_players = player.in_all_rounds()
        for each_player in all_players:
            combined_payoff = combined_payoff + float(round(each_player.payoff,2))
            total_correct = total_correct + each_player.correct_ans_result
            total_wrong = total_wrong + each_player.wrong_ans_result
        participant = player.participant
        participant.round1result = combined_payoff
        return {
            "combined_payoff":combined_payoff,"correct_ans_result":total_correct,
            "wrong_ans_result":total_wrong
        }

    @staticmethod
    def app_after_this_page(player:Player, upcoming_apps):
        return upcoming_apps[-1]

page_sequence = [Start, MyPage,  CombinedResult]
