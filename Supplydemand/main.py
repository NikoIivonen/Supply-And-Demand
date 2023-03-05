import pygame
from time import time
from random import randint, uniform, choice
from math import sqrt, log2, floor, tanh


pygame.init()
screen = pygame.display.set_mode( (1200, 1000) )

font = pygame.font.SysFont("Arial", 20, True)
font_time = pygame.font.SysFont("Arial", 40, True)

lowest_price = 10
highest_quality = 10

img_shop = pygame.image.load("shop.png").convert_alpha()
img_customer = pygame.image.load("customer.png").convert_alpha()

def sign():
    return choice([-1,1,1,1,1,1,1,1,1,1])

def dist(x1, x2, y1, y2):
    return sqrt( (x1-x2)**2 + (y1-y2)**2 )

def r(m):
    return randint(0, m)

def get_time(d, h, m):
    global lowest_price, highest_quality
    hour = h
    mins = m
    day = d
    mins += 1.5
    if mins >= 60:
        mins = 0
        hour += 1
    if hour >= 24:
        hour = 0
        mins = 0
        day += 1
        for c in customers:
            c.pay()
            c.x = c.home.x
            c.y = c.home.y
            c.satisfied = False
            c.choose_shop()

        lowest_price = sorted(shops, key=lambda s: s.price)[0].price
        highest_quality = sorted(shops, key=lambda s: s.quality)[-1].quality
        for s in shops:
            s.pay()
            s.change_price()

        if day >= 15:
            day = 1
            new_gen()
            print(len(shops), len(houses), len(customers))

        print("-------------------------------")
    return day, hour, mins


class Customer:

    def __init__(self, i):
        self.home = houses[i]
        self.home.family.append(self)
        self.x = self.home.x
        self.y = self.home.y
        self.customer = pygame.Rect(self.x, self.y, 10, 10)
        self.money = 100
        self.costs = randint(10, 30)
        self.salary = randint(20, 50)
        self.cheapest = None
        self.need = 1
        self.satisfied = False
        self.speed = 30
        self.max_price = randint(7, 20)

    def pay(self):
        self.money += self.salary
        self.money -= self.costs
        self.satisfied = False

    def draw(self):
        self.customer = pygame.Rect(self.x, self.y, 10, 10)
        screen.blit(img_customer, (self.x, self.y))
        # text = font.render(f"${self.money:.2f}", True, (0, 0, 0))
        # screen.blit(text, (self.x, self.y))

    def choose_shop(self):
        max_dist = 1100/( sqrt(max(self.money, 0.01))*0.1 )
        shops_in_range = [ s for s in shops if dist(self.home.x, s.x, self.home.y, s.y) <= max_dist and s.price <= self.max_price ]
        cheapest = sorted( shops_in_range, key=lambda s: (s.price - s.quality, dist(self.home.x, s.x, self.home.y, s.y)))
        if len(cheapest) == 0:
            self.cheapest = None
            self.satisfied = True
        else:
            self.cheapest = cheapest[0]

    def move(self):
        if not self.satisfied:
            dx = self.cheapest.x - self.x
            dy = self.cheapest.y - self.y

            self.x += dx/self.speed
            self.y += dy/self.speed

            if dist(self.x, self.cheapest.x, self.y, self.cheapest.y) <= 5:
                can_spend = max(self.money - self.costs, 0)
                try:
                    can_buy = floor(can_spend / self.cheapest.price)
                except:
                    print(self.cheapest.price, self.cheapest.cost_per_item, self.cheapest.quality, self.cheapest.min_price)
                amount = min(can_buy, self.need)
                self.money -= amount * self.cheapest.price
                self.cheapest.money_gotten += amount * self.cheapest.price
                self.cheapest.sold += amount
                self.satisfied = True
        else:
            dx = self.home.x - self.x
            dy = self.home.y - self.y

            self.x += dx/self.speed
            self.y += dy/self.speed


class House:

    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.house = pygame.Rect(self.x, self.y, 20, 20)
        self.family = []
        self.color = (220, 0, 0)

    def draw(self):
        self.house = pygame.Rect(self.x, self.y, 20, 20)
        pygame.draw.rect(screen, self.color, self.house)


