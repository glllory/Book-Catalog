from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from database_setup import Base, Category, Item, User

engine = create_engine('sqlite:///catalog.db')
Base.metadata.bind = engine
DBSession = sessionmaker(bind=engine)
session = DBSession()
Base.metadata.drop_all()
Base.metadata.create_all()

# Add users
User1 = User(name="Majd Saleh", email="mjd.s.m55@gmail.com")
session.add(User1)
session.commit()


# Add categories
category1 = Category(name="Comics")
session.add(category1)
session.commit()

category2 = Category(name="Fiction")
session.add(category2)
session.commit()

category3 = Category(name="Classics")
session.add(category3)
session.commit()

category4 = Category(name="Fantasy")
session.add(category4)
session.commit()


# Add items
# category1
item = Item(name="Paper Girls, Vol. 5", description="...... etc..",
            category_id=category1.id, user_id=User1.id)
session.add(item)
session.commit()

item = Item(name="Mera: Queen of Atlantis", description="Just in time..etc..",
            category_id=category1.id, user_id=User1.id)
session.add(item)
session.commit()

item = Item(name="Eternity Girl", description="aroline Sharp has been a etc..",
            category_id=category1.id, user_id=User1.id)
session.add(item)
session.commit()

# category2
item = Item(name="The Disasters",
            description="Hotshot pilot Nax Hall has a history of etc..",
            category_id=category2.id, user_id=User1.id)
session.add(item)
session.commit()

item = Item(name="Once Upon a River",
            description="Hotshot pilot Nax Hall has a history of etc..",
            category_id=category2.id, user_id=User1.id)
session.add(item)
session.commit()

item = Item(name="The Blue",
            description="In eighteenth century London, porcelain .. etc..",
            category_id=category2.id, user_id=User1.id)
session.add(item)
session.commit()

# category3
item = Item(name="Fahrenheit 451",
            description="Guy Montag is a fireman. In his world, where etc..",
            category_id=category3.id, user_id=User1.id)
session.add(item)
session.commit()

item = Item(name="1984",
            description="Among the seminal texts of the 20th century, etc..",
            category_id=category3.id, user_id=User1.id)
session.add(item)
session.commit()

item = Item(name="Brave New World",
            description="Brave New World is a dystopian novel written ..etc..",
            category_id=category3.id, user_id=User1.id)
session.add(item)
session.commit()

# category4
item = Item(name="Evermore",
            description="Jules Ember was raised hearing legends of the etc..",
            category_id=category4.id, user_id=User1.id)
session.add(item)
session.commit()

item = Item(name="The Cursed Sea",
            description="Wilhemina Heidle, the exiled princess of ..  etc..",
            category_id=category4.id, user_id=User1.id)
session.add(item)
session.commit()

item = Item(name="CAPTIVE",
            description="An unapologetic and haunting tale of power, etc..",
            category_id=category4.id, user_id=User1.id)
session.add(item)
session.commit()

print("DONE")
