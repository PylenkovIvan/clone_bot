import logging
import asyncio
from telegram.ext import Application, MessageHandler, filters, CommandHandler
from telegram import ReplyKeyboardMarkup, ReplyKeyboardRemove
import random

logging.basicConfig(format='%(asctime)s - %(levelname)s - %(message)s', level=logging.DEBUG)


logger = logging.getLogger(__name__)


TIMER = 45

d_of_tasks = dict()
active_tasks_array = list()
failed_tasks = list()
crash_fl = False
fl_enter = False
players = set()
waiting_player = ''
captain_player = ''


def get_main_keyboard():
    reply_keyboard = [
        ['Помощь', 'Активные задания'],
        ['Выполнить задание', 'Экстренное собрание'],
        ['Сбой системы']
    ]

    return ReplyKeyboardMarkup(
        reply_keyboard,
        resize_keyboard=True,
        one_time_keyboard=False
    )


async def broadcast(context, text, reply_markup=None):
    global players
    for player_id in players:
        try:
            await context.bot.send_message(
                chat_id=player_id,
                text=text,
                reply_markup=reply_markup
            )
        except:
            pass


def remove_job_if_exists(name, context):
    current_jobs = context.job_queue.get_jobs_by_name(name)
    if not current_jobs:
        return False
    for job in current_jobs:
        job.schedule_removal()
    return True


def restart_game():
    global active_tasks_array
    global d_of_tasks
    global failed_tasks
    global crash_fl
    global fl_enter
    global players
    d_of_tasks = {1: 'Комната экипажа (2)',
                  2: 'Санузел, второй этаж',
                  3: 'Коридор, второй этаж',
                  4: 'Комната экипажа (1)',
                  5: 'Оружейная',
                  6: 'Открытый космос',
                  7: 'Камбуз',
                  8: 'Открытый космос',
                  9: 'Санузел, первый этаж',
                  10: 'Мостик',
                  11: 'Кафетерий',
                  12: 'Коридор, первый этаж',
                  13: 'Комната экипажа (1)',
                  14: 'Кафетерий',
                  15: 'Комната экипажа (2)',
                  16: 'Оружейная',
                  17: 'Коридор, первый этаж',
                  18: 'Коридор, второй этаж',
                  19: 'Мостик',
                  20: 'Мастерская',
                  21: 'Машинное отделение',
                  22: 'Открытый космос',
                  23: 'Комната экипажа (2)',
                  24: 'Санузел, второй этаж',
                  25: 'Коридор, второй этаж',
                  26: 'Оружейная',
                  27: 'Камбуз',
                  28: 'Открытый космос',
                  29: 'Санузел, первый этаж',
                  30: 'Мостик',
                  31: 'Кафетерий',
                  32: 'Коридор, второй этаж',
                  33: 'Открытый космос',
                  34: 'Машинное отделение',
                  35: 'Мастерская',
                  36: 'Кафетерий'}
    active_tasks_array = [i for i in range(1, 37)]
    failed_tasks = list()
    crash_fl = False
    fl_enter = False
    players = set()


async def start_game(update, context):
    restart_game()
    await update.message.reply_text(
        'Игра началась!'
    )


async def captain(update, context):
    global captain_player
    captain_player = update.effective_chat.id
    await update.message.reply_text(
        'Бортовой компьютер подключен'
    )


async def start(update, context):
    global players

    user_id = update.effective_chat.id
    players.add(user_id)

    await update.message.reply_text(
        'Йо-хо-хо, все на борт!',
        reply_markup=get_main_keyboard()
    )


async def help_command(update, context):
    await update.message.reply_text('Команды для работы с бортовым компьютером: \n'
                                    '1. "/active_tasks" - выведет список невыполненных заданий \n'
                                    '2. "/complete_task" - запросит номер выполненного задания и '
                                    'отметит его как завершённое (ну или не отметит...) \n'
                                    '3. "/finish" - закончит игру \n'
                                    '4. "/emergency_meeting" - экстренное собрание \n'
                                    '5. "/help" - помощь. А, ну да... \n'
                                    'Названия комнат: \n'
                                    '1. Комната экипажа (1) - Детская №1 \n'
                                    '2. Комната экипажа (2) - Детская №2 \n'
                                    '3. Мостик - Зал \n'
                                    '4. Камбуз - Кухня \n'
                                    '5. Оружейная - Гостиная \n'
                                    '6. Санузел (1) - Туалет на первом этаже \n'
                                    '7. Санузел (2) - Туалет на втором этаже \n'
                                    '8. Открытый космос - Веранда \n'
                                    '9. Кафетерий - Столовая \n'
                                    'Если вы являетесь инженером, то после выполнения всех своих'
                                    ' заданий \n'
                                    'активируйте задание номер 100 в /complete_task \n',
                                    reply_markup=get_main_keyboard())


