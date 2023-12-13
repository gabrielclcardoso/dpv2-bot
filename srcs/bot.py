from telegram.ext import CommandHandler, Application, filters, MessageHandler
import logging
import json
import os
import sys
import query

help_str = '''
Available commands:\n
/help
Prints out instructions\n
/update {mix_ids separated by space}
Updates monitored information about the mixode(s) on the databse\n
/add {mix_ids separated by space}
Adds mixode(s) to the databse of monitored mixnodes\n
/delete {mix_ids separated by space}
Deletes mixode(s) from the databse of monitored mixnodes\n
/database
Sends the current database that's being monitored
'''
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


async def has_permissions(update, context):
    if str(update.message.chat.id) != CHAT_ID:
        await context.bot.send_message(
            update.effective_chat.id,
            'No private commands allowed ;)',
            reply_to_message_id=update.message.message_id
        )
        await context.bot.send_message(
            CHAT_ID,
            'The following command was just tried in a different chat:',
        )
        await context.bot.forward_message(
            CHAT_ID, update.effective_chat.id, update.message.message_id
        )
        return False
    try:
        ADMINS = await application.bot.get_chat_administrators(CHAT_ID)
    except:
        await context.bot.send_message(
            update.effective_chat.id,
            'unable to check permissions for this command',
            reply_to_message_id=update.message.message_id
        )
        return False
    if update.effective_user not in (admin.user for admin in ADMINS):
        await context.bot.send_message(
            update.effective_chat.id,
            'only admins can run this command',
            reply_to_message_id=update.message.message_id
        )
        return False
    return True


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
                CHAT_ID,
                query.message(DATABASE, current, warnings)
            )


async def update_node(update, context):
    if not await has_permissions(update, context):
        return
    for mix_id in context.args:
        if mix_id not in DATABASE:
            await context.bot.send_message(
                update.effective_chat.id,
                f'Mixnode {mix_id} is not on the database',
                reply_to_message_id=update.message.message_id
            )
            continue
        try:
            current = query.query_api(mix_id)
            node = DATABASE[mix_id]
        except:
            await context.bot.send_message(
                update.effective_chat.id,
                f'Failed to update mixnode {mix_id}',
                reply_to_message_id=update.message.message_id
            )
            continue
        node['location']['country_name'] = current['location']['country_name']
        node['mix_node']['host'] = current['mix_node']['host']
        node['operating_cost']['amount'] = current['operating_cost']['amount']
        node['profit_margin_percent'] = current['profit_margin_percent']
        DATABASE[mix_id] = node
        await context.bot.send_message(
            update.effective_chat.id,
            f'Updated mixnode {mix_id}',
            reply_to_message_id=update.message.message_id
        )
    with open('../data/database.json', 'w') as mod_file:
        mod_file.write(json.dumps(DATABASE))


async def add_node(update, context):
    if not await has_permissions(update, context):
        return
    for mix_id in context.args:
        if mix_id in DATABASE:
            await context.bot.send_message(
                update.effective_chat.id,
                f'Mixnode {mix_id} already inside the database',
                reply_to_message_id=update.message.message_id
            )
            continue
        try:
            mixnode = query.query_api(mix_id)
            DATABASE[mix_id] = mixnode
            await context.bot.send_message(
                update.effective_chat.id,
                f'Added mixnode {mix_id}',
                reply_to_message_id=update.message.message_id
            )
        except:
            await context.bot.send_message(
                update.effective_chat.id,
                f'Failed to add mixnode {mix_id}',
                reply_to_message_id=update.message.message_id
            )
    with open('../data/database.json', 'w') as mod_file:
        mod_file.write(json.dumps(DATABASE))


async def del_node(update, context):
    if not await has_permissions(update, context):
        return
    for mix_id in context.args:
        if mix_id not in DATABASE:
            await context.bot.send_message(
                update.effective_chat.id,
                f'Mixnode {mix_id} is not in the database',
                reply_to_message_id=update.message.message_id
            )
            continue
        try:
            del DATABASE[mix_id]
            await context.bot.send_message(
                update.effective_chat.id,
                f'Deleted mixnode {mix_id}',
                reply_to_message_id=update.message.message_id
            )
        except KeyError:
            await context.bot.send_message(
                update.effective_chat.id,
                f'Failed to delete mixnode {mix_id}',
                reply_to_message_id=update.message.message_id
            )
    with open('../data/database.json', 'w') as mod_file:
        mod_file.write(json.dumps(DATABASE))


async def send_data(update, context):
    if not await has_permissions(update, context):
        return
    await context.bot.send_document(
        update.effective_chat.id,
        open('../data/database.json', 'r'),
        reply_to_message_id=update.message.message_id
    )


async def help(update, context):
    await context.bot.send_message(
        update.effective_chat.id,
        help_str,
        reply_to_message_id=update.message.message_id
    )

application = Application.builder().token(TOKEN).build()
application.add_handler(CommandHandler('update', update_node))
application.add_handler(CommandHandler('add', add_node))
application.add_handler(CommandHandler('delete', del_node))
application.add_handler(CommandHandler('database', send_data))
application.add_handler(MessageHandler(filters.COMMAND, help))

job_queue = application.job_queue
job_queue.run_repeating(check_nodes, interval=60, first=1)

application.run_polling()
