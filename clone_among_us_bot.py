import logging
import asyncio
from telegram.ext import Application, MessageHandler, filters, CommandHandler
from telegram import ReplyKeyboardMarkup, ReplyKeyboardRemove
import random
from datetime import datetime

logging.basicConfig(format='%(asctime)s - %(levelname)s - %(message)s', level=logging.DEBUG)


logger = logging.getLogger(__name__)


TIMER = 45

d_of_tasks = dict()
active_tasks_array = list()
failed_tasks = list()
crash_fl = False
players = set()
captain_player = ''
waiting_players = set()
kill_logs = list()
start_g = datetime.now()
casino_logs = dict()
LUCK = ["Мастер Джекпота", "Фартовый Король", "Разрушитель вероятности", "Казино Дон",
        "Капо слотов", "Хозяин слот-машины", "Сломавший матрицу"]
UNLUCK = ["Лицо нуля", "Архонт пустого кошелька", "Падший множитель",
          "Легенда лоу-таба", "Олух"]


def get_main_keyboard():
    reply_keyboard = [
        ['Помощь', 'Активные задания'],
        ['Выполнить задание', 'Экстренное собрание'],
        ['Сбой системы', 'Убить'],
        ['Убийства', 'Камеры']
    ]

    return ReplyKeyboardMarkup(
        reply_keyboard,
        resize_keyboard=True,
        one_time_keyboard=False
    )


