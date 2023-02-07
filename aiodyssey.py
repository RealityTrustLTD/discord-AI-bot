import os
import io
import discord
import sqlite3
from PIL import Image
from discord.ext import commands
from discord.utils import get
#from stability_sdk import client
#import stability_sdk.interfaces.gooseai.generation.generation_pb2 as generation
import openai
import requests
import ask_openai
#import test
from collections import defaultdict
import datetime
import random

def generate_referral_code(message):
    return str(message.author.id) + str(random.randint(1000, 9999))
    
ask_bot = ask_openai.ask_prompt
#bot = commands.Bot(command_prefix='!')
conn = sqlite3.connect('discord.db')
c = conn.cursor()

conn.commit()
conn.close()

client = discord.Client()

@client.event
async def on_member_join(member):
    # Get the role IDs
    new_member_role_id = IDNUMBER-FOR-NEW-MEMBER-ROLE-HERE
    registered_member_role_id = IDNUMBER-FOR-REGISTERED-MEMBER-ROLE-HERE

    # Add the "New Member" role to the user
    print(f'Adding role {role} to user {member}')
    await member.add_roles(discord.Object(id=new_member_role_id))
    
##BEGIN CONRAD AI FUNCT

MEMORY_LIMIT = 4

class AIPromptResponse:
    def __init__(self, prompt, response, author = "You"):
        self.prompt = prompt
        self.resp = response.strip()
        self.author = author
    def __str__(self):
        return "".join(["\n", self.author, ": ", self.prompt, "\nConrad: ", self.resp, "\n"])

class AIMemory:
    BASE_TEXT="general purpose assistant, PHD level specialties in math, multiple branches of science, history, politics, psychology, metaphysics, occult knowledge, and theology\n\n"
    BASE_PROMPT=AIPromptResponse("conrad what else do you know about this topic?\n", "")
    def __init__(self):
        self.req_resps = []
    def update(self, prompt, response, author="You"):
        self.req_resps.append(AIPromptResponse(prompt, response))
        if len(self.req_resps) > MEMORY_LIMIT:
            self.req_resps.pop(0)
    def clear(self):
        self.req_resps = []
    def get(self):
        result = "".join([self.BASE_TEXT])
        if len(self.req_resps) <= 2:
            result += str(self.BASE_PROMPT)
        else:
            for val in self.req_resps:
                result += str(val)
        return result
##END AI FUNCT

last_ai_request = defaultdict(AIMemory)
enabled_channels = dict()

#CONFIRM CONNECT IN CONSOLE
@client.event
async def on_ready():
    print('Logged in as')
    print(client.user.name)
    print(client.user.id)
    print('------')

##CHECK IF MEMBERS HAVE CHANGED THEIR USERNAME
@client.event
async def on_member_update(before, after):
    if before.name != after.name:
        # Update the database with the new username
        conn = sqlite3.connect('discord.db')
        c = conn.cursor()
        c.execute("UPDATE users SET name=? WHERE id=?", (after.name, after.id))
        conn.commit()
        conn.close()
        

###COMMAND FUNCTIONS###
@client.event
async def on_message(message):

# Set up environment variables for API key for OPEN AI
    os.environ['OPENAI_API_KEY'] = 'YOUR-OPEN-AI-API-KEY-GOES-HERE' ###OPEN AI API KEY
    ###ALT KEY os.environ['OPENAI_API_KEY'] = 'AN-ALTERNATE-KEY-SPACE' 
# Set up connection to OpenAI API
    openai.api_key = os.environ['OPENAI_API_KEY']
    
# Set up environment variables for host and API key in stable diffusion
    os.environ['STABILITY_HOST'] = 'grpc.stability.ai:443'
    os.environ['STABILITY_KEY'] = 'STABILITY-AI-API-KEY-GOES-HERE'
    
    #stability_api = client.StabilityInference(
        #key=os.environ['STABILITY_KEY'], # API Key reference.
        #verbose=True, # Print debug messages.
        #engine="stable-diffusion-v1-5", # Set the engine to use for generation. 
         #Available engines: stable-diffusion-v1 stable-diffusion-v1-5 stable-diffusion-512-v2-0 stable-diffusion-768-v2-0 
         #stable-diffusion-512-v2-1 stable-diffusion-768-v2-1 stable-inpainting-v1-0 stable-inpainting-512-v2-0
#)

##TEST THE BOT CONNECTION   
    if message.content.startswith('!stable'):
        await message.channel.send('this command is currently causing problems use **!dalle** instead for now.')

###ADMIN#!LISTUSERS COMMAND 
    if message.content == '!listusers':
        # Check if the user has the appropriate role to run this command
        if "Administrator" in [role.name for role in message.author.roles]:
            # Connect to the database
            conn = sqlite3.connect('discord.db')
            c = conn.cursor()
            
            # Get a list of all users from the database
            c.execute("SELECT * FROM users")
            users = c.fetchall()
            
            # Create the list of users to display
            user_list = []
            for user in users:
                user_list.append(f"{user[1]} (ID: {user[0]}) - Level: {user[3]} - Currency: {user[2]} - Character Count: {user[4]}")
            
            # Send the list of users to the channel
            await message.channel.send("\n".join(user_list))
            
            # Close the database connection
            conn.close()
        else:
            # If the user does not have the appropriate role, send an error message
            await message.channel.send("You do not have permission to use this command.")

