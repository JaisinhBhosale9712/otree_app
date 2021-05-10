from otree.api import *
import random
import pdb

c = Currency

doc = """
Your app description
"""


class Constants(BaseConstants):
    name_in_url = 'secondproject'
    players_per_group = 2
    num_rounds = 1000


class Subsession(BaseSubsession):
    pass


class Group(BaseGroup):
    pass



class Player(BasePlayer):
    groupa = models.BooleanField()
    groupb = models.BooleanField()
    participant1 = models.StringField()
    participant2 = models.StringField()
    show_now = models.BooleanField(initial=False,label="Do you want to end game")
    correct_ans = models.IntegerField()
    submitted_ans = models.IntegerField()
    correct_ans_result = models.IntegerField(initial=0)
    wrong_ans_result = models.IntegerField(initial=0)
    Option1 = models.FloatField(label="How much do you want to invest in option1")
    Option2 = models.FloatField(label="How much do you want to invest in option2")
    payoff_1 = models.CurrencyField()
    payoff_2 = models.CurrencyField()


def Option1_max(player:Player):
    if player.id_in_group == 1:
        return player.payoff_1
    else:
        return player.payoff_2

def Option2_max(player:Player):
    if player.id_in_group == 1:
        return player.payoff_1 - player.Option1
    else:
        return player.payoff_2 - player.Option1



# PAGESS

class Start0(Page):
    def before_next_page(player: Player, timeout_happened):
        participant = player.participant
        import time

        # remember to add 'expiry' to PARTICIPANT_FIELDS.
        participant.expiry = time.time() + 10

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
        random_number = random.randint(1,8)   #change number of zeros
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
            player.payoff = c(0.01) #change currency here
        else:
            player.wrong_ans_result = 1
            player.correct_ans_result = 0

class Start(Page):
    timeout_seconds = 3
    def vars_for_template(player: Player):

        if player.id_in_group == 1:
            return {
                "true_false": player.participant1,
            }
        else:
            return {
                "true_false": player.participant2,
            }

    def is_displayed(self):
        return self.round_number == 1

class WaitForP1(WaitPage):
    def after_all_players_arrive(group: Group):

        import time

        # remember to add 'expiry' to PARTICIPANT_FIELDS.

        import random
        player_list = group.get_players()
        p1 = player_list[0]
        p2 = player_list[1]
        p1.participant.expiry = time.time() + 135   #change time for round two here
        p2.participant.expiry = time.time() + 135   #change time for round two here
        list_t_f = [True, False]
        p1.groupa = random.choice(list_t_f)
        p2.groupb = not p1.groupa
        #pdb.set_trace()
        if p1.groupa == True:
            p1.participant1 = "A"
            p2.participant2 = "B"

        else:
            p2.participant2 = "A"
            p1.participant1 = "B"

    def is_displayed(group: Group):
        return group.round_number == 1


#set base payout


class Task(Page):
    form_model = 'player'
    form_fields = ['submitted_ans','show_now']

    def get_timeout_seconds(player: Player):
        participant = player.participant
        import time
        return participant.expiry - time.time()

    def vars_for_template(player: Player):
        random_number = random.randint(1, 8)  #change number of zeros dispayed here for round 2
        random_zeros = "0" * random_number
        player.correct_ans = random_zeros.count("0")
        return {
            "random_zeros": random_zeros,
            "player": player
        }

        #

    def before_next_page(player: Player, timeout_happened):
        if player.submitted_ans == player.correct_ans:
            player.wrong_ans_result = 0
            player.correct_ans_result = 1
            player.payoff = c(0.01) #change currency here
        else:
            player.wrong_ans_result = 1
            player.correct_ans_result = 0




class Results(Page):
    form_model = "player"
    form_fields = ["Option1"]

    def is_displayed(player: Player):
        import time
        participant = player.participant
        return participant.expiry - time.time() < 2 or player.show_now == True

    def vars_for_template(player: Player):
        global combined_payoff
        combined_payoff = 0
        total_correct = 0
        total_wrong = -1
        i = 0
        j = 0
        all_players = player.in_all_rounds()
        for each_player in all_players:
            if each_player.id_in_group == 2 and i == 0:
                i = i + 1
                if each_player.groupb == True:
                    combined_payoff = c(0.50)  #change fixed currency for round 2 here

            if each_player.id_in_group == 1 and j == 0:
                j = j + 1
                if each_player.groupa == True:
                    combined_payoff = c(0.50)   #change fixed currency for round 2 here
            if total_wrong == -1:
                total_wrong = 0
            combined_payoff = combined_payoff + float(round(each_player.payoff,2))
            total_correct = total_correct + each_player.correct_ans_result
            total_wrong = total_wrong + each_player.wrong_ans_result
        participant = player.participant
        combined_payoff = combined_payoff + participant.round1result
        if all_players[0].id_in_group == 1:
            player.payoff_1 = combined_payoff
        else:
            player.payoff_2 = combined_payoff



        return {
            "combined_payoff":combined_payoff,"correct_ans_result":total_correct,
            "wrong_ans_result":total_wrong
        }

class Result1(Page):
    form_model = "player"
    form_fields = ["Option2"]

    def is_displayed(player: Player):
        import time
        participant = player.participant
        return player.show_now == True

    def vars_for_template(player: Player):
        if player.id_in_group == 1:
            pay = player.payoff_1
            pay = pay - player.Option1
        else:
            pay = player.payoff_2
            pay = pay - player.Option1

        return {
            "pay":pay
        }

class Result2(Page):
    def is_displayed(player: Player):
        import time
        participant = player.participant
        return player.show_now == True

    def vars_for_template(player: Player):
        if player.id_in_group == 1:
            difference = player.payoff_1 - (player.Option1 + player.Option2)
            option1_amount = player.Option1 + difference
            option2_amount = player.Option2
        else:
            difference = player.payoff_2 - (player.Option1 + player.Option2)
            option1_amount = player.Option1+difference
            option2_amount = player.Option2

        return {
            "option1_amount": option1_amount,
            "option2_amount": option2_amount
        }









page_sequence = [WaitForP1, Start,  Task, Results, Result1, Result2]
