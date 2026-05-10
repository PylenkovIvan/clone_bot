import logging
import asyncio
from telegram.ext import Application, MessageHandler, filters, CommandHandler
from telegram import ReplyKeyboardMarkup, ReplyKeyboardRemove
import random

logging.basicConfig(format='%(asctime)s - %(levelname)s - %(message)s', level=logging.DEBUG)


logger = logging.getLogger(__name__)


TIMER = 45


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
    crash_fl = False
    fl_enter = False
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


async def start(update, context):
    global active_tasks_array
    global d_of_tasks
    global failed_tasks
    global crash_fl
    restart_game()
    await update.message.reply_text(
        'Игра началась!',
        reply_markup=get_main_keyboard()
    )


async def help_command(update, context):
    reply_keyboard = [['/help', '/active_tasks'],
                      ['/complete_task', '/give_file'],
                      ['/emergency_meeting'],
                      ['/finish'],
                      ['/crash']]
    markup = ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=False)
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
                                    reply_markup=markup)


async def active_tasks(update, context):
    global d_of_tasks
    global active_tasks_array
    global crash_fl
    if not crash_fl:
        tasks = ''
        reply_keyboard = [['/help', '/active_tasks'],
                          ['/complete_task', '/give_file'],
                          ['/emergency_meeting'],
                          ['/finish'],
                          ['/crash']]
        markup = ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=False)
        for el in active_tasks_array:
            tasks += f'Задание №{el}: {d_of_tasks[el]} \n'
        await update.message.reply_text(tasks, reply_markup=markup)
    if crash_fl:
        await update.message.reply_text('Сбои в системе. Команда не принята')


async def complete_task(update, context):
    global crash_fl
    global fl_enter
    if not crash_fl:
        fl_enter = True
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
    if crash_fl:
        await update.message.reply_text('Сбои в системе. Команда не принята')
    if not crash_fl:
        fl = True
        task_number = update.message.text
        task_number = task_number.strip()
        for el in task_number:
            if el not in '0123456789':
                fl = False
        if fl:
            task_number = int(update.message.text)
        reply_keyboard = [['/help', '/active_tasks'],
                          ['/complete_task', '/give_file'],
                          ['/emergency_meeting'],
                          ['/finish'],
                          ['/crash']]
        markup = ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=False)
        if task_number == 100:
            if not fl_enter:
                reply_keyboard = [['/help', '/active_tasks'],
                                  ['/complete_task', '/give_file'],
                                  ['/emergency_meeting'],
                                  ['/finish'],
                                  ['/crash']]
                markup = ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=False)
                await update.message.reply_text('Активируйте команду /complete_task',
                                                reply_markup=markup)
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
                        reply_keyboard = [['/start']]
                        markup = ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=False)
                        restart_game()
                    await update.message.reply_text(text,
                                                    reply_markup=markup)
                    await asyncio.sleep(0.1)
        elif task_number in active_tasks_array:
            if not fl_enter:
                reply_keyboard = [['/help', '/active_tasks'],
                                  ['/complete_task', '/give_file'],
                                  ['/emergency_meeting'],
                                  ['/finish'],
                                  ['/crash']]
                markup = ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=False)
                await update.message.reply_text('Активируйте команду /complete_task',
                                                reply_markup=markup)
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
                        reply_keyboard = [['/start']]
                        markup = ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=False)
                        restart_game()
                    await update.message.reply_text(text,
                                                    reply_markup=markup)
                if n == 7 and task_number not in failed_tasks:
                    if len(failed_tasks) < len(active_tasks_array) // 2:
                        failed_tasks.append(task_number)
                        await update.message.reply_text(
                            f'Задание не выполнено. Оно не прошло проверку...',
                            reply_markup=markup)
                    else:
                        del active_tasks_array[active_tasks_array.index(task_number)]
                        text = f'Задание №{task_number} выполнено!'
                        if len(failed_tasks) != 0:
                            can_complete = failed_tasks[0]
                            del failed_tasks[0]
                            text += f' Можно выполнить задание №{can_complete}'
                        if len(active_tasks_array) == 0:
                            text += '\nВсе задания выполнены!'
                            reply_keyboard = [['/start']]
                            markup = ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=False)
                            restart_game()
                        await update.message.reply_text(text,
                                                        reply_markup=markup)
                elif task_number in failed_tasks:
                    await update.message.reply_text('Задание пока нельзя выполнить',
                                                    reply_markup=markup)
        elif task_number not in active_tasks_array and task_number in range(1, 37):
            if not fl_enter:
                reply_keyboard = [['/help', '/active_tasks'],
                                  ['/complete_task', '/give_file'],
                                  ['/emergency_meeting'],
                                  ['/finish'],
                                  ['/crash']]
                markup = ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=False)
                await update.message.reply_text('Активируйте команду /complete_task',
                                                reply_markup=markup)
            else:
                fl_enter = False
                await update.message.reply_text('Задание было выполнено до вас',
                                                reply_markup=markup)
        else:
            fl_enter = False
            await update.message.reply_text('Бортовой компьютер не разобрал вашего сообщения',
                                            reply_markup=markup)


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
    chat_id = update.message.chat_id
    job_removed = remove_job_if_exists(str(chat_id), context)
    context.job_queue.run_once(task, TIMER, chat_id=chat_id, name=str(chat_id), data=TIMER)
    crash_fl = True
    await update.message.reply_text("Всё сломалось, помогите!", reply_markup=ReplyKeyboardRemove())


