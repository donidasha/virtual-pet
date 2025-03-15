import json
import pygame as pg
import random
# Коментарий
# инициализация pg
pg.init()

# Иконка
icon = pg.image.load("images/health.png")
pg.display.set_icon(icon)

# размеры окна
SCREEN_WIDTH = 900
SCREEN_HEIGHT = 550

ICON_SIZE = 80

DOG_WIDTH = 310
DOG_HEIGHT = 500

BUTTON_WIDTH = 200
BUTTON_HEIGHT = 60

FOOD_SIZE = 200
TOY_SIZE = 100

GRID = 10

FPS = 60

font = pg.font.Font(None, 40)
font_mini = pg.font.Font(None, 15)
font_maxi = pg.font.Font(None, 200)

def load_image(file, width, height):
    image = pg.image.load(file).convert_alpha()
    image = pg.transform.scale(image, (width, height))
    return image

def text_render(text):
    return font.render(str(text), True, "black")

# Исходные данные
new_game_data = {
    "happiness": 100,
    "satiety": 100,
    "health": 100,
    "money": 0,
    "coins_per_second": 1,
    "costs_of_upgrade": {
        "100": False,
        "1000": False,
        "5000": False,
        "10000": False
    },
    "clothes": [
        {
            "name": "Синяя футболка",
            "price": 10,
            "image": "images/items/blue t-shirt.png",
            "is_using": False,
            "is_bought": False
        },
        {
            "name": "Ботинки",
            "price": 50,
            "image": "images/items/boots.png",
            "is_using": False,
            "is_bought": False
        },
        {
            "name": "Шляпа",
            "price": 50,
            "image": "images/items/hat.png",
            "is_using": False,
            "is_bought": False
        }
    ]
}