####ADDME COMMAND            
    if message.content == '!addme':
        # Connect to the database
        conn = sqlite3.connect('discord.db')
        c = conn.cursor()
        # Get the role IDs
        #new_member_role_id = NEW-MEMBER-ROLE-ID
        registered_member_role_id = REGISTERED-registered_member_role_id
        # Check if the user is already in the database
        c.execute("SELECT * FROM users WHERE id=?", (message.author.id,))
        result = c.fetchone()
        if result is None:
            # If the user is not in the database, insert them with default values
            c.execute("INSERT INTO users (id, name, currency, level, character_count) VALUES (?, ?, ?, ?, ?)", (message.author.id, message.author.name, 25, 0, 0))
            conn.commit()
            # Add the "Registered Member" role to the user
            await message.author.add_roles(discord.Object(id=registered_member_role_id))
            await message.channel.send("Welcome to AI ODYSSEY! You have been added with 25 currency. You have also been given the Registered Member role.")
        else:
            # If the user is already in the database, send an error message
            await message.channel.send("You are already in the database.")
        # Close the database connection
        conn.close()
#####BASIC SUBSCRIPTION
    if message.content == '!basicsub':
        # Connect to the database
        conn = sqlite3.connect('discord.db')
        c = conn.cursor()

        # Retrieve the user's currency from the database
        c.execute("SELECT currency FROM users WHERE id=?", (message.author.id,))
        result = c.fetchone()
        if result is None:
            # If the user is not in the database, send an error message and return
            await message.channel.send("You are not a registered member of the server. Use the !addme command to register and become a member.")
            return

        # If the user is in the database, check if they have enough currency
        currency = result[0]
        if currency < 10000:
            await message.channel.send("You don't have enough currency to purchase the Basic Subscriber role. Earn more currency by participating in the chat or ask a friend to use the !pay command to transfer currency from other users.")
            return

        # If the user has enough currency, add the Basic Subscriber role
        role = discord.utils.get(message.guild.roles, id=BSUB_member_role_id) ##ADD YOUR ROLE ID FOR BSUB MEMBERS HERE
        print(f'Adding role {role} to user {message.author}')
        await message.author.add_roles(role)
        await message.channel.send(f'Successfully added the Basic Subscriber role to {message.author.mention}')

        # Deduct 10000 currency from the user's total
        currency -= 10000
        c.execute("UPDATE users SET currency=? WHERE id=?", (currency, message.author.id))
        conn.commit()
        
        # Send a message indicating the charge and remaining balance
        await message.channel.send(f'Charged **10000** currency. Remaining balance: {currency}')

        # Close the database connection
        conn.close()
    
###########PREMIUM MEMBERS
    if message.content == '!premiumsub':
        # Connect to the database
        conn = sqlite3.connect('discord.db')
        c = conn.cursor()

        # Retrieve the user's currency from the database
        c.execute("SELECT currency FROM users WHERE id=?", (message.author.id,))
        result = c.fetchone()
        if result is None:
            # If the user is not in the database, send an error message and return
            await message.channel.send("You are not a registered member of the server. Use the !addme command to register and become a member.")
            return

        # If the user is in the database, check if they have enough currency
        currency = result[0]
        if currency < 1000000:
            await message.channel.send("You don't have enough currency to purchase the Basic Subscriber role. Earn more currency by participating in the chat or ask a friend to use the !pay command to transfer currency from other users.")
            return

        # If the user has enough currency, add the Premium Subscriber role
        role = discord.utils.get(message.guild.roles, id=PSUB_member_role_id) ##ADD YOUR ROLE ID FOR PSUB MEMBERS HERE
        print(f'Adding role {role} to user {message.author}')
        await message.author.add_roles(role)
        await message.channel.send(f'Successfully added the Basic Subscriber role to {message.author.mention}')

        # Deduct 10000 currency from the user's total
        currency -= 1000000
        c.execute("UPDATE users SET currency=? WHERE id=?", (currency, message.author.id))
        conn.commit()
        
        # Send a message indicating the charge and remaining balance
        await message.channel.send(f'Charged **1,000,0000** currency. Remaining balance: {currency}')

        # Close the database connection
        conn.close()

##!PAY (USER) (AMOUNT) COMMAND	
    if message.content.startswith('!pay'):
        # Split the message into arguments
        args = message.content.split()
        
        # Check if the correct number of arguments was provided
        if len(args) < 3:
            await message.channel.send("Invalid number of arguments. Use the format: !pay [recipient] [amount]")
            return
        
        # Get the recipient's username and the amount to transfer
        recipient_name = " ".join(args[1:-1])
        amount = int(args[-1])
        
        # Connect to the database
        conn = sqlite3.connect('discord.db')
        c = conn.cursor()
        
        # Check if the recipient is in the database
        c.execute("SELECT * FROM users WHERE name=?", (recipient_name,))
        recipient = c.fetchone()
        if recipient is None:
            await message.channel.send("That user doesnt exist. Make sure to check the CAPITALIZATION and for any p.u.n.c.t.u.a.t.i.o.n. in the username you are attempting to send to.")
            return
        
        # Check if the sender has enough currency to make the transfer
        c.execute("SELECT * FROM users WHERE id=?", (message.author.id,))
        sender = c.fetchone()
        if sender[2] < amount:
            await message.channel.send("You do not have enough currency to make this transfer.")
            return
        
        # Update the sender's and recipient's currency in the database
        c.execute("UPDATE users SET currency=currency-? WHERE id=?", (amount, message.author.id))
        c.execute("UPDATE users SET currency=currency+? WHERE id=?", (amount, recipient[0]))
        conn.commit()
        
        # Send a confirmation message
        await message.channel.send(f"{amount} currency transferred from {message.author.name} to {recipient_name}.")

