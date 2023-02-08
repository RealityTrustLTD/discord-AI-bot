# discord-AI-bot
AI driven discord bot written in python. Capable of a number of features including: 

Using OPENAI to chat, 
answer questions, 
generate images, 
and narrate AI driven multiplayer text stories. 

Additionally it has a full economy
roles, 
subscriptions, 
referral system,
...and more


REQUIREMENTS: PYTHON, DISCORD, SQLITE

REQUIRES Python 3.10.5, 2x SQLITE Databases (1 for the bot functions) and (a second instance for the AI driven multiplayer text game), an OPEN AI API key, a Stability Diffusion API Key, and only works with Python Discord 2.7. and a Discord Bot API. 

INSTALLATION: 

1. Set up your instance / operating environment.
2. Edit the scripts with your own API keys and Discord info.
3. Set up your SQLITE Databases.
4. Connect your bot. 



The bot will respond to the following commands: 

IMPORTANT: A ! IS REQUIRED BEFORE EVERY COMMAND

addme: Adds you to the server and gives you 25 currency
referral: !referral [CODE] = Redeem Your Referral Code
report: !report [user] [reason] = Report a user or post to the Mod Team
mycode: !mycode = your referral code
currency: Your Currency balance. Currency is required to interact with AI
pay: !pay [username includes spaces] [amount] = Send currency to another user
earn: Use this command once every 5 hours for 5 FREE CURRENCY
characters: Your Character balance. Characters can be exchanged for Currency
exchange: !exchange [amout] = Trade Characters for Currency. Exchange rate 500:1
conrad: !conrad [converasation] = ASK GPT-3 A Question (PHD level specialties in math, multiple branches of science, history, politics, psychology, metaphysics, and more.(COST: 5 Currency)
largeimage: !largeimage [prompt] = AI Generates a 1024x1024 image. (COST: 2 Currency)
dalle: !dalle [prompt] = AI Generates 512x512 image. (COST: 1 Currency)
story: !story [story prompt] = StoryFlow Multiplayer Story MAX 500 CHARACTERS (Cost 50 Currency)
action: !action [desired action] = Add your actions to a StoryFlow Story, you can add multiple actions. (Cost 1 Currency).
continue: After the group has finished adding actions, Continue your StoryFlow Story. (Cost 3 Currency)
basicsub: !basicsub = Buy A Basic Subscription. Get an extra 33 Currency daily. More server channels. Generate referral codes. (COST 10,000 Currency)
premiumsub: !premiumsub = Buy A Premium Subscription. Get an extra 99 Currency daily. Directly support our script development, and pay for server time with API access. (COST 1,000,000 Currency)
!getcode: !getcode = Generate your referral code

The Bot also features several admin commands used for adding/removing users, granting tokens, and managing the server. 


Its a great little bot, but i know that making it open source will make it so much better if the right person finds it. Have fun!!