class Dog(pg.sprite.Sprite):
    def __init__(self):
        pg.sprite.Sprite.__init__(self)
        
        self.image = load_image("images/dog.png", DOG_WIDTH // 2, DOG_HEIGHT // 2)
        self.rect = self.image.get_rect()
        
        self.rect.centerx = SCREEN_WIDTH // 2
        self.rect.centery = SCREEN_HEIGHT - GRID * 14
    
    def update(self):
        keys = pg.key.get_pressed()
        if keys[pg.K_a]:
            self.rect.x -= 2
        if keys[pg.K_d]:
            self.rect.x += 2
            
class Toy(pg.sprite.Sprite):
    def __init__(self):
        pg.sprite.Sprite.__init__(self)
        file = random.choice(["images/toys/ball.png", "images/toys/blue bone.png", "images/toys/red bone.png"])
        
        self.image = load_image(file, TOY_SIZE, TOY_SIZE)
        self.rect = self.image.get_rect()
        
        self.rect.x = random.randint(GRID * 9 , SCREEN_WIDTH - GRID * 23)
        self.rect.y = 30
        
    def update(self):
        self.rect.y +=2
        

class Item:
    def __init__(self, name, price, file, is_using, is_bought):
        self.name = name
        self.price = price
        self.file = file
        self.image = load_image(file, DOG_WIDTH // 1.7, DOG_HEIGHT // 1.7)
        self.is_using = is_using
        self.is_bought = is_bought
        
        self.full_image = load_image(file, DOG_WIDTH, DOG_HEIGHT)
        
        
class Button:
    def __init__(self, text, x, y, width=BUTTON_WIDTH, height=BUTTON_HEIGHT, text_font=font, func=None):
        self.func=func
        
        self.image = load_image("images/button.png", width, height)
        self.rect = self.image.get_rect()
        self.rect.topleft = (x, y)
        
        self.text_font = text_font
        self.text = self.text_font.render(str(text), True, "black")
        self.text_rect = self.text.get_rect()
        self.text_rect.center = self.rect.center
        
    def draw(self, screen):
        screen.blit(self.image, self.rect)
        screen.blit(self.text, self.text_rect)
        
    def is_clicked(self, event):
        if event.type == pg.MOUSEBUTTONDOWN and event.button == 1:
            if self.rect.collidepoint(event.pos):
                self.func()
        
class ClothesMenu:
    def __init__(self, game, data):
        self.game = game
        
        self.menu_page = load_image("images/menu/menu_page.png", SCREEN_WIDTH, SCREEN_HEIGHT)
        
        # список одежды
        self.items = []
        
        for item in data:
            item_object = Item(item["name"],item["price"], item["image"], item["is_using"], item["is_bought"])
            
            self.items.append(item_object)
            
        self.current_item = 0
        self.render_item()
        self.next_button = Button("Вперёд", SCREEN_WIDTH - BUTTON_WIDTH - GRID * 10, SCREEN_HEIGHT - GRID * 14,
                                  width=BUTTON_WIDTH // 1.2, height=BUTTON_HEIGHT // 1.2, func=self.to_next)
        self.previous_button = Button("Назад", GRID * 14, SCREEN_HEIGHT - GRID * 14,
                                      width=BUTTON_WIDTH // 1.2, height=BUTTON_HEIGHT // 1.2, func=self.to_previous)
        self.buy_button = Button("Купить", SCREEN_WIDTH // 2.5, SCREEN_HEIGHT // 2 + GRID * 10,
                                 width=BUTTON_WIDTH // 1.2, height=BUTTON_HEIGHT // 1.2, func=self.buy)
        self.use_button = Button("Надеть", GRID * 14, SCREEN_HEIGHT - BUTTON_HEIGHT - GRID * 14,
                                 width=BUTTON_WIDTH // 1.2, height=BUTTON_HEIGHT // 1.2, func=self.use_item)
        
        self.use_text = text_render("Надето")
        self.use_text_rect = self.use_text.get_rect()
        self.use_text_rect.midright = (SCREEN_WIDTH - GRID * 15, GRID * 13)
        
        self.buy_text = text_render("Куплено")
        self.buy_text_rect = self.buy_text.get_rect()
        self.buy_text_rect.midright = (SCREEN_WIDTH - GRID * 14, GRID * 20)
        
        self.bottom_label_off = load_image("images/menu/bottom_label_off.png", SCREEN_WIDTH, SCREEN_HEIGHT)
        self.bottom_label_on = load_image("images/menu/bottom_label_on.png", SCREEN_WIDTH, SCREEN_HEIGHT)
        self.top_label_off = load_image("images/menu/top_label_off.png", SCREEN_WIDTH, SCREEN_HEIGHT)
        self.top_label_on = load_image("images/menu/top_label_on.png", SCREEN_WIDTH, SCREEN_HEIGHT)

    def render_item(self):
        self.item_rect = self.items[self.current_item].image.get_rect()
        self.item_rect.center = (SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2)
        
        self.price_text = text_render(self.items[self.current_item].price)
        self.price_text_rect = self.price_text.get_rect()
        self.price_text_rect.center = (SCREEN_WIDTH // 2, GRID * 18)
        
        self.name_text = text_render(self.items[self.current_item].name)
        self.name_text_rect = self.name_text.get_rect()
        self.name_text_rect.center =(SCREEN_WIDTH // 2, GRID * 12)
        
    def to_next(self):
        if self.current_item != len(self.items) - 1:
            self.current_item +=1
            self.render_item()
            
    def to_previous(self):
        if self.current_item!= 0:
            self.current_item -= 1
            self.render_item()
            
    def buy(self):
        # clothes_item = self.items[self.current_item]
        if self.game.money >= self.items[self.current_item].price and not self.items[self.current_item].is_bought:
            self.game.money -= self.items[self.current_item].price
            self.items[self.current_item].is_bought = True
            
    def use_item(self):
        if self.items[self.current_item].is_bought:
            self.items[self.current_item].is_using = not self.items[self.current_item].is_using
            
            
            
    def draw(self, screen):
        screen.blit(self.menu_page, (0, 0))
        
        screen.blit(self.items[self.current_item].image, self.item_rect)
        screen.blit(self.price_text, self.price_text_rect)
        screen.blit(self.name_text, self.name_text_rect)
        
        if self.items[self.current_item].is_bought:
            screen.blit(self.bottom_label_on, (0, 0))
        else:
            screen.blit(self.bottom_label_off, (0, 0))
            
        if self.items[self.current_item].is_using:
            screen.blit(self.top_label_on, (0, 0))
        else:
            screen.blit(self.top_label_off, (0, 0))
        
        self.next_button.draw(screen)
        self.previous_button.draw(screen)
        self.buy_button.draw(screen)
        self.use_button.draw(screen)
        
        screen.blit(self.price_text, self.price_text_rect)
        screen.blit(self.name_text, self.name_text_rect)
        screen.blit(self.use_text, self.use_text_rect)
        screen.blit(self.buy_text, self.buy_text_rect)
        
class Food:
    def __init__(self,name, price, file, satiety, medicine_power=0):
        self.name = name
        self.price = price
        self.file = file
        self.satiety = satiety
        self.medicine_power = medicine_power
        self.image = load_image(file, FOOD_SIZE, FOOD_SIZE)
        
class FoodMenu:
    def __init__(self, game):
        self.game = game
        
        self.menu_page = load_image("images/menu/menu_page.png", SCREEN_WIDTH, SCREEN_HEIGHT)
        
        # список еды
        self.items = [Food("Мясо", 30, "images/food/meat.png", 10),
                      Food("Корм", 40, "images/food/dog food.png", 15),
                      Food("Элитный корм", 100, "images/food/dog food elite.png", 25, medicine_power=2),
                      Food("Лекарство", 200, "images/food/medicine.png", 0, medicine_power=10)]
        
        self.current_item = 0
        self.render_item()
        
        self.next_button = Button("Вперёд", SCREEN_WIDTH - BUTTON_WIDTH - GRID * 10, SCREEN_HEIGHT - GRID * 14,
                                  width=BUTTON_WIDTH // 1.2, height=BUTTON_HEIGHT // 1.2, func=self.to_next)
        self.previous_button = Button("Назад", GRID * 14, SCREEN_HEIGHT - GRID * 14,
                                      width=BUTTON_WIDTH // 1.2, height=BUTTON_HEIGHT // 1.2, func=self.to_previous)
        self.buy_button = Button("Купить", SCREEN_WIDTH // 2.5, SCREEN_HEIGHT // 2 + GRID * 10,
                                 width=BUTTON_WIDTH // 1.2, height=BUTTON_HEIGHT // 1.2, func=self.buy)
        
    def render_item(self):
        self.item_rect = self.items[0].image.get_rect()
        self.item_rect.center = (SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2)
        
        self.price_text = text_render(self.items[self.current_item].price)
        self.price_text_rect = self.price_text.get_rect()
        self.price_text_rect.center = (SCREEN_WIDTH // 2, GRID * 18)
        
        self.name_text = text_render(self.items[self.current_item].name)
        self.name_text_rect = self.name_text.get_rect()
        self.name_text_rect.center = (SCREEN_WIDTH // 2, GRID * 12)
        
    def to_next(self):
        if self.current_item != len(self.items) - 1:
            self.current_item +=1
            self.render_item()
            
    def to_previous(self):
        if self.current_item!= 0:
            self.current_item -= 1
            self.render_item()
        
    def buy(self):
        if self.game.money >= self.items[self.current_item].price:
            self.game.money -= self.items[self.current_item].price
            # self.items[self.current_item].is_bought
            self.game.satiety += self.items[self.current_item].satiety
            
    def draw(self, screen):
        screen.blit(self.menu_page, (0, 0))
        
        screen.blit(self.items[self.current_item].image, self.item_rect)
        screen.blit(self.price_text, self.price_text_rect)
        screen.blit(self.name_text, self.name_text_rect)
        
        self.next_button.draw(screen)
        self.previous_button.draw(screen)
        self.buy_button.draw(screen)
        
class MiniGame:
    def __init__(self, game):
        self.game = game
        
        self.background = load_image("images/game_background.png", SCREEN_WIDTH, SCREEN_HEIGHT)
        # Начинаем игру
        self.new_game()
        
    def new_game(self):
        self.dog = Dog()
        self.score = 0
        self.toys = pg.sprite.Group()
        self.start_time = pg.time.get_ticks()
        self.interval = 1000 * 15
        
    def update(self):
        self.dog.update()
        self.toys.update()
        if random.randint(0, 100) == 0:
            self.toys.add(Toy())
        hits = pg.sprite.spritecollide(self.dog, self.toys, True, pg.sprite.collide_rect_ratio(0.6))
        self.score += len(hits)
        if pg.time.get_ticks() - self.start_time > self.interval:
            self.game.happiness += int(self.score // 2)
            self.game.mode = "Main"
        
    def draw(self,screen):
        screen.blit(self.background, (0, 0))
        screen.blit(self.dog.image, self.dog.rect)
        score_text = text_render(self.score)
        screen.blit(score_text, (GRID * 11, GRID * 8))
        self.toys.draw(screen)
class Game:
    def __init__(self):
        # получаем данные из файла
        with open("save.json", "r", encoding="utf-8") as f:
            data = json.load(f)
            
        self.happiness = data["happiness"]
        self.satiety = data["satiety"]
        self.health = data["health"]
        self.money = data["money"]
        self.coins_per_second = data["coins_per_second"]
            
        self.items_on = []
            
        self.mode = "Main"
    
        
        # создание окна
        self.screen = pg.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pg.display.set_caption("Виртуальный питомец")
        
        self.mode = "Main"
        
        # загрузка фона
        self.background = load_image("images/background.png", SCREEN_WIDTH, SCREEN_HEIGHT)
        
        # загруска иконок
        
        self.happiness_image = load_image("images/happiness.png", ICON_SIZE, ICON_SIZE)
        self.satiety_image = load_image("images/satiety.png", ICON_SIZE, ICON_SIZE)
        self.health_image = load_image("images/health.png", ICON_SIZE, ICON_SIZE)
        self.money_image = load_image("images/money.png", ICON_SIZE, ICON_SIZE)
        
        # создание кнопок
        button_x = SCREEN_WIDTH - BUTTON_WIDTH - GRID

        self.eat_button = Button("Еда", button_x, GRID * 9, func=self.food_menu_on)
        self.clothes_button = Button("Одежда", button_x, GRID * 10 + BUTTON_HEIGHT, func=self.clothes_on)
        self.play_button = Button("Игры", button_x, GRID * 11 + BUTTON_HEIGHT * 2, func=self.game_on)


        
        # СОЗДАНИЕ СОБЫТИЙ ДЛЯ КЛИКЕРА
        self.INCREASE_COINS = pg.USEREVENT + 1
        pg.time.set_timer(self.INCREASE_COINS, 1000)
        
        self.DECREASE = pg.USEREVENT + 2
        pg.time.set_timer(self.DECREASE, 1000)
        
        self.clock = pg.time.Clock
        
        self.clothes_menu = ClothesMenu(self, data["clothes"])
        self.food_menu = FoodMenu(self)
        self.mini_game = MiniGame(self)
        
        
        #   загрузка изображений для собаки
        self.body = load_image("images/dog.png", DOG_WIDTH, DOG_HEIGHT)
        
        self.clock = pg.time.Clock()
        self.run()
        
    def food_menu_on(self):
        self.mode = "Food menu"
        print(self.mode)
        
    def clothes_on(self):
        self.mode = "Clothes menu"
        print(self.mode)
        
    def game_on(self):
        self.mode = "Mini game"
        self.mini_game.new_game()
        print(self.mode)
        
    def event(self):
        for event in pg.event.get():
            if event.type == pg.QUIT:
                if self.mode == "Game over":
                    data = new_game_data
                else:
                    data = {"happiness": self.happiness,
                            "satiety" : self.satiety,
                            "health" : self.health,
                            "money" : self.money,
                            "coins_per_second" : self.coins_per_second,
                            "clothes": []}
                    # Добавляем одежду
                    for item in self.clothes_menu.items:
                        data["clothes"].append({"name" : item.name,
                                                "price" : item.price,
                                                "image" : item.file,
                                                "is_using" : item.is_using,
                                                "is_bought" : item.is_bought})
                # Пересохраняем файл
                with open('save.json', 'w', encoding='utf-8') as f:
                    json.dump(data, f, ensure_ascii=False, indent=4)
                    
                pg.quit()
                exit()
            if event.type == pg.KEYDOWN:
                if event.key == pg.K_ESCAPE:
                    self.mode = "Main"
            if event.type == self.INCREASE_COINS:
                self.money += self.coins_per_second
                
            if event.type == self.DECREASE:
                chance = random.randint(1, 10)
                if chance < 5:
                    self.satiety -= self.coins_per_second
                elif chance < 9:
                    self.happiness -= self.coins_per_second
                else:
                    self.health -= self.coins_per_second
            if event.type == pg.MOUSEBUTTONDOWN and event.button == 1:
                self.money += self.coins_per_second
            if self.mode == "Main":
                self.eat_button.is_clicked(event)
                self.clothes_button.is_clicked(event)
                self.play_button.is_clicked(event)
            if self.mode == "Clothes menu":
                self.clothes_menu.next_button.is_clicked(event)
                self.clothes_menu.previous_button.is_clicked(event)
                self.clothes_menu.buy_button.is_clicked(event)
                self.clothes_menu.use_button.is_clicked(event)
            if self.mode == "Food menu":
                self.food_menu.draw
                self.food_menu.next_button.is_clicked(event)
                self.food_menu.previous_button.is_clicked(event)
                self.food_menu.buy_button.is_clicked(event)
            

                
    def update(self):
        if self.happiness <=0 or self.satiety <=0 or self.health <=0:
            self.mode = "Game over"
            
        if self.mode == "Mini game":
            self.mini_game.update()
        
    def draw(self):
        # отрисовка интерфейса
        self.screen.blit(self.background, (0, 0))
        
        # отрисовка собаки
        self.screen.blit(self.body, (SCREEN_WIDTH // 2 - DOG_WIDTH // 2 , GRID * 10))
        
        for item in self.clothes_menu.items:
            if item.is_using:
                self.screen.blit(item.full_image, (SCREEN_WIDTH // 2 - DOG_WIDTH// 2, GRID *10))
        
        
        
        
        
        # отрисовка иконок
        self.screen.blit(self.happiness_image,(GRID, GRID))
        self.screen.blit(self.satiety_image,(GRID, GRID * 10))
        self.screen.blit(self.health_image,(GRID, GRID * 20))
        self.screen.blit(self.money_image,(SCREEN_WIDTH - GRID *10, GRID))
        
        self.screen.blit(text_render(self.happiness), (GRID + ICON_SIZE, GRID * 4))
        self.screen.blit(text_render(self.satiety), (GRID + ICON_SIZE, GRID * 5 + ICON_SIZE))
        self.screen.blit(text_render(self.health), (GRID + ICON_SIZE, GRID * 6 + ICON_SIZE * 2))
        self.screen.blit(text_render(self.money), (SCREEN_WIDTH - GRID * 15, GRID * 4))
        
        # отрисовка кнопок
        self.eat_button.draw(self.screen)
        self.clothes_button.draw(self.screen)
        self.play_button.draw(self.screen)
        
        if self.mode == "Clothes menu":
            self.clothes_menu.draw(self.screen)
            
        if self.mode == "Food menu":
            self.food_menu.draw(self.screen)
        
        if self.mode == "Mini game":
            self.mini_game.draw(self.screen)
            
        if self.mode == "Game over":
            text = font_maxi.render("ПРОИГРЫШ!", True, "red")
            text_rect = text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2))
            self.screen.blit(self.background, (0, 0))
            self.screen.blit(text, text_rect)
            
            
            
        





        
    def run(self):
        while True:
            self.event()
            self.update()
            self.draw()
            pg.display.flip()
            self.clock.tick(FPS)
        
# точка входа в игру
if __name__ == "__main__":
    Game()