async def active_tasks(update, context):
    global d_of_tasks
    global active_tasks_array
    global crash_fl
    if not crash_fl:
        tasks = ''
        for el in active_tasks_array:
            tasks += f'Задание №{el}: {d_of_tasks[el]} \n'
        await update.message.reply_text(tasks, reply_markup=get_main_keyboard())
    if crash_fl:
        await update.message.reply_text('Сбои в системе. Команда не принята')


async def complete_task(update, context):
    global crash_fl
    global fl_enter
    global waiting_player
    if not crash_fl:
        fl_enter = True
        waiting_player = update.effective_user.id
        await update.message.reply_text(
            "Введите номер выполненного задания",
            reply_markup=ReplyKeyboardRemove()
        )
    if crash_fl:
        await update.message.reply_text('Сбои в системе. Команда не принята')


async def enter_task(update, context):
    global d_of_tasks
    global active_tasks_array
    global failed_tasks
    global crash_fl
    global fl_enter
    global waiting_player
    if crash_fl:
        await update.message.reply_text('Сбои в системе. Команда не принята')
        return

    if waiting_player != update.effective_user.id:
        await update.message.reply_text(
            "Обрабатывается задание другого игрока\nПопробуйте позднее"
        )
        return

    fl = True
    task_number = update.message.text
    task_number = task_number.strip()
    for el in task_number:
        if el not in '0123456789':
            fl = False
    if fl:
        task_number = int(update.message.text)
    if task_number == 100:
        if not fl_enter:
            await update.message.reply_text('Активируйте команду /complete_task',
                                            reply_markup=get_main_keyboard())
        else:
            fl_enter = False
            for i in range(len(active_tasks_array)):
                task_number = random.sample(active_tasks_array, 1)
                del active_tasks_array[active_tasks_array.index(task_number[0])]
                text = f'Задание №{task_number[0]} выполнено!'
                if task_number in failed_tasks:
                    del failed_tasks[failed_tasks.index(task_number[0])]
                if len(active_tasks_array) == 0:
                    text += '\nВсе задания выполнены!'
                    restart_game()
                await update.message.reply_text(text, reply_markup=get_main_keyboard())
                await asyncio.sleep(0.1)
    elif task_number in active_tasks_array:
        if not fl_enter:
            await update.message.reply_text('Активируйте команду /complete_task',
                                            reply_markup=get_main_keyboard())
        else:
            fl_enter = False
            n = random.randint(1, 20)
            if n != 7 and task_number not in failed_tasks:
                del active_tasks_array[active_tasks_array.index(task_number)]
                text = f'Задание №{task_number} выполнено!'
                if len(failed_tasks) != 0:
                    can_complete = failed_tasks[0]
                    del failed_tasks[0]
                    text += f' Можно выполнить задание №{can_complete}'
                if len(active_tasks_array) == 0:
                    text += '\nВсе задания выполнены!'
                    restart_game()
                await update.message.reply_text(text, reply_markup=get_main_keyboard())
            if n == 7 and task_number not in failed_tasks:
                if len(failed_tasks) < len(active_tasks_array) // 2:
                    failed_tasks.append(task_number)
                    await update.message.reply_text(
                        f'Задание не выполнено. Оно не прошло проверку...',
                        reply_markup=get_main_keyboard())
                else:
                    del active_tasks_array[active_tasks_array.index(task_number)]
                    text = f'Задание №{task_number} выполнено!'
                    if len(failed_tasks) != 0:
                        can_complete = failed_tasks[0]
                        del failed_tasks[0]
                        text += f' Можно выполнить задание №{can_complete}'
                    if len(active_tasks_array) == 0:
                        text += '\nВсе задания выполнены!'
                        restart_game()
                    await update.message.reply_text(text, reply_markup=get_main_keyboard())
            elif task_number in failed_tasks:
                await update.message.reply_text('Задание пока нельзя выполнить',
                                                reply_markup=get_main_keyboard())
    elif task_number not in active_tasks_array and task_number in range(1, 37):
        if not fl_enter:
            await update.message.reply_text('Активируйте команду /complete_task',
                                            reply_markup=get_main_keyboard())
        else:
            fl_enter = False
            await update.message.reply_text('Задание было выполнено до вас',
                                            reply_markup=get_main_keyboard())
    else:
        fl_enter = False
        await update.message.reply_text('Бортовой компьютер не разобрал вашего сообщения',
                                        reply_markup=get_main_keyboard())


