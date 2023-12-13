from telegram.ext import CommandHandler, Application
import logging
import json
import os
import sys
import query

try:
    TOKEN = os.environ['TOKEN']
except KeyError:
    sys.stderr.write("TOKEN envrionment variable not set.\n")
    exit(1)
try:
    CHAT_ID = os.environ['CHAT_ID']
except KeyError:
    sys.stderr.write("CHAT_ID envrionment variable not set.\n")
    exit(1)
try:
    with open('../data/database.json') as file:
        DATABASE = json.load(file)
except:
    sys.stderr.write("Unable to load database")
    exit(1)

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)


async def check_nodes(context):
    for mix_id in DATABASE:
        try:
            current = query.query_api(mix_id)
        except ValueError:
            sys.stderr.write('Error fetching info for node ' + mix_id)
            continue
        warnings = query.compare_info(DATABASE, current)
        if warnings.__len__() == 0:
            continue
        else:
            await context.bot.send_message(
                chat_id=CHAT_ID, text=query.message(DATABASE, current, warnings))


async def update_node(update, context):
    for mix_id in context.args:
        if mix_id not in DATABASE:
            await context.bot.send_message(chat_id=CHAT_ID, text=f'Mixnode {mix_id} is not on the database')
            continue
        try:
            current = query.query_api(mix_id)
            node = DATABASE[mix_id]
        except:
            await context.bot.send_message(chat_id=CHAT_ID, text=f'Failed to update mixnode {mix_id}')
            continue
        node['location']['country_name'] = current['location']['country_name']
        node['mix_node']['host'] = current['mix_node']['host']
        node['operating_cost']['amount'] = current['operating_cost']['amount']
        node['profit_margin_percent'] = current['profit_margin_percent']
        DATABASE[mix_id] = node
        await context.bot.send_message(chat_id=CHAT_ID, text=f'Updated mixnode {mix_id}')
    with open('../data/database.json', 'w') as mod_file:
        mod_file.write(json.dumps(DATABASE))


async def add_node(update, context):
    for mix_id in context.args:
        if mix_id in DATABASE:
            await context.bot.send_message(chat_id=CHAT_ID, text=f'Mixnode {mix_id} already inside the database')
            continue
        try:
            mixnode = query.query_api(mix_id)
            DATABASE[mix_id] = mixnode
            await context.bot.send_message(chat_id=CHAT_ID, text=f'Added mixnode {mix_id}')
        except:
            await context.bot.send_message(chat_id=CHAT_ID, text=f'Failed to add mixnode {mix_id}')
    with open('../data/database.json', 'w') as mod_file:
        mod_file.write(json.dumps(DATABASE))


async def del_node(update, context):
    for mix_id in context.args:
        if mix_id not in DATABASE:
            await context.bot.send_message(chat_id=CHAT_ID, text=f'Mixnode {mix_id} is not in the database')
            continue
        try:
            del DATABASE[mix_id]
            await context.bot.send_message(chat_id=CHAT_ID, text=f'Deleted mixnode {mix_id}')
        except KeyError:
            await context.bot.send_message(chat_id=CHAT_ID, text=f'Failed to delete mixnode {mix_id}')
    with open('../data/database.json', 'w') as mod_file:
        mod_file.write(json.dumps(DATABASE))


async def help(update, context):
    await context.bot.send_message(chat_id=CHAT_ID, text='help message')

application = Application.builder().token(TOKEN).build()

application.add_handler(CommandHandler('update', update_node))
application.add_handler(CommandHandler('add', add_node))
application.add_handler(CommandHandler('delete', del_node))
application.add_handler(CommandHandler('help', help))

job_queue = application.job_queue
job_queue.run_repeating(check_nodes, interval=60, first=1)

application.run_polling()