class Shop:

    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.shop = pygame.Rect(self.x, self.y, 100, 100)
        self.profit_yd = 0
        self.cost_per_item = randint(3, 6)
        self.costs = randint(25, 50)
        self.price = 10
        self.color = (139, 69, 19)
        self.money_gotten = 0
        self.sold = 0
        self.weights = [uniform(-1, 1), uniform(-1, 1), uniform(-1, 1), uniform(-1, 1), uniform(-1, 1)]
        self.weights1 = [uniform(-1, 1), uniform(-1, 1), uniform(-1, 1), uniform(-1, 1), uniform(-1, 1)]
        self.total_profit = 0
        self.min_price = self.cost_per_item + 1
        self.quality = 10

    def change_price(self):
        data = [self.profit_yd, self.costs, self.price-self.cost_per_item, lowest_price, highest_quality]
        total = 0
        for i, d in enumerate(data):
            total += self.weights[i]*d

        output = tanh(total)
        change = round(output*100,2)/100
        # print([ float(f"{w:.3f}") for w in self.weights ], " | ", total, " | ", output)
        self.price += change
        print(change)

        total = 0
        for i, d in enumerate(data):
            total += self.weights1[i]*d

        output = tanh(total)
        change = round(output*100,2)/100
        # print([ float(f"{w:.3f}") for w in self.weights ], " | ", total, " | ", output)
        if self.quality > 1:
            self.quality += change
            self.quality = max(1, self.quality)
            self.cost_per_item += change / 2
            self.min_price = self.cost_per_item + 1

        self.min_price = max(1, self.min_price)
        self.price = max(self.price, self.min_price)
        self.cost_per_item = max(self.cost_per_item, 1)

    def draw(self):
        screen.blit(img_shop, (self.x, self.y))

        text = font.render(f"${self.price:.2f} | {self.quality:.2f} | ${self.cost_per_item:.2f} | ${self.costs:.2f}", True, (0, 0, 0))
        screen.blit(text, (self.x, self.y + 40))
        text = font.render(f"${self.total_profit:.2f}", True, (0, 0, 0))
        screen.blit(text, (self.x, self.y + 60))

    def pay(self):
        self.profit_yd = self.money_gotten - self.cost_per_item*self.sold - self.costs
        self.money_gotten = 0
        self.sold = 0
        self.total_profit += self.profit_yd

    def children(self, n):
        childs = []
        for _ in range(n):
            new_weights = [ w*uniform(0.9, 1.1)*sign() for w in self.weights ]
            child = Shop(r(1100), r(900))
            child.weights = new_weights
            childs.append(child)

        return childs



shops = [ Shop(r(1100), r(900)) for _ in range(6) ]
houses = [ House(r(1100), r(900)) for _ in range(100) ]
customers = [ Customer(c) for c in range(100) ]

def overlap():

    for house in houses:
        if any( [house.house.colliderect(s.shop) for s in shops] ):
            houses.remove(house)
            for c in house.family:
                customers.remove(c)

overlap()

def new_gen():
    global shops, houses, customers, gen
    print("Hei")
    best = sorted( shops, key=lambda s: s.total_profit, reverse=True)[:2]
    shops.clear()
    for b in best:
        shops += b.children(3)
    houses = [House(r(1100), r(900)) for _ in range(100)]
    customers = [Customer(c) for c in range(100)]
    overlap()
    gen += 1
    for c in customers:
        c.choose_shop()

day = 1
hour = 0
mins = 0

print(len(customers), len(houses))

for c in customers:
    c.choose_shop()

gen = 1

while True:

    for e in pygame.event.get():
        if e.type == pygame.QUIT:
            pygame.quit()
            exit()

    screen.fill( (220, 220, 220) )


    """HOUSES"""

    for house in houses:
        house.draw()

    """SHOPS"""

    for shop in shops:
        shop.draw()

    """CUSTOMERS"""

    for cust in customers:
        cust.draw()
        cust.move()

    """TIME"""

    day, hour, mins = get_time(day, hour, mins)
    sh = f"0{hour}" if hour < 10 else hour
    sm = f"0{mins:.0f}" if mins < 10 else f"{mins:.0f}"
    text = font_time.render(f"{sh}:{sm}   Day {day}", True, (0,0,0))
    screen.blit(text, (450, 50))

    text = font_time.render(f"Gen {gen}", True, (0,0,0))
    screen.blit(text, (450, 10))

    pygame.display.flip()