from commands.base_command  import BaseCommand
from utils                  import get_emoji
from random                 import randint

class Roll(BaseCommand):

    def __init__(self):
        description = "Generates a random number between two given numbers"
        params = ["lower", "upper"]
        super().__init__(description, params)

    async def handle(self, params, message, client):
        num_params = len(params)

        try:
            if num_params == 0:
                lower = 1
                upper = 100
            elif num_params == 1:
                lower = 1
                upper = int(params[0])
            elif num_params == 2:
                lower = int(params[0])
                upper = int(params[1])
            else:
                await message.channel.send("Too many arguments")
                return
        except ValueError:
            await message.channel.send("Please provide valid numbers")
            return
        
        if lower < 1:
            await message.channel.send("The values must be greater than 0")

        if lower > upper:
            await message.channel.send("The lower bound cannot be higher than the upper bound")
            return

        value = randint(lower, upper)
        reply = get_emoji(":game_die:") + f" You rolled **{value}** out of **{upper}**!"

        await message.channel.send(reply)