def get_joke_keyboard():
    reply_keyboard = [
        ['ʜǝlԀ', 'ʞsɐ⊥ ǝʌᴉʇɔ∀'],
        ['sllᴉʞ', 'sɐɹǝɯɐɔ'],
        ['ʞsɐ⊥ ǝʇǝldɯoɔ', 'ɓuᴉʇǝǝɯ ʎɔuǝɹǝɯǝ'],
        ['ɥsɐɹɔ ɯǝʇsʎs', 'llᴉʞ']
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


async def restart_game(context=None):
    global active_tasks_array
    global d_of_tasks
    global failed_tasks
    global crash_fl
    global players
    global captain_player
    global kill_logs
    global waiting_players
    global start_g
    global casino_logs
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
    kill_logs = list()
    crash_fl = False
    await broadcast(context, 'Игра завершена!')
    players = set()
    captain_player = ''
    waiting_players = set()
    start_g = datetime.now()
    casino_logs = dict()
    if context and context.job_queue:
        for job in context.job_queue.jobs():
            job.schedule_removal()


async def start_game(update, context):
    await restart_game(context)
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
    global casino_logs

    user_id = update.effective_chat.id
    players.add(user_id)
    casino_logs[user_id] = [0, 0]

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
    global casino_logs
    if not crash_fl:
        tasks = ''
        for el in active_tasks_array:
            tasks += f'Задание №{el}: {d_of_tasks[el]} \n'
        if casino_logs[update.effective_user.id][1] == 2:
            await update.message.reply_text(tasks, reply_markup=get_joke_keyboard())
            return
        if casino_logs[update.effective_user.id][1] == 1:
            await update.message.reply_text(
                f'Конечно, {random.choice(LUCK)}, '
                f'вот активные задания\n' + tasks,
                reply_markup=get_main_keyboard())
            return
        if casino_logs[update.effective_user.id][1] == 3:
            await update.message.reply_text(
                f'Куда тебе, {random.choice(UNLUCK)}, '
                f'ты же всё сломаешь\n' + tasks,
                reply_markup=get_main_keyboard())
            return
        await update.message.reply_text(tasks, reply_markup=get_main_keyboard())
    if crash_fl:
        await update.message.reply_text('Сбои в системе. Команда не принята')


async def complete_task(update, context):
    global crash_fl
    global waiting_players
    global casino_logs
    if not crash_fl:
        waiting_players.add(update.effective_user.id)
        if casino_logs[update.effective_user.id][1] == 2:
            await update.message.reply_text("Введите номер выполненного задания",
                                            reply_markup=get_joke_keyboard())
            return
        if casino_logs[update.effective_user.id][1] == 1:
            await update.message.reply_text(f'Такие как Вы, {random.choice(LUCK)}, '
                                            f'могут не выполнять задания\nВведите номер задания',
                                            reply_markup=get_main_keyboard())
            return
        if casino_logs[update.effective_user.id][1] == 3:
            await update.message.reply_text(f'Сломал, {random.choice(UNLUCK)}? '
                                            f'Ладно, позволяю тебе, {random.choice(UNLUCK)},'
                                            f'ввести номер задания\n',
                                            reply_markup=get_main_keyboard())
            return
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
    global waiting_players
    global casino_logs
    if crash_fl:
        await update.message.reply_text('Сбои в системе. Команда не принята')
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
        if update.effective_user.id not in waiting_players:
            if casino_logs[update.effective_user.id][1] == 2:
                await update.message.reply_text("Активируйте команду /complete_task",
                                                reply_markup=get_joke_keyboard())
                return
            await update.message.reply_text('Активируйте команду /complete_task',
                                            reply_markup=get_main_keyboard())
        else:
            waiting_players.discard(update.effective_user.id)
            for i in range(len(active_tasks_array)):
                task_number = random.sample(active_tasks_array, 1)
                del active_tasks_array[active_tasks_array.index(task_number[0])]
                text = f'Задание №{task_number[0]} выполнено!'
                if task_number in failed_tasks:
                    del failed_tasks[failed_tasks.index(task_number[0])]
                if len(active_tasks_array) == 0:
                    text += '\nВсе задания выполнены!'
                    await restart_game(context)
                if casino_logs[update.effective_user.id][1] == 2:
                    await update.message.reply_text(text,
                                                    reply_markup=get_joke_keyboard())
                    return
                await update.message.reply_text(text, reply_markup=get_main_keyboard())
                await asyncio.sleep(0.1)
    elif task_number in active_tasks_array:
        if update.effective_user.id not in waiting_players:
            if casino_logs[update.effective_user.id][1] == 2:
                await update.message.reply_text("Активируйте команду /complete_task",
                                                reply_markup=get_joke_keyboard())
                return
            await update.message.reply_text('Активируйте команду /complete_task',
                                            reply_markup=get_main_keyboard())
        else:
            waiting_players.discard(update.effective_user.id)
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
                    await restart_game(context)
                if casino_logs[update.effective_user.id][1] == 2:
                    await update.message.reply_text(text,
                                                    reply_markup=get_joke_keyboard())
                    return
                await update.message.reply_text(text, reply_markup=get_main_keyboard())
            if n == 7 and task_number not in failed_tasks:
                if len(failed_tasks) < len(active_tasks_array) // 2:
                    failed_tasks.append(task_number)
                    if casino_logs[update.effective_user.id][1] == 2:
                        await update.message.reply_text(
                            f'Задание не выполнено. Оно не прошло проверку...',
                            reply_markup=get_joke_keyboard())
                        return
                    if casino_logs[update.effective_user.id][1] == 3:
                        await update.message.reply_text(
                            f'ДА НУ КАК!!! ТЫ ЧЕ С ЭТИМ ЗАДАНИЕМ ДЕЛАЛ, ЧТОБЫ ЕГО НЕ ВЫПОЛНИТЬ, '
                            f'{random.choice(UNLUCK)}, А? Я ТЕБЯ С КОРАБЛЯ ВЫКИНУ, БУДЕШЬ'
                            f'ОРБИТУ ДРАИТЬ! ТОЛЬКО ПОПРОБУЙ ЭТО ПОВТОРИТЬ!',
                            reply_markup=get_joke_keyboard())
                        return
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
                        await restart_game(context)
                    if casino_logs[update.effective_user.id][1] == 2:
                        await update.message.reply_text(text, reply_markup=get_joke_keyboard())
                        return
                    await update.message.reply_text(text, reply_markup=get_main_keyboard())
            elif task_number in failed_tasks:
                if casino_logs[update.effective_user.id][1] == 2:
                    await update.message.reply_text('Задание пока нельзя выполнить',
                                                    reply_markup=get_joke_keyboard())
                    return
                await update.message.reply_text('Задание пока нельзя выполнить',
                                                reply_markup=get_main_keyboard())
    elif task_number not in active_tasks_array and task_number in range(1, 37):
        if update.effective_user.id not in waiting_players:
            if casino_logs[update.effective_user.id][1] == 2:
                await update.message.reply_text('Активируйте команду /complete_task',
                                                reply_markup=get_joke_keyboard())
                return
            await update.message.reply_text('Активируйте команду /complete_task',
                                            reply_markup=get_main_keyboard())
        else:
            waiting_players.discard(update.effective_user.id)
            if casino_logs[update.effective_user.id][1] == 2:
                await update.message.reply_text('Задание было выполнено до вас',
                                                reply_markup=get_joke_keyboard())
                return
            await update.message.reply_text('Задание было выполнено до вас',
                                            reply_markup=get_main_keyboard())
    else:
        waiting_players.discard(update.effective_user.id)
        if casino_logs[update.effective_user.id][1] == 2:
            await update.message.reply_text('Бортовой компьютер не разобрал вашего сообщения',
                                            reply_markup=get_joke_keyboard())
            return
        await update.message.reply_text('Бортовой компьютер не разобрал вашего сообщения',
                                        reply_markup=get_main_keyboard())


async def finish(update, context):
    global captain_player
    global casino_logs
    if update.effective_chat.id != captain_player:
        await update.message.reply_text('Отказано',
                                        reply_markup=get_main_keyboard())
        return
    reply_keyboard = [['/start_game']]
    markup = ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=False)
    await restart_game(context)
    await broadcast(context, 'Игра завершена. '
                             'Введите команду "/start_game" для запуска новой игры',
                    markup)