async def finish(update, context):
    global d_of_tasks
    global active_tasks_array
    global failed_tasks
    global crash_fl
    reply_keyboard = [['/start']]
    markup = ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=False)
    restart_game()
    await update.message.reply_text('Игра завершена. '
                                    'Введите команду "/start" для запуска новой игры',
                                    reply_markup=markup)


async def crash(update, context):
    global crash_fl
    if crash_fl:
        return
    crash_fl = True
    await broadcast(context, 'Всё сломалось, помогите!')
    context.job_queue.run_once(task, TIMER)


async def meeting(update, context):
    global crash_fl
    if crash_fl:
        await update.message.reply_text('Сбои в системе. Команда не принята')
        return

    await broadcast(context, 'Общий сбор!', get_main_keyboard())


async def fix_errors(update, context):
    global crash_fl
    global active_tasks_array
    global captain_player
    if update.effective_chat.id != captain_player:
        await update.message.reply_text('Отказано', reply_markup=get_main_keyboard())
    crash_fl = False
    failed_tasks_after_crash = list()
    for i in range(1, 37):
        if i not in active_tasks_array:
            failed_tasks_after_crash.append(i)
    if failed_tasks_after_crash == list():
        failed_tasks_after_crash.append(1)
    failed_task = random.sample(failed_tasks_after_crash, 1)[0]
    if failed_task not in active_tasks_array:
        active_tasks_array.append(failed_task)
    active_tasks_array.sort()
    chat_id = update.message.chat_id
    job_removed = remove_job_if_exists(str(chat_id), context)
    text = f'Система восстановлена. Пострадало задание №{failed_task}' \
        if job_removed else 'Ты инструкцию читал?! \n' \
                            'Сказано: "Активировать при крайней необходимости" \n' \
                            'Давай проверим: сбой есть? ... ' \
                            'Сбоев нет. \n' \
                            'Тогда зачем ты меня до заводских настроек хотел сбросить?! \n' \
                            'А если бы я реально перезапустился?! \n' \
                            'Тут такое бы произошло! \n' \
                            'С кем я на корабле... \n' \
                            'Остановите, я выйду...'
    await update.message.reply_text(text, reply_markup=get_main_keyboard())


async def task(context):
    await broadcast(
        context,
        "Критическое повреждение системы...\nИгра окончена."
    )
    restart_game()


async def text_buttons(update, context):
    text = update.message.text

    if text.startswith('/'):
        return

    if text == 'Помощь':
        await help_command(update, context)

    elif text == 'Активные задания':
        await active_tasks(update, context)

    elif text == 'Выполнить задание':
        await complete_task(update, context)

    elif text == 'Экстренное собрание':
        await meeting(update, context)

    elif text == 'Завершить игру':
        await finish(update, context)

    elif text == 'Сбой системы':
        await crash(update, context)

    else:
        await enter_task(update, context)


def main():
    TOKEN = '5837168283:AAHdzQQLAzX5a4C3fDcOg05PNkYdPWt1lxE'
    application = (Application.builder().token(TOKEN).build())
    application.add_handler(CommandHandler('start', start))
    application.add_handler(CommandHandler('start_game', start_game))
    application.add_handler(CommandHandler('help', help_command))
    application.add_handler(CommandHandler('active_tasks', active_tasks))
    application.add_handler(CommandHandler('complete_task', complete_task))
    application.add_handler(CommandHandler('crash', crash))
    application.add_handler(CommandHandler('145288', fix_errors))
    application.add_handler(CommandHandler('bigboss', captain))
    application.add_handler(CommandHandler('emergency_meeting', meeting))
    application.add_handler(CommandHandler('finish', finish))
    text_handler = MessageHandler(filters.TEXT, text_buttons)
    application.add_handler(text_handler)
    application.run_polling()


if __name__ == '__main__':
    main()