async def meeting(update, context):
    global crash_fl
    reply_keyboard = [['/help', '/active_tasks'],
                      ['/complete_task', '/give_file'],
                      ['/emergency_meeting'],
                      ['/finish'],
                      ['/crash']]
    markup = ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=False)
    if not crash_fl:
        await update.message.reply_text("Собрание", reply_markup=markup)
    if crash_fl:
        await update.message.reply_text('Сбои в системе. Команда не принята')


async def first_level(update, context):
    global crash_fl
    reply_keyboard = [['/help', '/active_tasks'],
                      ['/complete_task', '/give_file'],
                      ['/emergency_meeting'],
                      ['/finish'],
                      ['/crash']]
    markup = ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=False)
    if not crash_fl:
        await update.effective_message.reply_photo('first_level.jpg', reply_markup=markup)
    if crash_fl:
        await update.message.reply_text('Сбои в системе. Команда не принята')


async def second_level(update, context):
    global crash_fl
    reply_keyboard = [['/help', '/active_tasks'],
                      ['/complete_task', '/give_file'],
                      ['/emergency_meeting'],
                      ['/finish'],
                      ['/crash']]
    markup = ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=False)
    if not crash_fl:
        await update.effective_message.reply_photo('second_level.jpg', reply_markup=markup)
    if crash_fl:
        await update.message.reply_text('Сбои в системе. Команда не принята')


async def fix_errors(update, context):
    global crash_fl
    global active_tasks_array
    crash_fl = False
    reply_keyboard = [['/help', '/active_tasks'],
                      ['/complete_task', '/give_file'],
                      ['/emergency_meeting'],
                      ['/finish'],
                      ['/crash']]
    markup = ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=False)
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
    await update.message.reply_text(text, reply_markup=markup)


async def task(context):
    global d_of_tasks
    global active_tasks_array
    global failed_tasks
    global crash_fl
    restart_game()
    reply_keyboard = [['/start']]
    markup = ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=False)
    await context.bot.send_message(context.job.chat_id, text=f'Критическое повреждение системы. '
                                                             f'Дальнейшее управление невозможно. '
                                                             f'Игра завершена...',
                                   reply_markup=markup)


async def text_buttons(update, context):
    text = update.message.text

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
    application.add_handler(CommandHandler('help', help_command))
    application.add_handler(CommandHandler('active_tasks', active_tasks))
    application.add_handler(CommandHandler('complete_task', complete_task))
    application.add_handler(CommandHandler('crash', crash))
    application.add_handler(CommandHandler('first_level', first_level))
    application.add_handler(CommandHandler('second_level', second_level))
    application.add_handler(CommandHandler('145288', fix_errors))
    application.add_handler(CommandHandler('emergency_meeting', meeting))
    application.add_handler(CommandHandler('finish', finish))
    text_handler = MessageHandler(filters.TEXT, text_buttons)
    application.add_handler(text_handler)
    application.run_polling()


if __name__ == '__main__':
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
    main()