async def crash(update, context):
    global crash_fl
    if crash_fl:
        await broadcast(context, f'Всё уже сломали до тебя!, '
                                 f'{update.effective_user.first_name}')
        return
    crash_fl = True
    await broadcast(context, 'Всё сломалось, помогите!')
    remove_job_if_exists("global_crash", context)
    context.job_queue.run_once(
        task,
        TIMER,
        name="global_crash"
    )


async def meeting(update, context):
    global crash_fl
    global casino_logs
    if crash_fl:
        await update.message.reply_text('Сбои в системе. Команда не принята')
        return

    if casino_logs[update.effective_user.id][1] == 1:
        await broadcast(context, f'{random.choice(LUCK)} созывает {random.choice(["своё казино-стадо", "статистику", "крипов", "переменных удачи"])}')
        return
    if casino_logs[update.effective_user.id][1] == 3:
        await broadcast(context, f'{random.choice(UNLUCK)} просит {random.choice(["Великих", "Лордов", "Всех", "услышать своё пустое мнение и"])} подойти к столу')
        return
    await broadcast(context, 'Общий сбор!', get_main_keyboard())


async def fix_errors(update, context):
    global crash_fl
    global active_tasks_array
    global captain_player
    global casino_logs
    if update.effective_chat.id != captain_player:
        if casino_logs[update.effective_user.id][1] == 2:
            await update.message.reply_text('Отказано',
                                            reply_markup=get_joke_keyboard())
            return
        await update.message.reply_text('Отказано', reply_markup=get_main_keyboard())
        return
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
    job_removed = remove_job_if_exists("global_crash", context)
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
    if casino_logs[update.effective_user.id][1] == 2:
        await update.message.reply_text(text,
                                        reply_markup=get_joke_keyboard())
        return
    await update.message.reply_text(text, reply_markup=get_main_keyboard())


async def task(context):
    await broadcast(
        context,
        "Критическое повреждение системы...\nИгра окончена."
    )
    await restart_game(context)


async def kill(update, context):
    global kill_logs
    global start_g
    user_id = update.effective_user.id

    current_jobs = context.job_queue.get_jobs_by_name(f"kill_{user_id}")

    if current_jobs:
        await update.message.reply_text(
            "Идёт перезарядка"
        )
        return

    seconds = int((datetime.now() - start_g).total_seconds())

    minutes = seconds // 60
    seconds = seconds % 60
    kill_logs.append(f'{minutes:02}:{seconds:02}')

    context.job_queue.run_once(
        kill_task,
        TIMER,
        name=f"kill_{user_id}",
        data=user_id
    )

    await update.message.reply_text(
        f"Произошло убийство!"
    )


async def kill_task(context):
    user_id = context.job.data
    try:
        await context.bot.send_message(
            chat_id=user_id,
            text="Перезарядка завершена"
        )
    except:
        pass


async def status(update, context):
    global players
    if not players:
        await update.message.reply_text("Игроков нет")
        return

    text = "Подключённые игроки:\n"

    for i, player_id in enumerate(players, 1):
        try:
            user = await context.bot.get_chat(player_id)
            name = user.first_name or "Без имени"
            username = f" (@{user.username})" if user.username else ""

            text += f"{i}. {name}{username}\n"
        except:
            text += f"{i}. {player_id}\n"

    await update.message.reply_text(text)


async def kill_log(update, context):
    global kill_logs

    if not kill_logs:
        await update.message.reply_text("Убийств ещё не было")
        return

    text = "Лог убийств:\n\n"

    for i, entry in enumerate(kill_logs, 1):
        text += f"{i}. {entry}\n"

    await update.message.reply_text(text)