##ADMIN##### !SETLEVEL (USER) (LEVEL) this function is used to allow people to generate a referral code (1) is the needed level
	
    if message.content.startswith('!setlevel'):
        # Check if the user has the appropriate role to run this command
        if "Administrator" in [role.name for role in message.author.roles]:
            # Split the message into arguments
            args = message.content.split()
            
            # Check if the correct number of arguments was provided
            if len(args) < 3:
                await message.channel.send("Invalid number of arguments. Use the format: !setlevel [username] [level]")
                return
            
            # Get the username and the level to set
            username = " ".join(args[1:-1])
            level = int(args[-1])
            
            # Connect to the database
            conn = sqlite3.connect('discord.db')
            c = conn.cursor()
            
            # Check if the user is in the database
            c.execute("SELECT * FROM users WHERE name=?", (username,))
            user = c.fetchone()
            if user is None:
                await message.channel.send("User not found.")
                return
            
            # Update the user's level in the database
            c.execute("UPDATE users SET level=? WHERE id=?", (level, user[0]))
            conn.commit()
            
            # Send a confirmation message
            await message.channel.send(f"{username}'s level set to {level}.")
        else:
            # If the user does not have the appropriate role, send an error message
            await message.channel.send("You do not have permission to use this command.")
    
##ADMIN#### !REMOVEUSER (USER)   
    if message.content.startswith('!removeuser'):
        # Check if the user has the appropriate role to run this command
        if "Administrator" in [role.name for role in message.author.roles]:
            # Split the message into arguments
            args = message.content.split()
            
            # Check if the correct number of arguments was provided
            if len(args) < 2:
                await message.channel.send("Invalid number of arguments. Use the format: !removeuser [username]")
                return
            
            # Get the username to remove
            username = " ".join(args[1:])
            
            # Connect to the database
            conn = sqlite3.connect('discord.db')
            c = conn.cursor()
            
            # Check if the user is in the database
            c.execute("SELECT * FROM users WHERE name=?", (username,))
            user = c.fetchone()
            if user is None:
                await message.channel.send("User not found.")
                return
            
            # Remove the user from the database
            c.execute("DELETE FROM users WHERE id=?", (user[0],))
            conn.commit()
            
            # Send a confirmation message
            await message.channel.send(f"{username} removed from the database.")
        else:
            # If the user does not have the appropriate role, send an error message
            await message.channel.send("You do not have permission to use this command.")

##USERS CAN CHECK THEIR !CURRENCY
    if message.content == '!currency':
        # Connect to the database
        conn = sqlite3.connect('discord.db')
        c = conn.cursor()
        
        # Get the user's currency balance from the database
        c.execute("SELECT currency FROM users WHERE id=?", (message.author.id,))
        result = c.fetchone()
        
        if result is None:
            # If the user is not in the database, send an error message
            await message.channel.send("You are not a full member of the server! TYPE **!addme** in the chat to add yourself with full membership. Then use the **!help** command to see more options.")
        else:
            # If the user is in the database, send their currency balance
            await message.channel.send(f"Your currency balance is {result[0]}.")
            
        # Close the database connection
        conn.close()

##USERS CAN CHECK THEIR referal code    
    if message.content == '!mycode':
        # Connect to the database
        conn = sqlite3.connect('discord.db')
        c = conn.cursor()
        
        # Get the user's level from the database
        c.execute("SELECT level FROM users WHERE id=?", (message.author.id,))
        result = c.fetchone()
        
        if result is None:
            # If the user is not in the database, send an error message
            await message.channel.send("You are not a full member of the server! TYPE **!addme** in the chat to add yourself with full membership. Then use the **!help** command to see more options.")
        else:
            # If the user is in the database, send their level
            await message.channel.send(f"Your referral code is {result[0]}.")
            
        # Close the database connection
        conn.close()
    
###ADMIN WIPE COMMAND    # Check if the message starts with !wipe
    if message.content.startswith('!wipe'):
        # Split the message into arguments
        args = message.content.split()

        # Check if the correct number of arguments was provided
        if len(args) != 2:
            await message.channel.send("Invalid number of arguments. Use the format: !wipe [number of messages]")
            return

        # Check if the user has the appropriate role to run this command
        if "Administrator" in [role.name for role in message.author.roles]:
            # Get the number of messages to delete
            num_messages = int(args[1])

            # Check if the number of messages to delete is within the valid range (1-99)
            if num_messages < 1 or num_messages > 99:
                await message.channel.send("Number of messages must be between 1 and 99.")
                return

            # Get a list of the specified number of messages in the channel
            messages = await message.channel.history(limit=num_messages).flatten()
            
            # Delete the messages
            await message.channel.delete_messages(messages)
            await message.channel.send(f"{num_messages} messages deleted.")
        else:
            # If the user does not have the appropriate role, send an error message
            await message.channel.send("You do not have permission to use this command.")
            
##!STATS COMMAND
    if message.content == '!thiscommandisdepreciated':
        # Connect to the database
        conn = sqlite3.connect('discord.db')
        c = conn.cursor()
        
        # Get the user's database information
        c.execute("SELECT * FROM users WHERE id=?", (message.author.id,))
        user_data = c.fetchone()
        if user_data is None:
            # If the user is not in the database, send an error message
            await message.channel.send("You are not a full member of the server! TYPE **!addme** in the chat to add yourself with full membership. Then use the **!help** command to see more options.")
        else:
            # If the user is in the database, retrieve their Discord information
            user_info = await client.fetch_user(message.author.id)
            
            # Create the stats message
            stats_message = f"Username: {user_info.name}\n"
            stats_message += f"ID: {user_info.id}\n"
            stats_message += f"Level: {user_data[3]}\n"
            stats_message += f"Currency: {user_data[2]}\n"
            stats_message += f"Character Count: {user_data[4]}\n"
            stats_message += f"Created At: {user_info.created_at}\n"
            stats_message += f"Avatar URL: {user_info.avatar_url}"
            
            # Send the stats message to the channel
            await message.channel.send(stats_message)
        
        # Close the database connection
        conn.close()

