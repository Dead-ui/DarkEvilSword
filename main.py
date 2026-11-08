#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Запуск:  python3 main.py
"""

from __future__ import annotations

import random
import sys
from dataclasses import dataclass, field
from typing import Dict, List, Tuple

#  ОФОРМЛЕНИЕ ТЕРМИНАЛА

USE_COLOR = sys.stdout.isatty()

if sys.platform == "win32":
    import os

    os.system("")


def _supports(symbol: str) -> bool:
    try:
        symbol.encode(sys.stdout.encoding or "utf-8")
        return True
    except (UnicodeEncodeError, LookupError):
        return False


BAR_FULL = "█" if _supports("█") else "#"
BAR_EMPTY = "░" if _supports("░") else "-"


def _paint(text: str, code: str) -> str:
    return f"\033[{code}m{text}\033[0m" if USE_COLOR else text


def bold(t: str) -> str:
    return _paint(t, "1")


def red(t: str) -> str:
    return _paint(t, "31")


def green(t: str) -> str:
    return _paint(t, "32")


def yellow(t: str) -> str:
    return _paint(t, "33")


def blue(t: str) -> str:
    return _paint(t, "34")


def cyan(t: str) -> str:
    return _paint(t, "36")


def grey(t: str) -> str:
    return _paint(t, "90")


def line(char: str = "-", width: int = 58) -> str:
    return char * width


def ask(prompt: str) -> str:
    try:
        return input(prompt).strip()
    except (EOFError, KeyboardInterrupt):
        print("\nДо встречи, герой!")
        sys.exit(0)


def bar(current: int, maximum: int, color: str = "32", width: int = 20) -> str:
    current = max(0, min(current, maximum))
    filled = int(round(width * current / maximum)) if maximum else 0
    return _paint(BAR_FULL * filled + BAR_EMPTY * (width - filled), color)

#  ДАННЫЕ: ОРУЖИЕ, УМЕНИЯ, КЛАССЫ


@dataclass(frozen=True)
class Weapon:
    name: str
    bonus: int      # прибавка к атаке
    price: int      # 0 — стартовое оружие

    def label(self) -> str:
        return f"{self.name} (+{self.bonus} к атаке)"


@dataclass(frozen=True)
class Skill:
    name: str
    mana: int
    desc: str
    kind: str
    power: float = 1.0
    hits: int = 1
    heal_pct: float = 0.0
    value: int = 0
    duration: int = 0
    crit: float = 0.0


@dataclass(frozen=True)
class HeroClass:
    name: str
    motto: str
    hp: int
    mana: int
    attack: int
    defense: int
    skills: Tuple[Skill, ...]


#3 оружия на каждый класс

WEAPONS: Dict[str, Tuple[Weapon, ...]] = {
    "Воин": (
        Weapon("Ржавый меч", 0, 0),
        Weapon("Стальной меч", 7, 90),
        Weapon("Клинок героя", 15, 220),
    ),
    "Маг": (
        Weapon("Деревянный посох", 0, 0),
        Weapon("Посох огня", 8, 90),
        Weapon("Посох архимага", 17, 220),
    ),
    "Стрелок": (
        Weapon("Простой лук", 0, 0),
        Weapon("Охотничий лук", 7, 90),
        Weapon("Лук ветра", 15, 220),
    ),
    "Ассасин": (
        Weapon("Тусклый кинжал", 0, 0),
        Weapon("Парные кинжалы", 8, 90),
        Weapon("Кинжал теней", 16, 220),
    ),
}


#Классы и их умения

CLASSES: Dict[str, HeroClass] = {
    "Воин": HeroClass(
        name="Воин",
        motto="сила и сталь",
        hp=140,
        mana=50,
        attack=15,
        defense=5,
        skills=(
            Skill("Мощный удар", 12, "удар в 1.8 раза сильнее", "damage", power=1.8),
            Skill("Боевой клич", 15, "+8 к атаке до конца боя", "buff", value=8),
            Skill("Второе дыхание", 20, "восстановить 35% HP", "heal", heal_pct=0.35),
        ),
    ),
    "Маг": HeroClass(
        name="Маг",
        motto="тайные знания и стихии",
        hp=100,
        mana=120,
        attack=12,
        defense=2,
        skills=(
            Skill("Огненный шар", 18, "урон в 2.1 раза больше", "damage", power=2.1),
            Skill("Ледяная стрела", 22, "1.4x урон и враг пропускает ход", "freeze", power=1.4),
            Skill("Исцеление", 28, "восстановить 40% HP", "heal", heal_pct=0.40),
        ),
    ),
    "Стрелок": HeroClass(
        name="Стрелок",
        motto="меткий глаз и верная стрела",
        hp=120,
        mana=70,
        attack=13,
        defense=4,
        skills=(
            Skill("Точный выстрел", 12, "1.7x урон, шанс крита 35%", "damage", power=1.7, crit=0.35),
            Skill("Двойной выстрел", 16, "два попадания по 0.9x", "multi", power=0.9, hits=2),
            Skill("Ядовитая стрела", 14, "0.8x урон и яд на 3 хода", "poison", power=0.8, value=6, duration=3),
        ),
    ),
    "Ассасин": HeroClass(
        name="Ассасин",
        motto="тень, клинок и точный расчёт",
        hp=112,
        mana=80,
        attack=14,
        defense=3,
        skills=(
            Skill("Удар в спину", 12, "2.0x урон, шанс крита 25%", "damage", power=2.0, crit=0.25),
            Skill("Дымовая завеса", 14, "уклониться от следующей атаки", "dodge"),
            Skill("Отравленный клинок", 16, "урон и сильный яд на 3 хода", "poison", power=1.0, value=8, duration=3),
        ),
    ),
}


#Магазин

HEALTH_POTION_PRICE = 25
MANA_POTION_PRICE = 20
HEAL_PCT = 0.45
MANA_PCT = 0.50


#ИГРОК И ВРАГИ



@dataclass
class Player:
    name: str
    hero_class: HeroClass
    max_hp: int
    hp: int
    max_mana: int
    mana: int
    base_attack: int
    defense: int
    gold: int
    weapon: Weapon
    owned: List[Weapon] = field(default_factory=list)
    hp_potions: int = 1
    mana_potions: int = 1
    buff_attack: int = 0
    dodge: bool = False
    kills: int = 0

    @property
    def attack(self) -> int:
        return self.base_attack + self.weapon.bonus + self.buff_attack

    @property
    def alive(self) -> bool:
        return self.hp > 0

    @property
    def cls_name(self) -> str:
        return self.hero_class.name

    @property
    def skills(self) -> Tuple[Skill, ...]:
        return self.hero_class.skills


@dataclass
class Enemy:
    name: str
    max_hp: int
    attack: int
    defense: int
    gold: int
    intro: str = ""
    special: str = ""
    special_power: float = 1.5
    special_every: int = 0
    hp: int = 0
    poison_turns: int = 0
    poison_damage: int = 0
    frozen: bool = False
    turn: int = 0

    def __post_init__(self) -> None:
        self.hp = self.max_hp


def make_mobs() -> List[Enemy]:
    return [
        Enemy(
            name="Лесной гоблин",
            max_hp=55,
            attack=9,
            defense=1,
            gold=35,
            intro="Из-за кустов выпрыгивает гоблин с ржавым ножом. Он явно голоден!",
        ),
        Enemy(
            name="Волк-альфа",
            max_hp=78,
            attack=11,
            defense=2,
            gold=50,
            intro="Стая отступила, но вожак остался. Волк скалится и медленно обходит вас.",
        ),
        Enemy(
            name="Разбойник из чащи",
            max_hp=98,
            attack=13,
            defense=3,
            gold=70,
            intro="На тропу выходит разбойник. «Кошелёк или жизнь», — усмехается он.",
        ),
    ]


def make_boss() -> Enemy:
    return Enemy(
        name="Горток, король гоблинов",
        max_hp=200,
        attack=15,
        defense=4,
        gold=150,
        intro=(
            "Пещера. На троне из костей сидит огромный гоблин в железной короне.\n"
            "«Кто посмел войти в мои владения?!» — ревёт Горток и поднимает булаву."
        ),
        special="Королевский удар",
        special_power=1.6,
        special_every=3,
    )



#БОЕВАЯ МАТЕМАТИКА


def roll_damage(raw: float, defense: int) -> int:
    damage = (raw - defense * 0.6) * random.uniform(0.9, 1.1)
    return max(1, round(damage))


def player_attack(p: Player, e: Enemy) -> None:
    crit = random.random() < 0.10
    damage = roll_damage(p.attack, e.defense)
    if crit:
        damage = round(damage * 1.5)
    e.hp = max(0, e.hp - damage)
    text = f"Вы бьёте {e.name} и наносите {damage} урона."
    print(yellow("КРИТ! ") + text if crit else text)


def apply_skill(p: Player, e: Enemy, skill: Skill) -> None:
    p.mana -= skill.mana
    print(cyan(f"\nВы применяете «{skill.name}»!"))

    if skill.kind == "heal":
        before = p.hp
        p.hp = min(p.max_hp, p.hp + int(p.max_hp * skill.heal_pct))
        print(green(f"Восстановлено {p.hp - before} HP."))
        return

    if skill.kind == "buff":
        p.buff_attack += skill.value
        print(yellow(f"Атака повышена на {skill.value} до конца боя (теперь {p.attack})."))
        return

    if skill.kind == "dodge":
        p.dodge = True
        print(cyan("Вы растворяетесь в дымке и готовы уклониться от следующей атаки."))
        return

    if skill.kind == "multi":
        total = 0
        for i in range(skill.hits):
            damage = roll_damage(p.attack * skill.power, e.defense)
            crit = random.random() < (skill.crit or 0.10)
            if crit:
                damage = round(damage * 1.5)
            e.hp = max(0, e.hp - damage)
            total += damage
            mark = yellow(" (крит!)") if crit else ""
            print(f"  Попадание {i + 1}: {damage} урона{mark}")
            if e.hp <= 0:
                break
        print(f"Всего нанесено {total} урона.")
        return

    crit = random.random() < (skill.crit or 0.10)
    damage = roll_damage(p.attack * skill.power, e.defense)
    if crit:
        damage = round(damage * 1.5)
    e.hp = max(0, e.hp - damage)
    text = f"Нанесено {damage} урона."
    print(yellow("КРИТ! ") + text if crit else text)

    if skill.kind == "freeze" and e.hp > 0:
        e.frozen = True
        print(cyan(f"{e.name} скован льдом и пропустит ход!"))
    elif skill.kind == "poison" and e.hp > 0:
        e.poison_damage = skill.value
        e.poison_turns = skill.duration
        print(green(f"{e.name} отравлен: {skill.value} урона в течение {skill.duration} ходов."))


def enemy_turn(p: Player, e: Enemy) -> None:
    print()

    if e.poison_turns > 0 and e.hp > 0:
        e.hp = max(0, e.hp - e.poison_damage)
        e.poison_turns -= 1
        print(green(f"Яд отнимает у {e.name} {e.poison_damage} HP (осталось {e.poison_turns} ход.)."))
        if e.hp <= 0:
            return

    if e.frozen:
        e.frozen = False
        print(cyan(f"{e.name} не может пошевелиться и пропускает ход."))
        return

    e.turn += 1
    if e.special and e.special_every and e.turn % e.special_every == 0:
        raw = e.attack * e.special_power
        move = e.special
    else:
        raw = e.attack
        move = "Атака"

    if p.dodge:
        p.dodge = False
        print(cyan(f"{e.name}: {move} — вы уклонились!"))
        return

    damage = roll_damage(raw, p.defense)
    p.hp = max(0, p.hp - damage)
    print(red(f"{e.name}: {move} — {damage} урона. У вас осталось {p.hp}/{p.max_hp} HP."))



#ИНТЕРФЕЙС БОЯ


def show_status(p: Player, e: Enemy) -> None:
    print()
    print(line("="))
    print(f"{bold(p.name)} — {p.hero_class.name}   {grey('золото: ' + str(p.gold))}")
    print(f"HP {bar(p.hp, p.max_hp, '32')} {p.hp}/{p.max_hp}   "
          f"MP {bar(p.mana, p.max_mana, '34')} {p.mana}/{p.max_mana}")
    extras = [f"оружие: {p.weapon.name} (+{p.weapon.bonus})"]
    if p.buff_attack:
        extras.append(yellow(f"клич: +{p.buff_attack} атаки"))
    if p.dodge:
        extras.append(cyan("готов уклониться"))
    print(" | ".join(extras))
    print(f"Зелья: здоровья x{p.hp_potions}, маны x{p.mana_potions}")
    print(line("-"))
    print(f"{bold(e.name)}: HP {bar(e.hp, e.max_hp, '31')} {e.hp}/{e.max_hp}")
    if e.poison_turns > 0:
        print(green(f"Отравлен: {e.poison_damage} урона, осталось {e.poison_turns} ход."))
    if e.frozen:
        print(cyan("Скован льдом — пропустит ход."))
    print(line("="))


def use_potion_menu(p: Player) -> bool:
    while True:
        print("\nЗелья:")
        print(f"  1. Здоровье x{p.hp_potions} (+{int(HEAL_PCT * 100)}% HP)")
        print(f"  2. Мана x{p.mana_potions} (+{int(MANA_PCT * 100)}% MP)")
        print("  0. Назад")
        raw = ask("> ")

        if raw == "0":
            return False

        if raw == "1":
            if p.hp_potions <= 0:
                print(red("Зелий здоровья нет."))
                continue
            if p.hp >= p.max_hp:
                print("Здоровье уже полное.")
                continue
            p.hp_potions -= 1
            before = p.hp
            p.hp = min(p.max_hp, p.hp + int(p.max_hp * HEAL_PCT))
            print(green(f"Вы выпили зелье здоровья: +{p.hp - before} HP."))
            return True

        if raw == "2":
            if p.mana_potions <= 0:
                print(red("Зелий маны нет."))
                continue
            if p.mana >= p.max_mana:
                print("Мана уже полная.")
                continue
            p.mana_potions -= 1
            before = p.mana
            p.mana = min(p.max_mana, p.mana + int(p.max_mana * MANA_PCT))
            print(blue(f"Вы выпили зелье маны: +{p.mana - before} MP."))
            return True

        print("Нет такого варианта.")


def use_skill_menu(p: Player, e: Enemy) -> bool:
    while True:
        print("\nУмения:")
        for i, skill in enumerate(p.skills, 1):
            note = red(" (мало маны)") if p.mana < skill.mana else ""
            print(f"  {i}. {skill.name} — {skill.mana} MP — {skill.desc}{note}")
        print("  0. Назад")
        raw = ask("> ")

        if raw == "0":
            return False
        if not (raw.isdigit() and 1 <= int(raw) <= len(p.skills)):
            print("Нет такого умения.")
            continue

        skill = p.skills[int(raw) - 1]
        if p.mana < skill.mana:
            print(red("Недостаточно маны."))
            continue
        if skill.kind == "heal" and p.hp >= p.max_hp:
            print("Здоровье уже полное.")
            continue
        if skill.kind == "buff" and p.buff_attack >= skill.value:
            print("Боевой клич уже действует.")
            continue
        if skill.kind == "dodge" and p.dodge:
            print("Вы уже готовы уклониться.")
            continue

        apply_skill(p, e, skill)
        return True


def player_turn(p: Player, e: Enemy) -> None:
    while True:
        print("\nЧто делаете?")
        print("  1. Атака")
        print("  2. Умение")
        print("  3. Зелье")
        raw = ask("> ")

        if raw == "1":
            player_attack(p, e)
            return
        if raw == "2":
            if use_skill_menu(p, e):
                return
            continue
        if raw == "3":
            if use_potion_menu(p):
                return
            continue
        print("Нет такого варианта.")


def combat(p: Player, e: Enemy) -> bool:
    p.buff_attack = 0
    p.dodge = False
    print()
    print(line("="))
    print(bold(e.name))
    print(e.intro)
    print(line("="))

    while p.alive and e.hp > 0:
        show_status(p, e)
        player_turn(p, e)
        if e.hp <= 0:
            break
        enemy_turn(p, e)

    print()
    if not p.alive:
        return False

    print(green(f"{e.name} повержен!"))
    p.kills += 1
    return True


#  МАГАЗИН


def shop(p: Player, title: str) -> None:
    weapons = WEAPONS[p.hero_class.name]

    while True:
        print()
        print(line("="))
        print(bold("ЛАВКА: " + title))
        print(f"Золото: {yellow(str(p.gold))}   "
              f"Зелья: HP x{p.hp_potions}, MP x{p.mana_potions}")
        print(f"В руках: {p.weapon.label()}")
        print(line("-"))
        print(f"  1. Зелье здоровья — {HEALTH_POTION_PRICE} золота (+{int(HEAL_PCT * 100)}% HP)")
        print(f"  2. Зелье маны     — {MANA_POTION_PRICE} золота (+{int(MANA_PCT * 100)}% MP)")
        print("  Оружие вашего класса (выберите 3-5):")
        for i, weapon in enumerate(weapons, 3):
            if weapon == p.weapon:
                state = green("в руках")
            elif weapon in p.owned:
                state = "куплено (нажмите, чтобы взять)"
            elif weapon.price == 0:
                state = "стартовое"
            else:
                state = f"{weapon.price} золота"
            print(f"     {i}. {weapon.label()} — {state}")
        print("  0. Уйти")
        raw = ask("> ")

        if raw == "0":
            print(grey("Вы выходите из лавки."))
            return

        if raw == "1":
            if p.gold < HEALTH_POTION_PRICE:
                print(red("Не хватает золота."))
            else:
                p.gold -= HEALTH_POTION_PRICE
                p.hp_potions += 1
                print(green(f"Куплено зелье здоровья. Всего: {p.hp_potions}."))
            continue

        if raw == "2":
            if p.gold < MANA_POTION_PRICE:
                print(red("Не хватает золота."))
            else:
                p.gold -= MANA_POTION_PRICE
                p.mana_potions += 1
                print(blue(f"Куплено зелье маны. Всего: {p.mana_potions}."))
            continue

        if raw.isdigit() and 3 <= int(raw) <= 2 + len(weapons):
            weapon = weapons[int(raw) - 3]

            if weapon in p.owned:
                p.weapon = weapon
                print(green(f"Вы взяли {weapon.name}."))
            elif p.gold < weapon.price:
                print(red("Не хватает золота."))
            else:
                p.gold -= weapon.price
                p.owned.append(weapon)
                p.weapon = weapon
                print(green(f"Куплено и экипировано: {weapon.label()}!"))
            continue

        print("Нет такого варианта.")


#СОЗДАНИЕ ГЕРОЯ И СЮЖЕТ


def print_banner() -> None:
    print()
    print(line("="))
    print(bold("                  Т Р О П А   Г Е Р О Я"))
    print("         мини-квест: лес, мобы и король гоблинов")
    print(line("="))


def intro() -> None:
    print()
    print(bold("ПРОЛОГ"))
    print(
        "Деревня Холмогорье жила спокойно, пока из Зачарованного леса\n"
        "не повадились гоблины. Они жгут амбары, угоняют скот и требуют дань.\n"
        "Старейшина собирает героев, но идти вызвался только ты."
    )
    print(
        "\nТвой путь лежит через лес: три встречи с чудовищами, торговец\n"
        "у костра — и логово самого короля гоблинов."
    )


def create_player() -> Player:
    print()
    print(line("-"))
    print(bold("СОЗДАНИЕ ГЕРОЯ"))
    name = ask("Введите имя героя: ") or "Безымянный"

    classes = list(CLASSES.values())
    print("\nВыберите класс:")
    for i, hero_class in enumerate(classes, 1):
        print(f"  {i}. {bold(hero_class.name)} — {hero_class.motto}")

    while True:
        raw = ask("Номер класса: ")
        if raw.isdigit() and 1 <= int(raw) <= len(classes):
            hero_class = classes[int(raw) - 1]
            break
        print("Введите номер из списка.")

    print()
    print(bold(f"{hero_class.name}"))
    print(f"HP: {hero_class.hp}   Мана: {hero_class.mana}   "
          f"Атака: {hero_class.attack}   Защита: {hero_class.defense}")
    print("Оружие класса:")
    for weapon in WEAPONS[hero_class.name]:
        price = f"{weapon.price} золота" if weapon.price else "стартовое"
        print(f"  • {weapon.label()} — {price}")
    print("Умения класса:")
    for skill in hero_class.skills:
        print(f"  • {skill.name} ({skill.mana} MP) — {skill.desc}")

    starting_weapon = WEAPONS[hero_class.name][0]
    print()
    print(f"Итак, {bold(name)}! {hero_class.name} с оружием «{starting_weapon.name}» "
          f"отправляется в путь. Удачи!")
    print(grey("Совет: атака, умение и зелье — это по одному ходу. "
               "Следите за HP и маной, отдых между боями восстанавливает силы."))

    return Player(
        name=name,
        hero_class=hero_class,
        max_hp=hero_class.hp,
        hp=hero_class.hp,
        max_mana=hero_class.mana,
        mana=hero_class.mana,
        base_attack=hero_class.attack,
        defense=hero_class.defense,
        gold=50,
        weapon=starting_weapon,
        owned=[starting_weapon],
    )


#ЭКРАНЫ КОНЦА


def game_over(p: Player) -> None:
    print()
    print(line("="))
    print(red(bold("ВЫ ПАЛИ...")))
    print(f"{p.name}, ваш путь закончился в Зачарованном лесу.")
    print(f"Побеждено врагов: {p.kills}. Золото: {p.gold}.")
    print(line("="))


def victory(p: Player) -> None:
    print()
    print(line("="))
    print(green(bold("                    ПОБЕДА!")))
    print(line("="))
    print(
        f"{p.name} побеждает Гортока! Гоблины в панике бегут из леса,\n"
        "а над Холмогорьем снова встаёт спокойное солнце."
    )
    print()
    print(f"Класс: {p.hero_class.name}")
    print(f"Побеждено врагов: {p.kills}")
    print(f"Осталось золота: {p.gold}")
    print(f"Оружие: {p.weapon.label()}")
    print(line("="))



#ИГРОВОЙ ЦИКЛ

def play() -> bool:
    intro()
    player = create_player()
    shop(player, "Деревенский рынок")

    mobs = make_mobs()
    for number, mob in enumerate(mobs, 1):
        print()
        print(line("="))
        print(bold(f"ЛЕСНАЯ ТРОПА — ВРАГ {number} ИЗ {len(mobs)}"))
        print(line("="))

        if not combat(player, mob):
            game_over(player)
            return False

        player.gold += mob.gold
        heal = int(player.max_hp * 0.25)
        mana = int(player.max_mana * 0.40)
        player.hp = min(player.max_hp, player.hp + heal)
        player.mana = min(player.max_mana, player.mana + mana)
        print(f"Добыча: {yellow(str(mob.gold) + ' золота')}. "
              f"Отдых: +{heal} HP, +{mana} MP.")

        shop(player, "Торговец у костра")

    boss = make_boss()
    print()
    print(line("="))
    print(bold("ЛОГОВО КОРОЛЯ ГОБЛИНОВ"))
    print(line("="))

    if not combat(player, boss):
        game_over(player)
        return False

    player.gold += boss.gold
    victory(player)
    return True


def main() -> None:
    print_banner()
    while True:
        play()
        print()
        again = ask("Сыграть ещё раз? (д/н): ").lower()
        if again not in ("д", "да", "y", "yes"):
            print("Спасибо за игру!")
            break
        print_banner()


if __name__ == "__main__":
    main()