async def cam(update, context):
    global casino_logs
    if casino_logs[update.effective_user.id][1] == 1:
        await update.message.reply_text(
            f'{random.choice(LUCK)}, уберите крыс с корабля\n'
            f'https://telemost.yandex.ru/j/32983473105542',
            reply_markup=get_joke_keyboard())
        return
    if casino_logs[update.effective_user.id][1] == 2:
        await update.message.reply_text('https://telemost.yandex.ru/j/32983473105542',
                                        reply_markup=get_joke_keyboard())
        return
    await update.message.reply_text('https://telemost.yandex.ru/j/32983473105542',
                                    reply_markup=get_main_keyboard())


async def casino(update, context):
    global casino_logs
    user_id = update.effective_user.id
    if casino_logs[user_id][0] > 3:
        if casino_logs[update.effective_user.id][1] == 2:
            await update.message.reply_text('Лудоман! Доступ заблокирован',
                                            reply_markup=get_joke_keyboard())
            return
        if casino_logs[update.effective_user.id][1] == 2:
            await update.message.reply_text(f'Сожалею, {random.choice(LUCK)}, '
                                            f'такие, как Вы, не играют',
                                            reply_markup=get_main_keyboard())
            return
        await update.message.reply_text('Лудоман! Доступ заблокирован',
                                        reply_markup=get_main_keyboard())
        return
    casino_logs[user_id][0] += 1

    slots = ["🎰", "🎲", "🤡", "🚀", "🚨"]

    msg = await update.message.reply_text("🎰 Запуск казино...")
    text = ''
    for i in range(10):
        text = random.choice(slots) + " " + random.choice(slots) + " " + random.choice(slots)
        await msg.edit_text(text)
        await asyncio.sleep(0.3)

    if text == '🎰 🎰 🎰':
        await update.message.reply_text('!!!MAX WIN!!!', reply_markup=get_main_keyboard())
        casino_logs[user_id][1] = 1
        await broadcast(context, f'{update.effective_user.first_name} - {random.choice(LUCK)}',
                        get_main_keyboard())
    if text == '🎲 🎲 🎲':
        await update.message.reply_text('!!!YOU WIN ƃuᴉɥʇǝɯoS!!!', reply_markup=get_main_keyboard())
        casino_logs[user_id][1] = 2
    if text == '🤡 🤡 🤡':
        await update.message.reply_text('вхаахаахаах 👉 🤡 👈', reply_markup=get_main_keyboard())
        await update.message.reply_text('У тебя есть шанс оставить это втайне',
                                        reply_markup=get_main_keyboard())
        casino_logs[user_id][1] = 3
    if text == '🚀 🚀 🚀':
        await update.message.reply_text('!!!ДоДеП!!!', reply_markup=get_main_keyboard())
        casino_logs[user_id][0] -= 5
    if text == '🚨 🚨 🚨':
        await update.message.reply_text('Объявление!', reply_markup=get_main_keyboard())
        await broadcast(context, f'{update.effective_user.first_name} - Лудоман',
                        get_main_keyboard())


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

    elif text == 'Убить':
        await kill(update, context)

    elif text == 'Убийства':
        await kill_log(update, context)

    elif text == 'Камеры':
        await cam(update, context)

    elif 'мам' in text.lower():
        await update.message.reply_text('Встретимся у твоей мамки',
                                        reply_markup=get_main_keyboard())

    elif text == "Let's go gambling!":
        await casino(update, context)

    if text == 'ʜǝlԀ':
        await help_command(update, context)

    elif text == 'ʞsɐ⊥ ǝʌᴉʇɔ∀':
        await active_tasks(update, context)

    elif text == 'ʞsɐ⊥ ǝʇǝldɯoɔ':
        await complete_task(update, context)

    elif text == 'ɓuᴉʇǝǝɯ ʎɔuǝɹǝɯǝ':
        await meeting(update, context)

    elif text == 'ɥsɐɹɔ ɯǝʇsʎs':
        await crash(update, context)

    elif text == 'llᴉʞ':
        await kill(update, context)

    elif text == 'sɐɹǝɯɐɔ':
        await cam(update, context)

    elif text == 'sllᴉʞ':
        await kill_log(update, context)

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
    application.add_handler(CommandHandler('kill', kill))
    application.add_handler(CommandHandler('status', status))
    application.add_handler(CommandHandler('kill_log', kill_log))
    application.add_handler(CommandHandler('cam', cam))
    application.add_handler(CommandHandler('casino', casino))
    text_handler = MessageHandler(filters.TEXT, text_buttons)
    application.add_handler(text_handler)
    application.run_polling()


if __name__ == '__main__':
    main()