##ADMIN ####ADD FUNDS TO USER !ADDFUNDS
    if message.content.startswith('!addfunds'):
        # Split the command into the command name and the arguments
        command, *args = message.content.split()

        # Check if the user has the required permissions to use this command
        if not message.author.guild_permissions.manage_guild:
            await message.channel.send("You don't have permission to use this command.")
            return

        # Check if the correct number of arguments was provided
        if len(args) != 2:
            await message.channel.send("Invalid number of arguments. Usage: !addfunds <ID> <amount>")
            return

        # Parse the ID and amount arguments
        try:
            id = int(args[0])
            amount = int(args[1])
        except ValueError:
            await message.channel.send("Invalid ID or amount. ID must be an integer and amount must be a non-negative integer.")
            return

        # Connect to the database
        conn = sqlite3.connect('discord.db')
        c = conn.cursor()

        # Retrieve the user's currency from the database
        c.execute("SELECT currency FROM users WHERE id=?", (id,))
        result = c.fetchone()
        if result is None:
            # If the user is not in the database, send an error message
            await message.channel.send("User not found in the database.")
        else:
            # If the user is in the database, add the specified amount to their currency
            currency = result[0]
            currency += amount
            c.execute("UPDATE users SET currency=? WHERE id=?", (currency, id))
            conn.commit()

            # Send a message indicating the update
            await message.channel.send(f'Added {amount} currency to user with ID {id}. New balance: {currency}')

        # Close the database connection
        conn.close()
        
##VIEW CHARACTER BALANCE
    #Check if the message is !characters
    if message.content == '!characters':
        # Connect to the database
        conn = sqlite3.connect('discord.db')
        c = conn.cursor()

        # Get the user's record from the database
        c.execute("SELECT * FROM users WHERE id=?", (message.author.id,))
        user = c.fetchone()

        # Check if the user is in the database
        if user is None:
            await message.channel.send("You are not in the database. Please use the !addme command to add yourself to the database. We will give you 50 currency for joining!")
            return

        # Calculate the amount of currency the user's characters can be exchanged for
        currency = user[4] // 500

        # Send a message to the channel indicating the user's character count and how much currency the characters can be exchanged for
        await message.channel.send(f"You have {user[4]} characters. They can be exchanged for {currency} currency using the !exchange command. The exchange rate is 500:1")

        # Close the database connection
        conn.close()
    
###DALLE IMAGE GENERATION            
    if message.content.startswith('!dalle'):
        # Connect to the database
        conn = sqlite3.connect('discord.db')
        c = conn.cursor()

        # Retrieve the user's currency from the database
        c.execute("SELECT currency FROM users WHERE id=?", (message.author.id,))
        result = c.fetchone()
        if result is None:
            # If the user is not in the database, send an error message and return
            await message.channel.send("You are not a full member of the server! TYPE **!addme** in the chat to add yourself with full membership. Then use the **!help** command to see more options.")
            return

        # If the user is in the database, check if they have enough currency
        currency = result[0]
        if currency < 2:
            await message.channel.send("You don't have enough currency to use this command. Earn more currency by participating in the chat or ask a friend to use the **!pay** command to transfer currency from other users.")
            return

        # If the user has enough currency, generate the image
        prompt = message.content[len('!dalle'):].strip()
        print(f'Generating image with prompt: {prompt}')
        response = openai.Image.create(
            model='image-alpha-001',
            size='512x512',
            prompt=prompt
        )
        print(f'Received response from OpenAI API: {response}')

        # Save generated image
        img_url = response['data'][0]['url']
        print(f'Received image URL: {img_url}')
        img = Image.open(requests.get(img_url, stream=True).raw)
        img_file = io.BytesIO()
        img.save(img_file, format='PNG')
        img_file.seek(0)
        #await message.channel.send(file=discord.File(img_file, 'image.png'))
        await message.channel.send(f'{message.author.mention} generated this image using the prompt: **{prompt}** ...Charged **2** currency. Remaining balance: {currency}', file=discord.File(img_file, 'image.png'))

        # Deduct 2 currency from the user's total
        currency -= 2
        c.execute("UPDATE users SET currency=? WHERE id=?", (currency, message.author.id))
        conn.commit()
        
        # Send a message indicating the charge and remaining balance
        #await message.channel.send(f'Charged **2** currency. Remaining balance: {currency}')

        # Close the database connection
        conn.close()
    
####EXCHANGE## Check if the message starts with !exchange
    if message.content.startswith('!exchange'):
        # Split the message into arguments
        args = message.content.split()

        # Check if the correct number of arguments was provided
        if len(args) != 2:
            await message.channel.send("Command invalid. Use the format: !exchange [character count] The exchange rate is 500:1 so make sure you make exchanges in multiples of 500")
            return

        # Get the character count to exchange
        character_count = int(args[1])

        # Calculate the currency to be earned based on the exchange rate (500 characters per 1 currency)
        currency = character_count // 500

        # Connect to the database
        conn = sqlite3.connect('discord.db')
        c = conn.cursor()

        # Get the user's record from the database
        c.execute("SELECT * FROM users WHERE id=?", (message.author.id,))
        user = c.fetchone()

        # Check if the user is in the database
        if user is None:
            await message.channel.send("You are not a full member of the server! TYPE **!addme** in the chat to add yourself with full membership. Then use the **!help** command to see more options.")
            return

        # Check if the user has enough characters to exchange
        if user[4] < character_count:
            await message.channel.send("You do not have enough characters to exchange. The exchange rate is 500:1 so you must have at least 500 characters. Participate in the chate to earn more characters!")
            return

        # Deduct the exchanged characters from the user's character count
        c.execute("UPDATE users SET character_count=character_count-? WHERE id=?", (character_count, message.author.id))
        conn.commit()

        # Add the exchanged currency to the user's currency
        c.execute("UPDATE users SET currency=currency+? WHERE id=?", (currency, message.author.id))
        conn.commit()

        # Send a message to the channel indicating how many characters were exchanged and how much currency was earned
        await message.channel.send(f"{character_count} characters exchanged for {currency} currency.")

        # Close the database connection
        conn.close()
    
#####CONRAD AI# Check if the message is !conrad
    data = message.content
    source = ""
    if message.content.startswith('!conrad'):
        # Connect to the database
        conn = sqlite3.connect('discord.db')
        c = conn.cursor()

        # Get the user's record from the database
        c.execute("SELECT * FROM users WHERE id=?", (message.author.id,))
        user = c.fetchone()

        # Check if the user is in the database
        if user is None:
            # If the user is not in the database, encourage them to join
            await message.channel.send("You are not a full member of the server! TYPE **!addme** in the chat to add yourself with full membership. Then use the **!help** command to see more options.")
            return

        # Check if the user has enough currency to make the request
        if user[2] < 5:
            await message.channel.send("You do not have enough currency to make this request.")
            return

        # Deduct 5 currency from the user's balance
        c.execute("UPDATE users SET currency=currency-5 WHERE id=?", (message.author.id,))
        conn.commit()

        # Get the prompt from the message
        prompt = message.content[len('!conrad'):].strip()

        # Format the prompt for the bot
        ai_prompt = "{0}\nYou: {1}\nConrad:".format(last_ai_request[source].get(), prompt)

        # Send the prompt to the bot and get the response
        result = ask_bot(ai_prompt)
        if result is not None:
            last_ai_request[source].update(prompt, result)
            await message.channel.send(result)

        # Close the database connection
        conn.close()
    
###EARN # Check if the message is !earn
    if message.content == '!earn':
        # Connect to the database
        conn = sqlite3.connect('discord.db')
        c = conn.cursor()

        # Get the user's record from the database
        c.execute("SELECT * FROM users WHERE id=?", (message.author.id,))
        user = c.fetchone()

        # Check if the user is in the database
        if user is None:
            # If the user is not in the database, encourage them to join
            await message.channel.send("You are not in the database. Use the !addme command to join.")
            return

        # Get the current time and the user's last earnings date
        current_time = datetime.datetime.now()
        last_earnings_date = user[5]

        # Check if it has been at least 5 hours since the user's last earnings
        if last_earnings_date is not None:
            last_earnings_date = datetime.datetime.fromisoformat(last_earnings_date)
            time_remaining = datetime.timedelta(hours=5) - (current_time - last_earnings_date)
            if time_remaining.total_seconds() > 0:
                await message.channel.send(f"You have already earned currency today. Please try again in {time_remaining}.")
                return

        # Update the user's currency balance and last earnings date in the database
        c.execute("UPDATE users SET currency=currency+5, last_earnings_date=? WHERE id=?", (current_time, message.author.id))
        conn.commit()

        # Send a message to the user indicating that they have earned currency
        await message.channel.send("You have earned 5 currency!")

        # Close the database connection
        conn.close()
 ###ECONOMY COMMAND   
    if message.content == '!economy':
        # Connect to the database
        conn = sqlite3.connect('discord.db')
        c = conn.cursor()

        # Retrieve total currency in circulation from the database
        c.execute("SELECT SUM(currency) FROM users")
        result = c.fetchone()
        total_currency = result[0]

        # Retrieve number of registered users from the database
        c.execute("SELECT COUNT(*) FROM users")
        result = c.fetchone()
        num_users = result[0]

        # Calculate average currency per user
        average_currency = total_currency / num_users

        # Send a message with the economy data
        await message.channel.send(f'Total currency in circulation: {total_currency}\nNumber of registered users: {num_users}\nAverage currency per user: {average_currency:.2f}')

        # Close the database connection
        conn.close()
 ####ADMIN GIFT COMMAND   
    if message.content.startswith('!gift'):
        # Check if the user has the appropriate role to run this command
        if "Administrator" in [role.name for role in message.author.roles]:
            # Split the command into the currency amount and public message
            prompt = message.content[len('!gift'):].strip()
            prompt_parts = prompt.split(' ', 1)
            if len(prompt_parts) < 2:
                # If the command is not formatted correctly, send an error message
                await message.channel.send("Invalid command format. Please use !gift [amount] [message].")
                return
            currency_amount = int(prompt_parts[0])
            public_message = prompt_parts[1]

            # Connect to the database
            conn = sqlite3.connect('discord.db')
            c = conn.cursor()

            # Give the specified amount of currency to all registered users
            c.execute("UPDATE users SET currency=currency+?", (currency_amount,))
            conn.commit()

            # Close the database connection
            conn.close()

            # Send the public message to the specified channel
            channel = client.get_channel(1058157154856607814)
            await channel.send(public_message)
        else:
            # If the user does not have the appropriate role, send an error message
            await message.channel.send("You do not have permission to use this command.")
####BEGIN STORYFLOW
    if message.content.startswith('!story'):
        # Connect to the database
        conn = sqlite3.connect('discord.db')
        c = conn.cursor()

        # Retrieve the user's currency from the database
        c.execute("SELECT currency FROM users WHERE id=?", (message.author.id,))
        result = c.fetchone()
        if result is None:
            # If the user is not in the database, send an error message and return
            await message.channel.send("You are not a registered member of the server! Use the **!addme** command to register and gain access to more commands.")
            return

        # If the user is in the database, check if they have enough currency
        currency = result[0]
        if currency < 50:
            await message.channel.send("You don't have enough currency to use this command. Earn more currency by participating in the chat or ask a friend to use the **!pay** command to transfer currency from other users.")
            return

        # If the user has enough currency, generate the story
        prompt = message.content[len('!story'):].strip()
        print(f'Generating story with prompt: {prompt}')
        response = openai.Completion.create(
            engine='text-davinci-003',
            prompt=prompt,
            max_tokens=512,
            temperature=0.8
        )
        print(f'Received response from OpenAI API: {response}')
        story = response['choices'][0]['text']

        # Send the generated story to the channel
        await message.channel.send(f'{story}\n\n**Prepare your responses with the !action command. ..When you (or) the group is ready to continue the story, use the !continue command.**')

        # Deduct 50 currency from the user's total
        currency -= 50
        c.execute("UPDATE users SET currency=? WHERE id=?", (currency, message.author.id))
        conn.commit()

        # Send a message indicating the charge and remaining balance
        await message.channel.send(f'Charged **50** currency. Remaining balance: {currency}')

        # Close the database connection
        conn.close()
    
    if message.content.startswith('!action'):
        # Connect to the database
        conn = sqlite3.connect('discord.db')
        c = conn.cursor()

        # Retrieve the user's currency from the database
        c.execute("SELECT currency FROM users WHERE id=?", (message.author.id,))
        result = c.fetchone()
        if result is None:
            # If the user is not in the database, send an error message and return
            await message.channel.send("You are not a full member of the server! TYPE **!addme** in the chat to add yourself with full membership. Then use the **!help** command to see more options.")
            return

        # If the user is in the database, check if they have enough currency
        currency = result[0]
        if currency < 1:
            await message.channel.send("You don't have enough currency to use this command. Earn more currency by participating in the chat or ask a friend to use the **!pay** command to transfer currency from other users.")
            return
#####STORYFLOW ACTION 

        # If the user has enough currency, add their action to the database
        prompt = message.content[len('!action'):].strip()
        action_conn = sqlite3.connect('action.db')
        action_c = action_conn.cursor()
        action_c.execute("INSERT INTO actions (username, prompt) VALUES (?, ?)", (message.author.name, prompt))
        action_conn.commit()
        action_conn.close()

        # Deduct 3 currency from the user's total
        currency -= 1
        c.execute("UPDATE users SET currency=? WHERE id=?", (currency, message.author.id))
        conn.commit()
        
        # Send a message indicating the charge and remaining balance
        await message.channel.send(f'Action Submitted: Charged **1** currency. Remaining balance: {currency}')

        # Close the database connection
        conn.close()

####CONTINUE STORYFLOW 
    if message.content == '!continue':
    
        # Connect to the database
        conn = sqlite3.connect('discord.db')
        c = conn.cursor()

        # Retrieve the user's currency from the database
        c.execute("SELECT currency FROM users WHERE id=?", (message.author.id,))
        result = c.fetchone()
        if result is None:
            # If the user is not in the database, send an error message and return
            await message.channel.send("You are not a full member of the server! TYPE **!addme** in the chat to add yourself with full membership. Then use the **!help** command to see more options.")
            return

        # If the user is in the database, check if they have enough currency
        currency = result[0]
        if currency < 3:
            await message.channel.send("It costs 3 Currency to continue a story. You don't have enough currency to use this command. Earn more currency by participating in the chat or ask a friend to use the **!pay** command to transfer currency from other users.")
            return
        
        # Connect to the action database
        action_conn = sqlite3.connect('action.db')
        action_c = action_conn.cursor()

        # Retrieve all of the actions from the database
        action_c.execute("SELECT username,prompt FROM actions")
        actions = action_c.fetchall()

        # Concatenate the actions and user names into a single string
        action_string = ' '.join(['{}: {}'.format(action[0], action[1]) for action in actions if len(action) == 2])
        #action_string = ' '.join([action[0] for action in actions if isinstance(action[0], str)])
        print(f"Expected Action String {action_string}")
        # Send the action string to OpenAI's API for summarization
        summary = openai.Completion.create(engine="text-davinci-003", prompt=action_string, temperature=0.6, top_p=1, frequency_penalty=0.5, max_tokens=300)

        # Hold the summarization in a variable
        summary_text = summary['choices'][0]['text']
        print(summary_text)
        await message.channel.send(f'{summary_text}\n\n')

        # Deduct 3 currency from the user's total
        currency -= 3
        c.execute("UPDATE users SET currency=? WHERE id=?", (currency, message.author.id))
        conn.commit()
        
        
            # Generate the image
        prompt = summary_text
        print(f'Generating image with prompt: {prompt}')
        
        try:
            # Generate the image using the OpenAI API
            response = openai.Image.create(
                model='image-alpha-001',
                size='512x512',
                prompt=prompt
            )
            img_url = response['data'][0]['url']
        except openai.error.InvalidRequestError:
            # If the request was rejected, display a local image file instead
            img_url = 'https://picsum.photos/200'
        else:
            img_url = response['data'][0]['url']
            print(f'Received image URL: {img_url}')
        img = Image.open(requests.get(img_url, stream=True).raw)
        img_file = io.BytesIO()
        img.save(img_file, format='PNG')
        img_file.seek(0)
        
        #Send the photo to the channel 
        await message.channel.send(file=discord.File(img_file, 'image.png'))

        # Close the database connection
        conn.close()
        
        # Send a message indicating the charge and remaining balance
        #await message.channel.send(f'SYSTEM Charged **3** currency. Remaining balance: {currency}')

        # Clear the database
        action_c.execute("DELETE FROM actions")
        action_conn.commit()

        # Add a new entry to the database with the summary as the username and "Convert my short hand into a third party account" as the prompt
        #action_c.execute("INSERT INTO actions (username, prompt) VALUES (?, ?)", (".", "Convert this short list of actions into a two paragraph short story. Leave the storyline open for continuation."))
        # Add a new entry to the database with the summary as the username and "Convert my short hand into a third party account" as the prompt
        action_c.execute("INSERT INTO actions (username, prompt) VALUES (?, ?)", (summary_text[:400], "add these story details together and take a paragraph to continue, but not conclude the story."))
        action_conn.commit()
        #action_conn.commit()

        # Close the database connection
        action_conn.close()

        # Continue the story
        # Use the summary text to query OpenAI and continue the story
        #story = openai.Completion.create(engine="text-davinci-003", prompt=summary_text, temperature=0.5, top_p=1, frequency_penalty=0.5, max_tokens=150)
        #story_text = story['choices'][0]['text']
        #print(story_text)
        await message.channel.send(f'\n\n**SYSTEM CHARGED 3 CURRENCY - Prepare your responses with the !action command. ..When you (or) the group is ready to continue the story, use the !continue command.**')

    if message.content == '!endstory':
        # Connect to the action database
        action_conn = sqlite3.connect('action.db')
        action_c = action_conn.cursor()

        # Clear the database
        action_c.execute("DELETE FROM actions")
        action_conn.commit()

        # Add a new entry to the database with the summary as the username and "Convert my short hand into a third party account" as the prompt
        action_c.execute("INSERT INTO actions (username,prompt) VALUES (?,?)", ("Story prompt", "add these story details together and take a paragraph to continue, but not conclude the story."))
        action_conn.commit()

        # Close the database connection
        action_conn.close()

        # Send a message indicating that the story has ended and a new one has started
        await message.channel.send("The story has been ended. Use the **!story** command to begin a new story.")


####REPORT COMMAND
    if message.content.startswith('!report'):
        # Split the message into the command and the arguments
        report_message = message.content.split(' ')
        # Check if the user provided a target and a reason for the report
        if len(report_message) < 3:
            await message.channel.send("Invalid report format. Use `!report [user] [reason]`.")
            return

        # Get the target and reason for the report
        target = report_message[1]
        reason = ' '.join(report_message[2:])

        # Send a message to the Administrator role notifying them of the report
        report_embed = discord.Embed(title="User Report", color=0xFF0000)
        report_embed.add_field(name="Reporter", value=f"{message.author.mention}", inline=False)
        report_embed.add_field(name="Target", value=f"{target}", inline=False)
        report_embed.add_field(name="Reason", value=f"{reason}", inline=False)
        await message.channel.send(embed=report_embed, content="REPORT SENT")
        # Get the @Administrators role object
        #admins_role = discord.utils.get(message.guild.roles, name='Administrators')
    
        # Send the report to the @Administrators role
        #await message.channel.send(f'{admins_role.mention} The user {target_user} has been reported for the following reason: {reason}')
###GENERATE REFERRAL CODE        
    if message.content.startswith('!getcode'):
        
        # Connect to the database
        conn = sqlite3.connect('discord.db')
        c = conn.cursor()

        # Retrieve the user's level from the database
        c.execute("SELECT level FROM users WHERE id=?", (message.author.id,))
        result = c.fetchone()
        if result is None:
            # If the user is not in the database, send an error message and return
            await message.channel.send("You are not a full member of the server! TYPE **!addme** in the chat to add yourself with full membership. Then use the **!help** command to see more options.")
            return
        # If the user's level is not 1, send an error message and return
        elif result[0] != 1:
            await message.channel.send("You must have an invite to generate a code, contact an ADMIN to unlock.")
            return

        # If the user is a level 1 member, generate a referral code and store it in the database
        # Generate a random 9 digit whole number
        referral_code = random.randint(1000000000, 9999999999)

        # Store the referral code in the database
        c.execute("UPDATE users SET level=? WHERE id=?", (referral_code, message.author.id))
        conn.commit()

        # Send a message with the referral code to the user
        await message.channel.send(f'Your referral code is: {referral_code}')

        # Close the database connection
        conn.close()
####REDEEEM REFERRAL CODE
    if message.content.startswith('!referral'):
        # Connect to the database
        conn = sqlite3.connect('discord.db')
        c = conn.cursor()

        # Retrieve the referral code being redeemed and the user's referral code
        referral_code = message.content.split()[1]  # Get the second element in the list (the referral code)
        c.execute("SELECT level FROM users WHERE id=?", (message.author.id,))
        result = c.fetchone()
        #user_referral_code = result[0]
        user_referral_code = str(result[0])
        print(type(referral_code))
        print(type(user_referral_code))
        # Check if the referral code being redeemed matches the user's referral code
        if referral_code == user_referral_code:
            await message.channel.send("You cannot redeem your own referral code.")
            return
            
        # Check if the referral code is valid
        c.execute("SELECT * FROM users WHERE level=?", (referral_code,))
        result = c.fetchone()
        if result is None:
            # If the referral code is not valid, send an error message and return
            await message.channel.send("Invalid referral code. Please check your referral code and try again.")
            return
            
        # If the referral code is valid, reward the user and the referrer
        c.execute("UPDATE users SET currency=currency+50 WHERE id=?", (message.author.id,))
        c.execute("UPDATE users SET currency=currency+100 WHERE id=(SELECT id FROM users WHERE level=?)", (referral_code,))
        
        # Destroy the referral code
        c.execute("UPDATE users SET level=NULL WHERE id=(SELECT id FROM users WHERE level=?)", (referral_code,))
        
        # Commit the changes to the database and close the connection
        conn.commit()
        conn.close()
        
        # Send a message indicating that the referral has been redeemed
        await message.channel.send("Referral redeemed. You have received 50 currency. The referrer has also received a bonus thanks to you!")
####ADMIN REFERRAL CODE
    if message.content.startswith('!admincode'):
        # Split the command into a list of arguments
        args = message.content.split()

        # Check if the user is an admin
        if message.author.permissions_in(message.channel).administrator:
            # Connect to the database
            conn = sqlite3.connect('discord.db')
            c = conn.cursor()

            # Check if the user is in the database
            c.execute("SELECT * FROM users WHERE id=?", (args[1],))
            result = c.fetchone()
            if result is None:
                await message.channel.send("That user is not in the database!")
                return

            # Generate a referral code for the user
            code = random.randint(1000000000, 9999999999)
            c.execute("UPDATE users SET level=? WHERE id=?", (code, args[1]))
            conn.commit()

            # Send the referral code to the user
            user = message.guild.get_member(int(args[1]))
            #await user.send(f'Your referral code is: {code}')
            await message.channel.send(f'The Users Code is {code}')
        else:
            await message.channel.send("You do not have permission to use this command!")




####SET CURRENCY 
    if message.content.startswith('!setcurrency'):
        # Connect to the database
        conn = sqlite3.connect('discord.db')
        c = conn.cursor()

        # Parse the ID number and value from the command message
        try:
            id_num, value = message.content[len('!setcurrency'):].strip().split()
            id_num = int(id_num)
            value = int(value)
        except ValueError:
            # If the ID number or value is invalid, send an error message and return
            await message.channel.send("Invalid ID number or value. Please enter a valid ID number and value.")
            return

        # Check if the user has the appropriate role to run this command
        if "Administrator" in [role.name for role in message.author.roles]:
            # Update the user's currency in the database
            c.execute("UPDATE users SET currency=? WHERE id=?", (value, id_num))
            conn.commit()

            # Send a message indicating that the currency has been updated
            await message.channel.send(f"Currency for user with ID {id_num} has been set to {value}.")
        else:
            # If the user does not have the appropriate role, send an error message
            await message.channel.send("You do not have permission to use this command.")

        # Close the database connection
        conn.close()


    ##NEW COMMANDS GO ABOVE HERE
    
    if message.content == '!help':
        # Create the list of commands and their descriptions
        commands = [
            {
                "name": "IMPORTANT",
                "description": "A **!** IS REQUIRED BEFORE EVERY COMMAND"
            },
            {
                "name": "**addme**",
                "description": "Adds you to the server and gives you 25 currency"
            },
            {
                "name": "**referral**",
                "description": "!referral [CODE] = Redeem Your Referral Code"
            },
            {
                "name": "**report**",
                "description": "!report [user] [reason] = Report a user or post to the Mod Team"
            },
            {
                "name": "**mycode**",
                "description": "!mycode = your referral code"
            },
            {
                "name": "**currency**",
                "description": "Your Currency balance. Currency is required to interact with AI"
            },
            {
                "name": "**pay**",
                "description": "!pay [username includes spaces] [amount] = Send currency to another user"
            },
            {
                "name": "**earn**",
                "description": "Use this command once every 5 hours for **5 FREE CURRENCY**"
            },
            {
                "name": "**characters**",
                "description": "Your Character balance. Characters can be exchanged for Currency"
            },
            {
                "name": "**exchange**",
                "description": "!exchange [amout] = Trade Characters for Currency. Exchange rate 500:1"
            },
            {
                "name": "**conrad**",
                "description": "!conrad [converasation] = ASK GPT-3 A Question (PHD level specialties in math, multiple branches of science, history, politics, psychology, metaphysics, and more.(**COST: 5 Currency**)"
            },
            {
                "name": "**largeimage**",
                "description": "!largeimage [prompt] = AI Generates a 1024x1024 image. (**COST: 2 Currency**)"
            },
            {
                "name": "**dalle**",
                "description": "!dalle [prompt] = AI Generates 512x512 image. (**COST: 1 Currency**)"
            },
            {
                "name": "**story**",
                "description": "!story [story prompt] = StoryFlow Multiplayer Story MAX 500 CHARACTERS (**Cost 50 Currency**)"
            },
            {
                "name": "**action**",
                "description": "!action [desired action] = Add your actions to a StoryFlow Story, you can add multiple actions. (**Cost 1 Currency**)."
            },
            {
                "name": "**continue**",
                "description": "After the group has finished adding actions, Continue your StoryFlow Story. (**Cost 3 Currency**)"
            },
            {
                "name": "**basicsub**",
                "description": "!basicsub = Buy A Basic Subscription. Get an extra 33 Currency daily. More server channels. Generate referral codes. (**COST 10,000 Currency**)"
            },
            {
                "name": "**premiumsub**",
                "description": "!premiumsub = Buy A Premium Subscription. Get an extra 99 Currency daily. Directly support our script development, and pay for server time with API access. (**COST 1,000,000 Currency**)"
            },
            {
                "name": "**!getcode**",
                "description": "!getcode = Generate your referral code"
            },
        ]
        
        # Create the list of command strings to display
        command_list = []
        for command in commands:
            command_list.append(f"{command['name']}: {command['description']}")
        
        # Send the list of commands to the channel
        await message.channel.send("\n".join(command_list))
        
    #LOG THE CHARACTER COUNT OF ALL USERS TO THE DATABASE
    # Don't process messages from bots
    if message.author.bot:
        return

    # Connect to the database
    conn = sqlite3.connect('discord.db')
    c = conn.cursor()

    # Retrieve the user's character count from the database
    c.execute("SELECT character_count FROM users WHERE id=?", (message.author.id,))
    result = c.fetchone()
    if result is None:
        # If the user is not in the database, send an error message
        await message.channel.send("You are not a full member of the server! TYPE **!addme** in the chat to add yourself with full membership. Then use the **!help** command to see more options.")
    else:
        # If the user is in the database, add the message's character count to the total
        character_count = result[0]
        character_count += len(message.content)
        # Update the user's character count in the database
        c.execute("UPDATE users SET character_count=? WHERE id=?", (character_count, message.author.id))
        conn.commit()

    # Close the database connection
    conn.close()

client.run('YOURDISCORDTOKENGOESHERE') ##REPLACE THIS WITH YOUR DISCORD BOT TOKEN
